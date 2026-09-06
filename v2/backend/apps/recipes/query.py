"""Query helpers for catalog filters (same key OR, different keys AND)."""

from __future__ import annotations

from rest_framework.exceptions import APIException

from apps.recipes.constants import (
    ALLERGEN,
    COOK_METHOD,
    CUT,
    DISH_TYPE,
    EQUIPMENT,
    HAVE_GROUPS,
    INTENT,
    PROTEIN_BASE,
)


class BadQuery(APIException):
    status_code = 400
    default_detail = "Некорректный запрос."
    default_code = "bad_query"

FILTER_VOCAB = {
    "protein_base": PROTEIN_BASE,
    "cook_method": COOK_METHOD,
    "dish_type": DISH_TYPE,
    "equipment": EQUIPMENT,
    "cuts": CUT,
}


def split_query_values(request, key: str) -> list[str]:
    values: list[str] = []
    for raw in request.query_params.getlist(key):
        values.extend(part.strip() for part in raw.split(",") if part.strip())
    return values


def parse_codes(request, key: str) -> list[str]:
    allowed = FILTER_VOCAB[key]
    values = split_query_values(request, key)
    unknown = [code for code in values if code not in allowed]
    if unknown:
        raise BadQuery(f"Неизвестный код {key}: {', '.join(unknown)}")
    return values


def parse_optional_code(request, key: str, allowed: set[str]) -> str | None:
    raw = request.query_params.get(key)
    if raw is None or raw == "":
        return None
    value = str(raw).strip()
    if value not in allowed:
        raise BadQuery(f"Неизвестный код {key}: {value}")
    return value


def parse_have(
    request, known: set[str] | None = None, titles: dict[str, str] | None = None
) -> list[str]:
    """Pantry: shopping canonical, group, or Russian alias. Unknown → 400."""
    from apps.recipes.models import Ingredient
    from apps.recipes.pantry_vocab import CANONICAL_INGREDIENT_LABEL_RU, shopping_ids
    from apps.recipes.services.pantry import resolve_pantry_text, resolve_token

    values = split_query_values(request, "have")
    if not values:
        return []
    db_ids: set[str] = set()
    db_titles: dict[str, str] = {}
    if known is None:
        db_ids = set(Ingredient.objects.values_list("canonical_id", flat=True))
        db_titles = dict(Ingredient.objects.values_list("canonical_id", "title"))
    else:
        db_ids = set(known)
        db_titles = dict(titles or {})
    known = shopping_ids() | db_ids
    titles = {**CANONICAL_INGREDIENT_LABEL_RU, **db_titles}
    found: list[str] = []
    seen: set[str] = set()
    unknown: list[str] = []
    for raw in values:
        ids = resolve_token(raw, titles=titles, known=known)
        extra_unknown: list[str] = []
        if not ids:
            ids, extra_unknown = resolve_pantry_text(raw, titles=titles, known=known)
        if not ids:
            unknown.append(raw)
            continue
        unknown.extend(extra_unknown)
        for cid in ids:
            if cid not in seen:
                seen.add(cid)
                found.append(cid)
    if unknown:
        raise BadQuery(f"Неизвестный продукт: {', '.join(unknown)}")
    return found


def parse_have_groups(request) -> list[str]:
    values = split_query_values(request, "have_group")
    unknown = [code for code in values if code not in HAVE_GROUPS]
    if unknown:
        raise BadQuery(f"Неизвестный код have_group: {', '.join(unknown)}")
    return values


def parse_intent(request) -> list[str]:
    values = split_query_values(request, "intent")
    unknown = [code for code in values if code not in INTENT]
    if unknown:
        raise BadQuery(f"Неизвестный код intent: {', '.join(unknown)}")
    return values


def parse_without_allergens(request) -> list[str]:
    """«без чего»: `without` (preferred CSV) or `exclude_allergen`.

    Recipe is dropped if allergens.contains OR allergens.unknown includes the code.
    may_contain does not drop.
    """
    values = split_query_values(request, "without") or split_query_values(
        request, "exclude_allergen"
    )
    unknown = [code for code in values if code not in ALLERGEN]
    if unknown:
        raise BadQuery(f"Неизвестный код аллергена: {', '.join(unknown)}")
    return values


def parse_optional_decimal(request, key: str):
    raw = request.query_params.get(key)
    if raw is None or raw == "":
        return None
    from decimal import Decimal, InvalidOperation

    try:
        value = Decimal(str(raw).replace(",", "."))
    except (InvalidOperation, ValueError) as exc:
        raise BadQuery(f"Некорректное значение {key}.") from exc
    if value <= 0:
        raise BadQuery(f"{key} должен быть больше нуля.")
    return value
