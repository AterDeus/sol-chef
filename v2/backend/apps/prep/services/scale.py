from __future__ import annotations

from decimal import Decimal
from typing import Any

from apps.core.numbers import decimal_api
from apps.recipes.services.scale import apply_mode, format_display_amount, round_scaled


def kit_ratio(servings_base: int | None, servings: Decimal | None) -> tuple[Decimal, bool]:
    if servings_base is None or servings is None:
        return Decimal("1"), False
    return servings / Decimal(servings_base), True


def scale_qty(qty: Any, unit: str, ratio: Decimal, enabled: bool) -> Decimal:
    amount = qty if isinstance(qty, Decimal) else Decimal(str(qty))
    scaled = apply_mode(amount, ratio, "linear", True) if enabled else amount
    return round_scaled(scaled, unit)


def qty_payload(qty: Any, unit: str, ratio: Decimal, enabled: bool) -> dict:
    scaled = scale_qty(qty, unit, ratio, enabled)
    return {
        "qty": decimal_api(scaled),
        "unit": unit,
        "display_amount": format_display_amount(scaled, unit),
    }
