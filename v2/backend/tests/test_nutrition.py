from __future__ import annotations

import json
import os
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path
from types import SimpleNamespace

import pytest

from apps.recipes.serializers import serialize_display_line, serialize_recipe_detail
from apps.recipes.services.assemble import AssembledRecipe, apply_ingredient_delta
from apps.recipes.services.nutrition import (
    compute_recipe_nutrition,
    nutrition_line_projection,
    nutrition_skip_hint,
)
from apps.recipes.services.scale import ScaleResult, apply_mode

SEED = (
    Path(__file__).resolve().parents[1]
    / "apps"
    / "recipes"
    / "fixtures"
    / "ingredient_nutrition.json"
)


def _line(**kwargs) -> dict:
    row = {
        "canonical_id": "x",
        "name": "x",
        "amount": Decimal("100"),
        "amount_max": None,
        "unit": "g",
        "scalable": True,
        "scale_mode": "linear",
        "optional": False,
        "nutrition_exclude": False,
        "kcal_per_100g": Decimal("100"),
        "protein_g_per_100g": Decimal("10"),
        "fat_g_per_100g": Decimal("5"),
        "carbs_g_per_100g": Decimal("8"),
    }
    row.update(kwargs)
    return row


def _compute(lines, *, servings=None, ratio="1", enabled=False, yield_weight_g=None):
    return compute_recipe_nutrition(
        lines,
        servings=servings,
        ratio=Decimal(str(ratio)),
        scaling_enabled=enabled,
        yield_weight_g=yield_weight_g,
    )


def test_u23_sum_grams_kcal_from_canon_not_atwater():
    lines = [
        _line(
            amount=Decimal("100"),
            kcal_per_100g=Decimal("137"),
            protein_g_per_100g=Decimal("29.8"),
            fat_g_per_100g=Decimal("1.8"),
            carbs_g_per_100g=Decimal("0"),
        ),
        _line(
            amount=Decimal("80"),
            kcal_per_100g=Decimal("200"),
            protein_g_per_100g=Decimal("10"),
            fat_g_per_100g=Decimal("10"),
            carbs_g_per_100g=Decimal("10"),
        ),
        _line(
            amount=Decimal("50"),
            kcal_per_100g=Decimal("50"),
            protein_g_per_100g=Decimal("5"),
            fat_g_per_100g=Decimal("1"),
            carbs_g_per_100g=Decimal("2"),
        ),
    ]
    nut = _compute(lines)
    protein = Decimal("29.8") + Decimal("8") + Decimal("2.5")
    fat = Decimal("1.8") + Decimal("8") + Decimal("0.5")
    carbs = Decimal("0") + Decimal("8") + Decimal("1")
    atwater = protein * 4 + fat * 9 + carbs * 4
    assert nut["total"]["kcal"] == 322
    assert nut["total"]["protein_g"] == 40.3
    assert nut["total"]["fat_g"] == 10.3
    assert nut["total"]["carbs_g"] == 9
    assert nut["total"]["kcal"] != int(atwater)
    assert nut["incomplete"] is False


def test_u24_gentle_oil_after_apply_mode_not_total_times_ratio():
    oil = _line(
        canonical_id="vegetable_oil",
        amount=Decimal("1"),
        unit="tbsp",
        scale_mode="gentle",
        kcal_per_100g=Decimal("884"),
        protein_g_per_100g=Decimal("0"),
        fat_g_per_100g=Decimal("100"),
        carbs_g_per_100g=Decimal("0"),
        g_per_tbsp=Decimal("13.6"),
    )
    ratio = Decimal("4")
    nut = _compute([oil], ratio=ratio, enabled=True)
    scaled = apply_mode(Decimal("1"), ratio, "gentle", True)
    grams = scaled * Decimal("13.6")
    expected_kcal = int(
        (Decimal("884") * grams / Decimal("100")).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    )
    naive = int(
        ((Decimal("884") * Decimal("13.6") / Decimal("100")) * ratio).quantize(
            Decimal("1"), rounding=ROUND_HALF_UP
        )
    )
    assert nut["total"]["kcal"] == expected_kcal
    assert nut["total"]["kcal"] != naive


def test_u25_no_servings_per_serving_none():
    nut = _compute([_line()], servings=None)
    assert nut["per_serving"] is None


def test_u26_water_in_mass_zero_macros_meat_kcal():
    meat = _line(
        canonical_id="beef",
        amount=Decimal("100"),
        kcal_per_100g=Decimal("187"),
        protein_g_per_100g=Decimal("21"),
        fat_g_per_100g=Decimal("11"),
        carbs_g_per_100g=Decimal("0"),
    )
    water = _line(
        canonical_id="water",
        amount=Decimal("200"),
        kcal_per_100g=Decimal("0"),
        protein_g_per_100g=Decimal("0"),
        fat_g_per_100g=Decimal("0"),
        carbs_g_per_100g=Decimal("0"),
        density_g_per_ml=Decimal("1"),
    )
    nut = _compute([meat, water])
    assert nut["total"]["kcal"] == 187
    assert nut["total"]["protein_g"] == 21
    assert nut["per_100g_input"] is not None
    assert nut["per_100g_input"]["kcal"] == 62
    assert nut["per_100g_input"]["protein_g"] == 7
    assert nut["per_100g_input"]["fat_g"] == 3.7
    assert nut["per_100g_input"]["carbs_g"] == 0


def test_u27_nutrition_exclude_out_of_sum_and_mass():
    meat = _line(
        amount=Decimal("100"),
        kcal_per_100g=Decimal("187"),
        protein_g_per_100g=Decimal("21"),
        fat_g_per_100g=Decimal("11"),
        carbs_g_per_100g=Decimal("0"),
    )
    oil = _line(
        canonical_id="vegetable_oil",
        amount=Decimal("50"),
        kcal_per_100g=Decimal("884"),
        protein_g_per_100g=Decimal("0"),
        fat_g_per_100g=Decimal("100"),
        carbs_g_per_100g=Decimal("0"),
        nutrition_exclude=True,
    )
    nut = _compute([meat, oil])
    assert nut["total"]["kcal"] == 187
    assert nut["per_100g_input"]["kcal"] == 187
    assert nut["incomplete"] is False


def test_u28_optional_not_in_sum():
    required = _line(amount=Decimal("100"), kcal_per_100g=Decimal("100"))
    garnish = _line(
        canonical_id="parsley",
        amount=Decimal("50"),
        kcal_per_100g=Decimal("200"),
        optional=True,
    )
    nut = _compute([required, garnish])
    assert nut["total"]["kcal"] == 100
    assert nut["per_100g_input"]["kcal"] == 100


def test_u29_tbsp_without_g_per_tbsp_incomplete_no_15g():
    line = _line(
        amount=Decimal("1"),
        unit="tbsp",
        kcal_per_100g=Decimal("884"),
        protein_g_per_100g=Decimal("0"),
        fat_g_per_100g=Decimal("100"),
        carbs_g_per_100g=Decimal("0"),
    )
    nut = _compute([line])
    assert nut["incomplete"] is True
    assert nut["total"]["kcal"] == 0
    guessed = int((Decimal("884") * Decimal("15") / Decimal("100")).quantize(Decimal("1")))
    assert nut["total"]["kcal"] != guessed
    assert nutrition_line_projection(line) is None


def test_u30_delta_changes_total():
    base = [
        _line(
            canonical_id="beef",
            amount=Decimal("100"),
            kcal_per_100g=Decimal("187"),
            protein_g_per_100g=Decimal("21"),
            fat_g_per_100g=Decimal("11"),
            carbs_g_per_100g=Decimal("0"),
        )
    ]
    onion = _line(
        canonical_id="onion",
        amount=Decimal("100"),
        kcal_per_100g=Decimal("40"),
        protein_g_per_100g=Decimal("1.1"),
        fat_g_per_100g=Decimal("0.1"),
        carbs_g_per_100g=Decimal("9.3"),
        g_per_pcs=Decimal("100"),
        unit="pcs",
    )
    onion["amount"] = Decimal("1")
    with_delta = apply_ingredient_delta(
        base,
        {"add": [onion]},
    )
    base_nut = _compute(base)
    delta_nut = _compute(with_delta)
    assert delta_nut["total"]["kcal"] != base_nut["total"]["kcal"]
    assert delta_nut["total"]["kcal"] == base_nut["total"]["kcal"] + 40


def test_u32_salt_to_taste_not_incomplete():
    meat = _line(
        canonical_id="beef",
        amount=Decimal("100"),
        kcal_per_100g=Decimal("187"),
        protein_g_per_100g=Decimal("21"),
        fat_g_per_100g=Decimal("11"),
        carbs_g_per_100g=Decimal("0"),
    )
    salt = _line(
        canonical_id="salt",
        amount=None,
        unit="to_taste",
        scalable=False,
        kcal_per_100g=Decimal("0"),
        protein_g_per_100g=Decimal("0"),
        fat_g_per_100g=Decimal("0"),
        carbs_g_per_100g=Decimal("0"),
        g_per_tsp=Decimal("6"),
    )
    nut = _compute([meat, salt])
    assert nut["incomplete"] is False
    assert nut["total"]["kcal"] == 187
    assert nutrition_line_projection(salt) is None
    assert nutrition_skip_hint(salt) is False


def test_u32_honey_to_taste_not_incomplete():
    meat = _line(
        canonical_id="beef",
        amount=Decimal("100"),
        kcal_per_100g=Decimal("187"),
        protein_g_per_100g=Decimal("21"),
        fat_g_per_100g=Decimal("11"),
        carbs_g_per_100g=Decimal("0"),
    )
    honey = _line(
        canonical_id="honey",
        amount=None,
        unit="to_taste",
        scalable=False,
        kcal_per_100g=Decimal("304"),
        protein_g_per_100g=Decimal("0.3"),
        fat_g_per_100g=Decimal("0"),
        carbs_g_per_100g=Decimal("82"),
        g_per_tsp=Decimal("7"),
    )
    nut = _compute([meat, honey])
    assert nut["incomplete"] is False
    assert nut["total"]["kcal"] == 187
    assert nutrition_line_projection(honey) is None
    assert nutrition_skip_hint(honey) is True


def test_u32_skip_hint_on_display_line():
    scale = ScaleResult(
        enabled=False, mode="off", ratio=Decimal("1"), base_anchor=None, applied=None
    )
    salt = serialize_display_line(
        _line(
            canonical_id="salt",
            unit="to_taste",
            amount=None,
            scalable=False,
            kcal_per_100g=Decimal("0"),
        ),
        scale,
    )
    honey = serialize_display_line(
        _line(
            canonical_id="honey",
            unit="to_taste",
            amount=None,
            scalable=False,
            kcal_per_100g=Decimal("304"),
        ),
        scale,
    )
    grams = serialize_display_line(_line(), scale)
    pepper = serialize_display_line(
        _line(
            canonical_id="black_pepper",
            unit="pinch",
            amount=None,
            scalable=False,
            kcal_per_100g=Decimal("251"),
            fat_g_per_100g=Decimal("3.3"),
            carbs_g_per_100g=Decimal("64"),
        ),
        scale,
    )
    assert salt["nutrition_skip_hint"] is False
    assert honey["nutrition_skip_hint"] is True
    assert grams["nutrition_skip_hint"] is False
    assert pepper["nutrition_skip_hint"] is False


def test_u34_range_uses_amount_min_not_max():
    line = _line(
        amount=Decimal("1"),
        amount_max=Decimal("2"),
        unit="tbsp",
        kcal_per_100g=Decimal("53"),
        protein_g_per_100g=Decimal("8.1"),
        fat_g_per_100g=Decimal("0.1"),
        carbs_g_per_100g=Decimal("4.9"),
        g_per_tbsp=Decimal("16"),
    )
    nut = _compute([line])
    expected = (Decimal("53") * Decimal("16") / Decimal("100")).quantize(Decimal("1"))
    mid = (Decimal("53") * Decimal("24") / Decimal("100")).quantize(Decimal("1"))
    hi = (Decimal("53") * Decimal("32") / Decimal("100")).quantize(Decimal("1"))
    assert nut["total"]["kcal"] == int(expected)
    assert nut["total"]["kcal"] != int(mid)
    assert nut["total"]["kcal"] != int(hi)


def test_u35_keys_per_100g_input_not_aliases():
    nut = _compute([_line()])
    assert "per_100g_input" in nut
    assert "per_100g" not in nut
    assert "per_100g_raw" not in nut
    scale = ScaleResult(
        enabled=False, mode="off", ratio=Decimal("1"), base_anchor=None, applied=None
    )
    row = serialize_display_line(_line(name="говядина"), scale)
    assert "nutrition_line" in row
    assert row["nutrition_exclude"] is False
    excluded = serialize_display_line(_line(name="масло", nutrition_exclude=True), scale)
    assert excluded["nutrition_exclude"] is True
    assert excluded["nutrition_line"] is None
    recipe = SimpleNamespace(
        slug="x",
        title="X",
        protein_base="beef",
        dish_type="main",
        allowed_cuts=[],
        summary=None,
        source_name=None,
        source_url=None,
        editorial_tested=False,
        servings=None,
        yield_weight_g=None,
        yield_kind=None,
        scalable=True,
        time_total_minutes=None,
        time_active_minutes=None,
        effort_level=None,
        washing_level=None,
        use_cases=[],
        adaptations=[],
    )
    assembled = AssembledRecipe(
        ingredients=[_line(name="говядина")],
        steps=[],
        allergens={"contains": [], "may_contain": [], "unknown": []},
        high_risk_flags=[],
        caution_text=None,
        cook_method="pan_fry",
        protein_base="beef",
        equipment="skillet",
        applied_axes={"variant": None, "equipment": "skillet"},
        available_variants=[],
        available_equipment=["skillet"],
        variations=[],
        notes=[],
        prep=[],
    )
    payload = serialize_recipe_detail(recipe, assembled, scale)
    assert "nutrition" in payload
    assert "per_100g_input" in payload["nutrition"]
    assert "per_100g" not in payload["nutrition"]
    assert "per_100g_raw" not in payload
    assert "per_100g_raw" not in payload["nutrition"]
    assert payload["nutrition"]["per_100g_cooked"] is None
    assert row["nutrition_line"]["nutrition_factor"] == 1


def test_u36_nutrition_factor_halves_oil_contribution():
    oil = _line(
        canonical_id="vegetable_oil",
        amount=Decimal("1"),
        unit="tbsp",
        kcal_per_100g=Decimal("884"),
        protein_g_per_100g=Decimal("0"),
        fat_g_per_100g=Decimal("100"),
        carbs_g_per_100g=Decimal("0"),
        g_per_tbsp=Decimal("13.6"),
        nutrition_factor=Decimal("0.5"),
    )
    full = _compute([_line(**{**oil, "nutrition_factor": Decimal("1")})])
    half = _compute([oil])
    assert half["total"]["kcal"] == round(full["total"]["kcal"] / 2)
    proj = nutrition_line_projection(oil)
    assert proj["nutrition_factor"] == 0.5
    assert proj["grams_per_unit"] == 13.6


def test_u37_yield_scales_linear_and_is_not_input_alias():
    meat = _line(
        amount=Decimal("200"),
        kcal_per_100g=Decimal("100"),
        protein_g_per_100g=Decimal("20"),
        fat_g_per_100g=Decimal("5"),
        carbs_g_per_100g=Decimal("0"),
        scale_mode="linear",
    )
    nut = _compute(
        [meat],
        ratio="2",
        enabled=True,
        yield_weight_g=Decimal("500"),
    )
    assert nut["total"]["kcal"] == 400
    assert nut["per_100g_input"]["kcal"] == 100
    assert nut["per_100g_cooked"]["kcal"] == 40
    assert nut["per_100g_cooked"] != nut["per_100g_input"]


def test_u38_no_yield_means_per_100g_cooked_null():
    nut = _compute([_line()])
    assert nut["per_100g_cooked"] is None



def test_seed_json_covers_velvet_and_oil():
    data = json.loads(SEED.read_text(encoding="utf-8"))
    assert data["vegetable_oil"]["kcal"] == 884
    assert data["beef"]["kcal"] == 187
    assert data["egg_white"]["g_per_pcs"] == 33
    assert data["corn_starch"]["g_per_tbsp"] == 8
    assert data["soy_sauce"]["g_per_tbsp"] == 16
    assert data["baking_soda"]["kcal"] == 0
    assert data["water"]["density_g_per_ml"] == 1


def test_seed_row_defaults_map_kcal_fields():
    from apps.recipes.etl.nutrition import _row_defaults, load_seed

    row = load_seed()["vegetable_oil"]
    fields = _row_defaults("vegetable_oil", row)
    assert fields["kcal_per_100g"] == Decimal("884")
    assert fields["nutrition_basis"] == "raw_100g"
    assert fields["g_per_tbsp"] == Decimal("13.6")
    assert "title" not in fields
    assert "allergens_contains" not in fields


def test_load_ingredient_nutrition_updates_oil_kcal(monkeypatch):
    from apps.recipes.etl import nutrition as nutrition_etl

    class _Ing:
        def __init__(self, cid: str):
            self.canonical_id = cid
            self.kcal_per_100g = None
            self.protein_g_per_100g = None
            self.fat_g_per_100g = None
            self.carbs_g_per_100g = None
            self.nutrition_basis = None
            self.nutrition_source = None
            self.nutrition_source_id = None
            self.density_g_per_ml = None
            self.g_per_tsp = None
            self.g_per_tbsp = None
            self.g_per_pcs = None
            self.g_per_clove = None
            self.g_per_bunch = None
            self.g_per_slice = None
            self.title = "масло"
            self.allergens_contains = ["should_not_be_written"]

    oil = _Ing("vegetable_oil")
    bulk: list[object] = []

    class _Manager:
        def filter(self, *, canonical_id__in):
            return [oil] if "vegetable_oil" in canonical_id__in else []

        def bulk_update(self, rows, fields, batch_size=None):
            bulk.extend(rows)
            return len(rows)

    monkeypatch.setattr(nutrition_etl.Ingredient, "objects", _Manager())
    report = nutrition_etl.load_ingredient_nutrition()
    assert report["updated"] >= 1
    assert bulk == [oil]
    assert oil.kcal_per_100g == Decimal("884")
    assert oil.nutrition_basis == "raw_100g"
    assert oil.g_per_tbsp == Decimal("13.6")
    assert oil.title == "масло"
    assert oil.allergens_contains == ["should_not_be_written"]


@pytest.mark.skipif(
    not (os.environ.get("POSTGRES_HOST") or os.environ.get("DATABASE_URL")),
    reason="нет POSTGRES_HOST/DATABASE_URL",
)
@pytest.mark.django_db
def test_seed_loads_vegetable_oil_kcal():
    from apps.recipes.etl.nutrition import load_ingredient_nutrition
    from apps.recipes.models import Ingredient

    Ingredient.objects.create(canonical_id="vegetable_oil", title="масло")
    load_ingredient_nutrition()
    ing = Ingredient.objects.get(canonical_id="vegetable_oil")
    assert ing.kcal_per_100g == Decimal("884")
    assert ing.nutrition_basis == "raw_100g"
    assert ing.g_per_tbsp == Decimal("13.6")
