"""Write a parsed recipe dict into Postgres (V1 ETL and draft overlay)."""

from __future__ import annotations

from apps.recipes.models import (
    Ingredient,
    Recipe,
    RecipeIngredient,
    RecipeRevision,
    RecipeStep,
    RecipeVariant,
)


def upsert_recipe(item: dict) -> Recipe:
    recipe, _created = Recipe.objects.update_or_create(
        slug=item["slug"],
        defaults={
            "title": item["title"],
            "protein_base": item["protein_base"],
            "cook_method": item["cook_method"],
            "dish_type": item["dish_type"],
            "scale_mode": item.get("scale_mode") or "linear",
            "scalable": item.get("scalable", True),
            "servings": item.get("servings"),
            "summary": item.get("summary"),
            "source_name": item.get("source_name"),
            "source_url": item.get("source_url"),
            "source_type": item.get("source_type"),
            "editorial_tested": False,
            "high_risk_flags": item.get("high_risk_flags") or [],
            "caution_text": item.get("caution_text"),
            "energy_profile": item.get("energy_profile") or "standard",
            "status": item.get("status") or "published",
            "ingredient_titles": item.get("ingredient_titles") or "",
            "equipment": item.get("equipment"),
            "allowed_cuts": item.get("allowed_cuts") or [],
            "notes": item.get("notes") or [],
            "prep": item.get("prep") or [],
            "time_total_minutes": item.get("time_total_minutes"),
            "time_active_minutes": item.get("time_active_minutes"),
            "effort_level": item.get("effort_level"),
            "washing_level": item.get("washing_level"),
            "use_cases": item.get("use_cases") or [],
            "adaptations": item.get("adaptations") or [],
        },
    )
    recipe.full_clean(exclude=["search_vector"])
    recipe.save()

    for canon in item.get("new_canons") or []:
        Ingredient.objects.update_or_create(
            canonical_id=canon["canonical_id"],
            defaults={
                "title": canon.get("title") or canon["canonical_id"],
                "aliases": canon.get("aliases") or [],
                "allergens_contains": canon.get("contains") or [],
                "allergens_may_contain": canon.get("may_contain") or [],
                "allergens_unknown": canon.get("unknown") or [],
            },
        )

    RecipeIngredient.objects.filter(recipe=recipe).delete()
    RecipeStep.objects.filter(recipe=recipe).delete()
    RecipeVariant.objects.filter(recipe=recipe).delete()

    for line in item["lines"]:
        ingredient, _ = Ingredient.objects.update_or_create(
            canonical_id=line["canonical_id"],
            defaults={
                "title": line["ingredient_title"],
                "aliases": line.get("aliases") or [],
                "allergens_contains": line.get("contains") or [],
                "allergens_may_contain": line.get("may_contain") or [],
                "allergens_unknown": line.get("unknown") or [],
            },
        )
        RecipeIngredient.objects.create(
            recipe=recipe,
            ingredient=ingredient,
            position=line["position"],
            amount=line.get("amount"),
            amount_max=line.get("amount_max"),
            unit=line["unit"],
            detail=line.get("detail"),
            scale_mode=line.get("scale_mode") or "linear",
            scalable=bool(line.get("scalable", True)),
            is_anchor=bool(line.get("is_anchor")),
            optional=bool(line.get("optional", False)),
            choice_group=line.get("choice_group"),
            display_name=line.get("display_name"),
        )
    for step in item["steps"]:
        RecipeStep.objects.create(
            recipe=recipe,
            position=step["position"],
            text=step["text"],
            timer_seconds=step.get("timer_seconds"),
            timer_label=step.get("timer_label"),
            timer_note=step.get("timer_note"),
            pull_internal_temperature_c=step.get("pull_internal_temperature_c"),
            target_internal_temperature_c=step.get("target_internal_temperature_c"),
            hold_seconds=step.get("hold_seconds"),
            equipment_note=step.get("equipment_note"),
        )
    for variant in item.get("variants") or []:
        RecipeVariant.objects.create(
            recipe=recipe,
            axis=variant["axis"],
            code=variant["code"],
            title=variant["title"],
            has_delta=bool(variant.get("has_delta")),
            legacy_text=variant.get("legacy_text"),
            ingredient_delta=variant.get("ingredient_delta"),
            step_delta=variant.get("step_delta"),
            allergen_delta=variant.get("allergen_delta"),
            high_risk_delta=variant.get("high_risk_delta") or {},
            cook_method_override=variant.get("cook_method_override"),
            equipment=variant.get("equipment"),
            caution_text_override=variant.get("caution_text_override"),
        )

    payload = {
        "slug": item["slug"],
        "title": item["title"],
        "origin": item.get("origin") or "v1",
        "protein_base": item["protein_base"],
        "cook_method": item["cook_method"],
        "dish_type": item["dish_type"],
        "raw": item.get("raw"),
    }
    RecipeRevision.objects.update_or_create(
        recipe=recipe,
        status="published",
        defaults={"payload_json": payload},
    )
    return recipe
