"""Scaling domain service. Next.js does not compute ratio ** 0.7."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal
from typing import Any

from apps.recipes.constants import UNIT_LABEL_RU

GENTLE_EXPONENT = Decimal("0.7")
# V1 used 1+(ratio-1)*0.5 — never use that here.


class ScaleConflict(Exception):
    """Both servings and anchor_weight were provided — API 400."""


@dataclass(frozen=True)
class ScaleResult:
    enabled: bool
    mode: str  # anchor | servings | off
    ratio: Decimal
    base_anchor: dict[str, Any] | None
    applied: dict[str, Any] | None


def _d(value: Any) -> Decimal:
    if isinstance(value, Decimal):
        return value
    return Decimal(str(value))


def _quantize(value: Decimal, quant: Decimal) -> Decimal:
    return value.quantize(quant, rounding=ROUND_HALF_UP)


def round_scaled(amount: Decimal, unit: str, *, whole: bool = False) -> Decimal:
    """UI rounding from DEFAULTS (port of V1 roundScaled, not the gentle formula)."""
    if whole:
        rounded = _quantize(amount, Decimal("1"))
        return max(Decimal("1"), rounded)

    if unit in {"g", "ml"}:
        if amount >= 200:
            return _quantize(amount / Decimal("10"), Decimal("1")) * Decimal("10")
        if amount >= 50:
            return _quantize(amount / Decimal("5"), Decimal("1")) * Decimal("5")
        return _quantize(amount, Decimal("1"))

    if unit in {"kg", "l"}:
        return _quantize(amount, Decimal("0.01"))

    if unit in {"pcs", "clove", "bunch", "slice"}:
        half = _quantize(amount * 2, Decimal("1")) / Decimal("2")
        return max(Decimal("0.5"), half)

    if unit in {"tsp", "tbsp"}:
        return _quantize(amount * 4, Decimal("1")) / Decimal("4")

    return _quantize(amount, Decimal("0.1"))


def apply_mode(amount: Decimal, ratio: Decimal, scale_mode: str, scalable: bool) -> Decimal:
    if not scalable:
        return amount
    if scale_mode == "manual":
        return amount
    if scale_mode == "gentle":
        return amount * (ratio ** GENTLE_EXPONENT)
    return amount * ratio


def format_display_amount(
    amount: Decimal | None, unit: str, amount_max: Decimal | None = None
) -> str:
    label = UNIT_LABEL_RU.get(unit, unit)
    if unit in {"to_taste", "pinch"} or amount is None:
        return label
    text = _format_number(amount)
    if amount_max is not None:
        text = f"{text}–{_format_number(amount_max)}"
    return f"{text} {label}"


def _format_number(value: Decimal) -> str:
    normalized = value
    if normalized == normalized.to_integral_value():
        return str(int(normalized))
    text = format(normalized, "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text.replace(".", ",")


def base_anchor_amount(amount: Decimal, unit: str) -> tuple[Decimal, str] | None:
    """Convert kg/l to g/ml for ratio. Returns (amount, base_unit)."""
    if unit == "kg":
        return amount * Decimal("1000"), "g"
    if unit == "l":
        return amount * Decimal("1000"), "ml"
    if unit in {"g", "ml"}:
        return amount, unit
    return None


def _json_number(value: Decimal) -> int | float:
    if value == value.to_integral_value():
        return int(value)
    return float(value)


def resolve_scale(
    *,
    recipe_scalable: bool,
    recipe_servings: int | None,
    anchor_amount: Decimal | None,
    anchor_unit: str | None,
    servings: Decimal | None,
    anchor_weight: Decimal | None,
    anchor_name: str | None = None,
) -> ScaleResult:
    """Compute ratio from servings XOR anchor_weight.

    No servings and no anchor on the recipe → scaling off; do not invent 4 portions.
    recipe.scalable=false → ignore query, enabled=false.
    """
    if servings is not None and anchor_weight is not None:
        raise ScaleConflict("Нельзя передавать servings и anchor_weight одновременно.")

    off = ScaleResult(
        enabled=False, mode="off", ratio=Decimal("1"), base_anchor=None, applied=None
    )

    if not recipe_scalable:
        return off

    base = None
    if anchor_amount is not None and anchor_unit:
        converted = base_anchor_amount(anchor_amount, anchor_unit)
        if converted:
            base_val, base_unit = converted
            base = {
                "amount": _json_number(base_val),
                "unit": base_unit,
                "name": anchor_name or "",
            }

    has_servings_base = recipe_servings is not None and recipe_servings > 0
    has_anchor_base = base is not None

    if servings is None and anchor_weight is None:
        return off

    if servings is not None:
        if not has_servings_base:
            return off
        ratio = _d(servings) / Decimal(recipe_servings)
        return ScaleResult(
            enabled=True,
            mode="servings",
            ratio=ratio,
            base_anchor=base,
            applied={"servings": _json_number(_d(servings))},
        )

    if not has_anchor_base:
        return off
    ratio = _d(anchor_weight) / _d(base["amount"])
    return ScaleResult(
        enabled=True,
        mode="anchor",
        ratio=ratio,
        base_anchor=base,
        applied={"anchor_weight": _json_number(_d(anchor_weight))},
    )


def scale_line(
    *,
    amount: Decimal | None,
    amount_max: Decimal | None,
    unit: str,
    scale_mode: str,
    scalable: bool,
    ratio: Decimal,
    scaling_enabled: bool,
) -> tuple[Decimal | None, Decimal | None]:
    """Return scaled (and rounded) amount / amount_max. Timers/temps are never scaled."""
    if amount is None:
        return None, None
    if not scaling_enabled:
        return amount, amount_max

    whole = scale_mode == "whole" and scalable
    raw = apply_mode(amount, ratio, scale_mode, scalable)
    out = round_scaled(raw, unit, whole=whole)
    out_max = None
    if amount_max is not None:
        raw_max = apply_mode(amount_max, ratio, scale_mode, scalable)
        out_max = round_scaled(raw_max, unit, whole=whole)
    return out, out_max
