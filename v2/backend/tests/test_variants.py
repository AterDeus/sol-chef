from __future__ import annotations

from decimal import Decimal
from types import SimpleNamespace

from apps.recipes.query import BadQuery, parse_codes
from apps.recipes.services.assemble import (
    VariantError,
    apply_ingredient_delta,
    assemble_display,
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
