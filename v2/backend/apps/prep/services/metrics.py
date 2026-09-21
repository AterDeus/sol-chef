from __future__ import annotations

from decimal import Decimal

from apps.prep.models import PrepKit
from apps.recipes.services.assemble import assemble_recipe
from apps.recipes.services.nutrition import compute_recipe_nutrition


def calculate_average_slot_kcal(kit: PrepKit) -> int | None:
    values: list[int] = []
    slots = kit.slots.select_related("recipe").prefetch_related(
        "recipe__ingredients__ingredient",
        "recipe__steps",
        "recipe__variants",
    )

    for slot in slots:
        recipe = slot.recipe
        nutrition = compute_recipe_nutrition(
            assemble_recipe(recipe).ingredients,
            servings=recipe.servings or kit.servings_base or 2,
            ratio=Decimal("1"),
            scaling_enabled=False,
            yield_weight_g=recipe.yield_weight_g,
        )
        kcal = (nutrition.get("per_serving") or {}).get("kcal")
        if kcal is not None:
            values.append(int(kcal))

    return round(sum(values) / len(values)) if values else None


def refresh_kit_metrics(kit: PrepKit) -> PrepKit:
    metrics = dict(kit.metrics or {})
    metrics["kcal_avg_per_serving"] = calculate_average_slot_kcal(kit)
    PrepKit.objects.filter(pk=kit.pk).update(metrics=metrics)
    kit.metrics = metrics
    return kit
