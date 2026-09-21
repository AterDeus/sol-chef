"""Pure kit-payload rules. Persistence never sees a raw payload.get()."""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from apps.core.numbers import decimal_json
from apps.prep.constants import PrepMeal, PrepMode, PrepPlace
from apps.prep.services.importer.contracts import (
    ComponentDraft,
    ContainerDraft,
    KitDraft,
    SlotDraft,
)
from apps.prep.services.importer.normalizers import (
    PayloadError,
    entity_code,
    integer,
    kit_slug_of,
    nonnegative_decimal,
    positive_int,
)
from apps.recipes.constants import UNIT

FORBIDDEN_KEYS = frozenset(
    {
        "weekend_protocol",
        "qty_g",
        "eaten_by",
        "eaten_by_slots",
        "feeds_days",
        "weekend_active_hours_estimated",
    }
)
MEALS = tuple(PrepMeal.values)
REQUIRED_PAIRS = {(day, meal) for day in range(1, 8) for meal in MEALS}
SOURCE_WEEKEND = frozenset({"kind"})
SOURCE_SLOT = frozenset({"kind", "day", "meal"})


def _catch(errors: list[str], fn, *args, **kwargs):
    try:
        return fn(*args, **kwargs)
    except PayloadError as exc:
        errors.append(str(exc))
        return None


def _nonempty_steps(raw: Any, label: str, errors: list[str]) -> list[dict]:
    if not isinstance(raw, list) or not raw:
        errors.append(f"{label}: пустые steps.")
        return []
    steps: list[dict] = []
    for index, item in enumerate(raw):
        if not isinstance(item, dict):
            errors.append(f"{label}: шаг {index} не объект.")
            continue
        text = str(item.get("text") or "").strip()
        if not text:
            errors.append(f"{label}: шаг {index} без text.")
            continue
        steps.append(dict(item))
        steps[-1]["text"] = text
    if not steps:
        errors.append(f"{label}: пустые steps.")
    return steps


def _walk_forbidden(obj: Any, path: str, errors: list[str]) -> None:
    if isinstance(obj, dict):
        extra = FORBIDDEN_KEYS & set(obj)
        if extra:
            errors.append(f"{path}: запрещённые ключи {sorted(extra)}.")
        for key, value in obj.items():
            _walk_forbidden(value, f"{path}.{key}", errors)
    elif isinstance(obj, list):
        for index, value in enumerate(obj):
            _walk_forbidden(value, f"{path}[{index}]", errors)


def _validate_dish_use(
    item: dict,
    label: str,
    container_by_id: dict[str, dict],
    recipe_slugs: set[str],
    errors: list[str],
    *,
    require_label: bool,
    allow_empty_containers: bool = False,
) -> None:
    slug = str(item.get("slug") or "").strip()
    if not slug:
        errors.append(f"{label}: нет slug.")
    else:
        recipe_slugs.add(slug)
    if require_label and not str(item.get("label") or "").strip():
        errors.append(f"{label}: нет label.")
    mode = item.get("mode")
    if mode not in PrepMode.values:
        errors.append(f"{label}: mode assemble|finish|reheat.")
    ids = item.get("container_ids") or []
    if not isinstance(ids, list):
        errors.append(f"{label}: container_ids не список.")
        ids = []
    ids = [str(code) for code in ids]
    bad = [code for code in ids if code not in container_by_id]
    if bad:
        errors.append(f"{label}: чужие боксы {bad}.")
    if mode in {PrepMode.ASSEMBLE, PrepMode.FINISH} and not ids:
        extra = item.get("shopping_add") or []
        if allow_empty_containers and isinstance(extra, list) and extra:
            pass
        else:
            if allow_empty_containers:
                errors.append(f"{label}: без боксов нужен shopping_add.")
            else:
                errors.append(f"{label}: assemble/finish без container_ids.")
    if mode == PrepMode.REHEAT and ids:
        errors.append(f"{label}: reheat с боксами.")
    _nonempty_steps(item.get("steps"), label, errors)


def _validate_shopping_add(raw: Any, label: str, errors: list[str]) -> None:
    if raw in (None, [], {}):
        return
    if not isinstance(raw, list):
        errors.append(f"{label}: shopping_add не список.")
        return
    for index, row in enumerate(raw):
        if not isinstance(row, dict):
            errors.append(f"{label}: shopping_add[{index}] не объект.")
            continue
        if not str(row.get("canonical_id") or "").strip():
            errors.append(f"{label}: shopping_add[{index}] без canonical_id.")
        if row.get("unit") not in UNIT:
            errors.append(f"{label}: shopping_add[{index}] unit.")
        _catch(errors, nonnegative_decimal, row.get("qty"), field=f"{label} shopping_add[{index}]")


def _optional_positive(item: dict, key: str, label: str, errors: list[str]) -> int | None:
    if item.get(key) in (None, ""):
        return None
    return _catch(errors, positive_int, item.get(key), field=f"{label} {key}", nullable=False)


def collect_payload_errors(payload: dict) -> tuple[list[str], set[str]]:
    errors: list[str] = []
    recipe_slugs: set[str] = set()
    if not isinstance(payload, dict):
        return ["Корень JSON должен быть объектом."], recipe_slugs
    _walk_forbidden(payload, "kit", errors)
    slug = kit_slug_of(payload)
    if not slug:
        errors.append("Нет id/slug набора.")

    if payload.get("servings_base") not in (None, ""):
        _catch(
            errors,
            positive_int,
            payload.get("servings_base"),
            field="servings_base",
            nullable=False,
        )
    if payload.get("position") not in (None, ""):
        _catch(
            errors,
            integer,
            payload.get("position"),
            field="position",
            min_value=0,
        )

    components = payload.get("components")
    containers = payload.get("containers")
    slots = payload.get("slots")
    if not isinstance(components, list) or not components:
        errors.append("Нет components.")
        components = []
    if not isinstance(containers, list) or not containers:
        errors.append("Нет containers.")
        containers = []
    if not isinstance(slots, list):
        errors.append("Нет slots.")
        slots = []

    component_by_id: dict[str, dict] = {}
    for item in components:
        if not isinstance(item, dict):
            errors.append("component не объект.")
            continue
        code = entity_code(item)
        if not code:
            errors.append("component без id.")
            continue
        if code in component_by_id:
            errors.append(f"Дубль component {code}.")
            continue
        unit = item.get("unit")
        if unit not in UNIT:
            errors.append(f"component {code}: неизвестный unit.")
        _catch(errors, nonnegative_decimal, item.get("qty"), field=f"component {code}")
        component_by_id[code] = item

    container_by_id: dict[str, dict] = {}
    qty_by_component: dict[str, Decimal] = {code: Decimal("0") for code in component_by_id}
    for item in containers:
        if not isinstance(item, dict):
            errors.append("container не объект.")
            continue
        code = entity_code(item)
        if not code:
            errors.append("container без id.")
            continue
        if code in container_by_id:
            errors.append(f"Дубль container {code}.")
            continue
        parent = str(item.get("component_id") or item.get("component") or "").strip()
        if parent not in component_by_id:
            errors.append(f"container {code}: неизвестный component_id.")
        unit = item.get("unit")
        if unit not in UNIT:
            errors.append(f"container {code}: неизвестный unit.")
        elif parent in component_by_id and component_by_id[parent].get("unit") != unit:
            errors.append(f"container {code}: unit ≠ unit компонента.")
        place = item.get("place")
        if place not in PrepPlace.values:
            errors.append(f"container {code}: place fridge|freezer|pantry.")
        thaw = item.get("thaw_before_day")
        if thaw not in (None, ""):
            _catch(
                errors,
                integer,
                thaw,
                field=f"container {code} thaw_before_day",
                min_value=1,
                max_value=7,
            )
        qty = _catch(errors, nonnegative_decimal, item.get("qty"), field=f"container {code}")
        if qty is not None and parent in qty_by_component:
            qty_by_component[parent] += qty
        container_by_id[code] = item

    for code, item in component_by_id.items():
        try:
            expected = nonnegative_decimal(item.get("qty"), field=f"component {code}")
        except PayloadError:
            continue
        got = qty_by_component.get(code, Decimal("0"))
        if got != expected:
            errors.append(
                f"component {code}: сумма контейнеров {got} ≠ qty {expected}."
            )
        listed = item.get("container_ids")
        if listed is not None:
            if not isinstance(listed, list):
                errors.append(f"component {code}: container_ids не список.")
            else:
                actual = {
                    cid
                    for cid, box in container_by_id.items()
                    if str(box.get("component_id") or box.get("component") or "") == code
                }
                if set(map(str, listed)) != actual:
                    errors.append(f"component {code}: container_ids не сходятся.")

    if len(slots) != 14:
        errors.append(f"Нужно 14 слотов, сейчас {len(slots)}.")

    slot_pairs: set[tuple[int, str]] = set()
    slot_map: dict[tuple[int, str], dict] = {}
    grid_slugs = {
        str(row.get("slug") or "").strip()
        for row in slots
        if isinstance(row, dict) and str(row.get("slug") or "").strip()
    }
    for item in slots:
        if not isinstance(item, dict):
            errors.append("slot не объект.")
            continue
        day = _catch(errors, integer, item.get("day"), field="slot day", min_value=1, max_value=7)
        meal = item.get("meal")
        if day is None or meal not in MEALS:
            if day is not None:
                errors.append(f"slot day={item.get('day')} meal={meal}: не day×meal.")
            continue
        pair = (day, meal)
        if pair in slot_pairs:
            errors.append(f"Дубль слота {day}/{meal}.")
            continue
        slot_pairs.add(pair)
        slot_map[pair] = item
        slug = str(item.get("slug") or "").strip()
        if not slug:
            errors.append(f"слот {day}/{meal}: нет slug.")
        else:
            recipe_slugs.add(slug)
        mode = item.get("mode")
        if mode not in PrepMode.values:
            errors.append(f"слот {day}/{meal}: mode assemble|finish|reheat.")
        source = item.get("source")
        if not isinstance(source, dict):
            errors.append(f"слот {day}/{meal}: source не объект.")
            source = {}
        if "container_ids" in source:
            errors.append(f"слот {day}/{meal}: container_ids внутри source.")
        kind = source.get("kind")
        ids = item.get("container_ids")
        if ids is None:
            ids = []
        if not isinstance(ids, list):
            errors.append(f"слот {day}/{meal}: container_ids не список.")
            ids = []
        ids = [str(code) for code in ids]
        unknown_boxes = [code for code in ids if code not in container_by_id]
        if unknown_boxes:
            errors.append(f"слот {day}/{meal}: чужие container_ids {unknown_boxes}.")
        if mode in {PrepMode.ASSEMBLE, PrepMode.FINISH}:
            if kind != "weekend" or set(source) != SOURCE_WEEKEND:
                errors.append(f"слот {day}/{meal}: source только {{kind: weekend}}.")
            if not ids:
                errors.append(f"слот {day}/{meal}: assemble/finish без container_ids.")
        elif mode == PrepMode.REHEAT:
            if kind != "slot" or set(source) != SOURCE_SLOT:
                errors.append(
                    f"слот {day}/{meal}: source только {{kind, day, meal}} для reheat."
                )
            if ids:
                errors.append(f"слот {day}/{meal}: reheat с container_ids.")
            src_day = _catch(
                errors,
                integer,
                source.get("day"),
                field=f"слот {day}/{meal} source.day",
                min_value=1,
                max_value=7,
                nullable=True,
            )
            src_meal = source.get("meal")
            if src_day is None or src_meal not in MEALS:
                errors.append(f"слот {day}/{meal}: reheat source day/meal.")
            elif (src_day, src_meal) == (day, meal):
                errors.append(f"слот {day}/{meal}: reheat на себя.")
            elif src_day != day - 1:
                errors.append(f"слот {day}/{meal}: reheat только со вчера (день {day - 1}).")
        _nonempty_steps(item.get("steps"), f"слот {day}/{meal}", errors)
        alts = item.get("alternatives") or []
        if not isinstance(alts, list) or len(alts) > 3:
            errors.append(f"слот {day}/{meal}: alternatives 0–3.")
            alts = []
        for alt in alts:
            if not isinstance(alt, dict):
                errors.append(f"слот {day}/{meal}: alternative не объект.")
                continue
            _validate_dish_use(
                alt,
                f"слот {day}/{meal} alternative",
                container_by_id,
                recipe_slugs,
                errors,
                require_label=True,
            )
        nl = item.get("no_leftover")
        if nl in (None, {}, []):
            nl = None
        if mode == PrepMode.REHEAT:
            if not isinstance(nl, dict) or not str(nl.get("slug") or "").strip():
                errors.append(f"слот {day}/{meal}: reheat без no_leftover.")
            else:
                if nl.get("mode") == PrepMode.REHEAT:
                    errors.append(f"слот {day}/{meal}: no_leftover не reheat.")
                nl_slug = str(nl.get("slug") or "").strip()
                if nl_slug and nl_slug in grid_slugs:
                    errors.append(
                        f"слот {day}/{meal}: no_leftover.slug уже стоит в сетке набора."
                    )
                _validate_dish_use(
                    nl,
                    f"слот {day}/{meal} no_leftover",
                    container_by_id,
                    recipe_slugs,
                    errors,
                    require_label=False,
                    allow_empty_containers=True,
                )
                _validate_shopping_add(
                    nl.get("shopping_add"), f"слот {day}/{meal} no_leftover", errors
                )
        elif nl is not None:
            if not isinstance(nl, dict):
                errors.append(f"слот {day}/{meal}: no_leftover не объект.")
            elif nl.get("slug"):
                errors.append(f"слот {day}/{meal}: no_leftover-замена только у reheat.")
            else:
                _nonempty_steps(
                    nl.get("steps"), f"слот {day}/{meal} no_leftover", errors
                )
        _optional_positive(item, "servings_cooked", f"слот {day}/{meal}", errors)
        _optional_positive(item, "feeds_slots", f"слот {day}/{meal}", errors)
        if item.get("time_active_from_prep_min") not in (None, ""):
            _catch(
                errors,
                integer,
                item.get("time_active_from_prep_min"),
                field=f"слот {day}/{meal} time_active_from_prep_min",
                min_value=0,
            )
        if item.get("time_active_scratch_min") not in (None, ""):
            _catch(
                errors,
                integer,
                item.get("time_active_scratch_min"),
                field=f"слот {day}/{meal} time_active_scratch_min",
                min_value=0,
            )

    missing = REQUIRED_PAIRS - slot_pairs
    if missing and len(slots) == 14:
        errors.append(f"Не все пары day×meal: {sorted(missing)[:4]}…")

    for item in slots:
        if not isinstance(item, dict) or item.get("mode") != PrepMode.REHEAT:
            continue
        source = item.get("source") or {}
        if not isinstance(source, dict):
            continue
        try:
            src_day = integer(
                source.get("day"),
                field="reheat source.day",
                min_value=1,
                max_value=7,
                nullable=True,
            )
        except PayloadError:
            continue
        src_meal = source.get("meal")
        if src_day is None:
            continue
        src = (src_day, src_meal)
        if src not in slot_map and source.get("kind") == "slot":
            errors.append(
                f"слот {item.get('day')}/{item.get('meal')}: нет слота-источника."
            )

    shopping = payload.get("shopping") or []
    if not isinstance(shopping, list):
        errors.append("shopping не список.")
    else:
        for index, row in enumerate(shopping):
            if not isinstance(row, dict):
                errors.append(f"shopping[{index}] не объект.")
                continue
            if not str(row.get("canonical_id") or "").strip():
                errors.append(f"shopping[{index}]: нет canonical_id.")
            if row.get("unit") not in UNIT:
                errors.append(f"shopping[{index}]: unit.")
            _catch(errors, nonnegative_decimal, row.get("qty"), field=f"shopping[{index}]")

    return errors, recipe_slugs


def draft_from_payload(payload: dict, recipe_slugs: set[str]) -> KitDraft:
    slug = kit_slug_of(payload)
    raw_position = payload.get("position")
    position = (
        0
        if raw_position in (None, "")
        else integer(raw_position, field="position", min_value=0)
    )
    raw_servings = payload.get("servings_base")
    servings_base = (
        None
        if raw_servings in (None, "")
        else positive_int(raw_servings, field="servings_base")
    )

    components: list[ComponentDraft] = []
    for item in payload["components"]:
        code = entity_code(item)
        components.append(
            ComponentDraft(
                code=code,
                title=str(item.get("title") or code),
                canonical_ids=tuple(item.get("canonical_ids") or []),
                qty=nonnegative_decimal(item.get("qty"), field=f"component {code}"),
                unit=item["unit"],
                weekend_steps=list(item.get("weekend_steps") or []),
                parcook=dict(item.get("parcook") or {}),
                storage=dict(item.get("storage") or {}),
            )
        )

    containers: list[ContainerDraft] = []
    for item in payload["containers"]:
        code = entity_code(item)
        thaw_raw = item.get("thaw_before_day")
        thaw = (
            None
            if thaw_raw in (None, "")
            else integer(
                thaw_raw,
                field=f"container {code} thaw_before_day",
                min_value=1,
                max_value=7,
            )
        )
        containers.append(
            ContainerDraft(
                code=code,
                component_code=str(item.get("component_id") or item.get("component") or "").strip(),
                label=str(item.get("label") or code),
                qty=nonnegative_decimal(item.get("qty"), field=f"container {code}"),
                unit=item["unit"],
                place=item["place"],
                thaw_before_day=thaw,
            )
        )

    slots: list[SlotDraft] = []
    for item in payload["slots"]:
        day = integer(item.get("day"), field="slot day", min_value=1, max_value=7)
        meal = item["meal"]
        label = f"слот {day}/{meal}"
        steps = _nonempty_steps(item.get("steps"), label, [])
        nl_raw = item.get("no_leftover")
        no_leftover = dict(nl_raw) if isinstance(nl_raw, dict) else {}
        plate = item.get("plate") if isinstance(item.get("plate"), dict) else {}
        slots.append(
            SlotDraft(
                day=day,
                meal=meal,
                slug=str(item.get("slug") or "").strip(),
                mode=item["mode"],
                flavor=item.get("flavor") or None,
                plate=dict(plate),
                source=dict(item.get("source") or {}),
                container_ids=[str(code) for code in (item.get("container_ids") or [])],
                alternatives=list(item.get("alternatives") or []),
                servings_cooked=_optional_positive(item, "servings_cooked", label, []),
                feeds_slots=_optional_positive(item, "feeds_slots", label, []),
                time_active_from_prep_min=(
                    None
                    if item.get("time_active_from_prep_min") in (None, "")
                    else integer(
                        item.get("time_active_from_prep_min"),
                        field=f"{label} time_active_from_prep_min",
                        min_value=0,
                    )
                ),
                time_active_scratch_min=(
                    None
                    if item.get("time_active_scratch_min") in (None, "")
                    else integer(
                        item.get("time_active_scratch_min"),
                        field=f"{label} time_active_scratch_min",
                        min_value=0,
                    )
                ),
                steps=steps,
                no_leftover=no_leftover,
            )
        )

    shopping = []
    for row in payload.get("shopping") or []:
        if isinstance(row, dict):
            item = dict(row)
            item["qty"] = decimal_json(
                nonnegative_decimal(row.get("qty"), field="shopping")
            )
            shopping.append(item)

    return KitDraft(
        slug=slug,
        title=str(payload.get("title") or slug),
        summary=payload.get("summary") or None,
        servings_base=servings_base,
        caution_text=payload.get("caution_text") or None,
        rhythm=payload.get("rhythm") or None,
        position=position,
        metrics=dict(payload.get("metrics") or {}),
        weekend_timeline=list(payload.get("weekend_timeline") or []),
        shopping=shopping,
        allergens=dict(payload.get("allergens") or {}),
        components=tuple(components),
        containers=tuple(containers),
        slots=tuple(slots),
        recipe_slugs=frozenset(recipe_slugs),
    )
