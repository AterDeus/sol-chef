from __future__ import annotations

from collections import defaultdict, deque
from collections.abc import Iterable

from apps.prep.constants import MEAL_RANK
from apps.prep.models import PrepSlot
from apps.prep.services.read_model import KitData

SlotKey = tuple[int, str]


def slot_key(slot: PrepSlot) -> SlotKey:
    return slot.day, slot.meal


def slot_sort_key(slot: PrepSlot) -> tuple[int, int]:
    return slot.day, MEAL_RANK.get(slot.meal, 99)


def source_key(slot: PrepSlot) -> SlotKey | None:
    source = slot.source if isinstance(slot.source, dict) else {}
    if source.get("kind") != "slot":
        return None
    try:
        day = int(source.get("day"))
    except (TypeError, ValueError):
        return None
    meal = source.get("meal")
    return (day, meal) if meal in MEAL_RANK else None


def descendants(
    starts: Iterable[PrepSlot],
    reheat_by_source: dict[SlotKey, list[PrepSlot]],
) -> list[PrepSlot]:
    result: list[PrepSlot] = []
    queue = deque(starts)
    seen: set[SlotKey] = set()

    while queue:
        slot = queue.popleft()
        key = slot_key(slot)
        if key in seen:
            continue
        seen.add(key)
        result.append(slot)
        queue.extend(reheat_by_source.get(key, ()))

    return sorted(result, key=slot_sort_key)


def kit_graph(data: KitData) -> list[dict]:
    slot_rows = data.slots
    boxes_by_component: dict[int, set[str]] = defaultdict(set)
    for box in data.containers:
        boxes_by_component[box.component_id].add(box.code)

    reheat_by_source: dict[SlotKey, list[PrepSlot]] = defaultdict(list)
    for slot in slot_rows:
        if slot.mode != "reheat":
            continue
        if key := source_key(slot):
            reheat_by_source[key].append(slot)

    graph: list[dict] = []
    for component in data.components:
        component_boxes = boxes_by_component[component.pk]
        starts = [
            slot
            for slot in slot_rows
            if slot.mode != "reheat"
            and component_boxes.intersection(map(str, slot.container_ids or []))
        ]
        graph.append(
            {
                "code": component.code,
                "title": component.title,
                "slots": [
                    {
                        "day": slot.day,
                        "meal": slot.meal,
                        "slug": slot.recipe.slug,
                        "title": slot.recipe.title,
                        "mode": slot.mode,
                    }
                    for slot in descendants(starts, reheat_by_source)
                ],
            }
        )
    return graph
