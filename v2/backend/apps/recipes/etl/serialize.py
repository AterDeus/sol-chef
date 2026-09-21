"""Serialize a live Recipe row back to author draft JSON."""

from __future__ import annotations

from decimal import Decimal

from apps.core.numbers import decimal_json
from apps.recipes.models import Recipe


def _num(value):
    if value is None:
        return None
    if isinstance(value, Decimal):
        return decimal_json(value)
    return value


def recipe_to_draft(recipe: Recipe) -> dict:
    payload: dict = {
        "id": recipe.slug,
        "title": recipe.title,
        "summary": recipe.summary,
        "protein_base": recipe.protein_base,
        "cook_method": recipe.cook_method,
        "dish_type": recipe.dish_type,
        "equipment": recipe.equipment,
        "energy_profile": recipe.energy_profile or "standard",
        "allowed_cuts": list(recipe.allowed_cuts or []),
        "protein_bases_extra": list(recipe.protein_bases_extra or []),
        "scale_mode": recipe.scale_mode or "linear",
        "scalable": recipe.scalable,
        "source_type": recipe.source_type,
        "source_name": recipe.source_name,
        "source_url": recipe.source_url,
        "high_risk_flags": list(recipe.high_risk_flags or []),
        "caution_text": recipe.caution_text,
        "time_profile": {
            "total_minutes": recipe.time_total_minutes,
            "active_minutes": recipe.time_active_minutes,
        },
        "effort_level": recipe.effort_level,
        "washing_level": recipe.washing_level,
        "use_cases": list(recipe.use_cases or []),
        "adaptations": recipe.adaptations or [],
        "prep": recipe.prep or [],
        "notes": recipe.notes or [],
        "ingredients": [],
        "steps": [],
        "variants": [],
    }
    if recipe.servings is not None:
        payload["servings"] = recipe.servings
    if recipe.yield_weight_g is not None:
        payload["yield_weight_g"] = _num(recipe.yield_weight_g)
        if recipe.yield_kind:
            payload["yield_kind"] = recipe.yield_kind

    for line in recipe.ingredients.select_related("ingredient").all():
        row = {
            "position": line.position,
            "canonical_id": line.ingredient.canonical_id,
            "display_name": line.display_name or line.ingredient.title,
            "amount": _num(line.amount),
            "unit": line.unit,
            "scale_mode": line.scale_mode,
            "scalable": line.scalable,
            "is_anchor": line.is_anchor,
            "optional": line.optional,
        }
        if line.amount_max is not None:
            row["amount_max"] = _num(line.amount_max)
        if line.detail:
            row["detail"] = line.detail
        if line.choice_group:
            row["choice_group"] = line.choice_group
        if line.nutrition_exclude:
            row["nutrition_exclude"] = True
        if line.nutrition_factor is not None:
            row["nutrition_factor"] = _num(line.nutrition_factor)
        payload["ingredients"].append(row)

    for step in recipe.steps.all():
        row = {"position": step.position, "text": step.text}
        if step.timer_seconds is not None:
            row["timer_seconds"] = step.timer_seconds
        if step.timer_label:
            row["timer_label"] = step.timer_label
        if step.timer_note:
            row["timer_note"] = step.timer_note
        if step.pull_internal_temperature_c is not None:
            row["pull_internal_temperature_c"] = step.pull_internal_temperature_c
        if step.target_internal_temperature_c is not None:
            row["target_internal_temperature_c"] = step.target_internal_temperature_c
        if step.hold_seconds is not None:
            row["hold_seconds"] = step.hold_seconds
        if step.equipment_note:
            row["equipment_note"] = step.equipment_note
        payload["steps"].append(row)

    for variant in recipe.variants.all():
        row = {
            "axis": variant.axis,
            "code": variant.code,
            "title": variant.title,
            "has_delta": variant.has_delta,
        }
        if variant.legacy_text:
            row["legacy_text"] = variant.legacy_text
        if variant.ingredient_delta is not None:
            row["ingredient_delta"] = variant.ingredient_delta
        if variant.step_delta is not None:
            row["step_delta"] = variant.step_delta
        if variant.allergen_delta is not None:
            row["allergen_delta"] = variant.allergen_delta
        if variant.high_risk_delta:
            row["high_risk_delta"] = variant.high_risk_delta
        if variant.cook_method_override:
            row["cook_method_override"] = variant.cook_method_override
        if variant.protein_base_override:
            row["protein_base_override"] = variant.protein_base_override
        if variant.equipment:
            row["equipment"] = variant.equipment
        if variant.caution_text_override:
            row["caution_text_override"] = variant.caution_text_override
        payload["variants"].append(row)

    return payload
