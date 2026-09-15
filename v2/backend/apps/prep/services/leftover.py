"""Variant «Без вчерашнего»: cook leftover sources once, replace reheat slots."""

from __future__ import annotations

from decimal import Decimal

from apps.prep.exceptions import PrepError
from apps.prep.models import PrepKit
from apps.recipes.models import Recipe

TRUE = frozenset({"1", "true", "yes", "on"})
FALSE = frozenset({"0", "false", "no", "off", ""})


def parse_no_leftover(request) -> bool:
    raw = request.query_params.get("no_leftover")
    if raw is None or raw == "":
        return False
    value = str(raw).strip().lower()
    if value in TRUE:
        return True
    if value in FALSE:
        return False
    raise PrepError("no_leftover: 1 или 0.")


def no_leftover_payload(slot: PrepSlot) -> dict:
    data = slot.no_leftover
    return data if isinstance(data, dict) else {}


def leftover_qty_factors(kit: PrepKit) -> tuple[dict[str, Decimal], dict[str, Decimal]]:
    """Box code → factor, exclusive shopping canonical_id → factor."""
    slots = list(kit.slots.all())
    boxes = list(kit.containers.select_related("component").all())
    reheat_sources: set[tuple[int, str]] = set()
    source_feeds: dict[tuple[int, str], int] = {}
    for slot in slots:
        if slot.mode != "reheat":
            continue
        source = slot.source or {}
        if source.get("kind") != "slot":
            continue
        try:
            key = (int(source["day"]), str(source["meal"]))
        except (KeyError, TypeError, ValueError):
            continue
        reheat_sources.add(key)
    for slot in slots:
        key = (slot.day, slot.meal)
        if key in reheat_sources:
            source_feeds[key] = int(slot.feeds_slots or 1)

    weekend_users: dict[str, set[tuple[int, str]]] = {}
    for slot in slots:
        if slot.mode == "reheat":
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
        # mixed leftover/shared component: do not scale (sum qty must hold)

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


def replacement_slugs(kit: PrepKit) -> set[str]:
    slugs: set[str] = set()
    for slot in kit.slots.all():
        payload = no_leftover_payload(slot)
        slug = str(payload.get("slug") or "").strip()
        if slug:
            slugs.add(slug)
    return slugs


def recipes_for_replacements(kit: PrepKit) -> dict[str, Recipe]:
    slugs = replacement_slugs(kit)
    if not slugs:
        return {}
    return {row.slug: row for row in Recipe.objects.filter(slug__in=slugs, status="published")}


def leftover_plan_cost(kit: PrepKit) -> dict[str, int]:
    """Цена переключателя «Без вчерашнего»: N блюд и M уникальных позиций закупки."""
    dishes = sum(1 for slot in kit.slots.all() if slot.mode == "reheat")
    canonicals = {
        str(row.get("canonical_id") or "").strip()
        for row in shopping_additions(kit)
    }
    canonicals.discard("")
    return {"dishes": dishes, "shopping_add": len(canonicals)}


def shopping_additions(kit: PrepKit) -> list[dict]:
    rows: list[dict] = []
    for slot in kit.slots.all():
        if slot.mode != "reheat":
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
    index: dict[str, int] = {}
    for row in base:
        if not isinstance(row, dict):
            continue
        cid = str(row.get("canonical_id") or "").strip()
        item = dict(row)
        if cid:
            index[cid] = len(merged)
        merged.append(item)
    for row in additions:
        cid = str(row.get("canonical_id") or "").strip()
        if not cid:
            continue
        qty = Decimal(str(row.get("qty") or 0))
        if cid in index:
            target = merged[index[cid]]
            target["qty"] = Decimal(str(target.get("qty") or 0)) + qty
        else:
            merged.append(dict(row))
            index[cid] = len(merged) - 1
    return merged


def effective_qty_ratio(
    servings_ratio: Decimal, servings_enabled: bool, extra: Decimal
) -> tuple[Decimal, bool]:
    combined = (servings_ratio if servings_enabled else Decimal("1")) * extra
    return combined, servings_enabled or extra != Decimal("1")
