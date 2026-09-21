"""CookingSolution: pick axes, apply pantry/substitutions, rank, bucket."""

from __future__ import annotations

from dataclasses import dataclass, field
from types import SimpleNamespace

from apps.recipes.constants import BEST_BUCKET_LIMIT, COMPONENT_DISH_TYPES
from apps.recipes.services.assemble import VariantError, assemble_recipe
from apps.recipes.services.combinations import (
    MAX_CANDIDATES,
    axis_combos,
    combo_fits,
    combo_method_equipment,
    combo_protein_bases,
    combo_tie_key,
    combo_time_minutes,
)
from apps.recipes.services.ranking import score_and_why
from apps.recipes.services.snapshots import snapshot_fits, snapshots_are_fresh
from apps.recipes.services.solver_scoring import (
    axes_why,
    intent_adjust,
    is_core_line,
    is_desirable_line,
    match_pantry,
    pantry_score,
    pantry_why,
    protein_from_pantry,
    requires_prep as lines_require_prep,
    unmet_prep_core,
)
from apps.recipes.services.substitutions import SubRule, rules_for_recipe

__all__ = [
    "MAX_CANDIDATES",
    "CookingSolution",
    "assign_buckets",
    "axis_combos",
    "build_board",
    "combo_fits",
    "combo_method_equipment",
    "combo_protein_bases",
    "combo_time_minutes",
    "intent_adjust",
    "is_core_line",
    "is_desirable_line",
    "is_standalone_dish",
    "match_pantry",
    "pantry_score",
    "pantry_why",
    "protein_from_pantry",
    "serialize_solution",
    "solve_recipe",
]


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
    protein_bases: list[str] = field(default_factory=list)
    protein_variants: list[dict] = field(default_factory=list)
    time_total_minutes: int | None = None
    time_active_minutes: int | None = None
    requires_prep: bool = False


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
    explore = bool(have or filter_method or filter_equipment or filter_protein or intents)
    best: CookingSolution | None = None
    best_key: tuple | None = None
    recipe_rules = rules_for_recipe(recipe.slug, rules)
    titles = titles or {}

    scored: list[tuple] = []
    snaps = list(getattr(recipe, "axis_snapshots", None) or [])
    if snaps and snapshots_are_fresh(recipe):
        for snap in snaps:
            if len(scored) >= MAX_CANDIDATES:
                break
            if not explore and not snap.get("home"):
                continue
            if not snapshot_fits(snap, filter_method, filter_equipment, filter_protein):
                continue
            assembled = SimpleNamespace(
                ingredients=list(snap.get("lines") or []),
                allergens=snap.get("allergens") or {},
                high_risk_flags=list(snap.get("high_risk_flags") or []),
                cook_method=snap.get("cook_method") or recipe.cook_method,
                protein_base=snap.get("protein_base") or recipe.protein_base,
                equipment=snap.get("equipment"),
                applied_axes={
                    "variant": snap.get("variant"),
                    "equipment": snap.get("equipment"),
                },
            )
            protein_bases = list(snap.get("protein_bases") or [assembled.protein_base])
            combo_key = (
                int(snap.get("addon_penalty") or 0),
                int(snap.get("equipment_penalty") or 0),
            )
            step_count = int(snap.get("step_count") or 0)
            time_total = snap.get("time_total_minutes")
            time_active = snap.get("time_active_minutes")
            scored.append(
                (assembled, protein_bases, combo_key, step_count, time_total, time_active)
            )
    else:
        for addon, equipment_variant in axis_combos(recipe, explore=explore):
            if len(scored) >= MAX_CANDIDATES:
                break
            if not combo_fits(
                recipe, addon, equipment_variant, filter_method, filter_equipment, filter_protein
            ):
                continue
            variant_code = addon.code if addon is not None else None
            equipment_code = None
            if equipment_variant is not None:
                equipment_code = equipment_variant.equipment or equipment_variant.code
            elif filter_equipment and recipe.equipment in filter_equipment:
                equipment_code = recipe.equipment
            try:
                assembled = assemble_recipe(
                    recipe,
                    variant_code=variant_code,
                    equipment_code=equipment_code,
                    enrich=False,
                )
            except VariantError:
                continue
            protein_bases = combo_protein_bases(recipe, addon)
            combo_key = combo_tie_key(addon, equipment_variant)
            time_total, time_active = combo_time_minutes(recipe)
            scored.append(
                (
                    assembled,
                    protein_bases,
                    combo_key,
                    len(assembled.steps),
                    time_total,
                    time_active,
                )
            )

    for assembled, protein_bases, combo_key, step_count, time_total, time_active in scored:
        if unmet_prep_core(assembled.ingredients, have):
            continue
        if have:
            (
                shopping,
                substitutions,
                hits,
                missing,
                desirable,
                covered_ids,
                used_have,
            ) = match_pantry(assembled.ingredients, have, recipe_rules, titles)
        else:
            shopping, substitutions, desirable = [], [], []
            hits = missing = 0
            covered_ids, used_have = set(), set()
        chip_score, chip_why = score_and_why(
            protein_base=assembled.protein_base,
            cook_method=assembled.cook_method,
            dish_type=recipe.dish_type,
            equipment=assembled.equipment,
            editorial_tested=recipe.editorial_tested,
            filter_protein=filter_protein,
            filter_method=filter_method,
            filter_dish=filter_dish,
            filter_equipment=filter_equipment,
            protein_bases=protein_bases,
        )
        why = list(chip_why)
        axis_lines = axes_why(
            recipe, assembled, filter_method, filter_equipment, filter_protein
        )
        if any(line.endswith(" — вариант") for line in axis_lines):
            why = [line for line in why if not line.startswith("основа — ")]
        if any("вариант посуды" in line for line in axis_lines):
            why = [line for line in why if line != "совпал метод"]
        if any(" (вариант)" in line for line in axis_lines):
            why = [line for line in why if not line.startswith("совпала посуда")]
        why.extend(axis_lines)
        why.extend(pantry_why(shopping, substitutions, has_have=bool(have), desirable=desirable))
        protein_pts, protein_why = protein_from_pantry(
            recipe,
            have,
            covered_ids=covered_ids,
            titles=titles,
            protein_base=assembled.protein_base,
            used_have=used_have,
        )
        why.extend(protein_why)
        intent_pts, intent_why = intent_adjust(
            recipe,
            assembled,
            intents,
            step_count,
            time_total_minutes=time_total,
        )
        why.extend(intent_why)
        if "pantry" in intents and have:
            if missing == 0:
                intent_pts += 12
                if substitutions:
                    why.append("из того, что есть, с заменой")
                else:
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
            protein_base=assembled.protein_base,
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
            allergens=dict(assembled.allergens),
            high_risk_flags=list(assembled.high_risk_flags),
            has_delta_variants=bool(catalog_item["has_delta_variants"]),
            allowed_cuts=list(catalog_item.get("allowed_cuts") or []),
            pantry_hits=hits,
            step_count=step_count,
            have_used=have_used,
            have_all=have_all,
            protein_bases=list(catalog_item.get("protein_bases") or [recipe.protein_base]),
            protein_variants=list(catalog_item.get("protein_variants") or []),
            time_total_minutes=time_total,
            time_active_minutes=time_active,
            requires_prep=lines_require_prep(assembled.ingredients),
        )
        key = (
            -int(have_all),
            -have_used,
            -score,
            missing,
            len(substitutions),
            *combo_key,
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


def assign_buckets(
    solutions: list[CookingSolution], *, has_have: bool
) -> dict[str, list[CookingSolution]]:
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

    feat_time = featured.time_total_minutes
    take(
        "Быстрее",
        lambda item: feat_time is not None
        and item.time_total_minutes is not None
        and item.time_total_minutes < feat_time,
    )
    take(
        "На плите",
        lambda item: item.cook_method in {"pan_fry", "no_cook", "grill"},
    )
    take("В духовке", lambda item: item.cook_method == "oven")
    take("На несколько дней", lambda item: item.cook_method == "stew")
    while len(alts) < 3 and rest:
        alts.append(("Ещё вариант", rest.pop(0)))
    return featured, alts[:3]


def serialize_solution(item: CookingSolution) -> dict:
    return {
        "slug": item.slug,
        "title": item.title,
        "protein_base": item.protein_base,
        "protein_bases": item.protein_bases or [item.protein_base],
        "protein_variants": item.protein_variants,
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
        "time_profile": {
            "total_minutes": item.time_total_minutes,
            "active_minutes": item.time_active_minutes,
        },
        "requires_prep": item.requires_prep,
    }
