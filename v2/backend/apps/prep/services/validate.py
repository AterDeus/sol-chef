"""Validate and upsert a weekly-prep kit JSON (DATA-MODEL invariants)."""

from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Any

from django.db import transaction

from apps.prep.models import PrepComponent, PrepContainer, PrepKit, PrepSlot
from apps.recipes.constants import UNIT
from apps.recipes.models import Recipe

FORBIDDEN_KEYS = frozenset(
    {
        "weekend_protocol",
        "qty_g",
        "eaten_by",
        "eaten_by_slots",
        "feeds_days",
        "weekend_active_hours_estimated",
    }
)
MEALS = ("lunch", "dinner")
REQUIRED_PAIRS = {(day, meal) for day in range(1, 8) for meal in MEALS}
SOURCE_WEEKEND = frozenset({"kind"})
SOURCE_SLOT = frozenset({"kind", "day", "meal"})


class KitImportError(Exception):
    def __init__(self, errors: list[str]):
        self.errors = errors
        super().__init__("; ".join(errors))


def _dec(value: Any, label: str, errors: list[str]) -> Decimal | None:
    try:
        qty = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        errors.append(f"{label}: некорректное qty.")
        return None
    if qty < 0:
        errors.append(f"{label}: qty < 0.")
        return None
    return qty


def _nonempty_steps(raw: Any, label: str, errors: list[str]) -> list[dict]:
    if not isinstance(raw, list) or not raw:
        errors.append(f"{label}: пустые steps.")
        return []
    steps: list[dict] = []
    for index, item in enumerate(raw):
        if not isinstance(item, dict):
            errors.append(f"{label}: шаг {index} не объект.")
            continue
        text = str(item.get("text") or "").strip()
        if not text:
            errors.append(f"{label}: шаг {index} без text.")
            continue
        steps.append(dict(item))
        steps[-1]["text"] = text
    if not steps:
        errors.append(f"{label}: пустые steps.")
    return steps


def _walk_forbidden(obj: Any, path: str, errors: list[str]) -> None:
    if isinstance(obj, dict):
        extra = FORBIDDEN_KEYS & set(obj)
        if extra:
            errors.append(f"{path}: запрещённые ключи {sorted(extra)}.")
        for key, value in obj.items():
            _walk_forbidden(value, f"{path}.{key}", errors)
    elif isinstance(obj, list):
        for index, value in enumerate(obj):
            _walk_forbidden(value, f"{path}[{index}]", errors)


def _validate_dish_use(
    item: dict,
    label: str,
    container_by_id: dict[str, dict],
    recipe_slugs: set[str],
    errors: list[str],
    *,
    require_label: bool,
    allow_empty_containers: bool = False,
) -> None:
    slug = str(item.get("slug") or "").strip()
    if not slug:
        errors.append(f"{label}: нет slug.")
    else:
        recipe_slugs.add(slug)
    if require_label and not str(item.get("label") or "").strip():
        errors.append(f"{label}: нет label.")
    mode = item.get("mode")
    if mode not in {"assemble", "finish", "reheat"}:
        errors.append(f"{label}: mode assemble|finish|reheat.")
    ids = item.get("container_ids") or []
    if not isinstance(ids, list):
        errors.append(f"{label}: container_ids не список.")
        ids = []
    ids = [str(code) for code in ids]
    bad = [code for code in ids if code not in container_by_id]
    if bad:
        errors.append(f"{label}: чужие боксы {bad}.")
    if mode in {"assemble", "finish"} and not ids:
        extra = item.get("shopping_add") or []
        if allow_empty_containers and isinstance(extra, list) and extra:
            pass
        else:
            if allow_empty_containers:
                errors.append(f"{label}: без боксов нужен shopping_add.")
            else:
                errors.append(f"{label}: assemble/finish без container_ids.")
    if mode == "reheat" and ids:
        errors.append(f"{label}: reheat с боксами.")
    _nonempty_steps(item.get("steps"), label, errors)


def _validate_shopping_add(raw: Any, label: str, errors: list[str]) -> None:
    if raw in (None, [], {}):
        return
    if not isinstance(raw, list):
        errors.append(f"{label}: shopping_add не список.")
        return
    for index, row in enumerate(raw):
        if not isinstance(row, dict):
            errors.append(f"{label}: shopping_add[{index}] не объект.")
            continue
        if not str(row.get("canonical_id") or "").strip():
            errors.append(f"{label}: shopping_add[{index}] без canonical_id.")
        if row.get("unit") not in UNIT:
            errors.append(f"{label}: shopping_add[{index}] unit.")
        _dec(row.get("qty"), f"{label} shopping_add[{index}]", errors)


def kit_slug_of(payload: dict) -> str:
    raw = payload.get("slug") or payload.get("id")
    return str(raw or "").strip()


def validate_kit_payload(payload: dict) -> list[str]:
    errors: list[str] = []
    if not isinstance(payload, dict):
        return ["Корень JSON должен быть объектом."]
    _walk_forbidden(payload, "kit", errors)
    slug = kit_slug_of(payload)
    if not slug:
        errors.append("Нет id/slug набора.")

    components = payload.get("components")
    containers = payload.get("containers")
    slots = payload.get("slots")
    if not isinstance(components, list) or not components:
        errors.append("Нет components.")
        components = []
    if not isinstance(containers, list) or not containers:
        errors.append("Нет containers.")
        containers = []
    if not isinstance(slots, list):
        errors.append("Нет slots.")
        slots = []

    component_by_id: dict[str, dict] = {}
    for item in components:
        if not isinstance(item, dict):
            errors.append("component не объект.")
            continue
        code = str(item.get("id") or item.get("code") or "").strip()
        if not code:
            errors.append("component без id.")
            continue
        if code in component_by_id:
            errors.append(f"Дубль component {code}.")
            continue
        unit = item.get("unit")
        if unit not in UNIT:
            errors.append(f"component {code}: неизвестный unit.")
        _dec(item.get("qty"), f"component {code}", errors)
        component_by_id[code] = item

    container_by_id: dict[str, dict] = {}
    qty_by_component: dict[str, Decimal] = {code: Decimal("0") for code in component_by_id}
    for item in containers:
        if not isinstance(item, dict):
            errors.append("container не объект.")
            continue
        code = str(item.get("id") or item.get("code") or "").strip()
        if not code:
            errors.append("container без id.")
            continue
        if code in container_by_id:
            errors.append(f"Дубль container {code}.")
            continue
        parent = str(item.get("component_id") or item.get("component") or "").strip()
        if parent not in component_by_id:
            errors.append(f"container {code}: неизвестный component_id.")
        unit = item.get("unit")
        if unit not in UNIT:
            errors.append(f"container {code}: неизвестный unit.")
        elif parent in component_by_id and component_by_id[parent].get("unit") != unit:
            errors.append(f"container {code}: unit ≠ unit компонента.")
        place = item.get("place")
        if place not in {"fridge", "freezer", "pantry"}:
            errors.append(f"container {code}: place fridge|freezer|pantry.")
        thaw = item.get("thaw_before_day")
        if thaw is not None and thaw not in range(1, 8):
            errors.append(f"container {code}: thaw_before_day 1–7.")
        qty = _dec(item.get("qty"), f"container {code}", errors)
        if qty is not None and parent in qty_by_component:
            qty_by_component[parent] += qty
        container_by_id[code] = item

    for code, item in component_by_id.items():
        expected = _dec(item.get("qty"), f"component {code}", [])
        if expected is None:
            continue
        got = qty_by_component.get(code, Decimal("0"))
        if got != expected:
            errors.append(
                f"component {code}: сумма контейнеров {got} ≠ qty {expected}."
            )
        listed = item.get("container_ids")
        if listed is not None:
            if not isinstance(listed, list):
                errors.append(f"component {code}: container_ids не список.")
            else:
                actual = {
                    cid
                    for cid, box in container_by_id.items()
                    if str(box.get("component_id") or box.get("component") or "") == code
                }
                if set(map(str, listed)) != actual:
                    errors.append(f"component {code}: container_ids не сходятся.")

    if len(slots) != 14:
        errors.append(f"Нужно 14 слотов, сейчас {len(slots)}.")

    slot_pairs: set[tuple[int, str]] = set()
    slot_map: dict[tuple[int, str], dict] = {}
    recipe_slugs: set[str] = set()
    grid_slugs = {
        str(row.get("slug") or "").strip()
        for row in slots
        if isinstance(row, dict) and str(row.get("slug") or "").strip()
    }
    for item in slots:
        if not isinstance(item, dict):
            errors.append("slot не объект.")
            continue
        try:
            day = int(item.get("day"))
        except (TypeError, ValueError):
            errors.append("slot без day 1–7.")
            continue
        meal = item.get("meal")
        if day not in range(1, 8) or meal not in MEALS:
            errors.append(f"slot day={item.get('day')} meal={meal}: не day×meal.")
            continue
        pair = (day, meal)
        if pair in slot_pairs:
            errors.append(f"Дубль слота {day}/{meal}.")
            continue
        slot_pairs.add(pair)
        slot_map[pair] = item
        slug = str(item.get("slug") or "").strip()
        if not slug:
            errors.append(f"слот {day}/{meal}: нет slug.")
        else:
            recipe_slugs.add(slug)
        mode = item.get("mode")
        if mode not in {"assemble", "finish", "reheat"}:
            errors.append(f"слот {day}/{meal}: mode assemble|finish|reheat.")
        source = item.get("source")
        if not isinstance(source, dict):
            errors.append(f"слот {day}/{meal}: source не объект.")
            source = {}
        if "container_ids" in source:
            errors.append(f"слот {day}/{meal}: container_ids внутри source.")
        kind = source.get("kind")
        ids = item.get("container_ids")
        if ids is None:
            ids = []
        if not isinstance(ids, list):
            errors.append(f"слот {day}/{meal}: container_ids не список.")
            ids = []
        ids = [str(code) for code in ids]
        unknown_boxes = [code for code in ids if code not in container_by_id]
        if unknown_boxes:
            errors.append(f"слот {day}/{meal}: чужие container_ids {unknown_boxes}.")
        if mode in {"assemble", "finish"}:
            if kind != "weekend" or set(source) != SOURCE_WEEKEND:
                errors.append(f"слот {day}/{meal}: source только {{kind: weekend}}.")
            if not ids:
                errors.append(f"слот {day}/{meal}: assemble/finish без container_ids.")
        elif mode == "reheat":
            if kind != "slot" or set(source) != SOURCE_SLOT:
                errors.append(
                    f"слот {day}/{meal}: source только {{kind, day, meal}} для reheat."
                )
            if ids:
                errors.append(f"слот {day}/{meal}: reheat с container_ids.")
            try:
                src_day = int(source.get("day"))
            except (TypeError, ValueError):
                src_day = None
            src_meal = source.get("meal")
            if src_day not in range(1, 8) or src_meal not in MEALS:
                errors.append(f"слот {day}/{meal}: reheat source day/meal.")
            elif (src_day, src_meal) == (day, meal):
                errors.append(f"слот {day}/{meal}: reheat на себя.")
            elif src_day != day - 1:
                errors.append(f"слот {day}/{meal}: reheat только со вчера (день {day - 1}).")
        _nonempty_steps(item.get("steps"), f"слот {day}/{meal}", errors)
        alts = item.get("alternatives") or []
        if not isinstance(alts, list) or len(alts) > 3:
            errors.append(f"слот {day}/{meal}: alternatives 0–3.")
            alts = []
        for alt in alts:
            if not isinstance(alt, dict):
                errors.append(f"слот {day}/{meal}: alternative не объект.")
                continue
            _validate_dish_use(
                alt,
                f"слот {day}/{meal} alternative",
                container_by_id,
                recipe_slugs,
                errors,
                require_label=True,
            )
        nl = item.get("no_leftover")
        if nl in (None, {}, []):
            nl = None
        if mode == "reheat":
            if not isinstance(nl, dict) or not str(nl.get("slug") or "").strip():
                errors.append(f"слот {day}/{meal}: reheat без no_leftover.")
            else:
                if nl.get("mode") == "reheat":
                    errors.append(f"слот {day}/{meal}: no_leftover не reheat.")
                nl_slug = str(nl.get("slug") or "").strip()
                if nl_slug and nl_slug in grid_slugs:
                    errors.append(
                        f"слот {day}/{meal}: no_leftover.slug уже стоит в сетке набора."
                    )
                _validate_dish_use(
                    nl,
                    f"слот {day}/{meal} no_leftover",
                    container_by_id,
                    recipe_slugs,
                    errors,
                    require_label=False,
                    allow_empty_containers=True,
                )
                _validate_shopping_add(
                    nl.get("shopping_add"), f"слот {day}/{meal} no_leftover", errors
                )
        elif nl is not None:
            if not isinstance(nl, dict):
                errors.append(f"слот {day}/{meal}: no_leftover не объект.")
            elif nl.get("slug"):
                errors.append(f"слот {day}/{meal}: no_leftover-замена только у reheat.")
            else:
                _nonempty_steps(
                    nl.get("steps"), f"слот {day}/{meal} no_leftover", errors
                )


    missing = REQUIRED_PAIRS - slot_pairs
    if missing and len(slots) == 14:
        errors.append(f"Не все пары day×meal: {sorted(missing)[:4]}…")

    for item in slots:
        if not isinstance(item, dict) or item.get("mode") != "reheat":
            continue
        source = item.get("source") or {}
        try:
            src = (int(source.get("day")), source.get("meal"))
        except (TypeError, ValueError):
            continue
        if src not in slot_map and source.get("kind") == "slot":
            errors.append(
                f"слот {item.get('day')}/{item.get('meal')}: нет слота-источника."
            )

    shopping = payload.get("shopping") or []
    if not isinstance(shopping, list):
        errors.append("shopping не список.")
    else:
        for index, row in enumerate(shopping):
            if not isinstance(row, dict):
                errors.append(f"shopping[{index}] не объект.")
                continue
            if not str(row.get("canonical_id") or "").strip():
                errors.append(f"shopping[{index}]: нет canonical_id.")
            if row.get("unit") not in UNIT:
                errors.append(f"shopping[{index}]: unit.")
            _dec(row.get("qty"), f"shopping[{index}]", errors)

    published = set(
        Recipe.objects.filter(slug__in=recipe_slugs, status="published").values_list(
            "slug", flat=True
        )
    )
    missing_recipes = sorted(recipe_slugs - published)
    if missing_recipes:
        errors.append(f"unpublished/нет recipe: {', '.join(missing_recipes)}.")

    return errors


def _recipe_map(slugs: set[str]) -> dict[str, Recipe]:
    return {row.slug: row for row in Recipe.objects.filter(slug__in=slugs)}


def upsert_kit(payload: dict, *, dry_run: bool = False) -> PrepKit | None:
    errors = validate_kit_payload(payload)
    if errors:
        raise KitImportError(errors)
    if dry_run:
        return None
    slug = kit_slug_of(payload)
    recipes = _recipe_map(
        {
            str(item.get("slug") or "")
            for item in payload.get("slots") or []
            if isinstance(item, dict)
        }
        | {
            str(alt.get("slug") or "")
            for item in payload.get("slots") or []
            if isinstance(item, dict)
            for alt in (item.get("alternatives") or [])
            if isinstance(alt, dict)
        }
        | {
            str((item.get("no_leftover") or {}).get("slug") or "")
            for item in payload.get("slots") or []
            if isinstance(item, dict) and isinstance(item.get("no_leftover"), dict)
        }
    )
    with transaction.atomic():
        kit, _ = PrepKit.objects.update_or_create(
            slug=slug,
            defaults={
                "title": str(payload.get("title") or slug),
                "summary": payload.get("summary") or None,
                "servings_base": payload.get("servings_base"),
                "caution_text": payload.get("caution_text") or None,
                "rhythm": payload.get("rhythm") or None,
                "status": "published",
                "position": int(payload.get("position") or 0),
                "metrics": payload.get("metrics") or {},
                "weekend_timeline": payload.get("weekend_timeline") or [],
                "shopping": payload.get("shopping") or [],
                "allergens": payload.get("allergens") or {},
            },
        )
        kit.slots.all().delete()
        kit.containers.all().delete()
        kit.components.all().delete()
        components: dict[str, PrepComponent] = {}
        for item in payload["components"]:
            code = str(item.get("id") or item.get("code"))
            components[code] = PrepComponent.objects.create(
                kit=kit,
                code=code,
                title=str(item.get("title") or code),
                canonical_ids=item.get("canonical_ids") or [],
                qty=Decimal(str(item["qty"])),
                unit=item["unit"],
                weekend_steps=item.get("weekend_steps") or [],
                parcook=item.get("parcook") or {},
                storage=item.get("storage") or {},
            )
        for item in payload["containers"]:
            code = str(item.get("id") or item.get("code"))
            parent = str(item.get("component_id") or item.get("component"))
            PrepContainer.objects.create(
                kit=kit,
                code=code,
                label=str(item.get("label") or code),
                component=components[parent],
                qty=Decimal(str(item["qty"])),
                unit=item["unit"],
                place=item["place"],
                thaw_before_day=item.get("thaw_before_day"),
            )
        for item in payload["slots"]:
            PrepSlot.objects.create(
                kit=kit,
                day=int(item["day"]),
                meal=item["meal"],
                recipe=recipes[str(item["slug"])],
                mode=item["mode"],
                flavor=item.get("flavor") or None,
                plate=item.get("plate") if isinstance(item.get("plate"), dict) else {},
                source=item["source"],
                container_ids=[str(code) for code in (item.get("container_ids") or [])],
                alternatives=item.get("alternatives") or [],
                servings_cooked=item.get("servings_cooked"),
                feeds_slots=item.get("feeds_slots"),
                time_active_from_prep_min=item.get("time_active_from_prep_min"),
                time_active_scratch_min=item.get("time_active_scratch_min"),
                steps=item.get("steps") or [],
                no_leftover=item.get("no_leftover")
                if isinstance(item.get("no_leftover"), dict)
                else {},
            )
        return kit
