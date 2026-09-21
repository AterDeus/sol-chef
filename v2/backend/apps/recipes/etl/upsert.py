"""Write a parsed recipe dict into Postgres (V1 ETL and draft overlay)."""

from __future__ import annotations

import hashlib
import json
import logging

from django.db import transaction
from django.db.models import F, Max

from apps.recipes.domain.enums import RecipeStatus, ScaleMode
from apps.recipes.models import (
    Ingredient,
    Recipe,
    RecipeIngredient,
    RecipeRevision,
    RecipeStep,
    RecipeVariant,
)

logger = logging.getLogger(__name__)


def upsert_recipe(item: dict, *, publish: bool | None = None) -> Recipe:
    """Persist one recipe graph atomically. Snapshots rebuild after commit."""
    _validate_item(item)
    slug = item["slug"]
    with transaction.atomic():
        recipe = Recipe.objects.select_for_update().filter(slug=slug).first()
        if recipe is None:
            recipe = Recipe(slug=slug)
        status = _resolve_status(recipe, item, publish)
        _apply_recipe_fields(recipe, item, status)
        recipe.full_clean(exclude=["search_vector"])
        recipe.save()

        for canon in item.get("new_canons") or []:
            _upsert_ingredient(
                canon["canonical_id"],
                {
                    "title": canon.get("title") or canon["canonical_id"],
                    "aliases": canon.get("aliases") or [],
                    "allergens_contains": canon.get("contains") or [],
                    "allergens_may_contain": canon.get("may_contain") or [],
                    "allergens_unknown": canon.get("unknown") or [],
                },
            )

        _sync_ingredients(recipe, item["lines"])
        _sync_steps(recipe, item["steps"])
        _sync_variants(recipe, item.get("variants") or [])
        _append_revision(recipe, item, status)
        Recipe.objects.filter(pk=recipe.pk).update(content_version=F("content_version") + 1)
        recipe_id = recipe.pk
        transaction.on_commit(lambda: _refresh_snapshots_after_commit(recipe_id))

    recipe.refresh_from_db()
    return recipe


def _validate_item(item: dict) -> None:
    for key in ("slug", "title", "protein_base", "cook_method", "dish_type"):
        if not item.get(key):
            raise ValueError(f"upsert: нет {key}")
    if not item.get("lines"):
        raise ValueError("upsert: нет ingredients")
    if not item.get("steps"):
        raise ValueError("upsert: нет steps")


def _resolve_status(recipe: Recipe, item: dict, publish: bool | None) -> str:
    if publish is True:
        return RecipeStatus.PUBLISHED
    if publish is False:
        return RecipeStatus.DRAFT
    if recipe.pk:
        return recipe.status
    return item.get("status") or RecipeStatus.DRAFT


def _apply_recipe_fields(recipe: Recipe, item: dict, status: str) -> None:
    recipe.title = item["title"]
    recipe.protein_base = item["protein_base"]
    recipe.protein_bases_extra = item.get("protein_bases_extra") or []
    recipe.cook_method = item["cook_method"]
    recipe.dish_type = item["dish_type"]
    recipe.scale_mode = item.get("scale_mode") or ScaleMode.LINEAR
    recipe.scalable = item.get("scalable", True)
    recipe.servings = item.get("servings")
    recipe.yield_weight_g = item.get("yield_weight_g")
    recipe.yield_kind = item.get("yield_kind")
    recipe.summary = item.get("summary")
    recipe.source_name = item.get("source_name")
    recipe.source_url = item.get("source_url")
    recipe.source_type = item.get("source_type")
    recipe.editorial_tested = False
    recipe.high_risk_flags = item.get("high_risk_flags") or []
    recipe.caution_text = item.get("caution_text")
    recipe.energy_profile = item.get("energy_profile") or "standard"
    recipe.status = status
    recipe.ingredient_titles = item.get("ingredient_titles") or ""
    recipe.equipment = item.get("equipment")
    recipe.allowed_cuts = item.get("allowed_cuts") or []
    recipe.notes = item.get("notes") or []
    recipe.prep = item.get("prep") or []
    recipe.time_total_minutes = item.get("time_total_minutes")
    recipe.time_active_minutes = item.get("time_active_minutes")
    recipe.effort_level = item.get("effort_level")
    recipe.washing_level = item.get("washing_level")
    recipe.use_cases = item.get("use_cases") or []
    recipe.adaptations = item.get("adaptations") or []


def _upsert_ingredient(canonical_id: str, defaults: dict) -> Ingredient:
    ingredient = Ingredient.objects.filter(canonical_id=canonical_id).first()
    if ingredient is None:
        ingredient = Ingredient(canonical_id=canonical_id, **defaults)
        ingredient.full_clean()
        ingredient.save()
        return ingredient
    for field, value in defaults.items():
        setattr(ingredient, field, value)
    ingredient.full_clean()
    ingredient.save()
    return ingredient


def _sync_ingredients(recipe: Recipe, lines: list[dict]) -> None:
    existing = {row.position: row for row in RecipeIngredient.objects.filter(recipe=recipe)}
    wanted = {line["position"] for line in lines}
    gone = [pos for pos in existing if pos not in wanted]
    if gone:
        RecipeIngredient.objects.filter(recipe=recipe, position__in=gone).delete()
    for line in lines:
        ingredient = _upsert_ingredient(
            line["canonical_id"],
            {
                "title": line["ingredient_title"],
                "aliases": line.get("aliases") or [],
                "allergens_contains": line.get("contains") or [],
                "allergens_may_contain": line.get("may_contain") or [],
                "allergens_unknown": line.get("unknown") or [],
            },
        )
        values = {
            "ingredient": ingredient,
            "amount": line.get("amount"),
            "amount_max": line.get("amount_max"),
            "unit": line["unit"],
            "detail": line.get("detail"),
            "scale_mode": line.get("scale_mode") or ScaleMode.LINEAR,
            "scalable": line.get("scalable", True),
            "is_anchor": line.get("is_anchor", False),
            "optional": line.get("optional", False),
            "nutrition_exclude": line.get("nutrition_exclude", False),
            "nutrition_factor": line.get("nutrition_factor"),
            "choice_group": line.get("choice_group"),
            "display_name": line.get("display_name"),
        }
        row = existing.get(line["position"])
        if row is None:
            row = RecipeIngredient(recipe=recipe, position=line["position"], **values)
        else:
            for field, value in values.items():
                setattr(row, field, value)
        row.full_clean()
        row.save()


def _sync_steps(recipe: Recipe, steps: list[dict]) -> None:
    existing = {row.position: row for row in RecipeStep.objects.filter(recipe=recipe)}
    wanted = {step["position"] for step in steps}
    gone = [pos for pos in existing if pos not in wanted]
    if gone:
        RecipeStep.objects.filter(recipe=recipe, position__in=gone).delete()
    for step in steps:
        values = {
            "text": step["text"],
            "timer_seconds": step.get("timer_seconds"),
            "timer_label": step.get("timer_label"),
            "timer_note": step.get("timer_note"),
            "pull_internal_temperature_c": step.get("pull_internal_temperature_c"),
            "target_internal_temperature_c": step.get("target_internal_temperature_c"),
            "hold_seconds": step.get("hold_seconds"),
            "equipment_note": step.get("equipment_note"),
        }
        row = existing.get(step["position"])
        if row is None:
            row = RecipeStep(recipe=recipe, position=step["position"], **values)
        else:
            for field, value in values.items():
                setattr(row, field, value)
        row.full_clean()
        row.save()


def _sync_variants(recipe: Recipe, drafts: list[dict]) -> None:
    existing = {
        (row.axis, row.code): row for row in RecipeVariant.objects.filter(recipe=recipe)
    }
    wanted = {(item["axis"], item["code"]) for item in drafts}
    gone_ids = [row.pk for key, row in existing.items() if key not in wanted]
    if gone_ids:
        RecipeVariant.objects.filter(pk__in=gone_ids).delete()
    for item in drafts:
        values = {
            "title": item["title"],
            "has_delta": item.get("has_delta", False),
            "legacy_text": item.get("legacy_text"),
            "ingredient_delta": item.get("ingredient_delta"),
            "step_delta": item.get("step_delta"),
            "allergen_delta": item.get("allergen_delta"),
            "high_risk_delta": item.get("high_risk_delta") or {},
            "cook_method_override": item.get("cook_method_override"),
            "protein_base_override": item.get("protein_base_override"),
            "equipment": item.get("equipment"),
            "caution_text_override": item.get("caution_text_override"),
        }
        row = existing.get((item["axis"], item["code"]))
        if row is None:
            row = RecipeVariant(
                recipe=recipe, axis=item["axis"], code=item["code"], **values
            )
        else:
            for field, value in values.items():
                setattr(row, field, value)
        row.full_clean()
        row.save()


def _revision_payload(item: dict) -> dict:
    return {
        "slug": item["slug"],
        "title": item["title"],
        "origin": item.get("origin") or "v1",
        "protein_base": item["protein_base"],
        "cook_method": item["cook_method"],
        "dish_type": item["dish_type"],
        "raw": item.get("raw"),
    }


def payload_hash(payload: dict) -> str:
    encoded = json.dumps(payload, sort_keys=True, default=str, ensure_ascii=False)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _append_revision(recipe: Recipe, item: dict, status: str) -> RecipeRevision | None:
    payload = _revision_payload(item)
    digest = payload_hash(payload)
    last = (
        RecipeRevision.objects.filter(recipe=recipe)
        .order_by("-number")
        .first()
    )
    if last is not None and last.payload_hash == digest:
        return last
    next_number = 1
    if last is not None:
        next_number = last.number + 1
    else:
        max_number = RecipeRevision.objects.filter(recipe=recipe).aggregate(Max("number"))[
            "number__max"
        ]
        if max_number:
            next_number = max_number + 1
    revision = RecipeRevision(
        recipe=recipe,
        number=next_number,
        status=status,
        payload_json=payload,
        payload_hash=digest,
    )
    revision.full_clean()
    revision.save()
    return revision


def _refresh_snapshots_after_commit(recipe_id: int) -> None:
    from apps.recipes.services.snapshots import refresh_axis_snapshots

    recipe = Recipe.objects.filter(pk=recipe_id).first()
    if recipe is None:
        return
    try:
        refresh_axis_snapshots(recipe)
    except Exception:
        logger.exception("axis snapshots rebuild failed for recipe_id=%s", recipe_id)
