"""Strict JSON scalar parsers for draft ETL. Never bool(raw) on author input."""

from __future__ import annotations

import math
from decimal import Decimal, InvalidOperation
from typing import Any


class DraftValidationError(ValueError):
    pass


def as_bool(value: Any, *, field: str, default: bool | None = None) -> bool:
    if value is None:
        if default is None:
            raise DraftValidationError(f"{field}: требуется boolean")
        return default
    if isinstance(value, bool):
        return value
    raise DraftValidationError(f"{field}: требуется true или false")


def as_int(
    value: Any,
    *,
    field: str,
    min_value: int | None = None,
    max_value: int | None = None,
    nullable: bool = False,
) -> int | None:
    if value is None or value == "":
        if nullable:
            return None
        raise DraftValidationError(f"{field}: требуется integer")
    if isinstance(value, bool):
        raise DraftValidationError(f"{field}: требуется integer")
    if not isinstance(value, int):
        raise DraftValidationError(f"{field}: требуется integer")
    if min_value is not None and value < min_value:
        raise DraftValidationError(f"{field}: значение должно быть ≥ {min_value}")
    if max_value is not None and value > max_value:
        raise DraftValidationError(f"{field}: значение должно быть ≤ {max_value}")
    return value


def as_decimal(
    value: Any,
    *,
    field: str,
    nullable: bool = True,
    min_value: Decimal | None = None,
    max_value: Decimal | None = None,
) -> Decimal | None:
    if value is None or value == "":
        if nullable:
            return None
        raise DraftValidationError(f"{field}: требуется number")
    if isinstance(value, bool):
        raise DraftValidationError(f"{field}: требуется number")
    if isinstance(value, Decimal):
        number = value
    elif isinstance(value, int):
        number = Decimal(value)
    elif isinstance(value, float):
        if not math.isfinite(value):
            raise DraftValidationError(f"{field}: NaN/Infinity запрещены")
        number = Decimal(str(value))
    else:
        raise DraftValidationError(f"{field}: требуется number")
    if not number.is_finite():
        raise DraftValidationError(f"{field}: NaN/Infinity запрещены")
    if min_value is not None and number < min_value:
        raise DraftValidationError(f"{field}: значение должно быть ≥ {min_value}")
    if max_value is not None and number > max_value:
        raise DraftValidationError(f"{field}: значение должно быть ≤ {max_value}")
    return number


def finite_nonnegative(value: object, *, field: str) -> Decimal:
    if isinstance(value, bool):
        raise ValueError(f"{field}: нужно конечное значение ≥ 0")
    try:
        number = value if isinstance(value, Decimal) else Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise ValueError(f"{field}: нужно конечное значение ≥ 0") from exc
    if not number.is_finite() or number < 0:
        raise ValueError(f"{field}: нужно конечное значение ≥ 0")
    return number
