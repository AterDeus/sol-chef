from __future__ import annotations

import os
from decimal import Decimal
from types import SimpleNamespace

import pytest

from apps.recipes.query import BadQuery, parse_codes
from apps.recipes.services.assemble import (
    VariantError,
    apply_ingredient_delta,
    assemble_display,
    available_equipment_codes,
    catalog_protein_bases,
    catalog_protein_variants,
    count_anchors,
    pick_anchor,
    resolve_axes,
)
from apps.recipes.services.notes import split_notes_blob
from apps.recipes.services.scale import apply_mode, resolve_scale, scale_line


def _line(**kwargs):
    row = {
        "canonical_id": "beef",
        "name": "говядина",
        "amount": Decimal("500"),
        "amount_max": None,
        "unit": "g",
        "detail": None,
        "scalable": True,
        "scale_mode": "linear",
        "is_anchor": True,
        "position": 0,
        "allergens_contains": [],
        "allergens_may_contain": [],
        "allergens_unknown": [],
    }
    row.update(kwargs)
    return row


def test_u10_addon_delta_changes_display_legacy_does_not():
    base = [_line()]
    addon_delta = {
        "has_delta": True,
        "ingredient_delta": {
            "add": [
                {
                    "canonical_id": "mushroom",
                    "name": "шампиньоны",
                    "amount": Decimal("150"),
                    "unit": "g",
                    "scalable": True,
                    "scale_mode": "linear",
                }
            ]
        },
    }
    lines, *_rest = assemble_display(
        base_lines=base,
        base_steps=[],
        base_allergens={},
        base_flags=[],
        base_caution=None,
        base_cook_method="pan_fry",
        base_protein_base="beef",
        addon=addon_delta,
        equipment=None,
    )
    assert [row["canonical_id"] for row in lines] == ["beef", "mushroom"]

    legacy = {"has_delta": False, "ingredient_delta": addon_delta["ingredient_delta"]}
    lines_legacy, *_rest = assemble_display(
        base_lines=base,
        base_steps=[],
        base_allergens={},
        base_flags=[],
        base_caution=None,
        base_cook_method="pan_fry",
        base_protein_base="beef",
        addon=legacy,
        equipment=None,
    )
    assert [row["canonical_id"] for row in lines_legacy] == ["beef"]


def test_u11_unknown_variant_equipment_cuts():
    recipe = SimpleNamespace(equipment="skillet")
    try:
        resolve_axes(recipe=recipe, variants=[], variant_code="nope", equipment_code=None)
        raise AssertionError("expected VariantError")
    except VariantError:
        pass
    try:
        resolve_axes(recipe=recipe, variants=[], variant_code=None, equipment_code="kazan")
        raise AssertionError("expected VariantError")
    except VariantError:
        pass

    class DummyRequest:
        query_params = type(
            "Q",
            (),
            {
                "getlist": staticmethod(lambda key: ["not_a_cut"] if key == "cuts" else []),
            },
        )()

    try:
        parse_codes(DummyRequest(), "cuts")
        raise AssertionError("expected BadQuery")
    except BadQuery:
        pass


def test_air_fryer_method_variant_on_equipment_axis():
    variant = SimpleNamespace(
        axis="equipment",
        has_delta=True,
        code="air_fryer",
        equipment=None,
        cook_method_override="air_fryer",
    )
    recipe = SimpleNamespace(equipment="oven")
    assert available_equipment_codes(recipe, [variant]) == ["oven", "air_fryer"]
    addon, equipment_variant, applied = resolve_axes(
        recipe=recipe,
        variants=[variant],
        variant_code=None,
        equipment_code="air_fryer",
    )
    assert addon is None
    assert equipment_variant is variant
    assert applied == "air_fryer"
    try:
        resolve_axes(
            recipe=recipe,
            variants=[variant],
            variant_code=None,
            equipment_code="deep_fry",
        )
        raise AssertionError("expected VariantError")
    except VariantError:
        pass


def test_u12_notes_split_is_list_of_objects():
    assert split_notes_blob(None) == []
    one = split_notes_blob("Один абзац.")
    assert isinstance(one, list)
    assert one == [{"title": None, "text": "Один абзац."}]
    two = split_notes_blob("Первый.\n\nВторой.")
    assert len(two) == 2
    assert all(item["title"] is None and "text" in item for item in two)
    assert not isinstance(two, str)


def test_u13_scale_after_delta_uses_base_anchor():
    base = [_line(amount=Decimal("500"))]
    lines = apply_ingredient_delta(
        base,
        {
            "add": [
                {
                    "canonical_id": "parmesan",
                    "name": "пармезан",
                    "amount": Decimal("40"),
                    "unit": "g",
                    "scalable": True,
                    "scale_mode": "linear",
                }
            ]
        },
    )
    assert count_anchors(lines) == 1
    anchor = pick_anchor(lines)
    assert anchor["canonical_id"] == "beef"
    scale = resolve_scale(
        recipe_scalable=True,
        recipe_servings=None,
        anchor_amount=anchor["amount"],
        anchor_unit=anchor["unit"],
        servings=None,
        anchor_weight=Decimal("1000"),
        anchor_name=anchor["name"],
    )
    assert scale.ratio == Decimal("2")
    added = next(row for row in lines if row["canonical_id"] == "parmesan")
    scaled, _ = scale_line(
        amount=added["amount"],
        amount_max=None,
        unit="g",
        scale_mode="linear",
        scalable=True,
        ratio=scale.ratio,
        scaling_enabled=True,
    )
    assert scaled == apply_mode(Decimal("40"), Decimal("2"), "linear", True)
    beef, _ = scale_line(
        amount=anchor["amount"],
        amount_max=None,
        unit="g",
        scale_mode="linear",
        scalable=True,
        ratio=scale.ratio,
        scaling_enabled=True,
    )
    assert beef == Decimal("1000")


def test_protein_override_changes_display_base():
    lines, _steps, _allergens, _flags, _caution, _method, protein = assemble_display(
        base_lines=[_line()],
        base_steps=[],
        base_allergens={},
        base_flags=[],
        base_caution=None,
        base_cook_method="pan_fry",
        base_protein_base="poultry",
        addon={"has_delta": True, "protein_base_override": "beef"},
        equipment=None,
    )
    assert protein == "beef"
    assert [row["canonical_id"] for row in lines] == ["beef"]


def test_catalog_protein_lists_include_override_and_extra():
    class Related:
        def __init__(self, items):
            self._items = items

        def all(self):
            return self._items

    recipe = SimpleNamespace(
        protein_base="poultry",
        protein_bases_extra=["pork"],
        variants=Related(
            [
                SimpleNamespace(
                    axis="addon",
                    has_delta=True,
                    code="beef",
                    title="С говядиной",
                    protein_base_override="beef",
                ),
                SimpleNamespace(
                    axis="addon",
                    has_delta=True,
                    code="spicy",
                    title="Острее",
                    protein_base_override=None,
                ),
            ]
        ),
    )
    assert catalog_protein_bases(recipe) == ["poultry", "pork", "beef"]
    assert catalog_protein_variants(recipe) == [
        {"code": "beef", "title": "С говядиной", "protein_base": "beef"}
    ]


@pytest.mark.skipif(
    not (os.environ.get("POSTGRES_HOST") or os.environ.get("DATABASE_URL")),
    reason="нет POSTGRES_HOST/DATABASE_URL",
)
@pytest.mark.django_db
def test_i8b_protein_filter_matches_override():
    from rest_framework.test import APIClient

    from apps.recipes.models import Recipe, RecipeVariant

    recipe = Recipe.objects.create(
        slug="domashnyaya-shaurma-iz-kuritsy",
        title="Домашняя шаурма из курицы",
        protein_base="poultry",
        cook_method="pan_fry",
        dish_type="main",
        scale_mode="linear",
        scalable=True,
        energy_profile="standard",
        status="published",
    )
    RecipeVariant.objects.create(
        recipe=recipe,
        axis="addon",
        code="beef",
        title="С говядиной",
        has_delta=True,
        protein_base_override="beef",
        ingredient_delta={"add": []},
    )
    client = APIClient()
    listed = client.get("/api/recipes/", {"protein_base": "beef"})
    assert listed.status_code == 200
    slugs = [item["slug"] for item in listed.json()["results"]]
    assert recipe.slug in slugs
    card = next(item for item in listed.json()["results"] if item["slug"] == recipe.slug)
    assert card["protein_base"] == "poultry"
    assert "beef" in card["protein_bases"]
    assert card["protein_variants"] == [
        {"code": "beef", "title": "С говядиной", "protein_base": "beef"}
    ]
    rec = client.get("/api/recommendations/", {"protein_base": "beef"})
    assert rec.status_code == 200
    featured = rec.json().get("featured") or {}
    results = rec.json().get("results") or []
    rows = [featured] if featured.get("slug") else []
    rows.extend(results)
    hit = next((item for item in rows if item.get("slug") == recipe.slug), None)
    assert hit is not None
    assert hit["protein_base"] == "beef"
    assert hit["applied_axes"]["variant"] == "beef"
    assert "beef" in (hit.get("protein_bases") or [])
    assert hit.get("protein_variants") == [
        {"code": "beef", "title": "С говядиной", "protein_base": "beef"}
    ]


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
    }
    defaults.update(kwargs)
    return Recipe.objects.create(**defaults)


@pytest.mark.django_db
def test_i16_catalog_page_size():
    from rest_framework.test import APIClient

    for i in range(21):
        _card(slug=f"page-size-{i}", title=f"Page {i:02d}")
    client = APIClient()

    default = client.get("/api/recipes/")
    assert default.status_code == 200
    body = default.json()
    assert body["count"] == 21
    assert len(body["results"]) == 20
    assert body["next"] is not None

    small = client.get("/api/recipes/", {"page_size": 5})
    assert small.status_code == 200
    assert len(small.json()["results"]) == 5
    assert small.json()["count"] == 21

    huge = client.get("/api/recipes/", {"page_size": 999})
    assert huge.status_code == 200
    assert len(huge.json()["results"]) == 21

    sampled = client.get("/api/recipes/", {"sample": 3})
    assert sampled.status_code == 200
    body = sampled.json()
    assert len(body["results"]) == 3
    assert body["count"] == 3
    assert body["next"] is None

    assert client.get("/api/recipes/", {"sample": 0}).status_code == 400
    assert client.get("/api/recipes/", {"sample": 99}).status_code == 400
    assert client.get("/api/recipes/", {"sample": "x"}).status_code == 400
