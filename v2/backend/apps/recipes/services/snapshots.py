"""Precomputed axis snapshots so the calculator can rank without assemble."""

from __future__ import annotations

from typing import Any

LINE_KEYS = ("canonical_id", "name", "optional", "unit", "is_anchor")


def _line_stub(line: dict) -> dict[str, Any]:
    return {key: line.get(key) for key in LINE_KEYS}


def snapshots_are_fresh(recipe) -> bool:
    """True only when stored JSON matches the current content_version."""
    snaps = getattr(recipe, "axis_snapshots", None) or []
    if not snaps:
        return False
    content = int(getattr(recipe, "content_version", 1) or 1)
    snap_ver = int(getattr(recipe, "snapshot_version", 0) or 0)
    if snap_ver == content:
        return True
    # Rows from before 0013: snapshots existed, versions still at defaults.
    return snap_ver == 0 and content == 1


def snapshot_from_assembled(recipe, assembled, addon, equipment_variant) -> dict[str, Any]:
    from apps.recipes.services.combinations import combo_protein_bases, combo_time_minutes

    time_total, time_active = combo_time_minutes(recipe)
    variant_code = addon.code if addon is not None else None
    return {
        "variant": variant_code,
        "equipment": assembled.equipment,
        "home": addon is None and equipment_variant is None,
        "protein_base": assembled.protein_base,
        "protein_bases": combo_protein_bases(recipe, addon),
        "cook_method": assembled.cook_method,
        "lines": [_line_stub(line) for line in assembled.ingredients],
        "allergens": dict(assembled.allergens or {}),
        "high_risk_flags": list(assembled.high_risk_flags or []),
        "step_count": len(assembled.steps),
        "time_total_minutes": time_total,
        "time_active_minutes": time_active,
        "addon_penalty": 0 if addon is None else 1,
        "equipment_penalty": 0 if equipment_variant is None else 1,
    }


def snapshot_fits(
    snap: dict,
    methods: list[str],
    equipments: list[str],
    proteins: list[str] | None = None,
) -> bool:
    if methods and snap.get("cook_method") not in methods:
        return False
    if equipments and snap.get("equipment") not in equipments:
        return False
    if proteins:
        bases = list(snap.get("protein_bases") or [])
        if not any(code in proteins for code in bases):
            return False
    return True


def refresh_axis_snapshots(recipe) -> list[dict[str, Any]]:
    """Assemble every delta combo once and store stubs on the recipe row.

    Write only if content_version is unchanged during compute. No Celery.
    """
    from django.utils import timezone

    from apps.recipes.models import Recipe
    from apps.recipes.services.assemble import VariantError, assemble_recipe
    from apps.recipes.services.combinations import axis_combos

    expected_version = int(getattr(recipe, "content_version", 1) or 1)
    out: list[dict[str, Any]] = []
    for addon, equipment_variant in axis_combos(recipe, explore=True):
        variant_code = addon.code if addon is not None else None
        equipment_code = None
        if equipment_variant is not None:
            equipment_code = equipment_variant.equipment or equipment_variant.code
        try:
            assembled = assemble_recipe(
                recipe,
                variant_code=variant_code,
                equipment_code=equipment_code,
                enrich=False,
            )
        except VariantError:
            continue
        out.append(snapshot_from_assembled(recipe, assembled, addon, equipment_variant))
    now = timezone.now()
    updated = Recipe.objects.filter(pk=recipe.pk, content_version=expected_version).update(
        axis_snapshots=out,
        snapshot_version=expected_version,
        snapshots_updated_at=now,
    )
    if updated:
        recipe.axis_snapshots = out
        recipe.snapshot_version = expected_version
        recipe.snapshots_updated_at = now
    return out
