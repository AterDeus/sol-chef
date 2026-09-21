"""JSON-safe Decimal encoding. Do not use float() for authored quantities."""

from __future__ import annotations

import json
from decimal import Decimal


def decimal_json(value: Decimal | None) -> int | str | None:
    if value is None:
        return None
    if not isinstance(value, Decimal):
        value = Decimal(str(value))
    if not value.is_finite():
        raise ValueError("decimal must be finite")
    if value == value.to_integral_value():
        return int(value)
    return format(value.normalize(), "f")


def decimal_api(value: Decimal | None) -> int | float | str | None:
    """Public API number: int when whole, JSON number from decimal text otherwise.

    Avoids float(Decimal). Draft export still uses decimal_json strings.
    """
    encoded = decimal_json(value)
    if encoded is None or isinstance(encoded, int):
        return encoded
    return json.loads(encoded)
