from __future__ import annotations

from decimal import Decimal

from apps.recipes.services.scale import (
    ScaleConflict,
    apply_mode,
    resolve_scale,
    round_scaled,
)


def test_u1_gentle_uses_ratio_power_not_v1():
    amount = Decimal("10")
    ratio = Decimal("4")
    got = apply_mode(amount, ratio, "gentle", True)
    v2 = amount * (ratio ** Decimal("0.7"))
    v1 = amount * (Decimal("1") + (ratio - Decimal("1")) * Decimal("0.5"))
    assert got == v2
    assert got != v1


def test_u2_linear_multiplies_ratio():
    got = apply_mode(Decimal("100"), Decimal("2.5"), "linear", True)
    assert got == Decimal("250")


def test_u3_whole_integer_min_one():
    assert round_scaled(Decimal("0.2"), "pcs", whole=True) == Decimal("1")
    assert round_scaled(Decimal("2.4"), "pcs", whole=True) == Decimal("2")
    assert round_scaled(Decimal("2.5"), "pcs", whole=True) == Decimal("3")


def test_u4_manual_and_not_scalable_keep_amount():
    amount = Decimal("3")
    ratio = Decimal("10")
    assert apply_mode(amount, ratio, "manual", True) == amount
    assert apply_mode(amount, ratio, "linear", False) == amount
    assert apply_mode(amount, ratio, "gentle", False) == amount


def test_velvet_soda_scales_linear_with_meat():
    from apps.recipes.services.scale import scale_line

    amount, _ = scale_line(
        amount=Decimal("0.5"),
        amount_max=None,
        unit="tsp",
        scale_mode="linear",
        scalable=True,
        ratio=Decimal("6"),
        scaling_enabled=True,
    )
    assert amount == Decimal("3")


def test_u5_rounding_defaults():
    assert round_scaled(Decimal("247"), "g") == Decimal("250")
    assert round_scaled(Decimal("53"), "ml") == Decimal("55")
    assert round_scaled(Decimal("12.2"), "g") == Decimal("12")
    assert round_scaled(Decimal("1.239"), "kg") == Decimal("1.24")
    assert round_scaled(Decimal("0.2"), "pcs") == Decimal("0.5")
    assert round_scaled(Decimal("1.2"), "pcs") == Decimal("1.0")
    assert round_scaled(Decimal("0.6"), "tsp") == Decimal("0.5")
    assert round_scaled(Decimal("1.1"), "tbsp") == Decimal("1")


def test_u8_both_sources_raise():
    try:
        resolve_scale(
            recipe_scalable=True,
            recipe_servings=4,
            anchor_amount=Decimal("500"),
            anchor_unit="g",
            servings=Decimal("2"),
            anchor_weight=Decimal("600"),
        )
    except ScaleConflict:
        return
    raise AssertionError("expected ScaleConflict")


def test_u9_no_anchor_no_servings_does_not_invent_portions():
    result = resolve_scale(
        recipe_scalable=True,
        recipe_servings=None,
        anchor_amount=None,
        anchor_unit=None,
        servings=None,
        anchor_weight=None,
    )
    assert result.enabled is False
    assert result.mode == "off"
    assert result.ratio == Decimal("1")

    ignored = resolve_scale(
        recipe_scalable=True,
        recipe_servings=None,
        anchor_amount=None,
        anchor_unit=None,
        servings=Decimal("4"),
        anchor_weight=None,
    )
    assert ignored.enabled is False

    unscalable = resolve_scale(
        recipe_scalable=False,
        recipe_servings=4,
        anchor_amount=Decimal("500"),
        anchor_unit="g",
        servings=Decimal("8"),
        anchor_weight=None,
    )
    assert unscalable.enabled is False
