# Бэкенд sol-chef 2.0 — приложение prep — дамп для аудита

Снимок кода на 2026-09-20.
Источник: `v2/backend/apps/prep/`.
Наборы «На неделю»: слоты, масштабирование, разморозка, остатки, валидация.

Правило раскладки: **один файл = содержимое одного исходного `.py`**.
Заголовок блока — путь относительно `v2/`. Ниже — классы и функции верхнего уровня и полный исходник.
Не входят: `migrations/`, `__pycache__/`, пустые `__init__.py`.

## Оглавление

| # | Файл | Классы и функции | Строк |
|---|------|------------------|------:|
| 1 | `backend/apps/prep/admin.py` | `PrepComponentInline`, `PrepContainerInline`, `PrepSlotInline`, `PrepKitAdmin`, `PrepComponentAdmin`, `PrepContainerAdmin`, `PrepSlotAdmin` | 43 |
| 2 | `backend/apps/prep/apps.py` | `PrepConfig` | 8 |
| 3 | `backend/apps/prep/exceptions.py` | `PrepError` | 2 |
| 4 | `backend/apps/prep/management/commands/import_prep_kit.py` | `Command` | 35 |
| 5 | `backend/apps/prep/models.py` | `PrepKit`, `PrepComponent`, `PrepContainer`, `PrepSlot` | 136 |
| 6 | `backend/apps/prep/serializers.py` | `serialize_container`, `thaw_prep_items`, `average_slot_kcal`, `metrics_for_api`, `serialize_kit_list_item`, `serialize_kit_detail` | 356 |
| 7 | `backend/apps/prep/services/context.py` | `resolve_prep_for_recipe` | 173 |
| 8 | `backend/apps/prep/services/graph.py` | `kit_graph` | 64 |
| 9 | `backend/apps/prep/services/leftover.py` | `parse_no_leftover`, `no_leftover_payload`, `leftover_qty_factors`, `replacement_slugs`, `recipes_for_replacements`, `leftover_plan_cost`, `shopping_additions`, `merge_shopping`, `effective_qty_ratio` | 179 |
| 10 | `backend/apps/prep/services/scale.py` | `kit_ratio`, `scale_qty`, `qty_payload` | 29 |
| 11 | `backend/apps/prep/services/thaw.py` | `thaw_pull_for`, `thaw_lead_hours`, `container_number`, `format_container_list`, `thaw_day_reminder`, `thaw_prep_item_text`, `thaw_when_pulled`, `thaw_already_in_fridge_text` | 140 |
| 12 | `backend/apps/prep/services/validate.py` | `KitImportError`, `kit_slug_of`, `validate_kit_payload`, `upsert_kit` | 511 |
| 13 | `backend/apps/prep/urls.py` | — | 8 |
| 14 | `backend/apps/prep/views.py` | `PrepKitListView`, `PrepKitDetailView` | 33 |

Всего файлов: **14**. Строк исходников: **1717**.

---

## 1. `backend/apps/prep/admin.py`

- Путь: `v2/backend/apps/prep/admin.py`
- Классы и функции: PrepComponentInline, PrepContainerInline, PrepSlotInline, PrepKitAdmin, PrepComponentAdmin, PrepContainerAdmin, PrepSlotAdmin
- Строк: 43

```python
from django.contrib import admin

from apps.prep.models import PrepComponent, PrepContainer, PrepKit, PrepSlot


class PrepComponentInline(admin.TabularInline):
    model = PrepComponent
    extra = 0


class PrepContainerInline(admin.TabularInline):
    model = PrepContainer
    extra = 0


class PrepSlotInline(admin.TabularInline):
    model = PrepSlot
    extra = 0


@admin.register(PrepKit)
class PrepKitAdmin(admin.ModelAdmin):
    list_display = ("slug", "title", "status", "position", "servings_base")
    list_filter = ("status",)
    search_fields = ("slug", "title")
    inlines = [PrepComponentInline, PrepContainerInline, PrepSlotInline]


@admin.register(PrepComponent)
class PrepComponentAdmin(admin.ModelAdmin):
    list_display = ("kit", "code", "title")
    search_fields = ("code", "title")


@admin.register(PrepContainer)
class PrepContainerAdmin(admin.ModelAdmin):
    list_display = ("kit", "code", "label", "place")


@admin.register(PrepSlot)
class PrepSlotAdmin(admin.ModelAdmin):
    list_display = ("kit", "day", "meal", "recipe", "mode")
    list_filter = ("mode", "meal")
```

---

## 2. `backend/apps/prep/apps.py`

- Путь: `v2/backend/apps/prep/apps.py`
- Классы и функции: PrepConfig
- Строк: 8

```python
from django.apps import AppConfig


class PrepConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.prep"
    label = "prep"
    verbose_name = "Weekly prep"
```

---

## 3. `backend/apps/prep/exceptions.py`

- Путь: `v2/backend/apps/prep/exceptions.py`
- Классы и функции: PrepError
- Строк: 2

```python
class PrepError(Exception):
    """Bad prep query or payload — API 400."""
```

---

## 4. `backend/apps/prep/management/commands/import_prep_kit.py`

- Путь: `v2/backend/apps/prep/management/commands/import_prep_kit.py`
- Классы и функции: Command
- Строк: 35

```python
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from apps.prep.services.validate import KitImportError, upsert_kit
from apps.recipes.etl.draft import DraftError, load_json


class Command(BaseCommand):
    help = "Validate and upsert a weekly-prep kit JSON. --dry-run не пишет."

    def add_arguments(self, parser):
        parser.add_argument("--path", type=str, required=True, help="Файл kit JSON")
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Только валидатор, без записи",
        )

    def handle(self, *args, **options):
        path = Path(options["path"])
        try:
            payload = load_json(path)
        except DraftError as exc:
            raise CommandError(str(exc)) from exc
        try:
            kit = upsert_kit(payload, dry_run=bool(options["dry_run"]))
        except KitImportError as exc:
            for line in exc.errors:
                self.stderr.write(line)
            raise CommandError(f"Набор не принят ({len(exc.errors)} ошибок).") from exc
        if options["dry_run"]:
            self.stdout.write("dry-run ok")
            return
        self.stdout.write(f"imported {kit.slug}")
```

---

## 5. `backend/apps/prep/models.py`

- Путь: `v2/backend/apps/prep/models.py`
- Классы и функции: PrepKit, PrepComponent, PrepContainer, PrepSlot
- Строк: 136

```python
"""Weekly-prep kits — slot bodies, not a second Recipe body (DATA-MODEL)."""

from __future__ import annotations

from django.core.exceptions import ValidationError
from django.db import models

from apps.recipes.constants import UNIT
from apps.recipes.models import Recipe


def _choice(codes: frozenset[str] | tuple[str, ...]) -> list[tuple[str, str]]:
    return [(code, code) for code in sorted(codes)]


PREP_STATUS = frozenset({"draft", "published"})
PREP_MODE = frozenset({"assemble", "finish", "reheat"})
PREP_MEAL = frozenset({"lunch", "dinner"})
PREP_PLACE = frozenset({"fridge", "freezer", "pantry"})


class PrepKit(models.Model):
    slug = models.SlugField(max_length=200, unique=True)
    title = models.TextField()
    summary = models.TextField(null=True, blank=True)
    servings_base = models.PositiveIntegerField(null=True, blank=True)
    caution_text = models.TextField(null=True, blank=True)
    rhythm = models.TextField(null=True, blank=True)
    status = models.CharField(
        max_length=16, choices=_choice(PREP_STATUS), default="draft"
    )
    position = models.IntegerField(default=0)
    metrics = models.JSONField(default=dict, blank=True)
    weekend_timeline = models.JSONField(default=list, blank=True)
    shopping = models.JSONField(default=list, blank=True)
    allergens = models.JSONField(default=dict, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["position", "slug"]
        indexes = [
            models.Index(fields=["status", "position", "slug"]),
        ]

    def __str__(self) -> str:
        return self.slug


class PrepComponent(models.Model):
    kit = models.ForeignKey(PrepKit, on_delete=models.CASCADE, related_name="components")
    code = models.SlugField(max_length=80)
    title = models.TextField()
    canonical_ids = models.JSONField(default=list, blank=True)
    qty = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=16, choices=_choice(UNIT))
    weekend_steps = models.JSONField(default=list, blank=True)
    parcook = models.JSONField(default=dict, blank=True)
    storage = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["id"]
        constraints = [
            models.UniqueConstraint(
                fields=["kit", "code"],
                name="prep_component_unique_kit_code",
            )
        ]

    def __str__(self) -> str:
        return f"{self.kit.slug}:{self.code}"


class PrepContainer(models.Model):
    kit = models.ForeignKey(PrepKit, on_delete=models.CASCADE, related_name="containers")
    code = models.SlugField(max_length=80)
    label = models.TextField()
    component = models.ForeignKey(
        PrepComponent, on_delete=models.CASCADE, related_name="boxes"
    )
    qty = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=16, choices=_choice(UNIT))
    place = models.CharField(max_length=16, choices=_choice(PREP_PLACE))
    thaw_before_day = models.PositiveSmallIntegerField(null=True, blank=True)

    class Meta:
        ordering = ["id"]
        constraints = [
            models.UniqueConstraint(
                fields=["kit", "code"],
                name="prep_container_unique_kit_code",
            )
        ]

    def __str__(self) -> str:
        return f"{self.kit.slug}:{self.code}"

    def clean(self) -> None:
        if self.thaw_before_day is not None and not 1 <= self.thaw_before_day <= 7:
            raise ValidationError("thaw_before_day должен быть 1–7.")


class PrepSlot(models.Model):
    kit = models.ForeignKey(PrepKit, on_delete=models.CASCADE, related_name="slots")
    day = models.PositiveSmallIntegerField()
    meal = models.CharField(max_length=16, choices=_choice(PREP_MEAL))
    recipe = models.ForeignKey(
        Recipe, on_delete=models.PROTECT, related_name="prep_slots"
    )
    mode = models.CharField(max_length=16, choices=_choice(PREP_MODE))
    flavor = models.TextField(null=True, blank=True)
    plate = models.JSONField(default=dict, blank=True)
    source = models.JSONField(default=dict)
    container_ids = models.JSONField(default=list, blank=True)
    alternatives = models.JSONField(default=list, blank=True)
    servings_cooked = models.PositiveIntegerField(null=True, blank=True)
    feeds_slots = models.PositiveIntegerField(null=True, blank=True)
    time_active_from_prep_min = models.PositiveIntegerField(null=True, blank=True)
    time_active_scratch_min = models.PositiveIntegerField(null=True, blank=True)
    steps = models.JSONField(default=list)
    no_leftover = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["day", "meal"]
        constraints = [
            models.UniqueConstraint(
                fields=["kit", "day", "meal"],
                name="prep_slot_unique_kit_day_meal",
            )
        ]

    def __str__(self) -> str:
        return f"{self.kit.slug}:{self.day}:{self.meal}"

    def clean(self) -> None:
        if self.day < 1 or self.day > 7:
            raise ValidationError("day должен быть 1–7.")
```

---

## 6. `backend/apps/prep/serializers.py`

- Путь: `v2/backend/apps/prep/serializers.py`
- Классы и функции: serialize_container, thaw_prep_items, average_slot_kcal, metrics_for_api, serialize_kit_list_item, serialize_kit_detail
- Строк: 356

```python
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
    if metrics.get("kcal_avg_per_serving") is not None:
        return metrics
    kcal = average_slot_kcal(kit)
    if kcal is not None:
        metrics["kcal_avg_per_serving"] = kcal
        stored = dict(kit.metrics or {})
        stored["kcal_avg_per_serving"] = kcal
        PrepKit.objects.filter(pk=kit.pk).update(metrics=stored)
        kit.metrics = stored
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
```

---

## 7. `backend/apps/prep/services/context.py`

- Путь: `v2/backend/apps/prep/services/context.py`
- Классы и функции: resolve_prep_for_recipe
- Строк: 173

```python
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

    meal_rank = {"lunch": 0, "dinner": 1}
    my_rank = meal_rank.get(meal or "", 1)
    used_earlier: dict[str, bool] = {}
    for code in ids:
        used_earlier[code] = any(
            row.day == day
            and meal_rank.get(row.meal, 1) < my_rank
            and code in [str(item) for item in (row.container_ids or [])]
            for row in slots
        )

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
        "prep": thaw_prep_items(containers, day, used_earlier=used_earlier),
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
```

---

## 8. `backend/apps/prep/services/graph.py`

- Путь: `v2/backend/apps/prep/services/graph.py`
- Классы и функции: kit_graph
- Строк: 64

```python
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
```

---

## 9. `backend/apps/prep/services/leftover.py`

- Путь: `v2/backend/apps/prep/services/leftover.py`
- Классы и функции: parse_no_leftover, no_leftover_payload, leftover_qty_factors, replacement_slugs, recipes_for_replacements, leftover_plan_cost, shopping_additions, merge_shopping, effective_qty_ratio
- Строк: 179

```python
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
```

---

## 10. `backend/apps/prep/services/scale.py`

- Путь: `v2/backend/apps/prep/services/scale.py`
- Классы и функции: kit_ratio, scale_qty, qty_payload
- Строк: 29

```python
from __future__ import annotations

from decimal import Decimal
from typing import Any

from apps.recipes.services.scale import apply_mode, format_display_amount, round_scaled


def kit_ratio(servings_base: int | None, servings: Decimal | None) -> tuple[Decimal, bool]:
    if servings_base is None or servings is None:
        return Decimal("1"), False
    return servings / Decimal(servings_base), True


def scale_qty(qty: Any, unit: str, ratio: Decimal, enabled: bool) -> Decimal:
    amount = qty if isinstance(qty, Decimal) else Decimal(str(qty))
    scaled = apply_mode(amount, ratio, "linear", True) if enabled else amount
    return round_scaled(scaled, unit)


def qty_payload(qty: Any, unit: str, ratio: Decimal, enabled: bool) -> dict:
    scaled = scale_qty(qty, unit, ratio, enabled)
    as_int = scaled == scaled.to_integral_value()
    number: int | float = int(scaled) if as_int else float(scaled)
    return {
        "qty": number,
        "unit": unit,
        "display_amount": format_display_amount(scaled, unit),
    }
```

---

## 11. `backend/apps/prep/services/thaw.py`

- Путь: `v2/backend/apps/prep/services/thaw.py`
- Классы и функции: thaw_pull_for, thaw_lead_hours, container_number, format_container_list, thaw_day_reminder, thaw_prep_item_text, thaw_when_pulled, thaw_already_in_fridge_text
- Строк: 140

```python
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

DAY_GENITIVE = (
    "",
    "понедельника",
    "вторника",
    "среды",
    "четверга",
    "пятницы",
    "субботы",
    "воскресенья",
)
DAY_V = (
    "",
    "в понедельник",
    "во вторник",
    "в среду",
    "в четверг",
    "в пятницу",
    "в субботу",
    "в воскресенье",
)


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


def thaw_when_pulled(pull: str | None, thaw_before_day: int) -> str:
    day = int(thaw_before_day)
    if pull == THAW_MORNING:
        name = DAY_V[day] if 1 <= day <= 7 else ""
        return f"утром {name}".strip()
    if day <= 1:
        prev = "воскресенья"
    else:
        prev = DAY_GENITIVE[day - 1]
    return f"с вечера {prev}"


def thaw_already_in_fridge_text(
    *,
    label: str | None,
    pull: str | None,
    thaw_before_day: int,
) -> str:
    num = container_number(label)
    when = thaw_when_pulled(pull, thaw_before_day)
    if num:
        return f"Контейнер {num} уже в холодильнике: вы доставали его {when}."
    what = (label or "заготовка").strip()
    return f"{what} уже в холодильнике: вы доставали её {when}."
```

---

## 12. `backend/apps/prep/services/validate.py`

- Путь: `v2/backend/apps/prep/services/validate.py`
- Классы и функции: KitImportError, kit_slug_of, validate_kit_payload, upsert_kit
- Строк: 511

```python
"""Validate and upsert a weekly-prep kit JSON (DATA-MODEL invariants)."""

from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Any

from django.db import transaction

from apps.prep.models import PrepComponent, PrepContainer, PrepKit, PrepSlot
from apps.recipes.constants import UNIT
from apps.recipes.models import Recipe

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
MEALS = ("lunch", "dinner")
REQUIRED_PAIRS = {(day, meal) for day in range(1, 8) for meal in MEALS}
SOURCE_WEEKEND = frozenset({"kind"})
SOURCE_SLOT = frozenset({"kind", "day", "meal"})


class KitImportError(Exception):
    def __init__(self, errors: list[str]):
        self.errors = errors
        super().__init__("; ".join(errors))


def _dec(value: Any, label: str, errors: list[str]) -> Decimal | None:
    try:
        qty = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        errors.append(f"{label}: некорректное qty.")
        return None
    if qty < 0:
        errors.append(f"{label}: qty < 0.")
        return None
    return qty


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
    if mode not in {"assemble", "finish", "reheat"}:
        errors.append(f"{label}: mode assemble|finish|reheat.")
    ids = item.get("container_ids") or []
    if not isinstance(ids, list):
        errors.append(f"{label}: container_ids не список.")
        ids = []
    ids = [str(code) for code in ids]
    bad = [code for code in ids if code not in container_by_id]
    if bad:
        errors.append(f"{label}: чужие боксы {bad}.")
    if mode in {"assemble", "finish"} and not ids:
        extra = item.get("shopping_add") or []
        if allow_empty_containers and isinstance(extra, list) and extra:
            pass
        else:
            if allow_empty_containers:
                errors.append(f"{label}: без боксов нужен shopping_add.")
            else:
                errors.append(f"{label}: assemble/finish без container_ids.")
    if mode == "reheat" and ids:
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
        _dec(row.get("qty"), f"{label} shopping_add[{index}]", errors)


def kit_slug_of(payload: dict) -> str:
    raw = payload.get("slug") or payload.get("id")
    return str(raw or "").strip()


def validate_kit_payload(payload: dict) -> list[str]:
    errors: list[str] = []
    if not isinstance(payload, dict):
        return ["Корень JSON должен быть объектом."]
    _walk_forbidden(payload, "kit", errors)
    slug = kit_slug_of(payload)
    if not slug:
        errors.append("Нет id/slug набора.")

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
        code = str(item.get("id") or item.get("code") or "").strip()
        if not code:
            errors.append("component без id.")
            continue
        if code in component_by_id:
            errors.append(f"Дубль component {code}.")
            continue
        unit = item.get("unit")
        if unit not in UNIT:
            errors.append(f"component {code}: неизвестный unit.")
        _dec(item.get("qty"), f"component {code}", errors)
        component_by_id[code] = item

    container_by_id: dict[str, dict] = {}
    qty_by_component: dict[str, Decimal] = {code: Decimal("0") for code in component_by_id}
    for item in containers:
        if not isinstance(item, dict):
            errors.append("container не объект.")
            continue
        code = str(item.get("id") or item.get("code") or "").strip()
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
        if place not in {"fridge", "freezer", "pantry"}:
            errors.append(f"container {code}: place fridge|freezer|pantry.")
        thaw = item.get("thaw_before_day")
        if thaw is not None and thaw not in range(1, 8):
            errors.append(f"container {code}: thaw_before_day 1–7.")
        qty = _dec(item.get("qty"), f"container {code}", errors)
        if qty is not None and parent in qty_by_component:
            qty_by_component[parent] += qty
        container_by_id[code] = item

    for code, item in component_by_id.items():
        expected = _dec(item.get("qty"), f"component {code}", [])
        if expected is None:
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
    recipe_slugs: set[str] = set()
    grid_slugs = {
        str(row.get("slug") or "").strip()
        for row in slots
        if isinstance(row, dict) and str(row.get("slug") or "").strip()
    }
    for item in slots:
        if not isinstance(item, dict):
            errors.append("slot не объект.")
            continue
        try:
            day = int(item.get("day"))
        except (TypeError, ValueError):
            errors.append("slot без day 1–7.")
            continue
        meal = item.get("meal")
        if day not in range(1, 8) or meal not in MEALS:
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
        if mode not in {"assemble", "finish", "reheat"}:
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
        if mode in {"assemble", "finish"}:
            if kind != "weekend" or set(source) != SOURCE_WEEKEND:
                errors.append(f"слот {day}/{meal}: source только {{kind: weekend}}.")
            if not ids:
                errors.append(f"слот {day}/{meal}: assemble/finish без container_ids.")
        elif mode == "reheat":
            if kind != "slot" or set(source) != SOURCE_SLOT:
                errors.append(
                    f"слот {day}/{meal}: source только {{kind, day, meal}} для reheat."
                )
            if ids:
                errors.append(f"слот {day}/{meal}: reheat с container_ids.")
            try:
                src_day = int(source.get("day"))
            except (TypeError, ValueError):
                src_day = None
            src_meal = source.get("meal")
            if src_day not in range(1, 8) or src_meal not in MEALS:
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
        if mode == "reheat":
            if not isinstance(nl, dict) or not str(nl.get("slug") or "").strip():
                errors.append(f"слот {day}/{meal}: reheat без no_leftover.")
            else:
                if nl.get("mode") == "reheat":
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


    missing = REQUIRED_PAIRS - slot_pairs
    if missing and len(slots) == 14:
        errors.append(f"Не все пары day×meal: {sorted(missing)[:4]}…")

    for item in slots:
        if not isinstance(item, dict) or item.get("mode") != "reheat":
            continue
        source = item.get("source") or {}
        try:
            src = (int(source.get("day")), source.get("meal"))
        except (TypeError, ValueError):
            continue
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
            _dec(row.get("qty"), f"shopping[{index}]", errors)

    published = set(
        Recipe.objects.filter(slug__in=recipe_slugs, status="published").values_list(
            "slug", flat=True
        )
    )
    missing_recipes = sorted(recipe_slugs - published)
    if missing_recipes:
        errors.append(f"unpublished/нет recipe: {', '.join(missing_recipes)}.")

    return errors


def _recipe_map(slugs: set[str]) -> dict[str, Recipe]:
    return {row.slug: row for row in Recipe.objects.filter(slug__in=slugs)}


def upsert_kit(payload: dict, *, dry_run: bool = False) -> PrepKit | None:
    errors = validate_kit_payload(payload)
    if errors:
        raise KitImportError(errors)
    if dry_run:
        return None
    slug = kit_slug_of(payload)
    recipes = _recipe_map(
        {
            str(item.get("slug") or "")
            for item in payload.get("slots") or []
            if isinstance(item, dict)
        }
        | {
            str(alt.get("slug") or "")
            for item in payload.get("slots") or []
            if isinstance(item, dict)
            for alt in (item.get("alternatives") or [])
            if isinstance(alt, dict)
        }
        | {
            str((item.get("no_leftover") or {}).get("slug") or "")
            for item in payload.get("slots") or []
            if isinstance(item, dict) and isinstance(item.get("no_leftover"), dict)
        }
    )
    with transaction.atomic():
        kit, _ = PrepKit.objects.update_or_create(
            slug=slug,
            defaults={
                "title": str(payload.get("title") or slug),
                "summary": payload.get("summary") or None,
                "servings_base": payload.get("servings_base"),
                "caution_text": payload.get("caution_text") or None,
                "rhythm": payload.get("rhythm") or None,
                "status": "published",
                "position": int(payload.get("position") or 0),
                "metrics": payload.get("metrics") or {},
                "weekend_timeline": payload.get("weekend_timeline") or [],
                "shopping": payload.get("shopping") or [],
                "allergens": payload.get("allergens") or {},
            },
        )
        kit.slots.all().delete()
        kit.containers.all().delete()
        kit.components.all().delete()
        components: dict[str, PrepComponent] = {}
        for item in payload["components"]:
            code = str(item.get("id") or item.get("code"))
            components[code] = PrepComponent.objects.create(
                kit=kit,
                code=code,
                title=str(item.get("title") or code),
                canonical_ids=item.get("canonical_ids") or [],
                qty=Decimal(str(item["qty"])),
                unit=item["unit"],
                weekend_steps=item.get("weekend_steps") or [],
                parcook=item.get("parcook") or {},
                storage=item.get("storage") or {},
            )
        for item in payload["containers"]:
            code = str(item.get("id") or item.get("code"))
            parent = str(item.get("component_id") or item.get("component"))
            PrepContainer.objects.create(
                kit=kit,
                code=code,
                label=str(item.get("label") or code),
                component=components[parent],
                qty=Decimal(str(item["qty"])),
                unit=item["unit"],
                place=item["place"],
                thaw_before_day=item.get("thaw_before_day"),
            )
        for item in payload["slots"]:
            PrepSlot.objects.create(
                kit=kit,
                day=int(item["day"]),
                meal=item["meal"],
                recipe=recipes[str(item["slug"])],
                mode=item["mode"],
                flavor=item.get("flavor") or None,
                plate=item.get("plate") if isinstance(item.get("plate"), dict) else {},
                source=item["source"],
                container_ids=[str(code) for code in (item.get("container_ids") or [])],
                alternatives=item.get("alternatives") or [],
                servings_cooked=item.get("servings_cooked"),
                feeds_slots=item.get("feeds_slots"),
                time_active_from_prep_min=item.get("time_active_from_prep_min"),
                time_active_scratch_min=item.get("time_active_scratch_min"),
                steps=item.get("steps") or [],
                no_leftover=item.get("no_leftover")
                if isinstance(item.get("no_leftover"), dict)
                else {},
            )
        return kit
```

---

## 13. `backend/apps/prep/urls.py`

- Путь: `v2/backend/apps/prep/urls.py`
- Классы и функции: нет классов/функций верхнего уровня
- Строк: 8

```python
from django.urls import path

from apps.prep.views import PrepKitDetailView, PrepKitListView

urlpatterns = [
    path("prep-kits/", PrepKitListView.as_view(), name="prep-kit-list"),
    path("prep-kits/<slug:slug>/", PrepKitDetailView.as_view(), name="prep-kit-detail"),
]
```

---

## 14. `backend/apps/prep/views.py`

- Путь: `v2/backend/apps/prep/views.py`
- Классы и функции: PrepKitListView, PrepKitDetailView
- Строк: 33

```python
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.prep.models import PrepKit
from apps.prep.serializers import serialize_kit_detail, serialize_kit_list_item
from apps.prep.services.leftover import parse_no_leftover
from apps.recipes.query import parse_optional_decimal


def _published():
    return PrepKit.objects.filter(status="published")


class PrepKitListView(APIView):
    def get(self, request):
        kits = _published().order_by("position", "slug")
        return Response({"results": [serialize_kit_list_item(kit) for kit in kits]})


class PrepKitDetailView(APIView):
    def get(self, request, slug: str):
        kit = (
            _published()
            .prefetch_related("components", "containers__component", "slots__recipe")
            .filter(slug=slug)
            .first()
        )
        if kit is None:
            raise NotFound("Набор не найден.")
        servings = parse_optional_decimal(request, "servings")
        no_leftover = parse_no_leftover(request)
        return Response(serialize_kit_detail(kit, servings, no_leftover=no_leftover))
```

---
