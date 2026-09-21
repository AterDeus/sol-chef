from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Any


class PayloadError(ValueError):
    pass


def integer(
    value: Any,
    *,
    field: str,
    min_value: int | None = None,
    max_value: int | None = None,
    nullable: bool = False,
) -> int | None:
    if value in (None, "") and nullable:
        return None
    if isinstance(value, bool):
        raise PayloadError(f"{field}: требуется целое число.")
    try:
        number = int(value)
    except (TypeError, ValueError) as exc:
        raise PayloadError(f"{field}: требуется целое число.") from exc
    token = str(value).strip()
    if token not in {str(number), f"+{number}"}:
        raise PayloadError(f"{field}: требуется целое число без дробной части.")
    if min_value is not None and number < min_value:
        raise PayloadError(f"{field}: требуется число ≥ {min_value}.")
    if max_value is not None and number > max_value:
        raise PayloadError(f"{field}: требуется число ≤ {max_value}.")
    return number


def positive_int(
    value: Any, *, field: str, nullable: bool = False, max_value: int | None = None
) -> int | None:
    return integer(
        value, field=field, min_value=1, max_value=max_value, nullable=nullable
    )


def nonnegative_decimal(value: Any, *, field: str) -> Decimal:
    if isinstance(value, bool):
        raise PayloadError(f"{field}: некорректное количество.")
    try:
        number = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise PayloadError(f"{field}: некорректное количество.") from exc
    if not number.is_finite() or number < 0:
        raise PayloadError(f"{field}: требуется конечное число ≥ 0.")
    return number


def entity_code(item: dict) -> str:
    return str(item.get("id") or item.get("code") or "").strip()


def kit_slug_of(payload: dict) -> str:
    raw = payload.get("slug") or payload.get("id")
    return str(raw or "").strip()
