# Правки по аудиту `backend/apps/recipes`

## Список проблем

1. Приложение смешивает доменную модель, HTTP parsing, сериализацию API, ETL, поиск, расчёт питания и solver; несколько модулей превратились в монолиты (`etl/draft.py` — 782 строки, `services/solve.py` — 701, `services/assemble.py` — 572, `views.py` — 439).
2. `constants.py` объединяет vocabulary, UI-лейблы, V1-совместимость, import-константы, pantry taxonomy и импорт обратно из `pantry_vocab`; это циклически-хрупкий god-module.
3. `upsert_recipe()` не обёрнут целиком в `transaction.atomic()`: при ошибке после `update_or_create()` или после удаления дочерних объектов рецепт может оказаться частично перезаписанным.
4. `upsert_recipe()` удаляет и заново создаёт ингредиенты, шаги и варианты при каждом импорте: нестабильные PK, лишние запросы, побочные каскады и потеря истории изменений.
5. Импорт автоматически публикует draft: `parse_draft()` задаёт `status="published"`, а `upsert_recipe()` создаёт published revision. Это позволяет незавершённому или ошибочно одобренному контенту немедленно попасть в публичный API.
6. В `upsert_recipe()` `Recipe.full_clean()` вызывается уже после `update_or_create()`, то есть не защищает БД от невалидной промежуточной записи.
7. В моделях и ETL много критичных инвариантов проверяются только Python-кодом; `QuerySet.update`, bulk-операции и прямой SQL их обходят.
8. Валидатор `validate_draft()` слишком большой, изменяет/нормализует значения неявно через `bool()`/`int()`, а часть чисел допускает невалидные значения (`NaN`, бесконечность, дробные значения там, где нужно integer).
9. `bool("false") == True`: использование `bool(raw_value)` в `parse_draft()` приводит к тихой порче данных для `scalable`, `optional`, `is_anchor`, `nutrition_exclude` и `has_delta`.
10. Валидация и parsing вариантов неполны: `parse_draft()` читает только `variants`, хотя validator допускает legacy `variations`; часть JSON-delta структур не валидируется строго до выполнения в assembler.
11. `apply_ingredient_delta()` и `apply_step_delta()` молча игнорируют несуществующие цели `remove`/`replace` и конфликтующие изменения, из-за чего редактор не видит, что вариант фактически не применился.
12. `assemble_recipe()` и представление собранного рецепта совмещают загрузку ORM, выбор осей, применение дельт, аллергенный расчёт, бизнес-правила и DTO; это затрудняет повторное использование и тестирование.
13. `refresh_axis_snapshots()` выполняется синхронно в критическом пути импорта и многократно собирает рецепт; при большом числе вариантов стоимость растёт комбинаторно.
14. Снапшоты осей хранятся в JSON на `Recipe` и могут устареть после изменений ингредиентов, вариантов, времени или справочников; invalidation не выражен явно.
15. Solver строит и анализирует комбинации в Python после загрузки данных, а views содержат значительную часть query orchestration. Это угрожает latency и усложняет контроль query budget.
16. `RecipeListView`/`RecipeDetailView`/`RecommendationListView` и ручные query parsers смешивают HTTP-валидацию с доменной логикой; нет единых DRF serializers для query-параметров.
17. Поиск и фильтрация завязаны на PostgreSQL-специфичные функции и runtime-зависимости, но fallback/план индексации и тесты explain/query-count не зафиксированы.
18. `RecipeRevision` перезаписывается через `update_or_create(recipe, status="published")`, поэтому это не аудит и не история ревизий: старые опубликованные payload теряются.
19. Числа `Decimal` сериализуются в `float` в экспортёре и API-данных масштаба, что вносит ошибки точности.
20. `load_ingredient_nutrition()` делает UPDATE в цикле по одному ingredient, не проверяет конечность Decimal и не формирует отчёт о пропущенных/не найденных canonical_id.
21. В коде присутствуют жёстко заданные ожидаемые количества V1 (`EXPECTED_RECIPE_COUNT`, `EXPECTED_RECIPE_FILES`) и словари/эвристики, привязанные к историческому импорту; они смешаны с runtime-каталогом.
22. `api_exception_handler` из recipes импортирует `PrepError` из другого приложения, создавая обратную зависимость и размывая границы модулей.
23. Нет явно зафиксированной стратегии кэширования и инвалидации для тяжёлых detail/recommendation запросов.
24. Недостаточно тестов на транзакционность импорта, целостность delta, безопасность статусов, query budget, корректность Decimal и invalidation snapshots.

## 1. Разделить приложение по слоям

### Проблема

Текущая структура заставляет один модуль отвечать за несколько независимых задач. Например, `etl/draft.py` одновременно читает JSON, валидирует схему, проверяет доменные правила, нормализует значения и формирует словарь для БД. `views.py` одновременно читает query-параметры, строит queryset, вызывает solver и формирует API-ответы.

### Правка

Не делите код только «по типу файлов» (`services`, `utils`). Выделите явные bounded contexts.

| Пакет | Ответственность |
|---|---|
| `domain/` | enums, dataclasses, чистые инварианты, scale/delta/allergen правила |
| `application/` | use cases: import draft, get detail, search catalog, build recommendations |
| `infrastructure/` | Django ORM repositories, PostgreSQL search, snapshot storage |
| `api/` | DRF views, serializers, pagination, exception mapping |
| `etl/` | чтение legacy V1, draft JSON adapters, management commands |

Целевой поток detail endpoint:

```text
DRF query serializer
    → GetRecipeDetailUseCase
    → RecipeRepository.get_for_detail()
    → RecipeAssembler.assemble()
    → ScalingService.resolve()
    → RecipeDetailPresenter
    → Response
```

Такой разрез устраняет циклические импорты и позволяет unit-тестировать логику без Django/БД.

## 2. Разбить `constants.py`

### Проблема

`constants.py` содержит почти всё: доменные коды, русские лейблы, V1 mapping, expected counts, import aliases, pantry vocabulary и late import из `pantry_vocab`. Изменение справочника может вызвать циклическую зависимость и побочные импорты на старте приложения.

### Правка

Разделите данные по владельцу и назначению.

```text
apps/recipes/domain/enums.py          # RecipeStatus, Unit, CookMethod, ...
apps/recipes/domain/labels_ru.py      # UI labels
apps/recipes/domain/recipe_rules.py   # MAX_VARIANTS, safety rules
apps/recipes/etl/v1_constants.py      # V1 folder/unit mappings, expected fixtures
apps/recipes/pantry/vocabulary.py     # pantry/have/shopping taxonomy
```

Используйте `models.TextChoices` для значений, сохраняемых в БД, и обращайтесь к `.values` в валидаторах.

```python
# apps/recipes/domain/enums.py
from django.db import models


class RecipeStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    IN_REVIEW = "in_review", "In review"
    APPROVED = "approved", "Approved"
    PUBLISHED = "published", "Published"


class CookMethod(models.TextChoices):
    OVEN = "oven", "Oven"
    PAN_FRY = "pan_fry", "Pan fry"
    STEW = "stew", "Stew"
    BOIL = "boil", "Boil"
    GRILL = "grill", "Grill"
    STEAM = "steam", "Steam"
    NO_COOK = "no_cook", "No cook"
    AIR_FRYER = "air_fryer", "Air fryer"
    DEEP_FRY = "deep_fry", "Deep fry"
```

Не импортируйте `pantry_vocab` из общего `constants.py`. Импортируйте его только там, где реально нужен pantry use case.

## 3. Сделать импорт атомарным

### Проблема

Сейчас рецепт обновляется до проверки `full_clean()`, затем удаляются дочерние сущности, после чего идут десятки записей. Любая ошибка в середине оставляет БД в промежуточном состоянии.

### Правка

Весь persistence должен быть в единой транзакции. Валидация draft и разрешение ссылок выполняются до транзакции, запись — внутри неё. Для конкурентного импорта одного slug используйте `select_for_update()`.

```python
# apps/recipes/application/import_recipe.py
from django.db import transaction

from apps.recipes.infrastructure.repositories import RecipeRepository


class ImportRecipeUseCase:
    def __init__(self, repository: RecipeRepository):
        self.repository = repository

    def execute(self, draft, *, publish: bool = False):
        draft.validate_for_persistence()

        with transaction.atomic():
            recipe = self.repository.lock_or_create(slug=draft.slug)
            self.repository.apply_recipe_fields(recipe, draft, publish=publish)
            self.repository.sync_ingredients(recipe, draft.lines)
            self.repository.sync_steps(recipe, draft.steps)
            self.repository.sync_variants(recipe, draft.variants)
            self.repository.create_revision(recipe, draft)
            self.repository.mark_snapshot_stale(recipe)

        return recipe
```

Никогда не выполняйте часть sync до `atomic()`. Не запускайте тяжёлую пересборку snapshot внутри этой транзакции.

## 4. Не публиковать из draft по умолчанию

### Проблема

`parse_draft()` устанавливает `status="published"`, а `upsert_recipe()` создаёт revision со status `published`. Это делает публикацию побочным эффектом парсинга файла.

### Правка

Разделите импорт, review и публикацию. По умолчанию импортируйте в `draft` или `in_review`. Публичные views должны фильтровать только `published`.

```python
# domain/enums.py
class RecipeStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    IN_REVIEW = "in_review", "In review"
    APPROVED = "approved", "Approved"
    PUBLISHED = "published", "Published"
```

```python
# etl/draft.py
# Не возвращайте status="published" из parse_draft.
"status": RecipeStatus.DRAFT,
```

```python
# management/commands/import_draft.py
parser.add_argument(
    "--publish",
    action="store_true",
    help="Опубликовать рецепт после успешного импорта и проверок",
)
```

Публикацию лучше реализовать отдельной командой/административным action, который проверяет: revision одобрен, рецепт собирается, отсутствуют критичные предупреждения, snapshots актуальны.

## 5. Заменить destructive update на синхронизацию

### Проблема

Код:

```python
RecipeIngredient.objects.filter(recipe=recipe).delete()
RecipeStep.objects.filter(recipe=recipe).delete()
RecipeVariant.objects.filter(recipe=recipe).delete()
```

создаёт лишние DELETE/INSERT, меняет идентификаторы, ломает потенциальные ссылки и затрудняет аудит.

### Правка

Синхронизируйте дочерние сущности по естественным ключам:

- `RecipeIngredient`: `(recipe, position)` или отдельный стабильный `line_id` в draft;
- `RecipeStep`: `(recipe, position)` или стабильный `step_id`;
- `RecipeVariant`: `(recipe, code)`.

Для контента, который часто переупорядочивается, лучше ввести UUID `external_id` в JSON и в модели. Позиция остаётся только сортировкой, а не идентичностью.

```python
# пример: sync variants по коду

def sync_variants(recipe: Recipe, drafts: list[VariantDraft]) -> None:
    existing = {variant.code: variant for variant in recipe.variants.all()}
    expected_codes = {draft.code for draft in drafts}

    recipe.variants.exclude(code__in=expected_codes).delete()

    for draft in drafts:
        values = draft.to_model_values()
        variant = existing.get(draft.code)
        if variant is None:
            RecipeVariant.objects.create(recipe=recipe, code=draft.code, **values)
            continue
        for field, value in values.items():
            setattr(variant, field, value)
        variant.full_clean()
        variant.save(update_fields=list(values))
```

Если исторические PK не нужны принципиально, это должно быть явным решением: используйте immutable `RecipeRevision` и связывайте опубликованный рецепт с ревизией, а не подменяйте граф в строке Recipe.

## 6. Валидация до записи и ограничения БД

### Проблема

`full_clean()` после `update_or_create()` не предотвращает запись невалидного объекта. Кроме того, он не вызывается при `bulk_create`, `update` и прямом SQL.

### Правка

1. Валидируйте typed draft до persistence.
2. Вызывайте `full_clean()` до `save()` для объектов, создаваемых по одному.
3. Для числовых и уникальных инвариантов добавьте `CheckConstraint` / `UniqueConstraint`.
4. Для сложных JSON инвариантов оставьте application validation и обязательные тесты.

Пример важных DB constraints:

```python
# apps/recipes/models.py
from django.db.models import Q

class Recipe(models.Model):
    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=Q(servings__isnull=True) | Q(servings__gte=1),
                name="recipe_servings_positive",
            ),
            models.CheckConstraint(
                condition=Q(yield_weight_g__isnull=True) | Q(yield_weight_g__gt=0),
                name="recipe_yield_weight_positive",
            ),
            models.CheckConstraint(
                condition=Q(time_total_minutes__isnull=True) | Q(time_total_minutes__gte=1),
                name="recipe_total_time_positive",
            ),
            models.CheckConstraint(
                condition=Q(time_active_minutes__isnull=True) | Q(time_active_minutes__gte=0),
                name="recipe_active_time_nonnegative",
            ),
            models.CheckConstraint(
                condition=Q(time_total_minutes__isnull=True)
                | Q(time_active_minutes__isnull=True)
                | Q(time_active_minutes__lte=models.F("time_total_minutes")),
                name="recipe_active_time_not_greater_total",
            ),
        ]


class RecipeIngredient(models.Model):
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["recipe", "position"],
                name="recipe_ingredient_position_unique",
            ),
            models.CheckConstraint(
                condition=Q(amount__isnull=True) | Q(amount__gte=0),
                name="recipe_ingredient_amount_nonnegative",
            ),
            models.CheckConstraint(
                condition=Q(amount_max__isnull=True) | Q(amount_max__gte=0),
                name="recipe_ingredient_amount_max_nonnegative",
            ),
        ]
```

Перед миграцией выполните аудит текущих записей: `CheckConstraint` не должен неожиданно упасть на уже существующих данных.

## 7. Устранить опасные bool/int-преобразования

### Проблема

В Python `bool("false")` и `bool("0")` равны `True`. Сейчас это может включить масштабирование, сделать строку обязательной/якорной или активировать delta несмотря на значение из JSON.

### Правка

В парсере не применяйте `bool(value)` к внешнему вводу. Используйте строгий нормализатор.

```python
# apps/recipes/etl/normalizers.py
from __future__ import annotations

from typing import Any


class DraftValidationError(ValueError):
    pass


def as_bool(value: Any, *, field: str, default: bool | None = None) -> bool:
    if value is None:
        if default is None:
            raise DraftValidationError(f"{field}: требуется boolean")
        return default
    if isinstance(value, bool):
        return value
    raise DraftValidationError(f"{field}: требуется true или false")


def as_int(
    value: Any,
    *,
    field: str,
    min_value: int | None = None,
    nullable: bool = False,
) -> int | None:
    if value is None and nullable:
        return None
    if isinstance(value, bool):
        raise DraftValidationError(f"{field}: требуется integer")
    if not isinstance(value, int):
        raise DraftValidationError(f"{field}: требуется integer")
    if min_value is not None and value < min_value:
        raise DraftValidationError(f"{field}: значение должно быть ≥ {min_value}")
    return value
```

Для JSON authors лучше требовать реальные JSON boolean/number, а не принимать строки. Это резко уменьшает неявные трансформации и делает ошибки воспроизводимыми.

## 8. Разделить draft schema, нормализацию и бизнес-валидацию

### Проблема

`validate_draft()` содержит сотни веток и одновременно выполняет проверку схемы, safety rules, legacy compatibility и сверку с registry. Такой код трудно читать и невозможно уверенно менять без регрессий.

### Правка

Разделите этапы:

```text
load JSON
  → DraftSchema.parse(raw)          # типы, обязательные поля, неизвестные поля
  → normalize_draft(schema)         # Decimal, defaults, canonical ordering
  → validate_recipe_rules(draft)    # anchor, safety temperature, time profile
  → validate_variant_rules(draft)   # axis and delta contracts
  → validate_registry(draft, repo)  # Ingredient/recipe references
  → persist(draft)
```

Используйте Pydantic/DRF serializer/dataclass schema только в одном адаптере. Доменные валидаторы должны принимать typed dataclass, а не `dict[str, Any]`.

```python
@dataclass(frozen=True, slots=True)
class IngredientLineDraft:
    canonical_id: str
    position: int
    amount: Decimal | None
    amount_max: Decimal | None
    unit: Unit
    scalable: bool
    scale_mode: ScaleMode
    is_anchor: bool
    optional: bool

@dataclass(frozen=True, slots=True)
class RecipeDraft:
    slug: str
    title: str
    protein_base: ProteinBase
    cook_method: CookMethod
    lines: tuple[IngredientLineDraft, ...]
    steps: tuple[StepDraft, ...]
    variants: tuple[VariantDraft, ...]
```

## 9. Сделать delta-операции строгими и чистыми

### Проблема

В assembler невалидные `remove`/`replace` могут быть проигнорированы: если цель не найдена, алгоритм продолжает работу. Это порождает «успешный» вариант, который на деле не изменил рецепт. Конфликты (двойной replace одной линии, удаление и replace одной цели) также не явны.

### Правка

Сначала валидируйте delta against base lines/steps, затем применяйте. При отсутствии цели или конфликте выбрасывайте доменную ошибку с кодом и путём JSON.

```python
# apps/recipes/domain/delta.py
class DeltaConflict(ValueError):
    pass


def require_line_index(lines: list[dict], spec: dict, *, action: str) -> int:
    matches = find_matching_line_indexes(lines, spec)
    if not matches:
        raise DeltaConflict(f"{action}: target ingredient не найден")
    if len(matches) > 1:
        raise DeltaConflict(f"{action}: target ingredient неоднозначен")
    return matches[0]


def validate_ingredient_delta(base_lines: list[dict], delta: IngredientDelta) -> None:
    touched: set[int] = set()
    for action, specs in (("remove", delta.remove), ("replace", delta.replace)):
        for spec in specs:
            index = require_line_index(base_lines, spec, action=action)
            if index in touched:
                raise DeltaConflict(f"{action}: линия изменяется более одного раза")
            touched.add(index)
```

Не используйте `position` как единственный selector, если позиции могут меняться. Введите `line_id`/UUID для адресации в delta.

## 10. Упростить assembler через явный read model

### Проблема

`assemble_recipe()` знает и о Django related managers, и о domain delta, и о nutrition enrichment. Это создаёт неявные запросы и делает assembler сложно тестируемым.

### Правка

Сначала создайте immutable snapshot рецепта из ORM, затем собирайте его без доступа к БД.

```python
@dataclass(frozen=True, slots=True)
class RecipeReadModel:
    slug: str
    protein_base: str
    cook_method: str
    equipment: str | None
    ingredients: tuple[IngredientLine, ...]
    steps: tuple[RecipeStepData, ...]
    variants: tuple[VariantData, ...]
    allergens: AllergenSet


def build_read_model(recipe: Recipe) -> RecipeReadModel:
    # Repository обязан prefetch_related/select_related заранее.
    ...


def assemble(read_model: RecipeReadModel, selection: VariantSelection) -> AssembledRecipe:
    # Только чистая логика, без ORM/queries.
    ...
```

Nutrition enrichment вынесите в отдельный шаг `NutritionService.project(assembled)`; он не должен быть скрытым эффектом `assemble_recipe()`.

## 11. Сделать snapshots асинхронными и версионированными

### Проблема

`refresh_axis_snapshots(recipe)` вызывается синхронно после каждого upsert и перебирает комбинации осей. Снапшоты могут устареть, но в модели нет версии входных данных или статуса актуальности.

### Правка

Добавьте версию рецепта и состояние снимков. Сначала сохраните новую revision, затем поставьте фоновую задачу после commit.

```python
# models.py
class Recipe(models.Model):
    content_version = models.PositiveIntegerField(default=1)
    snapshot_version = models.PositiveIntegerField(default=0)
    snapshots_updated_at = models.DateTimeField(null=True, blank=True)
```

```python
# application/import_recipe.py
from django.db import transaction

# после sync
recipe.content_version = F("content_version") + 1
recipe.save(update_fields=["content_version"])
transaction.on_commit(lambda: rebuild_recipe_snapshots.delay(recipe.pk))
```

Worker должен:

1. Загрузить рецепт с полным graph prefetch.
2. Собрать snapshot для текущего `content_version`.
3. Записать его только если версия не изменилась во время выполнения.
4. Выставить `snapshot_version = content_version`.

Recommendation endpoint должен либо исключать stale snapshots, либо выполнять controlled fallback и явно сигнализировать деградацию в логах/метриках.

## 12. Сохранить настоящую историю ревизий

### Проблема

`RecipeRevision.objects.update_or_create(recipe=recipe, status="published")` оставляет максимум одну revision указанного статуса. Это противоречит названию модели и лишает возможности rollback/audit.

### Правка

Ревизия должна быть append-only и иметь номер/хеш payload. Рецепт хранит ссылку на текущую опубликованную ревизию либо версию.

```python
class RecipeRevision(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name="revisions")
    number = models.PositiveIntegerField()
    status = models.CharField(max_length=16, choices=RevisionStatus)
    payload_json = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["recipe", "number"],
                name="recipe_revision_number_unique",
            ),
        ]
```

Создание revision выполняйте через `RecipeRevision.objects.create(...)`, а не `update_or_create`. Для идемпотентного импорта используйте `payload_hash` и не создавайте новую revision, если содержимое не изменилось.

## 13. Убрать float из точных чисел

### Проблема

Экспорт draft и API преобразуют `Decimal` в `float`; например, 0.1 и 0.3 становятся бинарными приближениями. Это вызывает ложные diffs в экспортированных JSON и ошибки на клиенте.

### Правка

Для authored draft JSON используйте строки Decimal. Для API либо используйте строки, либо JSON number, построенный контролируемым decimal encoder, но не `float()`.

```python
from decimal import Decimal


def decimal_json(value: Decimal | None) -> int | str | None:
    if value is None:
        return None
    if value == value.to_integral_value():
        return int(value)
    return format(value.normalize(), "f")
```

Примените один helper во всех местах: `etl/serialize.py`, `serializers.py`, `services/nutrition.py`, `services/scale.py`, `prep` serializers. Контракт должен быть одинаковым во всём API.

## 14. Оптимизировать питание и ingredient registry

### Проблема

`load_ingredient_nutrition()` делает отдельный `UPDATE` для каждого cid, допускает `NaN`/Infinity через `Decimal`, не сообщает об отсутствующих ингредиентах и не проверяет диапазоны макронутриентов.

### Правка

Валидируйте seed полностью до обновления БД и применяйте изменения пакетно. Сначала соберите список валидных typed rows; если есть ошибки — не обновляйте ничего.

```python
from decimal import Decimal


def finite_nonnegative(value: object, *, field: str) -> Decimal:
    number = Decimal(str(value))
    if not number.is_finite() or number < 0:
        raise ValueError(f"{field}: нужно конечное значение ≥ 0")
    return number
```

Затем одним запросом найдите существующие `canonical_id`, сформируйте отчёт `updated`, `not_found`, `invalid`, и используйте `bulk_update` пакетами.

```python
rows = list(Ingredient.objects.filter(canonical_id__in=seed_ids))
# mutate rows only after complete seed validation
Ingredient.objects.bulk_update(rows, nutrition_fields, batch_size=500)
```

Не затирайте вручную отредактированные nutrition values без явного флага `--force` или стратегии приоритета источников.

## 15. Вынести query parsing в DRF serializers

### Проблема

`query.py` вручную читает `request.query_params`; views и сервисы затем повторно интерпретируют результаты. Ошибки разных query-параметров имеют разные форматы, а логика `have`, `intent`, `allergens`, `sample`, `servings`, осей и pagination расползается по нескольким модулям.

### Правка

Определите request serializer на каждый endpoint. Он должен преобразовать HTTP-ввод в typed query object и вернуть стандартный DRF 400.

```python
# apps/recipes/api/query_serializers.py
from rest_framework import serializers

class RecipeDetailQuerySerializer(serializers.Serializer):
    variant = serializers.SlugField(required=False)
    equipment = serializers.SlugField(required=False)
    servings = serializers.DecimalField(
        required=False,
        max_digits=8,
        decimal_places=2,
        min_value=1,
    )

class RecommendationQuerySerializer(serializers.Serializer):
    have = serializers.ListField(
        child=serializers.CharField(), required=False, default=list
    )
    have_group = serializers.ListField(
        child=serializers.CharField(), required=False, default=list
    )
    intent = serializers.ListField(
        child=serializers.CharField(), required=False, default=list
    )
    without_allergen = serializers.ListField(
        child=serializers.CharField(), required=False, default=list
    )
    sample = serializers.IntegerField(required=False, min_value=1, max_value=100)
```

Нормализация запятых/повторяющихся ключей остаётся в custom field. После `serializer.is_valid(raise_exception=True)` application layer не должен получать `request`.

## 16. Снизить сложность solver и защитить latency

### Проблема

`services/solve.py` имеет 701 строку, строит комбинации вариантов и проводит ranking в Python. Без лимитов на комбинации, query count и размер входа endpoint может деградировать при росте каталога или количества вариантов.

### Правка

Разделите solver на независимые чистые стадии:

```text
CandidateQueryBuilder → CandidateRepository → VariantCombinationGenerator
→ EligibilityFilter → PantryMatcher → Scorer → BucketAssigner → Presenter
```

Обязательные ограничения:

- Ограничьте число вариантов/комбинаций на один рецепт на уровне domain policy.
- Загружайте только поля, необходимые для карточки/снапшота (`only`, `values`, annotation).
- Фильтруйте status, аллергенные запреты, dish type и базовые intent constraints в SQL до Python ranking.
- Используйте предрассчитанные snapshots только при `snapshot_version == content_version`.
- Зафиксируйте верхнюю границу кандидатов перед Python scoring (`MAX_CANDIDATES`).
- Добавьте telemetry: число кандидатов, число комбинаций, время каждой стадии, fallback snapshot.

Не оптимизируйте «на глаз»: добавьте benchmark fixture с худшим реалистичным каталогом и test budget на число SQL-запросов.

## 17. Поиск PostgreSQL: индексы, fallback и контракт

### Проблема

Поиск использует PostgreSQL-специфичные `NormalizeRu`, `ToTsVector`, trigram similarity. Это нормально для production Postgres, но без миграций расширений/индексов, минимальной длины query и fallback он становится источником ошибок и медленных запросов.

### Правка

- В migration явно включите необходимые расширения (`pg_trgm`, при необходимости `unaccent`).
- Добавьте GIN индекс на `search_vector` и GIN/GiST trigram index на нормализованные текстовые поля в соответствии с реальным запросом.
- В `apply_catalog_search()` возвращайте queryset без similarity при пустом/коротком запросе.
- В API ограничьте длину query и экранируйте пользовательский ввод через Django expressions, а не raw SQL.
- Добавьте integration tests под PostgreSQL и отдельный fallback/skip для SQLite unit tests.

Пример migration-идеи:

```python
from django.contrib.postgres.indexes import GinIndex
from django.db import migrations

class Migration(migrations.Migration):
    operations = [
        migrations.RunSQL("CREATE EXTENSION IF NOT EXISTS pg_trgm"),
        migrations.AddIndex(
            model_name="recipe",
            index=GinIndex(fields=["search_vector"], name="recipe_search_vector_gin"),
        ),
    ]
```

Проверьте план `EXPLAIN (ANALYZE, BUFFERS)` на production-like данных: наличие индекса само по себе не гарантирует, что PostgreSQL его выберет.

## 18. Убрать cross-app исключение

### Проблема

`apps.recipes.exceptions` импортирует `PrepError` из `apps.prep.exceptions`. Базовое recipes-приложение теперь знает о prep, хотя prep уже зависит от recipes. Это создаёт цикл уровня архитектуры.

### Правка

Вынесите API-ошибки в общий модуль, например `apps.core.exceptions`, либо используйте стандартный `rest_framework.exceptions.ValidationError` непосредственно в API boundary.

```python
# apps/core/exceptions.py
class DomainValidationError(Exception):
    """Ошибка доменного use case, преобразуемая в HTTP 400 в API boundary."""
```

```python
# apps/core/api/exceptions.py
from rest_framework.response import Response
from rest_framework.views import exception_handler

from apps.core.exceptions import DomainValidationError


def api_exception_handler(exc, context):
    if isinstance(exc, DomainValidationError):
        return Response({"detail": str(exc)}, status=400)
    return exception_handler(exc, context)
```

`PrepError`, `VariantError`, `ScaleConflict` должны наследоваться от этой общей ошибки или быть преобразованы в неё application layer.

## 19. Кэширование и инвалидация

### Проблема

Detail endpoint выполняет сборку варианта, расчёт масштаба и nutrition; recommendation endpoint может запускать solver. Без стратегии кэширования одинаковые запросы повторяют одинаковую работу.

### Правка

Кэшировать нужно именно результат стабильного use case, с ключом, включающим версию контента и все параметры, влияющие на ответ.

```text
recipe-detail:{slug}:v{content_version}:variant={variant}:equipment={equipment}:servings={servings}
recommendations:v{catalog_version}:have={hash}:intent={hash}:without={hash}
```

- Деталь рецепта можно кэшировать коротко (например, 5–15 минут) и инвалидировать по `content_version`.
- Recommendation кэшируйте только после измерений и ограничьте TTL; не кэшируйте большие персональные наборы без размера/лимита.
- Валидация/публикация должны делать invalidation через `transaction.on_commit()`.
- Добавьте HTTP `ETag`/`Last-Modified` для public recipe detail.

## 20. Обязательные тесты

### Импорт и транзакции

- Ошибка на создании второго шага откатывает изменение Recipe и все дочерние сущности.
- Неудачный draft не создаёт ни Recipe, ни Ingredient, ни Revision.
- По умолчанию import создаёт `draft`/`in_review`; published появляется только через явную публикацию.
- Повторный импорт идентичного payload не создаёт новую revision.
- Изменённый payload создаёт следующую revision, не перезаписывая предыдущую.

### Валидация и данные

- Значения `"false"`, `"0"`, `1`, `0` в boolean-полях отвергаются, если контракт требует JSON boolean.
- `Decimal("NaN")`, `Decimal("Infinity")`, отрицательные amount и неверные integer-поля отвергаются.
- Delta с отсутствующей целью, двойным replace или remove+replace одной линии завершается понятной ошибкой.
- Variant из legacy `variations` либо нормализуется до `variants`, либо отклоняется единообразно.
- Все constraints проверяются на уровне БД через `IntegrityError`/migration tests.

### Сборка и снапшоты

- Assembler работает только с read model и не выполняет SQL.
- Изменение ингредиента/варианта увеличивает `content_version` и делает snapshot stale.
- Worker не перезаписывает snapshot, если content version изменилась во время расчёта.
- Recommendation не использует stale snapshot как актуальный.

### API и производительность

- Detail endpoint имеет фиксированный query budget с несколькими ингредиентами, шагами и вариантами.
- Catalog/list endpoint не имеет N+1 при сериализации ingredient titles, variants и аллергенов.
- Recommendation ограничивает число кандидатов/combos и укладывается в установленный budget на worst-case fixture.
- GET endpoints не содержат `INSERT`, `UPDATE`, `DELETE`.
- Поиск проверяется integration-тестом на PostgreSQL с индексами и пустым/коротким query.

## Рекомендуемый порядок внедрения

1. Сначала закрыть риски данных: `transaction.atomic`, запрет автопубликации, строгий boolean/number parsing, DB constraints и тесты отката.
2. Убрать destructive update либо осознанно перейти на immutable revisions с настоящей историей.
3. Разделить `constants.py`, вынести cross-app исключения в `core`, зафиксировать dependency direction.
4. Разбить `draft.py` на schema → normalize → domain validation → repository; параллельно сделать delta validation строгой.
5. Ввести read model и чистый assembler; вынести nutrition enrichment.
6. Добавить versioned/stale snapshots и перенести rebuild в фоновую задачу после commit.
7. Декомпозировать solver/views, внедрить DRF query serializers, candidate limits, telemetry и query-budget tests.
8. Только после измерений добавить result caching и PostgreSQL index tuning.
