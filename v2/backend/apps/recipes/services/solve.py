"""CookingSolution: pick axes, apply pantry/substitutions, rank, bucket."""

from __future__ import annotations

from dataclasses import dataclass, field

from django.conf import settings

from apps.recipes.constants import (
    BEST_BUCKET_LIMIT,
    COMPONENT_DISH_TYPES,
    COOK_METHOD_LABEL_RU,
    EQUIPMENT_LABEL_RU,
)
from apps.recipes.pantry_vocab import (
    FISH_CANNED,
    FISH_FRESH,
    FISH_PROTEIN,
    HAVE_GROUP_PROTEIN,
    HAVE_GROUPS,
    availability_class,
    shopping_label,
)
from apps.recipes.services.assemble import VariantError, assemble_recipe
from apps.recipes.services.ranking import score_and_why
from apps.recipes.services.substitutions import SubRule, cover_need, rules_for_recipe


@dataclass
class CookingSolution:
    slug: str
    title: str
    protein_base: str
    cook_method: str
    dish_type: str
    equipment: str | None
    applied_axes: dict[str, str | None]
    bucket: str
    why: list[str]
    score: int
    shopping_delta: list[dict]
    substitutions: list[dict]
    allergens: dict
    high_risk_flags: list[str]
    has_delta_variants: bool
    allowed_cuts: list[str] = field(default_factory=list)
    pantry_hits: int = 0
    step_count: int = 0
    have_used: int = 0
    have_all: bool = False


def is_core_line(line: dict) -> bool:
    if line.get("optional"):
        return False
    cid = line.get("canonical_id") or ""
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
    cid = line.get("canonical_id") or ""
    return availability_class(cid) == "common"


def combo_method_equipment(recipe, addon, equipment_variant) -> tuple[str, str | None]:
    method = recipe.cook_method
    equipment = recipe.equipment
    if equipment_variant is not None:
        if equipment_variant.cook_method_override:
            method = equipment_variant.cook_method_override
        equipment = equipment_variant.equipment or equipment_variant.code
    return method, equipment


def intent_adjust(recipe, assembled, intents: list[str], step_count: int) -> tuple[int, list[str]]:
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
    if "oven" in intents:
        if method == "oven":
            score += 10
            why.append("духовка")
    if "light" in intents and getattr(recipe, "energy_profile", "standard") == "light":
        score += 8
        why.append("профиль полегче")
    if "easy" in intents:
        score -= min(step_count, 8)
        if method in {"oven", "stew", "no_cook"}:
            score += 4
            why.append("меньше стоять у плиты")
    if "batch" in intents and method in {"stew", "oven"}:
        score += 8
        why.append("можно на несколько дней")
    return score, why


def combo_fits(recipe, addon, equipment_variant, methods: list[str], equipments: list[str]) -> bool:
    method, equipment = combo_method_equipment(recipe, addon, equipment_variant)
    if methods and method not in methods:
        return False
    if equipments and equipment not in equipments:
        return False
    return True


def axis_combos(recipe, *, explore: bool) -> list[tuple[object | None, object | None]]:
    variants = list(recipe.variants.all())
    if not explore:
        return [(None, None)]
    addons: list[object | None] = [None]
    addons.extend(item for item in variants if item.axis == "addon" and item.has_delta)
    equipments: list[object | None] = [None]
    equipments.extend(item for item in variants if item.axis == "equipment" and item.has_delta)
    return [(addon, eq) for addon in addons for eq in equipments]


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
        need = line.get("canonical_id") or ""
        title = line.get("name") or shopping_label(need, titles)
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
) -> tuple[int, list[str]]:
    """Bonus only if a core line from `have` actually covers this recipe.

    Ground beef in the cupboard is not a steak, a chuck roast, or butter.
    """
    if not have or not covered_ids:
        return 0, []
    score = 0
    why: list[str] = []
    titles = titles or {}
    covered = set(covered_ids)
    fresh = bool(covered & FISH_FRESH)
    canned = bool(covered & FISH_CANNED)
    if fresh and recipe.protein_base in FISH_PROTEIN:
        score += 8
        why.append("есть рыба")
    elif canned and not fresh and recipe.protein_base in FISH_PROTEIN:
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
        matched = covered & set(HAVE_GROUPS[group])
        if matched and recipe.protein_base in bases:
            score += 6
            label = shopping_label(sorted(matched)[0], titles)
            why.append(f"есть {label}")
            break
    return score, why


def axes_why(recipe, assembled, methods: list[str], equipments: list[str]) -> list[str]:
    extra: list[str] = []
    if methods and assembled.cook_method in methods and assembled.cook_method != recipe.cook_method:
        label = COOK_METHOD_LABEL_RU.get(assembled.cook_method, assembled.cook_method)
        extra.append(f"{label} — вариант посуды")
    if (
        equipments
        and assembled.equipment in equipments
        and assembled.equipment
        and assembled.equipment != recipe.equipment
    ):
        label = EQUIPMENT_LABEL_RU.get(assembled.equipment, assembled.equipment)
        extra.append(f"посуда — {label} (вариант)")
    return extra


def _combo_key(addon, equipment_variant) -> tuple[int, int]:
    """Prefer base (no addon, no equipment variant) on ties."""
    return (0 if addon is None else 1, 0 if equipment_variant is None else 1)


def solve_recipe(
    recipe,
    *,
    filter_protein: list[str],
    filter_method: list[str],
    filter_dish: list[str],
    filter_equipment: list[str],
    have: list[str],
    catalog_item: dict,
    rules: list[SubRule],
    titles: dict[str, str] | None = None,
    intents: list[str] | None = None,
    explicit_have: list[str] | None = None,
) -> CookingSolution | None:
    intents = intents or []
    explicit = [cid for cid in (explicit_have or []) if cid]
    explicit_set = set(explicit)
    explore = bool(have or filter_method or filter_equipment or intents)
    best: CookingSolution | None = None
    best_key: tuple | None = None
    recipe_rules = rules_for_recipe(recipe.slug, rules)
    titles = titles or {}

    for addon, equipment_variant in axis_combos(recipe, explore=explore):
        if not combo_fits(recipe, addon, equipment_variant, filter_method, filter_equipment):
            continue
        variant_code = addon.code if addon is not None else None
        equipment_code = None
        if equipment_variant is not None:
            equipment_code = equipment_variant.equipment or equipment_variant.code
        elif filter_equipment and recipe.equipment in filter_equipment:
            equipment_code = recipe.equipment
        try:
            assembled = assemble_recipe(
                recipe, variant_code=variant_code, equipment_code=equipment_code
            )
        except VariantError:
            continue

        shopping, substitutions, hits, missing, desirable, covered_ids, used_have = match_pantry(
            assembled.ingredients, have, recipe_rules, titles
        )
        chip_score, chip_why = score_and_why(
            protein_base=recipe.protein_base,
            cook_method=assembled.cook_method,
            dish_type=recipe.dish_type,
            equipment=assembled.equipment,
            editorial_tested=recipe.editorial_tested,
            filter_protein=filter_protein,
            filter_method=filter_method,
            filter_dish=filter_dish,
            filter_equipment=filter_equipment,
        )
        why = list(chip_why)
        axis_lines = axes_why(recipe, assembled, filter_method, filter_equipment)
        if any("вариант посуды" in line for line in axis_lines):
            why = [line for line in why if line != "совпал метод"]
        if any(" (вариант)" in line for line in axis_lines):
            why = [line for line in why if not line.startswith("совпала посуда")]
        why.extend(axis_lines)
        why.extend(pantry_why(shopping, substitutions, has_have=bool(have), desirable=desirable))
        protein_pts, protein_why = protein_from_pantry(
            recipe, have, covered_ids=covered_ids, titles=titles
        )
        why.extend(protein_why)
        step_count = len(assembled.steps)
        intent_pts, intent_why = intent_adjust(recipe, assembled, intents, step_count)
        why.extend(intent_why)
        if "pantry" in intents and have:
            if missing == 0:
                intent_pts += 12
                why.append("из того, что есть")
            else:
                intent_pts -= missing * 3
        have_used = len(used_have & explicit_set) if explicit_set else 0
        have_all = bool(explicit_set) and explicit_set <= used_have
        if have_all and len(explicit_set) >= 2:
            intent_pts += 16
            why.append("из всего выбранного")
        score = (
            chip_score
            + pantry_score(hits, missing, substitutions, has_have=bool(have))
            + intent_pts
            + protein_pts
        )
        solution = CookingSolution(
            slug=recipe.slug,
            title=recipe.title,
            protein_base=recipe.protein_base,
            cook_method=assembled.cook_method,
            dish_type=recipe.dish_type,
            equipment=assembled.equipment,
            applied_axes={
                "variant": assembled.applied_axes.get("variant"),
                "equipment": assembled.applied_axes.get("equipment"),
            },
            bucket="match",
            why=why,
            score=score,
            shopping_delta=shopping,
            substitutions=[
                {key: item[key] for key in ("from_id", "from_title", "to_id", "to_title")}
                for item in substitutions
            ],
            allergens=catalog_item["allergens"],
            high_risk_flags=list(catalog_item["high_risk_flags"]),
            has_delta_variants=bool(catalog_item["has_delta_variants"]),
            allowed_cuts=list(catalog_item.get("allowed_cuts") or []),
            pantry_hits=hits,
            step_count=step_count,
            have_used=have_used,
            have_all=have_all,
        )
        key = (
            -int(have_all),
            -have_used,
            -score,
            missing,
            len(substitutions),
            *_combo_key(addon, equipment_variant),
            recipe.title,
        )
        if best_key is None or key < best_key:
            best = solution
            best_key = key
    return best


def is_standalone_dish(dish_type: str) -> bool:
    return dish_type not in COMPONENT_DISH_TYPES


def _board_sort(item: CookingSolution) -> tuple:
    return (
        int(not is_standalone_dish(item.dish_type)),
        -int(item.have_all),
        -item.have_used,
        -item.pantry_hits,
        -item.score,
        item.title,
    )


def assign_buckets(solutions: list[CookingSolution], *, has_have: bool) -> dict[str, list[CookingSolution]]:
    if not has_have:
        for item in solutions:
            item.bucket = "match"
        return {"now": [], "almost": [], "best": []}

    now: list[CookingSolution] = []
    almost: list[CookingSolution] = []
    rest: list[CookingSolution] = []
    for item in solutions:
        missing = len(item.shopping_delta)
        hits = item.pantry_hits
        if hits <= 0:
            item.bucket = "rest"
            continue
        if missing == 0:
            item.bucket = "now"
            now.append(item)
        elif missing <= 2:
            item.bucket = "almost"
            almost.append(item)
        else:
            rest.append(item)
    now.sort(key=_board_sort)
    almost.sort(key=_board_sort)
    rest.sort(key=_board_sort)
    best = rest[:BEST_BUCKET_LIMIT]
    for item in best:
        item.bucket = "best"
    for item in rest[BEST_BUCKET_LIMIT:]:
        item.bucket = "rest"
    return {"now": now, "almost": almost, "best": best}


def build_board(
    solutions: list[CookingSolution],
    buckets: dict[str, list[CookingSolution]],
    *,
    has_have: bool,
) -> tuple[CookingSolution | None, list[tuple[str, CookingSolution]]]:
    if has_have:
        # Only dishes that use something from `have`. Unused pantry (steak
        # while you have mince, whipped butter, …) stays off the board.
        pool = buckets["now"] + buckets["almost"] + buckets["best"]
    else:
        pool = list(solutions)
    meals = [item for item in pool if is_standalone_dish(item.dish_type)]
    if meals:
        pool = meals
    if not has_have:
        pool = pool[:8]
    if not pool:
        return None, []
    complete = [item for item in pool if item.have_all]
    if complete:
        complete.sort(key=_board_sort)
        featured = complete[0]
    else:
        featured = pool[0]
    rest = [item for item in pool if item.slug != featured.slug]
    alts: list[tuple[str, CookingSolution]] = []

    def take(label: str, predicate) -> None:
        for index, item in enumerate(rest):
            if predicate(item):
                alts.append((label, item))
                rest.pop(index)
                return

    take(
        "Быстрее",
        lambda item: item.cook_method in {"pan_fry", "no_cook", "grill"}
        and item.step_count <= featured.step_count,
    )
    take("Проще", lambda item: item.cook_method in {"oven", "stew"})
    take("На несколько дней", lambda item: item.cook_method == "stew")
    while len(alts) < 3 and rest:
        alts.append(("Ещё вариант", rest.pop(0)))
    return featured, alts[:3]


def serialize_solution(item: CookingSolution) -> dict:
    return {
        "slug": item.slug,
        "title": item.title,
        "protein_base": item.protein_base,
        "cook_method": item.cook_method,
        "dish_type": item.dish_type,
        "equipment": item.equipment,
        "allowed_cuts": item.allowed_cuts,
        "applied_axes": item.applied_axes,
        "bucket": item.bucket,
        "why": item.why,
        "score": item.score,
        "shopping_delta": item.shopping_delta,
        "substitutions": item.substitutions,
        "allergens": item.allergens,
        "high_risk_flags": item.high_risk_flags,
        "has_delta_variants": item.has_delta_variants,
        "step_count": item.step_count,
    }

