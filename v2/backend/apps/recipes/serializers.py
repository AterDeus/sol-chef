from __future__ import annotations

from decimal import Decimal

from apps.recipes.models import Recipe
from apps.recipes.services.assemble import AssembledRecipe, catalog_allergens, pick_anchor
from apps.recipes.services.nutrition import (
    compute_recipe_nutrition,
    nutrition_line_projection,
    nutrition_skip_hint,
)
from apps.recipes.services.scale import (
    ScaleResult,
    format_display_amount,
    scale_line,
)


def _num(value: Decimal | None) -> int | float | None:
    if value is None:
        return None
    if not isinstance(value, Decimal):
        value = Decimal(str(value))
    if value == value.to_integral_value():
        return int(value)
    return float(value)


def catalog_scaling(recipe: Recipe) -> dict:
    has_anchor = any(line.is_anchor for line in recipe.ingredients.all())
    enabled = bool(recipe.scalable) and (recipe.servings is not None or has_anchor)
    return {"enabled": enabled}


def serialize_recipe_list_item(recipe: Recipe) -> dict:
    variants = list(recipe.variants.all())
    return {
        "slug": recipe.slug,
        "title": recipe.title,
        "protein_base": recipe.protein_base,
        "cook_method": recipe.cook_method,
        "dish_type": recipe.dish_type,
        "equipment": recipe.equipment,
        "allowed_cuts": list(recipe.allowed_cuts or []),
        "summary": recipe.summary,
        "editorial_tested": recipe.editorial_tested,
        "high_risk_flags": list(recipe.high_risk_flags or []),
        "allergens": catalog_allergens(recipe),
        "has_delta_variants": any(
            item.axis == "addon" and item.has_delta for item in variants
        ),
        "scaling": catalog_scaling(recipe),
        "time_profile": {
            "total_minutes": recipe.time_total_minutes,
            "active_minutes": recipe.time_active_minutes,
        },
        "effort_level": recipe.effort_level,
        "washing_level": recipe.washing_level,
        "use_cases": list(recipe.use_cases or []),
    }


def serialize_display_line(line: dict, scale: ScaleResult) -> dict:
    amount, amount_max = scale_line(
        amount=line.get("amount"),
        amount_max=line.get("amount_max"),
        unit=line["unit"],
        scale_mode=line.get("scale_mode") or "linear",
        scalable=bool(line.get("scalable", True)),
        ratio=scale.ratio,
        scaling_enabled=scale.enabled,
    )
    return {
        "name": line["name"],
        "amount": _num(amount),
        "amount_max": _num(amount_max),
        "unit": line["unit"],
        "detail": line.get("detail"),
        "scalable": bool(line.get("scalable", True)),
        "scale_mode": line.get("scale_mode") or "linear",
        "is_anchor": bool(line.get("is_anchor")),
        "optional": bool(line.get("optional")),
        "nutrition_exclude": bool(line.get("nutrition_exclude")),
        "nutrition_skip_hint": nutrition_skip_hint(line),
        "display_amount": format_display_amount(amount, line["unit"], amount_max),
        "nutrition_line": nutrition_line_projection(line),
    }


def serialize_display_step(step: dict) -> dict:
    return {
        "text": step.get("text") or "",
        "timer_seconds": step.get("timer_seconds"),
        "timer_label": step.get("timer_label"),
        "timer_note": step.get("timer_note"),
        "pull_internal_temperature_c": step.get("pull_internal_temperature_c"),
        "target_internal_temperature_c": step.get("target_internal_temperature_c"),
        "hold_seconds": step.get("hold_seconds"),
    }


def serialize_recipe_detail(
    recipe: Recipe, assembled: AssembledRecipe, scale: ScaleResult
) -> dict:
    ingredients = [serialize_display_line(line, scale) for line in assembled.ingredients]
    steps = [serialize_display_step(step) for step in assembled.steps]
    anchor = pick_anchor(assembled.ingredients)
    base_anchor = scale.base_anchor
    if base_anchor is None and anchor and anchor.get("amount") is not None:
        from apps.recipes.services.scale import base_anchor_amount

        converted = base_anchor_amount(anchor["amount"], anchor["unit"])
        if converted:
            base_val, base_unit = converted
            base_anchor = {
                "amount": _num(base_val),
                "unit": base_unit,
                "name": anchor.get("name") or "",
            }
    can_scale = bool(recipe.scalable) and (
        recipe.servings is not None or base_anchor is not None
    )
    if not can_scale:
        scaling = {"enabled": False, "mode": "off", "ratio": 1, "base_anchor": base_anchor}
    else:
        scaling = {
            "enabled": True,
            "mode": scale.mode,
            "ratio": float(scale.ratio),
            "base_anchor": base_anchor,
            "applied": scale.applied,
        }
    nutrition = compute_recipe_nutrition(
        assembled.ingredients,
        servings=recipe.servings,
        ratio=scale.ratio,
        scaling_enabled=scale.enabled,
        yield_weight_g=recipe.yield_weight_g,
    )
    return {
        "slug": recipe.slug,
        "title": recipe.title,
        "protein_base": recipe.protein_base,
        "cook_method": assembled.cook_method,
        "dish_type": recipe.dish_type,
        "equipment": assembled.equipment,
        "allowed_cuts": list(recipe.allowed_cuts or []),
        "applied_axes": assembled.applied_axes,
        "available_variants": assembled.available_variants,
        "available_equipment": assembled.available_equipment,
        "summary": recipe.summary,
        "source_name": recipe.source_name,
        "source_url": recipe.source_url or None,
        "editorial_tested": recipe.editorial_tested,
        "high_risk_flags": assembled.high_risk_flags,
        "caution_text": assembled.caution_text,
        "allergens": assembled.allergens,
        "nutrition": nutrition,
        "scaling": scaling,
        "servings": recipe.servings,
        "yield_weight_g": _num(recipe.yield_weight_g),
        "yield_kind": recipe.yield_kind,
        "ingredients": ingredients,
        "steps": steps,
        "variations": assembled.variations,
        "notes": assembled.notes,
        "prep": assembled.prep,
        "time_profile": {
            "total_minutes": recipe.time_total_minutes,
            "active_minutes": recipe.time_active_minutes,
        },
        "effort_level": recipe.effort_level,
        "washing_level": recipe.washing_level,
        "use_cases": list(recipe.use_cases or []),
        "adaptations": recipe.adaptations if isinstance(recipe.adaptations, list) else [],
    }
