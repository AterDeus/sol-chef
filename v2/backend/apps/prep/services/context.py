from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from rest_framework.request import Request

from apps.core.numbers import decimal_api
from apps.prep.api.query_serializers import RecipePrepQuerySerializer
from apps.prep.constants import MEAL_RANK, PrepMode, PrepStatus
from apps.prep.exceptions import PrepError
from apps.prep.models import PrepKit, PrepSlot
from apps.prep.serializers import serialize_container, thaw_prep_items
from apps.prep.services.leftover import leftover_qty_factors, no_leftover_payload
from apps.prep.services.read_model import KitData, load_kit_data
from apps.prep.services.scale import kit_ratio
from apps.recipes.models import Recipe
from apps.recipes.serializers import serialize_display_step

QUERY_KEYS = ("prep", "day", "meal", "servings", "no_leftover")


@dataclass(frozen=True, slots=True)
class PrepQuery:
    kit_slug: str
    day: int | None
    meal: str | None
    servings: Decimal | None
    no_leftover: bool


@dataclass(frozen=True, slots=True)
class ResolvedSlot:
    slot: PrepSlot
    day: int
    meal: str
    mode: str
    container_ids: tuple[str, ...]
    steps: list
    source: dict
    alternatives: list[dict]


@dataclass(frozen=True, slots=True)
class Scaling:
    ratio: Decimal
    enabled: bool
    applied_servings: int | None


def _first_error(errors) -> str:
    if isinstance(errors, dict):
        for value in errors.values():
            return _first_error(value)
    if isinstance(errors, list) and errors:
        return _first_error(errors[0])
    return str(errors)


def _query_data(request: Request) -> dict:
    data: dict[str, str] = {}
    for key in QUERY_KEYS:
        raw = request.query_params.get(key)
        if raw is None or str(raw).strip() == "":
            continue
        value = str(raw).strip()
        if key == "servings":
            value = value.replace(",", ".")
        data[key] = value
    return data


def parse_recipe_prep_query(request: Request) -> PrepQuery | None:
    data = _query_data(request)
    if not any(key in data for key in ("prep", "day", "meal")):
        return None
    serializer = RecipePrepQuerySerializer(data=data)
    if not serializer.is_valid():
        raise PrepError(_first_error(serializer.errors))
    if request.query_params.get("anchor_weight"):
        raise PrepError("prep нельзя вместе с anchor_weight.")
    attrs = serializer.validated_data
    slug = (attrs.get("prep") or "").strip()
    if not slug:
        raise PrepError("Нужен query prep.")
    return PrepQuery(
        kit_slug=slug,
        day=attrs.get("day"),
        meal=attrs.get("meal"),
        servings=attrs.get("servings"),
        no_leftover=bool(attrs.get("no_leftover")),
    )


def find_published_kit(slug: str) -> PrepKit:
    kit = (
        PrepKit.objects.filter(slug=slug, status=PrepStatus.PUBLISHED)
        .prefetch_related(
            "components",
            "containers__component",
            "slots__recipe",
        )
        .first()
    )
    if kit is None:
        raise PrepError("Набор не найден.")
    return kit


def load_published_kit_data(slug: str) -> KitData:
    return load_kit_data(find_published_kit(slug))


def resolve_slot(
    kit_data: KitData, recipe: Recipe, day: int | None, meal: str | None
) -> PrepSlot:
    slots = kit_data.slots
    if day is not None:
        slot = next((row for row in slots if row.day == day and row.meal == meal), None)
        if slot is None:
            raise PrepError("Слот набора не найден.")
        return slot
    matches = [row for row in slots if row.recipe_id == recipe.pk]
    if len(matches) != 1:
        raise PrepError("Укажите day и meal: слот неоднозначен.")
    return matches[0]


def effective_container_ids(slot: PrepSlot, *, no_leftover: bool) -> set[str]:
    payload = no_leftover_payload(slot)
    if no_leftover and slot.mode == PrepMode.REHEAT and payload.get("slug"):
        return {str(code) for code in payload.get("container_ids") or []}
    return {str(code) for code in slot.container_ids or []}


def containers_used_before(
    slots: tuple[PrepSlot, ...] | list[PrepSlot],
    *,
    day: int,
    meal: str,
    requested_ids: set[str],
    no_leftover: bool,
) -> dict[str, bool]:
    current_rank = MEAL_RANK[meal]
    used: set[str] = set()
    for slot in slots:
        # Same-day earlier meal only: previous days are already covered by
        # thaw_before_day < day. Counting them here would claim a morning lunch
        # pull on the thaw day even when lunch did not use the box.
        is_earlier = slot.day == day and MEAL_RANK.get(slot.meal, 99) < current_rank
        if is_earlier:
            used.update(effective_container_ids(slot, no_leftover=no_leftover))
    return {code: code in used for code in requested_ids}


def resolve_slot_variant(
    slot: PrepSlot, recipe: Recipe, *, no_leftover: bool
) -> ResolvedSlot:
    nl = no_leftover_payload(slot)
    replacement = (
        nl if no_leftover and slot.mode == PrepMode.REHEAT and nl.get("slug") else None
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

    if replacement is not None:
        mode = replacement.get("mode") or PrepMode.FINISH
        ids = tuple(str(code) for code in (replacement.get("container_ids") or []))
        raw_steps = replacement.get("steps") or []
        source = {"kind": "weekend"}
        alts_out: list[dict] = []
    elif alt is not None:
        mode = alt.get("mode") or slot.mode
        ids = tuple(str(code) for code in (alt.get("container_ids") or []))
        raw_steps = alt.get("steps") or []
        source = slot.source
        alts_out = []
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
    else:
        mode = slot.mode
        ids = tuple(str(code) for code in (slot.container_ids or []))
        raw_steps = (
            nl.get("steps") if no_leftover and nl.get("steps") else (slot.steps or [])
        )
        source = slot.source
        alts_out = []
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

    return ResolvedSlot(
        slot=slot,
        day=slot.day,
        meal=slot.meal,
        mode=mode,
        container_ids=ids,
        steps=list(raw_steps),
        source=source if isinstance(source, dict) else {},
        alternatives=alts_out,
    )


def resolve_scaling(servings_base: int | None, requested: Decimal | None) -> Scaling:
    ratio, enabled = kit_ratio(
        servings_base,
        requested if requested is not None else Decimal(servings_base or 1),
    )
    servings = requested
    if servings_base is None:
        enabled = False
        ratio = Decimal("1")
    elif requested is None:
        enabled = True
        ratio = Decimal("1")
        servings = Decimal(servings_base)
    applied = int(servings) if servings is not None else servings_base
    return Scaling(ratio=ratio, enabled=enabled, applied_servings=applied)


def serialize_resolved_context(
    kit_data: KitData,
    resolved: ResolvedSlot,
    scaling: Scaling,
    *,
    no_leftover: bool,
) -> dict:
    box_factor = leftover_qty_factors(kit_data)[0] if no_leftover else {}
    boxes = kit_data.containers_by_code
    ids = list(resolved.container_ids)
    used_earlier = containers_used_before(
        kit_data.slots,
        day=resolved.day,
        meal=resolved.meal,
        requested_ids=set(ids),
        no_leftover=no_leftover,
    )
    containers = []
    for code in ids:
        box = boxes.get(code)
        if box is not None:
            containers.append(
                serialize_container(
                    box,
                    scaling.ratio,
                    scaling.enabled,
                    extra=box_factor.get(code, Decimal("1")),
                )
            )
    steps = [
        serialize_display_step(step if isinstance(step, dict) else {"text": str(step)})
        for step in resolved.steps
    ]
    kit = kit_data.kit
    return {
        "steps": steps,
        "prep": thaw_prep_items(containers, resolved.day, used_earlier=used_earlier),
        "prep_context": {
            "kit": {"slug": kit.slug, "title": kit.title},
            "day": resolved.day,
            "meal": resolved.meal,
            "mode": resolved.mode,
            "source": resolved.source,
            "containers": containers,
            "alternatives": resolved.alternatives,
            "no_leftover": no_leftover,
        },
        "scaling": {
            "enabled": bool(kit.servings_base),
            "mode": "servings" if kit.servings_base else "off",
            "ratio": decimal_api(scaling.ratio),
            "applied": {"servings": scaling.applied_servings},
        },
    }


def resolve_prep_for_recipe(recipe: Recipe, request: Request) -> dict | None:
    query = parse_recipe_prep_query(request)
    if query is None:
        return None
    kit_data = load_published_kit_data(query.kit_slug)
    slot = resolve_slot(kit_data, recipe, query.day, query.meal)
    resolved = resolve_slot_variant(slot, recipe, no_leftover=query.no_leftover)
    scaling = resolve_scaling(kit_data.kit.servings_base, query.servings)
    return serialize_resolved_context(
        kit_data, resolved, scaling, no_leftover=query.no_leftover
    )
