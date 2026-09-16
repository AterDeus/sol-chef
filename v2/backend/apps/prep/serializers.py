from __future__ import annotations

from decimal import Decimal

from apps.prep.models import PrepComponent, PrepContainer, PrepKit, PrepSlot
from apps.prep.services.graph import kit_graph
from apps.prep.services.leftover import (
    effective_qty_ratio,
    leftover_plan_cost,
    leftover_qty_factors,
    merge_shopping,
    no_leftover_payload,
    recipes_for_replacements,
    shopping_additions,
)
from apps.prep.services.thaw import (
    container_number,
    thaw_already_in_fridge_text,
    thaw_lead_hours,
    thaw_prep_item_text,
    thaw_pull_for,
)
from apps.prep.services.scale import kit_ratio, qty_payload
from apps.recipes.services.assemble import assemble_recipe
from apps.recipes.services.nutrition import compute_recipe_nutrition


def serialize_container(
    box: PrepContainer,
    ratio: Decimal,
    enabled: bool,
    extra: Decimal | None = None,
) -> dict:
    combined, on = effective_qty_ratio(ratio, enabled, extra or Decimal("1"))
    payload = qty_payload(box.qty, box.unit, combined, on)
    thaw_pull = thaw_pull_for(
        box.place, box.thaw_before_day, box.unit, box.component.code
    )
    return {
        "code": box.code,
        "label": box.label,
        "component_code": box.component.code,
        "component_title": box.component.title,
        "place": box.place,
        "thaw_before_day": box.thaw_before_day,
        "thaw_pull": thaw_pull,
        **payload,
    }


def thaw_prep_items(
    containers: list[dict],
    day: int,
    *,
    used_earlier: dict[str, bool] | None = None,
) -> list[dict]:
    already = used_earlier or {}
    items: list[dict] = []
    for box in containers:
        thaw = box.get("thaw_before_day")
        if thaw is None or int(thaw) > day:
            continue
        pull = box.get("thaw_pull") or thaw_pull_for(
            box.get("place") or "",
            int(thaw),
            box.get("unit"),
            box.get("component_code"),
        )
        code = str(box.get("code") or "")
        same_day_already = int(thaw) == day and bool(already.get(code))
        if int(thaw) < day or already.get(code):
            if same_day_already:
                num = container_number(box.get("label"))
                text = (
                    f"Контейнер {num} уже в холодильнике — вы достали его утром к обеду."
                    if num
                    else "Заготовка уже в холодильнике — вы достали её утром к обеду."
                )
            else:
                text = thaw_already_in_fridge_text(
                    label=box.get("label"),
                    pull=pull,
                    thaw_before_day=int(thaw),
                )
        else:
            text = thaw_prep_item_text(
                morning=pull == "morning",
                label=box.get("label"),
                component_title=box.get("component_title"),
            )
        items.append(
            {
                "type": "thaw",
                "text": text,
                "before_hours": thaw_lead_hours(pull, box.get("unit"), box.get("qty")),
            }
        )
    return items


def average_slot_kcal(kit: PrepKit) -> int | None:
    """Ориентир по основным рецептам слотов, не по полной тарелке с companion."""
    values: list[int] = []
    slots = kit.slots.select_related("recipe").prefetch_related(
        "recipe__ingredients__ingredient",
        "recipe__steps",
        "recipe__variants",
    )
    for slot in slots:
        recipe = slot.recipe
        assembled = assemble_recipe(recipe)
        servings = recipe.servings or kit.servings_base or 2
        nut = compute_recipe_nutrition(
            assembled.ingredients,
            servings=int(servings),
            ratio=Decimal("1"),
            scaling_enabled=False,
            yield_weight_g=recipe.yield_weight_g,
        )
        per = nut.get("per_serving") or {}
        kcal = per.get("kcal")
        if kcal:
            values.append(int(kcal))
    if not values:
        return None
    return int(round(sum(values) / len(values)))


def metrics_for_api(kit: PrepKit) -> dict:
    metrics = dict(kit.metrics or {})
    kcal = average_slot_kcal(kit)
    if kcal is not None:
        metrics["kcal_avg_per_serving"] = kcal
    return metrics


def serialize_kit_list_item(kit: PrepKit) -> dict:
    return {
        "slug": kit.slug,
        "title": kit.title,
        "summary": kit.summary,
        "rhythm": kit.rhythm,
        "position": kit.position,
        "metrics": metrics_for_api(kit),
    }


def _serialize_component(
    row: PrepComponent,
    ratio: Decimal,
    enabled: bool,
    extra: Decimal | None = None,
) -> dict:
    combined, on = effective_qty_ratio(ratio, enabled, extra or Decimal("1"))
    payload = qty_payload(row.qty, row.unit, combined, on)
    return {
        "code": row.code,
        "title": row.title,
        "canonical_ids": row.canonical_ids or [],
        "weekend_steps": row.weekend_steps or [],
        "parcook": row.parcook or {},
        "storage": row.storage or {},
        **payload,
    }


def _serialize_slot(
    slot: PrepSlot,
    boxes: dict[str, PrepContainer],
    ratio: Decimal,
    enabled: bool,
    *,
    box_factor: dict[str, Decimal],
    no_leftover: bool,
    recipes: dict,
    servings_base: int | None,
) -> dict:
    payload = no_leftover_payload(slot)
    recipe = slot.recipe
    mode = slot.mode
    ids = [str(code) for code in (slot.container_ids or [])]
    source = slot.source
    flavor = slot.flavor
    plate = slot.plate if isinstance(slot.plate, dict) else {}
    alts = []
    servings_cooked = slot.servings_cooked
    feeds_slots = slot.feeds_slots
    time_from = slot.time_active_from_prep_min
    time_scratch = slot.time_active_scratch_min

    if no_leftover and slot.mode == "reheat" and payload.get("slug"):
        repl = recipes.get(str(payload["slug"]))
        if repl is not None:
            recipe = repl
        mode = payload.get("mode") or "finish"
        ids = [str(code) for code in (payload.get("container_ids") or [])]
        source = {"kind": "weekend"}
        flavor = payload.get("flavor") or flavor
        if isinstance(payload.get("plate"), dict):
            plate = payload["plate"]
        alts = []
        servings_cooked = servings_base
        feeds_slots = 1
        if payload.get("time_active_from_prep_min") is not None:
            time_from = payload.get("time_active_from_prep_min")
        if payload.get("time_active_scratch_min") is not None:
            time_scratch = payload.get("time_active_scratch_min")
    else:
        if no_leftover and (slot.feeds_slots or 0) >= 2:
            servings_cooked = servings_base
            feeds_slots = 1
        for item in slot.alternatives or []:
            if not isinstance(item, dict):
                continue
            alts.append(
                {
                    "slug": item.get("slug"),
                    "label": item.get("label"),
                    "mode": item.get("mode"),
                    "container_ids": item.get("container_ids") or [],
                }
            )

    plate_title = str(plate.get("title") or "").strip() or flavor or recipe.title
    plate_composition = str(plate.get("composition") or "").strip() or None
    return {
        "day": slot.day,
        "meal": slot.meal,
        "slug": recipe.slug,
        "title": recipe.title,
        "plate_title": plate_title,
        "plate_composition": plate_composition,
        "mode": mode,
        "flavor": flavor,
        "source": source,
        "container_ids": ids,
        "containers": [
            serialize_container(
                boxes[code],
                ratio,
                enabled,
                extra=box_factor.get(code, Decimal("1")),
            )
            for code in ids
            if code in boxes
        ],
        "alternatives": alts,
        "servings_cooked": servings_cooked,
        "feeds_slots": feeds_slots,
        "time_active_from_prep_min": time_from,
        "time_active_scratch_min": time_scratch,
    }


def serialize_kit_detail(
    kit: PrepKit, servings: Decimal | None, no_leftover: bool = False
) -> dict:
    ratio, enabled = kit_ratio(kit.servings_base, servings)
    if servings is None and kit.servings_base is not None:
        enabled = True
        ratio = Decimal("1")
        servings = Decimal(kit.servings_base)
    if kit.servings_base is None:
        enabled = False
        ratio = Decimal("1")
    boxes = {
        row.code: row for row in kit.containers.select_related("component").all()
    }
    box_factor, shop_factor = leftover_qty_factors(kit) if no_leftover else ({}, {})
    recipes = recipes_for_replacements(kit) if no_leftover else {}
    raw_shopping = list(kit.shopping or [])
    if no_leftover:
        raw_shopping = merge_shopping(raw_shopping, shopping_additions(kit))
        for row in raw_shopping:
            cid = str(row.get("canonical_id") or "")
            extra = shop_factor.get(cid)
            if extra is not None:
                row["qty"] = Decimal(str(row.get("qty") or 0)) * extra
    shopping = []
    for row in raw_shopping:
        if not isinstance(row, dict):
            continue
        unit = row.get("unit") or "g"
        payload = qty_payload(row.get("qty") or 0, unit, ratio, enabled)
        shopping.append(
            {
                "canonical_id": row.get("canonical_id"),
                "title_ru": row.get("title_ru"),
                **payload,
            }
        )
    applied = int(servings) if servings is not None else kit.servings_base
    components = list(kit.components.all())
    comp_factor: dict[str, Decimal] = {}
    boxes_by_comp: dict[str, list] = {}
    for box in boxes.values():
        boxes_by_comp.setdefault(box.component.code, []).append(box)
    for code, group in boxes_by_comp.items():
        if group and all(row.code in box_factor for row in group):
            comp_factor[code] = min(box_factor[row.code] for row in group)
    slot_rows = list(kit.slots.select_related("recipe").all())
    has_leftovers = any(row.mode == "reheat" for row in slot_rows)
    return {
        "slug": kit.slug,
        "title": kit.title,
        "summary": kit.summary,
        "servings_base": kit.servings_base,
        "no_leftover": bool(no_leftover),
        "has_leftovers": has_leftovers,
        "leftover_cost": leftover_plan_cost(kit),
        "scaling": {
            "enabled": bool(kit.servings_base),
            "mode": "servings" if kit.servings_base else "off",
            "ratio": float(ratio),
            "applied": {"servings": applied},
        },
        "caution_text": kit.caution_text,
        "rhythm": kit.rhythm,
        "metrics": metrics_for_api(kit),
        "allergens": kit.allergens or {"contains": [], "unknown": [], "may_contain": []},
        "shopping": shopping,
        "components": [
            _serialize_component(
                row, ratio, enabled, extra=comp_factor.get(row.code, Decimal("1"))
            )
            for row in components
        ],
        "containers": [
            serialize_container(
                row, ratio, enabled, extra=box_factor.get(row.code, Decimal("1"))
            )
            for row in boxes.values()
        ],
        "weekend_timeline": kit.weekend_timeline or [],
        "slots": [
            _serialize_slot(
                row,
                boxes,
                ratio,
                enabled,
                box_factor=box_factor,
                no_leftover=no_leftover,
                recipes=recipes,
                servings_base=kit.servings_base,
            )
            for row in slot_rows
        ],
        "graph": kit_graph(kit),
    }

