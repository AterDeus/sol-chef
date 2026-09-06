"""Map V1 ingredient rows to VOCAB units and scale_mode."""

from __future__ import annotations

from decimal import Decimal, InvalidOperation

from apps.recipes.constants import V1_UNIT_TO_VOCAB
from apps.recipes.etl.load import V1ImportError

# 1 Russian cup = 250 ml. VOCAB forbids storing cup; convert amount.
CUP_TO_ML = Decimal("250")

GENTLE_NAME_MARKERS = (
    "соль",
    "перец",
    "паприка",
    "зира",
    "кумин",
    "куркума",
    "кориандр",
    "корица",
    "гвоздика",
    "чили",
    "гарам",
    "шафран",
    "тимьян",
    "розмарин",
    "хлопья перца",
    "хлопья чили",
)

MANUAL_NAME_MARKERS = (
    "сода",
    "разрыхлител",
    "дрожж",
    "желатин",
)

EGG_NAME_MARKERS = ("яйц", "белок")

OIL_NAMES = (
    "растительное масло",
    "оливковое масло",
)

SPICE_OIL_UNITS = {"tsp", "tbsp"}


def parse_amount(value) -> Decimal | None:
    if value is None or value == "":
        return None
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise V1ImportError(f"Некорректное количество {value!r}") from exc


def map_unit_and_amount(v1_unit: str | None, amount: Decimal | None) -> tuple[str, Decimal | None]:
    if not v1_unit:
        return "to_taste", None
    unit = v1_unit.strip()
    if unit == "стакана":
        if amount is None:
            raise V1ImportError("Единица «стакана» без количества")
        return "ml", amount * CUP_TO_ML
    mapped = V1_UNIT_TO_VOCAB.get(unit)
    if mapped is None:
        raise V1ImportError(f"Неизвестная единица V1: {unit!r}")
    return mapped, amount


def infer_scale_mode(name: str, unit: str, explicit: str | None) -> str:
    if explicit in {"linear", "gentle", "whole", "manual"}:
        return explicit
    lower = name.lower()
    # Do NOT use V1 autodetet «soda → gentle».
    if any(marker in lower for marker in MANUAL_NAME_MARKERS):
        return "manual"
    if unit == "pcs" and any(marker in lower for marker in EGG_NAME_MARKERS):
        return "whole"
    if any(marker in lower for marker in GENTLE_NAME_MARKERS):
        return "gentle"
    if lower in OIL_NAMES and unit in SPICE_OIL_UNITS:
        return "gentle"
    return "linear"


def is_anchor_candidate(scalable: bool, amount: Decimal | None, unit: str) -> bool:
    return scalable and amount is not None and unit in {"g", "ml", "kg", "l"}


def is_optional_line(detail: str | None) -> bool:
    """Garnish / serving / «по желанию» — not required for the dish."""
    text = (detail or "").lower()
    return "для подачи" in text or "по желанию" in text
