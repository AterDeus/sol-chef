from __future__ import annotations

from decimal import Decimal

from rest_framework.request import Request

from apps.prep.exceptions import PrepError
from apps.prep.models import PrepKit
from apps.prep.serializers import serialize_container, thaw_prep_items
from apps.prep.services.leftover import leftover_qty_factors, no_leftover_payload, parse_no_leftover
from apps.prep.services.scale import kit_ratio
from apps.recipes.models import Recipe
from apps.recipes.query import parse_optional_decimal
from apps.recipes.serializers import serialize_display_step


def _int_query(request: Request, key: str) -> int | None:
    raw = request.query_params.get(key)
    if raw is None or raw == "":
        return None
    try:
        return int(raw)
    except (TypeError, ValueError) as exc:
        raise PrepError(f"Некорректное значение {key}.") from exc


def resolve_prep_for_recipe(recipe: Recipe, request: Request) -> dict | None:
    kit_slug = (request.query_params.get("prep") or "").strip() or None
    day = _int_query(request, "day")
    meal = (request.query_params.get("meal") or "").strip() or None
    if kit_slug is None and day is None and not meal:
        return None
    if kit_slug is None:
        raise PrepError("Нужен query prep.")
    if (day is None) != (not meal):
        raise PrepError("Нужны оба day и meal, либо ни одного.")
    if meal and meal not in {"lunch", "dinner"}:
        raise PrepError("meal: lunch или dinner.")
    if day is not None and day not in range(1, 8):
        raise PrepError("day должен быть 1–7.")
    if request.query_params.get("anchor_weight"):
        raise PrepError("prep нельзя вместе с anchor_weight.")

    kit = PrepKit.objects.filter(slug=kit_slug, status="published").first()
    if kit is None:
        raise PrepError("Набор не найден.")

    slots = list(kit.slots.select_related("recipe").all())
    if day is not None:
        slot = next((row for row in slots if row.day == day and row.meal == meal), None)
        if slot is None:
            raise PrepError("Слот набора не найден.")
    else:
        matches = [row for row in slots if row.recipe_id == recipe.pk]
        if len(matches) != 1:
            raise PrepError("Укажите day и meal: слот неоднозначен.")
        slot = matches[0]
        day = slot.day
        meal = slot.meal

    no_leftover = parse_no_leftover(request)
    nl = no_leftover_payload(slot)
    replacement = (
        nl
        if no_leftover and slot.mode == "reheat" and nl.get("slug")
        else None
    )

    alt = None
    if replacement is not None:
        if recipe.slug != replacement.get("slug"):
            raise PrepError("Этот рецепт не в слоте набора.")
    elif slot.recipe.slug != recipe.slug:
        for item in slot.alternatives or []:
            if isinstance(item, dict) and item.get("slug") == recipe.slug:
                alt = item
                break
        if alt is None:
            raise PrepError("Этот рецепт не в слоте набора.")

    servings = parse_optional_decimal(request, "servings")
    ratio, enabled = kit_ratio(
        kit.servings_base,
        servings if servings is not None else Decimal(kit.servings_base or 1),
    )
    if kit.servings_base is None:
        enabled = False
        ratio = Decimal("1")
    elif servings is None:
        enabled = True
        ratio = Decimal("1")
        servings = Decimal(kit.servings_base)

    box_factor = leftover_qty_factors(kit)[0] if no_leftover else {}
    boxes = {row.code: row for row in kit.containers.select_related("component").all()}
    if replacement is not None:
        mode = replacement.get("mode") or "finish"
        ids = [str(code) for code in (replacement.get("container_ids") or [])]
        raw_steps = replacement.get("steps") or []
        source = {"kind": "weekend"}
    elif alt is not None:
        mode = alt.get("mode") or slot.mode
        ids = [str(code) for code in (alt.get("container_ids") or [])]
        raw_steps = alt.get("steps") or []
        source = slot.source
    else:
        mode = slot.mode
        ids = [str(code) for code in (slot.container_ids or [])]
        raw_steps = (
            nl.get("steps")
            if no_leftover and nl.get("steps")
            else (slot.steps or [])
        )
        source = slot.source

    containers = []
    for code in ids:
        box = boxes.get(code)
        if box is not None:
            containers.append(
                serialize_container(
                    box, ratio, enabled, extra=box_factor.get(code, Decimal("1"))
                )
            )

    steps = [
        serialize_display_step(step if isinstance(step, dict) else {"text": str(step)})
        for step in raw_steps
    ]
    alts_out = []
    if replacement is None:
        for item in slot.alternatives or []:
            if not isinstance(item, dict):
                continue
            alts_out.append(
                {
                    "slug": item.get("slug"),
                    "label": item.get("label"),
                    "mode": item.get("mode"),
                }
            )
    applied_servings = int(servings) if servings is not None else kit.servings_base
    return {
        "steps": steps,
        "prep": thaw_prep_items(containers, day),
        "prep_context": {
            "kit": {"slug": kit.slug, "title": kit.title},
            "day": day,
            "meal": meal,
            "mode": mode,
            "source": source,
            "containers": containers,
            "alternatives": alts_out,
            "no_leftover": no_leftover,
        },
        "scaling": {
            "enabled": bool(kit.servings_base),
            "mode": "servings" if kit.servings_base else "off",
            "ratio": float(ratio),
            "applied": {"servings": applied_servings},
        },
    }
