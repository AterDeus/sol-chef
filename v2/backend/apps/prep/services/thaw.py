"""When to pull a freezer box — from type and size, not one evening-before template."""

from __future__ import annotations

import re
from typing import Any

_LABEL_NUM = re.compile(r"№\s*(\d+)")

# Cooked diced / sheet veg thaw in a few hours. Meat, fish, liquid do not.
DICED_COMPONENT_CODES = frozenset(
    {
        "roasted_vegetables",
        "roasted_pumpkin",
        "roasted_veg_near",
        "roasted_veg_pumpkin",
        "braised_cabbage",
    }
)

THAW_EVENING = "evening_before"
THAW_MORNING = "morning"


def thaw_pull_for(
    place: str,
    thaw_before_day: int | None,
    unit: str | None,
    component_code: str | None,
) -> str | None:
    if place != "freezer" or thaw_before_day is None:
        return None
    if unit == "ml":
        return THAW_EVENING
    if component_code in DICED_COMPONENT_CODES:
        return THAW_MORNING
    return THAW_EVENING


def thaw_lead_hours(pull: str | None, unit: str | None, qty: Any) -> int:
    if pull == THAW_MORNING:
        return 3
    try:
        amount = float(qty or 0)
    except (TypeError, ValueError):
        amount = 0.0
    if unit == "ml" and amount >= 1000:
        return 30
    return 12


def container_number(label: str | None) -> str | None:
    if not label:
        return None
    match = _LABEL_NUM.search(label)
    return f"№{match.group(1)}" if match else None


def format_container_list(labels: list[str]) -> str:
    nums = [container_number(label) for label in labels]
    if labels and all(nums):
        word = "контейнер" if len(nums) == 1 else "контейнеры"
        if len(nums) == 1:
            joined = nums[0]
        elif len(nums) == 2:
            joined = f"{nums[0]} и {nums[1]}"
        else:
            joined = ", ".join(nums[:-1]) + f" и {nums[-1]}"
        return f"{word} {joined}"
    return ", ".join(label for label in labels if label)


def thaw_day_reminder(*, evening: bool, prev_day_genitive: str | None, labels: list[str]) -> str:
    names = format_container_list(labels)
    if evening:
        day = prev_day_genitive or "кануна"
        return f"С вечера {day} достаньте из морозилки {names} и переложите в холодильник."
    return f"Утром достаньте из морозилки {names} и переложите в холодильник."


def thaw_prep_item_text(*, morning: bool, label: str | None, component_title: str | None) -> str:
    when = "Утром" if morning else "С вечера"
    num = container_number(label)
    title = (component_title or "").strip()
    if num and title:
        what = f"контейнер {num} ({title})"
    elif num:
        what = f"контейнер {num}"
    elif title:
        what = title
    else:
        what = (label or "заготовку").strip()
    return f"{when} достаньте {what} из морозилки и переложите в холодильник."
