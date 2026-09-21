"""Pantry matching, intent and axis why-lines. Do not change ranking weights usage."""

from __future__ import annotations

from django.conf import settings

from apps.recipes.constants import (
    COOK_METHOD_LABEL_RU,
    PROTEIN_BASE_LABEL_RU,
    label_equipment_axis,
)
from apps.recipes.pantry_vocab import (
    FISH_CANNED,
    FISH_FRESH,
    FISH_PROTEIN,
    HAVE_GROUP_PROTEIN,
    HAVE_GROUPS,
    PANTRY_PREP,
    availability_class,
    shopping_label,
)
from apps.recipes.services.substitutions import SubRule, cover_need


def is_core_line(line: dict) -> bool:
    if line.get("optional"):
        return False
    cid = (line.get("canonical_id") or "").strip()
    if not cid:
        return False
    klass = availability_class(cid)
    if klass in {"assumed", "common", "exotic"}:
        return False
    if line.get("is_anchor"):
        return True
    if line.get("unit") in {"pinch", "tsp"}:
        return False
    return True


def is_desirable_line(line: dict) -> bool:
    if line.get("optional"):
        return False
    cid = (line.get("canonical_id") or "").strip()
    if not cid:
        return False
    return availability_class(cid) == "common"


def line_canonical_id(line) -> str:
    if isinstance(line, dict):
        return (line.get("canonical_id") or "").strip()
    ingredient = getattr(line, "ingredient", None)
    return ((getattr(ingredient, "canonical_id", None) or "") if ingredient else "").strip()


def as_pantry_line(line) -> dict:
    if isinstance(line, dict):
        return line
    return {
        "canonical_id": line_canonical_id(line),
        "optional": bool(getattr(line, "optional", False)),
        "unit": getattr(line, "unit", None),
        "is_anchor": bool(getattr(line, "is_anchor", False)),
    }


def requires_prep(lines) -> bool:
    """True if a core line is a homemade leftover, not raw supermarket meat."""
    return any(
        is_core_line(as_pantry_line(line)) and line_canonical_id(line) in PANTRY_PREP
        for line in lines or []
    )


def unmet_prep_core(lines, have: list[str]) -> bool:
    """Leftover core is missing from pantry. Species chips do not cover it."""
    have_set = set(have)
    for line in lines or []:
        item = as_pantry_line(line)
        cid = line_canonical_id(item)
        if is_core_line(item) and cid in PANTRY_PREP and cid not in have_set:
            return True
    return False


def intent_adjust(
    recipe,
    assembled,
    intents: list[str],
    step_count: int,
    *,
    time_total_minutes: int | None = None,
) -> tuple[int, list[str]]:
    if not intents:
        return 0, []
    score = 0
    why: list[str] = []
    method = assembled.cook_method
    if "fast" in intents:
        if method in {"pan_fry", "no_cook", "grill"}:
            score += 8
            why.append("быстрее на плите")
        elif method in {"stew", "oven"}:
            score -= 3
        score -= min(step_count, 6)
        if time_total_minutes is not None:
            score -= min(int(time_total_minutes) // 15, 6)
            if time_total_minutes <= 30:
                why.append("быстрее по времени")
    if "oven" in intents:
        if method == "oven":
            score += 10
            why.append("духовка")
    if "light" in intents and getattr(recipe, "energy_profile", "standard") == "light":
        score += 8
        why.append("полегче по составу")
    if "easy" in intents:
        score -= min(step_count, 8)
        if method in {"oven", "stew", "no_cook"}:
            score += 4
            why.append("меньше стоять у плиты")
    if "batch" in intents and method in {"stew", "oven"}:
        score += 8
        why.append("можно на несколько дней")
    return score, why


def match_pantry(
    lines: list[dict],
    have: list[str],
    rules: list[SubRule],
    titles: dict[str, str] | None = None,
) -> tuple[list[dict], list[dict], int, int, list[dict], set[str], set[str]]:
    """Return shopping, substitutions, hits, missing, desirable, covered needs, used have ids."""
    have_set = set(have)
    titles = titles or {}
    shopping: list[dict] = []
    substitutions: list[dict] = []
    desirable: list[dict] = []
    covered_ids: set[str] = set()
    used_have: set[str] = set()
    hits = 0
    for line in lines:
        need = (line.get("canonical_id") or "").strip()
        title = line.get("name") or shopping_label(need, titles)
        if not need:
            continue
        if is_desirable_line(line):
            if need not in have_set:
                desirable.append({"canonical_id": need, "title": title})
            continue
        if not is_core_line(line):
            continue
        covered, quality = cover_need(need, have_set, rules)
        if covered is None:
            shopping.append({"canonical_id": need, "title": title})
            continue
        hits += 1
        covered_ids.add(need)
        if need in have_set:
            used_have.add(need)
        if covered in have_set:
            used_have.add(covered)
        if covered != need and quality is not None:
            to_title = shopping_label(covered, titles)
            substitutions.append(
                {
                    "from_id": need,
                    "from_title": title,
                    "to_id": covered,
                    "to_title": to_title,
                    "quality": quality,
                }
            )
    return shopping, substitutions, hits, len(shopping), desirable, covered_ids, used_have


def pantry_score(hits: int, missing: int, substitutions: list[dict], *, has_have: bool) -> int:
    if not has_have:
        return 0
    weights = settings.RANKING_WEIGHTS
    score = hits * int(weights["pantry_hit"])
    score += missing * int(weights["pantry_missing"])
    score += len(substitutions) * int(weights["substitution_friction"])
    if missing == 0:
        score += int(weights["pantry_complete"])
    return score


def pantry_why(
    shopping: list[dict],
    substitutions: list[dict],
    *,
    has_have: bool,
    desirable: list[dict] | None = None,
) -> list[str]:
    if not has_have:
        return []
    why: list[str] = []
    if not shopping:
        if substitutions:
            why.append("можно приготовить с заменой")
        else:
            why.append("можно приготовить сейчас")
    elif len(shopping) == 1:
        why.append(f"нужно докупить: {shopping[0]['title']}")
    else:
        names = ", ".join(item["title"] for item in shopping[:3])
        extra = f" и ещё {len(shopping) - 3}" if len(shopping) > 3 else ""
        why.append(f"нужно докупить: {names}{extra}")
    for item in substitutions:
        why.append(f"вместо {item['from_title']} — {item['to_title']}")
    if desirable:
        names = ", ".join(item["title"] for item in desirable[:3])
        why.append(f"желательно: {names}, но можно без этого")
    return why


def protein_from_pantry(
    recipe,
    have: list[str],
    *,
    covered_ids: set[str],
    titles: dict[str, str] | None = None,
    protein_base: str | None = None,
    used_have: set[str] | None = None,
) -> tuple[int, list[str]]:
    """Bonus only if a core line from `have` actually covers this recipe.

    Ground beef in the cupboard is not a steak, a chuck roast, or butter.
    The «есть …» line names what is in the pantry, never the recipe line
    a substitution replaced.
    """
    if not have or not covered_ids:
        return 0, []
    score = 0
    why: list[str] = []
    titles = titles or {}
    covered = set(covered_ids)
    have_set = set(have)
    # Label the pantry ids that actually covered a line. Never the recipe need:
    # chicken_breast ← thighs must read «есть куриные бёдра», same for any sub.
    if used_have is not None:
        pantry_used = set(used_have)
    else:
        pantry_used = have_set & covered
    fresh = bool(pantry_used & FISH_FRESH) or bool(covered & FISH_FRESH)
    canned = bool(pantry_used & FISH_CANNED) or bool(covered & FISH_CANNED)
    base = protein_base or recipe.protein_base
    if fresh and base in FISH_PROTEIN:
        score += 8
        why.append("есть рыба")
    elif canned and not fresh and base in FISH_PROTEIN:
        score += 3
        why.append("есть рыбные консервы")
    preference = (
        "chicken",
        "pork",
        "beef",
        "lamb",
        "eggs",
        "veg",
        "legumes",
        "meat",
    )
    for group in preference:
        bases = HAVE_GROUP_PROTEIN.get(group)
        if not bases:
            continue
        group_ids = set(HAVE_GROUPS[group])
        covered_in_group = covered & group_ids
        if not covered_in_group or base not in bases:
            continue
        score += 6
        named = pantry_used & group_ids or pantry_used
        if named:
            label = shopping_label(sorted(named)[0], titles)
            why.append(f"есть {label}")
        break
    return score, why


def axes_why(
    recipe, assembled, methods: list[str], equipments: list[str], proteins: list[str] | None = None
) -> list[str]:
    extra: list[str] = []
    proteins = proteins or []
    if (
        proteins
        and assembled.protein_base in proteins
        and assembled.protein_base != recipe.protein_base
    ):
        label = PROTEIN_BASE_LABEL_RU.get(assembled.protein_base, assembled.protein_base)
        extra.append(f"{label} — вариант")
    if methods and assembled.cook_method in methods and assembled.cook_method != recipe.cook_method:
        label = COOK_METHOD_LABEL_RU.get(assembled.cook_method, assembled.cook_method)
        extra.append(f"{label} — вариант посуды")
    if (
        equipments
        and assembled.equipment in equipments
        and assembled.equipment
        and assembled.equipment != recipe.equipment
    ):
        extra.append(f"посуда — {label_equipment_axis(assembled.equipment)} (вариант)")
    return extra
