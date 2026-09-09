from __future__ import annotations

from apps.prep.models import PrepKit, PrepSlot

MEAL_RANK = {"lunch": 0, "dinner": 1}


def _key(slot: PrepSlot) -> tuple[int, int]:
    return (slot.day, MEAL_RANK[slot.meal])


def kit_graph(kit: PrepKit) -> list[dict]:
    slots = list(kit.slots.select_related("recipe").all())
    boxes = {row.code: row for row in kit.containers.select_related("component").all()}

    def cascade_from(starts: list[PrepSlot]) -> list[PrepSlot]:
        seen = {(row.day, row.meal) for row in starts}
        out = list(starts)
        changed = True
        while changed:
            changed = False
            for slot in slots:
                if slot.mode != "reheat" or (slot.day, slot.meal) in seen:
                    continue
                source = slot.source or {}
                if source.get("kind") != "slot":
                    continue
                origin = (int(source["day"]), source["meal"])
                if origin in seen:
                    seen.add((slot.day, slot.meal))
                    out.append(slot)
                    changed = True
        return sorted(out, key=_key)

    graph: list[dict] = []
    for component in kit.components.all():
        weekend: list[PrepSlot] = []
        component_boxes = {
            code for code, box in boxes.items() if box.component_id == component.pk
        }
        for slot in slots:
            if slot.mode == "reheat":
                continue
            ids = set(slot.container_ids or [])
            if ids & component_boxes:
                weekend.append(slot)
        eaten = cascade_from(weekend)
        graph.append(
            {
                "code": component.code,
                "title": component.title,
                "slots": [
                    {
                        "day": row.day,
                        "meal": row.meal,
                        "slug": row.recipe.slug,
                        "title": row.recipe.title,
                        "mode": row.mode,
                    }
                    for row in eaten
                ],
            }
        )
    return graph
