"""Axis combination generation and eligibility. Ranking math lives in solver_scoring."""

from __future__ import annotations

MAX_CANDIDATES = 2000


def combo_method_equipment(recipe, addon, equipment_variant) -> tuple[str, str | None]:
    method = recipe.cook_method
    equipment = recipe.equipment
    if equipment_variant is not None:
        if equipment_variant.cook_method_override:
            method = equipment_variant.cook_method_override
        equipment = equipment_variant.equipment or equipment_variant.code
    return method, equipment


def combo_time_minutes(recipe) -> tuple[int | None, int | None]:
    total = getattr(recipe, "time_total_minutes", None)
    active = getattr(recipe, "time_active_minutes", None)
    return (
        int(total) if total is not None else None,
        int(active) if active is not None else None,
    )


def combo_protein_bases(recipe, addon) -> list[str]:
    override = getattr(addon, "protein_base_override", None) if addon is not None else None
    if override:
        return [override]
    ordered: list[str] = []
    home = getattr(recipe, "protein_base", None)
    if home:
        ordered.append(home)
    for code in getattr(recipe, "protein_bases_extra", None) or []:
        if code and code not in ordered:
            ordered.append(code)
    return ordered


def combo_fits(
    recipe,
    addon,
    equipment_variant,
    methods: list[str],
    equipments: list[str],
    proteins: list[str] | None = None,
) -> bool:
    method, equipment = combo_method_equipment(recipe, addon, equipment_variant)
    if methods and method not in methods:
        return False
    if equipments and equipment not in equipments:
        return False
    if proteins:
        bases = combo_protein_bases(recipe, addon)
        if not any(code in proteins for code in bases):
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


def combo_tie_key(addon, equipment_variant) -> tuple[int, int]:
    """Prefer base (no addon, no equipment variant) on ties."""
    return (0 if addon is None else 1, 0 if equipment_variant is None else 1)
