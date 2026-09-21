"""Variant «Без вчерашнего»: cook leftover sources once, replace reheat slots."""

from __future__ import annotations

from decimal import Decimal

from apps.prep.constants import NO_LEFTOVER_FALSE, NO_LEFTOVER_TRUE, PrepMode
from apps.prep.exceptions import PrepError
from apps.prep.models import PrepSlot
from apps.prep.services.graph import source_key
from apps.prep.services.read_model import KitData
from apps.recipes.models import Recipe


def parse_no_leftover(request) -> bool:
    raw = request.query_params.get("no_leftover")
    if raw is None or raw == "":
        return False
    value = str(raw).strip().lower()
    if value in NO_LEFTOVER_TRUE:
        return True
    if value in NO_LEFTOVER_FALSE:
        return False
    raise PrepError("no_leftover: 1 или 0.")


def no_leftover_payload(slot: PrepSlot) -> dict:
    data = slot.no_leftover
    return data if isinstance(data, dict) else {}


def leftover_qty_factors(data: KitData) -> tuple[dict[str, Decimal], dict[str, Decimal]]:
    """Box code → factor, exclusive shopping canonical_id → factor."""
    slots = list(data.slots)
    boxes = list(data.containers)
    reheat_sources: set[tuple[int, str]] = set()
    source_feeds: dict[tuple[int, str], int] = {}
    for slot in slots:
        if slot.mode != PrepMode.REHEAT:
            continue
        key = source_key(slot)
        if key is None:
            continue
        reheat_sources.add(key)
    for slot in slots:
        key = (slot.day, slot.meal)
        if key in reheat_sources:
            source_feeds[key] = int(slot.feeds_slots or 1)

    weekend_users: dict[str, set[tuple[int, str]]] = {}
    for slot in slots:
        if slot.mode == PrepMode.REHEAT:
            continue
        for code in slot.container_ids or []:
            weekend_users.setdefault(str(code), set()).add((slot.day, slot.meal))

    box_factor: dict[str, Decimal] = {}
    for slot in slots:
        key = (slot.day, slot.meal)
        feeds = source_feeds.get(key, 1)
        if feeds <= 1:
            continue
        factor = Decimal(1) / Decimal(feeds)
        for code in slot.container_ids or []:
            code = str(code)
            users = weekend_users.get(code, set())
            if users and users <= reheat_sources:
                prev = box_factor.get(code, factor)
                box_factor[code] = min(prev, factor)

    leftover_canonical: set[str] = set()
    other_canonical: set[str] = set()
    boxes_by_comp: dict[int, list] = {}
    for box in boxes:
        boxes_by_comp.setdefault(box.component_id, []).append(box)
        ids = {str(item) for item in (box.component.canonical_ids or [])}
        if box.code in box_factor:
            leftover_canonical |= ids
        else:
            other_canonical |= ids

    scaled_boxes: dict[str, Decimal] = {}
    for _comp_id, group in boxes_by_comp.items():
        if group and all(row.code in box_factor for row in group):
            factor = min(box_factor[row.code] for row in group)
            for row in group:
                scaled_boxes[row.code] = factor

    exclusive = leftover_canonical - other_canonical
    shop_factor: dict[str, Decimal] = {}
    for cid in exclusive:
        factors = [
            scaled_boxes[box.code]
            for box in boxes
            if box.code in scaled_boxes and cid in (box.component.canonical_ids or [])
        ]
        if factors:
            shop_factor[cid] = min(factors)
    return scaled_boxes, shop_factor


def replacement_slugs(data: KitData) -> set[str]:
    slugs: set[str] = set()
    for slot in data.slots:
        payload = no_leftover_payload(slot)
        slug = str(payload.get("slug") or "").strip()
        if slug:
            slugs.add(slug)
    return slugs


def recipes_for_replacements(data: KitData) -> dict[str, Recipe]:
    slugs = replacement_slugs(data)
    if not slugs:
        return {}
    return {
        row.slug: row
        for row in Recipe.objects.filter(slug__in=slugs, status="published")
    }


def leftover_plan_cost(data: KitData) -> dict[str, int]:
    """Цена переключателя «Без вчерашнего»: N блюд и M уникальных позиций закупки."""
    dishes = sum(1 for slot in data.slots if slot.mode == PrepMode.REHEAT)
    canonicals = {
        str(row.get("canonical_id") or "").strip() for row in shopping_additions(data)
    }
    canonicals.discard("")
    return {"dishes": dishes, "shopping_add": len(canonicals)}


def shopping_additions(data: KitData) -> list[dict]:
    rows: list[dict] = []
    for slot in data.slots:
        if slot.mode != PrepMode.REHEAT:
            continue
        payload = no_leftover_payload(slot)
        extra = payload.get("shopping_add") or []
        if not isinstance(extra, list):
            continue
        for item in extra:
            if isinstance(item, dict):
                rows.append(item)
    return rows


def merge_shopping(base: list, additions: list[dict]) -> list[dict]:
    merged: list[dict] = []
    index: dict[tuple[str, str], int] = {}

    for row in [*base, *additions]:
        if not isinstance(row, dict):
            continue
        canonical_id = str(row.get("canonical_id") or "").strip()
        unit = str(row.get("unit") or "").strip()
        if not canonical_id or not unit:
            continue

        key = canonical_id, unit
        qty = Decimal(str(row.get("qty") or 0))
        if key not in index:
            index[key] = len(merged)
            item = dict(row)
            item["qty"] = qty
            merged.append(item)
            continue

        target = merged[index[key]]
        target["qty"] = Decimal(str(target["qty"])) + qty

    return merged


def effective_qty_ratio(
    servings_ratio: Decimal, servings_enabled: bool, extra: Decimal
) -> tuple[Decimal, bool]:
    combined = (servings_ratio if servings_enabled else Decimal("1")) * extra
    return combined, servings_enabled or extra != Decimal("1")
