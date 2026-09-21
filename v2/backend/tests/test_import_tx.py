"""Import transaction, publish default, revision append, DB constraints."""

from __future__ import annotations

import os
from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db.utils import IntegrityError as DbIntegrityError

from apps.recipes.etl.upsert import upsert_recipe
from apps.recipes.models import (
    Ingredient,
    Recipe,
    RecipeIngredient,
    RecipeRevision,
    RecipeStep,
)

needs_postgres = pytest.mark.skipif(
    not (os.environ.get("POSTGRES_HOST") or os.environ.get("DATABASE_URL")),
    reason="нет POSTGRES_HOST/DATABASE_URL",
)


def _item(**overrides) -> dict:
    item = {
        "slug": "tx-import-card",
        "title": "Тестовая карта",
        "protein_base": "beef",
        "cook_method": "pan_fry",
        "dish_type": "main",
        "scale_mode": "linear",
        "scalable": True,
        "servings": None,
        "summary": None,
        "source_name": None,
        "source_url": None,
        "source_type": None,
        "high_risk_flags": [],
        "caution_text": None,
        "energy_profile": "standard",
        "equipment": "skillet",
        "allowed_cuts": [],
        "notes": [],
        "prep": [],
        "time_total_minutes": 20,
        "time_active_minutes": 10,
        "effort_level": 2,
        "washing_level": 1,
        "use_cases": [],
        "adaptations": [],
        "ingredient_titles": "говядина",
        "lines": [
            {
                "canonical_id": "beef-tx",
                "ingredient_title": "говядина",
                "aliases": [],
                "contains": [],
                "may_contain": [],
                "unknown": [],
                "position": 0,
                "amount": Decimal("500"),
                "amount_max": None,
                "unit": "g",
                "detail": None,
                "scale_mode": "linear",
                "scalable": True,
                "is_anchor": True,
                "optional": False,
                "nutrition_exclude": False,
                "nutrition_factor": None,
                "choice_group": None,
                "display_name": "говядина",
            }
        ],
        "steps": [
            {
                "position": 0,
                "text": "Обжарить порциями, не перегружать сковороду.",
                "timer_seconds": None,
                "timer_label": None,
                "timer_note": None,
                "pull_internal_temperature_c": None,
                "target_internal_temperature_c": None,
                "hold_seconds": None,
                "equipment_note": "Порциями.",
            }
        ],
        "variants": [],
        "origin": "draft",
        "raw": {"id": "tx-import-card", "title": "Тестовая карта"},
    }
    item.update(overrides)
    return item


@needs_postgres
@pytest.mark.django_db
def test_second_step_error_rolls_back_recipe_and_children():
    item = _item(
        steps=[
            {
                "position": 0,
                "text": "Первый шаг ок.",
                "timer_seconds": None,
                "timer_label": None,
                "timer_note": None,
                "pull_internal_temperature_c": None,
                "target_internal_temperature_c": None,
                "hold_seconds": None,
                "equipment_note": None,
            },
            {
                "position": 1,
                "text": "Пулл без цели.",
                "timer_seconds": None,
                "timer_label": None,
                "timer_note": None,
                "pull_internal_temperature_c": 60,
                "target_internal_temperature_c": None,
                "hold_seconds": None,
                "equipment_note": None,
            },
        ]
    )
    with pytest.raises(ValidationError):
        upsert_recipe(item)
    assert not Recipe.objects.filter(slug="tx-import-card").exists()
    assert not RecipeIngredient.objects.filter(ingredient__canonical_id="beef-tx").exists()
    assert not RecipeRevision.objects.filter(recipe__slug="tx-import-card").exists()
    assert not Ingredient.objects.filter(canonical_id="beef-tx").exists()


@needs_postgres
@pytest.mark.django_db
def test_new_recipe_is_draft_unless_publish_flag():
    recipe = upsert_recipe(_item())
    assert recipe.status == "draft"
    assert recipe.snapshot_version != recipe.content_version


@needs_postgres
@pytest.mark.django_db
def test_reimport_preserves_published_without_flag():
    first = upsert_recipe(_item(), publish=True)
    assert first.status == "published"
    pk = first.ingredients.get(position=0).pk
    again = upsert_recipe(_item())
    assert again.status == "published"
    assert again.ingredients.get(position=0).pk == pk


@needs_postgres
@pytest.mark.django_db
def test_identical_payload_does_not_append_revision():
    upsert_recipe(_item(), publish=True)
    upsert_recipe(_item(), publish=True)
    recipe = Recipe.objects.get(slug="tx-import-card")
    assert recipe.revisions.count() == 1
    assert recipe.revisions.get().number == 1


@needs_postgres
@pytest.mark.django_db
def test_changed_payload_appends_revision():
    upsert_recipe(_item(), publish=True)
    upsert_recipe(_item(title="Другое название"), publish=True)
    numbers = list(
        RecipeRevision.objects.filter(recipe__slug="tx-import-card")
        .order_by("number")
        .values_list("number", "payload_json")
    )
    assert [row[0] for row in numbers] == [1, 2]
    assert numbers[0][1]["title"] == "Тестовая карта"
    assert numbers[1][1]["title"] == "Другое название"


@needs_postgres
@pytest.mark.django_db
def test_sync_deletes_only_disappeared_positions():
    upsert_recipe(_item(), publish=True)
    item = _item()
    extra = dict(item["lines"][0])
    extra["canonical_id"] = "onion-tx"
    extra["ingredient_title"] = "лук"
    extra["display_name"] = "лук"
    extra["position"] = 1
    extra["is_anchor"] = False
    extra["amount"] = Decimal("100")
    item["lines"] = [item["lines"][0], extra]
    recipe = upsert_recipe(item, publish=True)
    assert recipe.ingredients.count() == 2
    kept_pk = recipe.ingredients.get(position=0).pk
    trimmed = _item()
    recipe = upsert_recipe(trimmed, publish=True)
    assert recipe.ingredients.count() == 1
    assert recipe.ingredients.get(position=0).pk == kept_pk
    assert not RecipeIngredient.objects.filter(ingredient__canonical_id="onion-tx").exists()


@needs_postgres
@pytest.mark.django_db
def test_unique_ingredient_position_constraint():
    recipe = upsert_recipe(_item(), publish=True)
    beef = Ingredient.objects.get(canonical_id="beef-tx")
    with pytest.raises((IntegrityError, DbIntegrityError)):
        RecipeIngredient.objects.create(
            recipe=recipe,
            ingredient=beef,
            position=0,
            unit="g",
            amount=Decimal("1"),
        )


@needs_postgres
@pytest.mark.django_db
def test_unique_step_position_constraint():
    recipe = upsert_recipe(_item(), publish=True)
    with pytest.raises((IntegrityError, DbIntegrityError)):
        RecipeStep.objects.create(recipe=recipe, position=0, text="дубль")
