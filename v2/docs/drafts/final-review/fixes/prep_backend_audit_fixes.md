# Правки по аудиту `backend/apps/prep`

## Список проблем

1. `metrics_for_api()` выполняет запись в БД во время GET-сериализации и провоцирует N+1-запросы при выводе списка наборов.
2. `serialize_kit_detail()` и связанные сервисы повторно загружают одни и те же связи, игнорируя `prefetch_related()` из view; особенно заметно для `slots`, `containers`, `components` и графа.
3. `kit_graph()` содержит алгоритм с квадратичной сложностью и хрупкий доступ к `source["day"]` / `source["meal"]`, который может упасть на неконсистентных данных.
4. Валидация импорта и запись в БД не разделены: `validate.py` содержит более 500 строк, смешивает нормализацию, правила домена, ORM-проверки и persistence.
5. `upsert_kit()` удаляет и заново создаёт весь граф дочерних сущностей: лишние DELETE/INSERT, нестабильные PK, риск каскадных побочных эффектов и сложная история изменений.
6. Валидация не проверяет ряд значений, которые затем записываются в модель: `servings_base`, `position`, `feeds_slots`, тайминги, допустимые ключи/типы JSON-полей.
7. Ограничения целостности живут только в `clean()`, но `objects.create()` и `update_or_create()` не вызывают `full_clean()`; некорректные значения можно записать обходя формы и импорт.
8. `PrepContainer` допускает связь с компонентом другого `PrepKit`; это не защищено ограничением базы и ломает инвариант набора.
9. `PrepSlot` допускает отрицательные/нецелые логические значения в JSON-структурах и не имеет DB-level проверки `day`.
10. Повторяются константы домена (`lunch/dinner`, `assemble/finish/reheat`, места хранения), а также логика масштаба и чтения query-параметров.
11. В `resolve_prep_for_recipe()` слишком много обязанностей: парсинг HTTP, загрузка ORM, выбор сценария, расчёт масштаба, подготовка контейнеров и формирование API-ответа.
12. `used_earlier` вычисляется не только по реально выбранным контейнерам сценария (alternative/no_leftover), а по исходным `slot.container_ids`; текст разморозки может быть неверным.
13. `merge_shopping()` объединяет позиции только по `canonical_id`, игнорируя единицу измерения и метаданные; разные единицы могут быть ошибочно сложены.
14. Использование `float` в публичном количестве и ratio создаёт потерю точности для Decimal-значений.
15. Набор импортируется сразу как `published`; отсутствует явная политика публикации и возможность загрузить черновик.
16. Нет пакетных вставок при импорте и нет тестового контракта для инвариантов, N+1 и сценариев `no_leftover`.

## 1. Убрать запись из GET и N+1 при списке

### Проблема

`serialize_kit_list_item()` вызывает `metrics_for_api()`, которая при отсутствии `kcal_avg_per_serving`:

- загружает слоты и глубокие связи для каждого набора;
- вызывает расчёт nutrition для каждого слота;
- выполняет `UPDATE` прямо в обработке GET.

Это нарушает принцип отсутствия side effects у чтения, делает latency списка непредсказуемой и создаёт N+1.

### Правка

Уберите ленивый расчёт и запись из сериализатора. Метрика должна быть либо частью импортируемого payload, либо пересчитываться отдельной командой/таской после изменения рецепта или набора.

```python
# backend/apps/prep/serializers.py

def metrics_for_api(kit: PrepKit) -> dict:
    return dict(kit.metrics or {})
```

Создайте отдельный сервис пересчёта.

```python
# backend/apps/prep/services/metrics.py
from __future__ import annotations

from decimal import Decimal

from apps.prep.models import PrepKit
from apps.recipes.services.assemble import assemble_recipe
from apps.recipes.services.nutrition import compute_recipe_nutrition


def calculate_average_slot_kcal(kit: PrepKit) -> int | None:
    values: list[int] = []
    slots = kit.slots.select_related("recipe").prefetch_related(
        "recipe__ingredients__ingredient",
        "recipe__steps",
        "recipe__variants",
    )

    for slot in slots:
        recipe = slot.recipe
        nutrition = compute_recipe_nutrition(
            assemble_recipe(recipe).ingredients,
            servings=recipe.servings or kit.servings_base or 2,
            ratio=Decimal("1"),
            scaling_enabled=False,
            yield_weight_g=recipe.yield_weight_g,
        )
        kcal = (nutrition.get("per_serving") or {}).get("kcal")
        if kcal is not None:
            values.append(int(kcal))

    return round(sum(values) / len(values)) if values else None


def refresh_kit_metrics(kit: PrepKit) -> PrepKit:
    metrics = dict(kit.metrics or {})
    metrics["kcal_avg_per_serving"] = calculate_average_slot_kcal(kit)
    PrepKit.objects.filter(pk=kit.pk).update(metrics=metrics)
    kit.metrics = metrics
    return kit
```

Вызывайте `refresh_kit_metrics()` из фоновой задачи или management command, но не из serializer/view.

## 2. Передавать загруженные данные, а не запрашивать ORM повторно

### Проблема

Detail view делает prefetch, но сериализатор вызывает `kit.containers.select_related(...).all()`, `kit.slots.select_related(...).all()` и сервисы, которые снова обращаются к related manager. Prefetch-кэш при вызове queryset с новыми параметрами не используется.

### Правка

Загрузите все данные один раз, соберите read model и передавайте её в сервисы. Это также сокращает неявные зависимости функций от ORM.

```python
# backend/apps/prep/services/read_model.py
from __future__ import annotations

from dataclasses import dataclass

from apps.prep.models import PrepComponent, PrepContainer, PrepKit, PrepSlot


@dataclass(frozen=True, slots=True)
class KitData:
    kit: PrepKit
    components: tuple[PrepComponent, ...]
    containers: tuple[PrepContainer, ...]
    slots: tuple[PrepSlot, ...]

    @property
    def containers_by_code(self) -> dict[str, PrepContainer]:
        return {container.code: container for container in self.containers}


def load_kit_data(kit: PrepKit) -> KitData:
    return KitData(
        kit=kit,
        components=tuple(kit.components.all()),
        containers=tuple(kit.containers.all()),
        slots=tuple(kit.slots.all()),
    )
```

```python
# backend/apps/prep/views.py
class PrepKitDetailView(APIView):
    def get(self, request, slug: str):
        kit = (
            _published()
            .prefetch_related(
                "components",
                "containers__component",
                "slots__recipe",
            )
            .filter(slug=slug)
            .first()
        )
        if kit is None:
            raise NotFound("Набор не найден.")

        return Response(
            serialize_kit_detail(
                load_kit_data(kit),
                parse_optional_decimal(request, "servings"),
                no_leftover=parse_no_leftover(request),
            )
        )
```

Затем измените сигнатуры `serialize_kit_detail`, `kit_graph`, `leftover_qty_factors`, `leftover_plan_cost`, `shopping_additions` так, чтобы они принимали `KitData`, а не `PrepKit`.

## 3. Упростить и ускорить построение графа

### Проблема

`cascade_from()` выполняет полный обход `slots` в цикле до стабилизации. При длинных цепочках это O(V²). Дополнительно `source["day"]` и `source["meal"]` способны выбросить исключение на данных, созданных не импортёром.

### Правка

Постройте обратный индекс `source_slot -> reheat slots` один раз и используйте BFS/DFS.

```python
# backend/apps/prep/services/graph.py
from __future__ import annotations

from collections import defaultdict, deque
from collections.abc import Iterable

from apps.prep.models import PrepComponent, PrepContainer, PrepSlot

MEAL_RANK = {"lunch": 0, "dinner": 1}
SlotKey = tuple[int, str]


def slot_key(slot: PrepSlot) -> SlotKey:
    return slot.day, slot.meal


def slot_sort_key(slot: PrepSlot) -> tuple[int, int]:
    return slot.day, MEAL_RANK[slot.meal]


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


def kit_graph(
    components: Iterable[PrepComponent],
    containers: Iterable[PrepContainer],
    slots: Iterable[PrepSlot],
) -> list[dict]:
    slot_rows = tuple(slots)
    boxes_by_component: dict[int, set[str]] = defaultdict(set)
    for box in containers:
        boxes_by_component[box.component_id].add(box.code)

    reheat_by_source: dict[SlotKey, list[PrepSlot]] = defaultdict(list)
    for slot in slot_rows:
        if slot.mode != "reheat":
            continue
        if key := source_key(slot):
            reheat_by_source[key].append(slot)

    graph: list[dict] = []
    for component in components:
        component_boxes = boxes_by_component[component.pk]
        starts = [
            slot
            for slot in slot_rows
            if slot.mode != "reheat"
            and component_boxes.intersection(map(str, slot.container_ids or []))
        ]
        graph.append({
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
        })
    return graph
```

## 4. Разделить validation, normalization и persistence

### Проблема

`validate.py` — монолитный модуль. Он одновременно:

- валидирует входную JSON-схему;
- нормализует поля;
- проверяет бизнес-инварианты;
- делает запросы к `Recipe`;
- удаляет/создаёт ORM-модели.

Такой код сложно тестировать, расширять и повторно использовать.

### Правка

Разбейте код на четыре уровня.

| Модуль | Ответственность |
|---|---|
| `contracts.py` | TypedDict/dataclass или Pydantic-схемы входного JSON |
| `normalizers.py` | Приведение `id/code`, Decimal, пустых значений и строк |
| `validators.py` | Чистые правила домена без ORM |
| `repository.py` | Загрузка рецептов и запись моделей внутри транзакции |
| `importer.py` | Оркестрация: parse → normalize → validate → resolve recipes → persist |

Минимальный контракт для результата валидации:

```python
# backend/apps/prep/services/importer/contracts.py
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class ContainerDraft:
    code: str
    component_code: str
    label: str
    qty: Decimal
    unit: str
    place: str
    thaw_before_day: int | None


@dataclass(frozen=True, slots=True)
class KitDraft:
    slug: str
    title: str
    status: str
    servings_base: int | None
    components: tuple[object, ...]
    containers: tuple[ContainerDraft, ...]
    slots: tuple[object, ...]
    shopping: tuple[dict, ...]
```

После нормализации persistence не должен использовать `payload.get(...)`: он получает только гарантированно валидный `KitDraft`.

## 5. Заменить destructive upsert на дифф или явную стратегию

### Проблема

Текущая последовательность:

```python
kit.slots.all().delete()
kit.containers.all().delete()
kit.components.all().delete()
```

создаёт большой объём операций, меняет все PK даже при одном изменении и разрушает внешние связи, если они появятся.

### Правка

Если сущности должны иметь стабильную идентичность, используйте синхронизацию по `(kit, code)` / `(kit, day, meal)`: обновляйте существующие, создавайте недостающие, удаляйте отсутствующие. Важно: контейнеры обновляйте после компонентов, слоты — после разрешения recipe map.

```python
# backend/apps/prep/services/repository.py
from __future__ import annotations

from apps.prep.models import PrepComponent, PrepKit


def sync_components(kit: PrepKit, drafts: list[object]) -> dict[str, PrepComponent]:
    existing = {item.code: item for item in kit.components.all()}
    expected_codes = {draft.code for draft in drafts}

    kit.components.exclude(code__in=expected_codes).delete()

    result: dict[str, PrepComponent] = {}
    for draft in drafts:
        component = existing.get(draft.code)
        values = {
            "title": draft.title,
            "canonical_ids": list(draft.canonical_ids),
            "qty": draft.qty,
            "unit": draft.unit,
            "weekend_steps": list(draft.weekend_steps),
            "parcook": dict(draft.parcook),
            "storage": dict(draft.storage),
        }
        if component is None:
            component = PrepComponent.objects.create(kit=kit, code=draft.code, **values)
        else:
            for name, value in values.items():
                setattr(component, name, value)
            component.full_clean()
            component.save(update_fields=[*values, "kit"])
        result[draft.code] = component
    return result
```

Если замена графа является осознанной частью доменной модели, зафиксируйте это явно: создавайте новую ревизию набора (`PrepKitRevision`) и публикуйте её атомарно вместо обновления опубликованной сущности на месте.

## 6. Добавить доменные ограничения в модели и БД

### Проблема

`clean()` не запускается при `objects.create()`, bulk-операциях и прямом доступе к БД. Текущий импорт также не вызывает `full_clean()`.

### Правка

Добавьте `CheckConstraint` для числовых диапазонов. Дополнительно проверяйте, что контейнер принадлежит компоненту того же набора, в `clean()` и во время import/sync. Для полноценной DB-защиты этого инварианта потребуется изменить модель данных: хранить `kit_id` как часть составного внешнего ключа невозможно в стандартном Django без raw SQL/триггера; практичный вариант — убрать дублирующий `PrepContainer.kit` или валидировать триггером PostgreSQL.

```python
# backend/apps/prep/models.py
from django.db.models import F, Q


class PrepContainer(models.Model):
    # Поля без изменений

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["kit", "code"],
                name="prep_container_unique_kit_code",
            ),
            models.CheckConstraint(
                condition=Q(thaw_before_day__isnull=True)
                | Q(thaw_before_day__gte=1, thaw_before_day__lte=7),
                name="prep_container_thaw_day_1_7",
            ),
        ]

    def clean(self) -> None:
        super().clean()
        if self.component_id and self.kit_id and self.component.kit_id != self.kit_id:
            raise ValidationError({"component": "Компонент должен принадлежать тому же набору."})


class PrepSlot(models.Model):
    # Поля без изменений

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["kit", "day", "meal"],
                name="prep_slot_unique_kit_day_meal",
            ),
            models.CheckConstraint(
                condition=Q(day__gte=1, day__lte=7),
                name="prep_slot_day_1_7",
            ),
            models.CheckConstraint(
                condition=Q(servings_cooked__isnull=True) | Q(servings_cooked__gte=1),
                name="prep_slot_servings_cooked_positive",
            ),
            models.CheckConstraint(
                condition=Q(feeds_slots__isnull=True) | Q(feeds_slots__gte=1),
                name="prep_slot_feeds_slots_positive",
            ),
        ]
```

Не импортируйте `F`, если оно не используется. После изменения моделей создайте и проверьте migration на production-копии данных перед деплоем.

## 7. Нормализовать и валидировать payload полностью

### Проблема

Некоторые поля преобразуются только при записи (`int(payload.get("position") or 0)`), поэтому ошибка может возникнуть вне понятного отчёта валидатора. `servings_base` и несколько счётчиков не проходят строгую проверку. `Decimal("NaN")` и бесконечности также не отсеиваются `_dec()`.

### Правка

Сделайте один нормализатор чисел и используйте его во всех полях.

```python
# backend/apps/prep/services/importer/normalizers.py
from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Any


class PayloadError(ValueError):
    pass


def positive_int(value: Any, *, field: str, nullable: bool = False) -> int | None:
    if value in (None, "") and nullable:
        return None
    if isinstance(value, bool):
        raise PayloadError(f"{field}: требуется целое число.")
    try:
        number = int(value)
    except (TypeError, ValueError) as exc:
        raise PayloadError(f"{field}: требуется целое число.") from exc
    if str(value).strip() not in {str(number), f"+{number}"}:
        raise PayloadError(f"{field}: требуется целое число без дробной части.")
    if number < 1:
        raise PayloadError(f"{field}: требуется число ≥ 1.")
    return number


def nonnegative_decimal(value: Any, *, field: str) -> Decimal:
    try:
        number = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise PayloadError(f"{field}: некорректное количество.") from exc
    if not number.is_finite() or number < 0:
        raise PayloadError(f"{field}: требуется конечное число ≥ 0.")
    return number
```

Для `position` выделите `integer(value, min_value=0)`. Не используйте `int()` как скрытую валидацию в repository.

## 8. Исправить сценарий разморозки для замен и альтернатив

### Проблема

В `resolve_prep_for_recipe()` показатель `used_earlier` ищет код только в исходных `row.container_ids`. Для alternative или `no_leftover` набор реально используемых контейнеров может отличаться. В результате API сообщает, что контейнер уже находится в холодильнике, хотя это не так, или наоборот.

### Правка

Сначала получите эффективные container IDs каждого слота для текущего режима, затем вычисляйте более раннее использование только по ним.

```python
# backend/apps/prep/services/context.py

def effective_container_ids(slot: PrepSlot, *, no_leftover: bool) -> set[str]:
    payload = no_leftover_payload(slot)
    if no_leftover and slot.mode == "reheat" and payload.get("slug"):
        return {str(code) for code in payload.get("container_ids") or []}
    return {str(code) for code in slot.container_ids or []}


def containers_used_before(
    slots: list[PrepSlot],
    *,
    day: int,
    meal: str,
    requested_ids: set[str],
    no_leftover: bool,
) -> dict[str, bool]:
    meal_rank = {"lunch": 0, "dinner": 1}
    current_rank = meal_rank[meal]
    used: set[str] = set()

    for slot in slots:
        is_earlier = slot.day < day or (
            slot.day == day and meal_rank[slot.meal] < current_rank
        )
        if is_earlier:
            used.update(effective_container_ids(slot, no_leftover=no_leftover))

    return {code: code in used for code in requested_ids}
```

Замените текущий цикл `for code in ids: ... any(...)` вызовом `containers_used_before(...)`.

## 9. Объединять shopping только при совместимых единицах

### Проблема

Сейчас два товара с одинаковым `canonical_id`, но единицами `g` и `ml`, будут слиты в одну запись. Даже если это не ожидается в данных, функция должна либо сохранять корректность, либо возвращать понятную ошибку.

### Правка

Используйте ключ `(canonical_id, unit)` и явно сохраняйте поля первой строки. Если по бизнес-правилу у canonical ID всегда одна единица, валидируйте это отдельно и возвращайте ошибку импорта.

```python
# backend/apps/prep/services/leftover.py
from decimal import Decimal


def merge_shopping(base: list[dict], additions: list[dict]) -> list[dict]:
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
```

В API-конвертере сериализуйте Decimal через единый JSON-safe преобразователь.

## 10. Не превращать Decimal в float

### Проблема

`qty_payload()` и `scaling.ratio` возвращают `float`. Для пищевых количеств ошибки часто малы, но они проявляются как артефакты (`0.30000000000000004`) и делают контракт API непредсказуемым.

### Правка

Выберите единый контракт: JSON number с контролируемой строковой конвертацией либо decimal string. Для точных пользовательских количеств предпочтительна строка; поле `display_amount` уже годится для UI, но машинное поле тоже не должно терять точность.

```python
# backend/apps/prep/services/scale.py
from decimal import Decimal
from typing import Any


def decimal_json(value: Decimal) -> int | str:
    if value == value.to_integral_value():
        return int(value)
    return format(value.normalize(), "f")


def qty_payload(qty: Any, unit: str, ratio: Decimal, enabled: bool) -> dict:
    scaled = scale_qty(qty, unit, ratio, enabled)
    return {
        "qty": decimal_json(scaled),
        "unit": unit,
        "display_amount": format_display_amount(scaled, unit),
    }
```

Для ratio используйте `format(ratio.normalize(), "f")` или возвращайте числитель/знаменатель, если фронтенд выполняет дальнейшие точные вычисления.

## 11. Убрать дублирование констант и HTTP-парсинга

### Проблема

Допустимые meal/mode/place повторяются в models, context, graph, validate. Это повышает риск расхождения при добавлении нового режима или при переименовании.

### Правка

Создайте один модуль domain constants и используйте `TextChoices` для Django-моделей.

```python
# backend/apps/prep/constants.py
from django.db import models


class PrepStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    PUBLISHED = "published", "Published"


class PrepMode(models.TextChoices):
    ASSEMBLE = "assemble", "Assemble"
    FINISH = "finish", "Finish"
    REHEAT = "reheat", "Reheat"


class PrepMeal(models.TextChoices):
    LUNCH = "lunch", "Lunch"
    DINNER = "dinner", "Dinner"


class PrepPlace(models.TextChoices):
    FRIDGE = "fridge", "Fridge"
    FREEZER = "freezer", "Freezer"
    PANTRY = "pantry", "Pantry"


MEAL_RANK = {PrepMeal.LUNCH: 0, PrepMeal.DINNER: 1}
```

```python
# models.py
from apps.prep.constants import PrepMeal, PrepMode, PrepPlace, PrepStatus

status = models.CharField(max_length=16, choices=PrepStatus, default=PrepStatus.DRAFT)
meal = models.CharField(max_length=16, choices=PrepMeal)
mode = models.CharField(max_length=16, choices=PrepMode)
place = models.CharField(max_length=16, choices=PrepPlace)
```

Для query-параметров используйте DRF serializer вместо ручного `_int_query()` и разрозненных проверок.

```python
# backend/apps/prep/api/query_serializers.py
from rest_framework import serializers

from apps.prep.constants import PrepMeal


class RecipePrepQuerySerializer(serializers.Serializer):
    prep = serializers.SlugField(required=False)
    day = serializers.IntegerField(required=False, min_value=1, max_value=7)
    meal = serializers.ChoiceField(required=False, choices=PrepMeal.values)
    servings = serializers.DecimalField(required=False, max_digits=8, decimal_places=2)
    no_leftover = serializers.BooleanField(required=False, default=False)

    def validate(self, attrs):
        has_day = "day" in attrs
        has_meal = "meal" in attrs
        if has_day != has_meal:
            raise serializers.ValidationError("Нужны оба day и meal, либо ни одного.")
        if (has_day or has_meal) and not attrs.get("prep"):
            raise serializers.ValidationError("Нужен query prep.")
        return attrs
```

Преобразуйте `ValidationError` serializer в единый API 400 handler, вместо ручного `PrepError` для каждого параметра.

## 12. Разделить context service на небольшие функции

### Проблема

`resolve_prep_for_recipe()` делает почти всё: HTTP-валидацию, поиск набора, выбор слота, режимы замен, расчёт масштаба, разморозку и presentation DTO. Это нарушает SRP, затрудняет модульные тесты и делает регрессии вероятными.

### Правка

Оставьте в public service оркестрацию, а детали вынесите в чистые функции.

```python
# Предлагаемая декомпозиция
parse_recipe_prep_query(request) -> PrepQuery
find_published_kit(slug) -> PrepKit
resolve_slot(kit_data, recipe, day, meal) -> PrepSlot
resolve_slot_variant(slot, recipe, no_leftover) -> ResolvedSlot
resolve_scaling(servings_base, requested) -> Scaling
serialize_resolved_context(...) -> dict
```

Оркестратор должен быть компактным:

```python
def resolve_prep_for_recipe(recipe: Recipe, request: Request) -> dict | None:
    query = parse_recipe_prep_query(request)
    if query is None:
        return None

    kit_data = load_published_kit_data(query.kit_slug)
    slot = resolve_slot(kit_data, recipe, query.day, query.meal)
    resolved = resolve_slot_variant(slot, recipe, no_leftover=query.no_leftover)
    scaling = resolve_scaling(kit_data.kit.servings_base, query.servings)
    return serialize_resolved_context(kit_data, resolved, scaling, query.no_leftover)
```

## 13. Сделать статус импорта явным

### Проблема

`upsert_kit()` всегда записывает `status="published"`. Ошибка в JSON или неполная редактура может немедленно попасть в публичный API после успешной технической валидации.

### Правка

Добавьте `status` в контракт импорта с default `draft`; публикацию вынесите в отдельную административную операцию или явный флаг команды.

```python
# import_prep_kit.py
parser.add_argument(
    "--publish",
    action="store_true",
    help="Опубликовать набор после успешного импорта",
)
```

```python
# importer.py
status = PrepStatus.PUBLISHED if publish else PrepStatus.DRAFT
```

Для обновления уже опубликованного набора безопаснее импортировать draft/revision и публиковать после smoke-проверки API.

## 14. Снизить число запросов при импорте

### Проблема

После удаления данных импорт создаёт компоненты, контейнеры и слоты по одному. На большом наборе это много round-trip запросов.

### Правка

После полной валидации и разрешения внешних ключей формируйте объекты и используйте `bulk_create`. Используйте это только если выбираете стратегию «полная замена графа»; при синхронизации стабильных PK важнее корректный diff.

```python
PrepComponent.objects.bulk_create(component_rows)
PrepContainer.objects.bulk_create(container_rows)
PrepSlot.objects.bulk_create(slot_rows)
```

После `bulk_create` не рассчитывайте на вызов `clean()`, `save()` и signals. Валидация должна завершаться до этой точки, а инварианты — быть защищены DB constraints.

## 15. Добавить тесты на инварианты и query budget

### Обязательные тесты

- `GET /prep-kits/` не выполняет `UPDATE` и не вызывает расчёт nutrition.
- Detail endpoint укладывается в фиксированное число SQL-запросов независимо от числа слотов/контейнеров в разумном диапазоне.
- Нельзя сохранить контейнер, указывающий на компонент другого набора.
- Импорт отвергает `NaN`, `Infinity`, дробное значение в integer-поле, `servings_base <= 0`, `feeds_slots <= 0`.
- `merge_shopping()` не объединяет разные единицы измерения.
- Для alternative/no_leftover корректно считается `used_earlier` и текст разморозки.
- Граф корректно обрабатывает поврежденный `source` без `KeyError` и строит длинную цепочку reheat.
- Импорт draft не делает набор публичным; publish меняет только явно выбранный набор.

Пример проверки отсутствия записи при GET:

```python
from django.test import TestCase
from django.test.utils import CaptureQueriesContext
from django.db import connection


class PrepKitListTests(TestCase):
    def test_list_does_not_write_metrics(self):
        with CaptureQueriesContext(connection) as queries:
            response = self.client.get("/api/prep-kits/")

        self.assertEqual(response.status_code, 200)
        sql = " ".join(query["sql"].upper() for query in queries)
        self.assertNotIn(" UPDATE ", sql)
        self.assertNotIn(" INSERT ", sql)
        self.assertNotIn(" DELETE ", sql)
```

## Рекомендуемый порядок внедрения

1. Сразу убрать запись из serializer и зафиксировать query budget тестами.
2. Вынести константы в `TextChoices`, добавить DB constraints и migration.
3. Ввести `KitData`, перестать повторно обращаться к related managers, переписать `kit_graph` на индекс + BFS.
4. Разделить импорт на нормализацию, чистую валидацию и repository.
5. Выбрать стратегию обновления: diff со стабильными PK либо versioned revisions; после выбора переписать `upsert_kit`.
6. Декомпозировать `resolve_prep_for_recipe` и покрыть режимы alternative/no_leftover тестами.
