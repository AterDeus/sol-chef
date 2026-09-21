from __future__ import annotations

import os

import pytest

needs_postgres = pytest.mark.skipif(
    not (os.environ.get("POSTGRES_HOST") or os.environ.get("DATABASE_URL")),
    reason="нет POSTGRES_HOST/DATABASE_URL",
)


def _write_sql(queries) -> list[str]:
    found: list[str] = []
    for item in queries:
        sql = item["sql"].lstrip()
        if sql.startswith('"'):
            sql = sql.strip('"')
        first = sql.split(None, 1)[0].upper() if sql else ""
        if first in {"INSERT", "UPDATE", "DELETE"}:
            found.append(item["sql"])
    return found


def _card(**kwargs):
    from apps.recipes.models import Recipe

    defaults = {
        "protein_base": "poultry",
        "cook_method": "pan_fry",
        "dish_type": "main",
        "scale_mode": "linear",
        "scalable": True,
        "energy_profile": "standard",
        "status": "published",
        "content_version": 1,
        "snapshot_version": 0,
    }
    defaults.update(kwargs)
    return Recipe.objects.create(**defaults)


@needs_postgres
@pytest.mark.django_db
def test_refresh_skips_write_when_content_version_changes():
    from django.core.cache import cache

    from apps.recipes.models import Recipe
    from apps.recipes.services.snapshots import refresh_axis_snapshots

    cache.clear()
    recipe = _card(slug="snap-version", title="Снапшот", content_version=5)
    refresh_axis_snapshots(recipe)
    recipe.refresh_from_db()
    assert recipe.snapshot_version == 5
    assert recipe.snapshots_updated_at is not None
    assert recipe.axis_snapshots

    Recipe.objects.filter(pk=recipe.pk).update(content_version=6)
    recipe.content_version = 5
    old_snaps = list(recipe.axis_snapshots)
    old_updated = recipe.snapshots_updated_at
    refresh_axis_snapshots(recipe)
    recipe.refresh_from_db()
    assert recipe.content_version == 6
    assert recipe.snapshot_version == 5
    assert recipe.axis_snapshots == old_snaps
    assert recipe.snapshots_updated_at == old_updated


@needs_postgres
@pytest.mark.django_db
def test_get_endpoints_query_budget_and_no_writes():
    from django.core.cache import cache
    from django.db import connection
    from django.test.utils import CaptureQueriesContext
    from rest_framework.test import APIClient

    from apps.recipes.models import Ingredient, RecipeIngredient, RecipeStep, RecipeVariant

    cache.clear()
    ing = Ingredient.objects.create(canonical_id="budget-chicken", title="курица")
    recipe = _card(
        slug="query-budget-card",
        title="Бюджет запросов",
        content_version=1,
        snapshot_version=0,
    )
    RecipeIngredient.objects.create(
        recipe=recipe,
        ingredient=ing,
        position=0,
        amount=500,
        unit="g",
        scalable=True,
        scale_mode="linear",
        is_anchor=True,
    )
    RecipeStep.objects.create(recipe=recipe, position=0, text="Жарить.")
    RecipeVariant.objects.create(
        recipe=recipe,
        axis="addon",
        code="spicy",
        title="Острее",
        has_delta=False,
    )
    client = APIClient()

    with CaptureQueriesContext(connection) as ctx:
        detail = client.get("/api/recipes/query-budget-card/")
    assert detail.status_code == 200
    assert _write_sql(ctx.captured_queries) == []
    assert len(ctx.captured_queries) <= 20

    with CaptureQueriesContext(connection) as ctx:
        listed = client.get("/api/recipes/")
    assert listed.status_code == 200
    assert _write_sql(ctx.captured_queries) == []
    assert len(ctx.captured_queries) <= 25

    with CaptureQueriesContext(connection) as ctx:
        rec = client.get("/api/recommendations/", {"protein_base": "poultry"})
    assert rec.status_code == 200
    assert _write_sql(ctx.captured_queries) == []
    assert len(ctx.captured_queries) <= 50
