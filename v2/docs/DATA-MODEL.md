# Модель данных 2.0

Контракт схемы. Коды полей — [VOCAB.md](VOCAB.md). Safety-инварианты — [SAFETY.md](SAFETY.md). Числа — [DEFAULTS.md](DEFAULTS.md). HTTP — [API.md](API.md). Задача сессии — [../CURRENT_SPRINT.md](../CURRENT_SPRINT.md).

Агент не выдумывает поля «на будущее», кроме явно помеченных *позже*.

## Приложения Django

| App | Модели |
|-----|--------|
| `recipes` | `Recipe`, `RecipeVariant`, `RecipeRevision`, `Ingredient`, `RecipeIngredient`, `RecipeStep`, `SubstitutionRule` |
| `content` | `ContentDocument` |

Сессии Django — в Postgres (не Redis). Аккаунты, кладовка, комментарии — не в срезе.

## `Recipe` — живая карточка

Каталог, фильтры и FTS читают **эту** таблицу, без JOIN к последней ревизии.

История — в `RecipeRevision`. Срез 1: ETL пишет `Recipe` + одну ревизию `published`. Статусы `draft` / `in_review` / `approved` в UI среза не показываются.

| Поле | Тип | Null | Смысл |
|------|-----|------|--------|
| `id` | PK | нет | внутренний |
| `slug` | slug, unique | нет | URL `/recipes/<slug>`; из V1 `id` |
| `title` | text | нет | заголовок |
| `protein_base` | VOCAB | нет | основа блюда |
| `cook_method` | VOCAB | нет | способ |
| `dish_type` | VOCAB | нет | роль на столе |
| `scale_mode` | enum | нет | дефолт рецепта; строка ингредиента может переопределить |
| `scalable` | bool | нет | `false` = количества не меняются |
| `servings` | positive int | да | база порций; в V1 у всех `NULL` |
| `summary` | text | да | лид |
| `source_name` | text | да | |
| `source_url` | URL | да | |
| `source_type` | text | да | `video` / `article` / … |
| `editorial_tested` | bool | нет | только человек; ETL: `false` |
| `high_risk_flags` | array of VOCAB | нет | пустой = нет флага |
| `caution_text` | text | да | обязателен, если есть high-risk |
| `energy_profile` | VOCAB | нет | дефолт оси energy; спринт 2 UI калоража нет; ETL: `standard` |
| `equipment` | VOCAB | да | дефолтная посуда базы; `NULL` если сосуда нет (`no_cook`) |
| `allowed_cuts` | VOCAB[] | нет | допустимые отрубы блюда; ETL V1: `[]` |
| `notes` | JSON list | нет | `[{ "title": string\|null, "text": string }, ...]`; не blob |
| `prep` | JSON list | нет | напоминания «Заранее»: `[{ "text": string, "before_min"?: int, "before_hours"?: int }]`. Нет предварительных действий — **ключа нет**, в БД `[]`. Пустой `[]` в JSON автора запрещён |
| `time_total_minutes` | positive int | да | стена до готовности, не сумма таймеров шагов. ETL V1: `NULL` |
| `time_active_minutes` | int | да | у плиты / руками. Не больше `time_total_minutes`. ETL V1: `NULL` |
| `effort_level` | 1–5 | да | сложность приёма, не калораж. ETL V1: `NULL` |
| `washing_level` | 1–5 | да | посуда и мойка. ETL V1: `NULL` |
| `use_cases` | VOCAB[] | нет | факторы решения калькулятора (`fast` `easy` `pantry` `one_pan` `batch` `budget` `light`). Не теги V1. ETL V1: `[]` |
| `adaptations` | JSON list | нет | разрешённые операции калькулятора, не чипы. `{type, from/to или ingredient, quality?}`. Типы: `substitution` `omission` `equipment` `method`. Пустой = нет разрешённых. ETL V1: `[]` |
| `status` | enum | нет | срез: `published` |
| `search_vector` | generated tsvector | — | см. «Поиск» |
| `updated_at` | timestamptz | нет | |

Нет поля `scalable_rule`. Нет колонки `variations` на `Recipe` (это `RecipeVariant`). Нет `scale_mode=fixed`.

Карточка 2.0 — три уровня, не квота вариантов:

- **A (обязательный):** id, title, summary, оси VOCAB, equipment, ingredients, steps, scale_mode/scalable, safety, provenance.
- **B (профиль):** `time_*`, `effort_level`, `washing_level`, `use_cases`. У оверлея обязателен. Таймеры шагов профиль не заменяют.
- **C (адаптивность):** `variants` 0–10 и `adaptations` только если есть реальная альтернатива или разрешённая операция. Не заполнять ради числа.

`energy_profile` — только калоражная ось (`standard` / написанный `light`/`rich`). Не решать через него «быстро / просто / мало посуды».

Вариант ≠ адаптация. Variant — редакционная версия блюда (чип, дельта состава). Adaptation — заранее разрешённая операция движка; runtime не фантазирует «наверное можно в духовке».

`new_ingredients` в JSON автора — **заявка** на канон, не второй реестр. После регистрации в `Ingredient` блок из утверждённого рецепта исчезает. Аллергены строки рецепта не источник истины — только таблица `Ingredient`.

### Инварианты рецепта

- `scalable=false` → query `servings` / `anchor_weight` не меняют количества.
- `servings IS NULL` и нет строки `is_anchor=true` **после сборки варианта** → масштабирование выключено. ETL **не** подставляет 4 порции.
- High-risk без `caution_text` → нельзя `published`. Вариант с флагом и `published` → `caution_text` базы или `caution_text_override`.
- `editorial_tested` агент не ставит.
- После сборки **не больше одной** строки `is_anchor=true`.
- Одно блюдо = один `slug`. Нет `family_id`.

## `RecipeVariant` — дельта оси

Не второй рецепт. Чип на странице меняет display-состав. Unique: `(recipe, axis, code)`.

| Поле | Тип | Null | Смысл |
|------|-----|------|--------|
| `recipe` | FK | нет | |
| `axis` | enum | нет | `addon` \| `equipment` \| `energy` |
| `code` | slug | нет | ключ query (`with_mushrooms`, `kazan`, `light`) |
| `title` | text | нет | русская подпись чипа |
| `has_delta` | bool | нет | `false` = только `legacy_text`, состав не врать |
| `legacy_text` | text | да | V1 `variations[].text` |
| `ingredient_delta` | JSON | да | `add` / `remove` / `replace`; обязателен `allergen_delta`, если не null |
| `step_delta` | JSON | да | `replace` по `position`; `insert` после `after_position` (0 = перед первым). **`remove` шага нет** в спринте 2 |
| `allergen_delta` | JSON | да | `contains_add/remove`, `may_contain_*`, `unknown_*` |
| `high_risk_delta` | JSON | нет | `{ "add": [], "remove": [] }` |
| `cook_method_override` | VOCAB | да | ось equipment, если метод тоже меняется |
| `equipment` | VOCAB | да | только `axis=equipment` |
| `caution_text_override` | text | да | |

Ось `addon`: взаимоисключающие чипы (база или ровно один `code`). Комбинации «грибы и пармезан» нет. Ось `energy`: `code` ∈ `light`\|`rich`; в спринте 2 query `energy=` **не принимать** (HUMAN 2.13, UI не в спринте).

`ingredient_delta.add[]` — те же поля, что у `RecipeIngredient` (без FK: `canonical_id`). `remove` / `replace` — `canonical_id` если уникален в базе, иначе `position`.

Якорь: флаг на **базовом** теле. Добавки якорь не ставят. `replace` якорной строки **наследует** якорь, если вариант явно не снял. Свой якорь у варианта — только если заменяет якорный продукт.

### Сборка display (Django, не Next)

Порядок: база → дельта `variant` (если `has_delta`) → дельта `equipment` (если не дефолт базы) → дельта `energy` (если когда-нибудь примут query) → **затем** `servings` XOR `anchor_weight`. `ratio` от уже собранного якоря.

`has_delta=false`: состав базы, `legacy_text` только для блока «Вариации». Нельзя отдать те же ингредиенты под видом выбранного чипа с дельтой.

Аллергены display = каноны строк после сборки; валидатор: совпадение с «база ⊕ allergen_delta». `unknown` не становится «нет». High-risk display = база ∪ add ∖ remove.

Таймеры и температуры не умножаются. `gentle` = `ratio^0.7`.

## `RecipeRevision`

Неизменяемый снимок на момент смены статуса (`draft → in_review → approved → published`).

| Поле | Тип | Смысл |
|------|-----|--------|
| `recipe` | FK | |
| `payload_json` | JSON | полный объект на тот момент |
| `status` | enum | статус этой ревизии |
| `created_at` | timestamptz | |

В срезе нужна, чтобы не переписывать модель на V2.1. Каталог её не джойнит.

## `Ingredient` — канон

Источник правды аллергена — эта таблица, не подстрока в рецепте и не копия `allergens_*` в каждом JSON. Оверлей ссылается `canonical_id`. `new_ingredients` — заявка: канона нет → зарегистрировать здесь → убрать блок из утверждённого файла.

| Поле | Тип | Null | Смысл |
|------|-----|------|--------|
| `id` | PK | нет | |
| `canonical_id` | slug, unique | нет | стабильный ключ (`cow_milk`, `wheat_flour`) |
| `title` | text | нет | русское имя для UI |
| `aliases` | text[] | нет | ё/е и синонимы для матчинга |
| `density_g_per_ml` | decimal | да | нет плотности → кладовка сравнивает факт наличия |
| `allergens_contains` | VOCAB[] | нет | 14 кодов; пустой = не содержит известных |
| `allergens_may_contain` | VOCAB[] | нет | следы, только если явно |
| `allergens_unknown` | VOCAB[] | нет | нельзя трактовать как «нет» |

V1-имена (`"сливки"`, `"муки"`) **не** пишутся в `title` как попало: ETL резолвит строку V1 → `canonical_id` через сид-словарь (см. ETL).

## `SubstitutionRule` — граф замен

Не второй рецепт. Калькулятор подставляет `to`, если `from` нет в `have=`. Runtime LLM нет.

| Поле | Тип | Null | Смысл |
|------|-----|------|--------|
| `from_ingredient` | FK `Ingredient` | нет | чего нет |
| `to_ingredient` | FK `Ingredient` | нет | чем закрыть |
| `recipe` | FK `Recipe` | да | `NULL` = глобально; иначе только это блюдо |
| `quality` | decimal 0.00–1.00 | нет | 1 = почти то же; порог отсечения — DEFAULTS |
| `forbidden` | bool | нет | даже при высоком quality не применять |
| `note` | text | нет | для модератора, не UI |

Unique: пара from/to глобально (`recipe IS NULL`); пара from/to внутри одного рецепта. Рецептное правило бьёт глобальное. `quality` ниже порога — как отсутствие правила. Сид: `fixtures/substitution_rules.json`. Нет канона в БД — строку сида пропустить.

## `RecipeIngredient`

| Поле | Тип | Null | Смысл |
|------|-----|------|--------|
| `recipe` | FK | нет | |
| `ingredient` | FK | нет | канон |
| `position` | int | нет | порядок в списке |
| `amount` | decimal(8,2) | **да** | `NULL` для `to_taste` / `pinch` / строк без числа |
| `amount_max` | decimal(8,2) | да | верх диапазона V1 (`2.5–3 кг`) |
| `unit` | VOCAB | нет | |
| `detail` | text | да | «нарезать кубиком» |
| `scale_mode` | enum | нет | `linear` \| `gentle` \| `whole` \| `manual` |
| `scalable` | bool | нет | `false` → amount не меняется; `scale_mode` игнорируется |
| `is_anchor` | bool | нет | якорь «У меня»; **≤ 1** на рецепт |
| `optional` | bool | нет | `true` = не обязателен для блюда («для подачи», «по желанию»); в аллергенах карточки не участвует |
| `choice_group` | text | да | «A или B» |
| `display_name` | text | да | как в V1, если отличается от канона |

`unit` ∈ `to_taste` \| `pinch` → `amount` должен быть `NULL`, `scalable=false`.

### Якорь

V1 **не** хранит флаг якоря. Эвристика V1 (`findScaleAnchor`): первый `scalable` ингредиент с единицей г/мл/кг/л.

ETL один раз проставляет `is_anchor=true` той строке. Дальше система не угадывает.

`base_anchor` — не колонка, а свойство: `amount` якоря, приведённый к г или мл (`кг`×1000, `л`×1000). `ratio = target_anchor / base_anchor`.

Проверка: в рецепте не больше одной строки с `is_anchor=true`. Ноль якорей при `servings IS NULL` — норма (масштаб выключен). Срез V1: 34 якоря г/мл, 4 рецепта без масштаба.

## `RecipeStep`

| Поле | Тип | Null | Смысл |
|------|-----|------|--------|
| `recipe` | FK | нет | |
| `position` | int | нет | |
| `text` | text | нет | |
| `timer_seconds` | int | да | из V1 `timer_min` × 60 |
| `timer_label` | text | да | |
| `timer_note` | text | да | |
| `pull_internal_temperature_c` | int | да | снятие с огня; не масштабируется |
| `target_internal_temperature_c` | int | да | безопасный конец; не масштабируется |
| `hold_seconds` | int | да | выдержка; не масштабируется |
| `equipment_note` | text | да | напр. не перегружать сковороду |

Температуры, hold и таймеры **никогда** не умножаются на `ratio`.

Валидатор — SAFETY: заполнен только `pull` без `target` → ошибка. Птица / свинина / фарш / готовая рыба — минимумы SAFETY.

**В JSON V1 полей `pull_*` / `target_*` нет** (проверено 2026-09-05, 43 рецепта). Текст в `notes` («72 °C») не считается полем. Срез обязан иметь сид температур для рецептов, которые иначе не пройдут валидатор; не выдумывать в импортере.

## `ContentDocument`

Справочники V1 разной формы JSON. Не нормализовать в десяток таблиц.

| Поле | Тип | Смысл |
|------|-----|--------|
| `type` | text | `guide` \| `meat` |
| `slug` | slug | внутри типа |
| `title` | text | |
| `payload_json` | JSON | исходная форма V1 |
| `updated_at` | timestamptz | |

Unique: `(type, slug)`.

Срез — ровно пять строк:

| type | slug | Роут Next | Источник V1 |
|------|------|-----------|-------------|
| `guide` | `grains` | `/grains` | `data/grains.json` |
| `guide` | `tips` | `/tips` | `data/tips.json` |
| `meat` | `beef` | `/meat/beef` | `data/meat-beef.json` |
| `meat` | `pork` | `/meat/pork` | `data/meat-pork.json` |
| `meat` | `poultry` | `/meat/poultry` | `data/meat-poultry.json` |

Пустых гидов (`seafood`, `vegetables`, …) не создавать.

## Поиск

С первой миграции. Не `__icontains`.

`unaccent` Postgres **не** переводит `ё`→`е`. Не полагаться на него для кириллицы.

```sql
CREATE OR REPLACE FUNCTION normalize_ru(text) RETURNS text AS $$
  SELECT lower(translate($1, 'Ёё', 'Ее'));
$$ LANGUAGE sql IMMUTABLE PARALLEL SAFE;
```

- `search_vector` — generated: `to_tsvector('russian', normalize_ru(title || ' ' || ingredient_titles || ' ' || coalesce(summary,'')))`.
- В вектор: заголовок, имена ингредиентов, лид. **Не** шаги целиком и **не** `source_url`.
- GIN по `search_vector`. `pg_trgm` по `normalize_ru(title)`.
- Конфиг `simple` не использовать для русских полей.
- Расширения init: `pg_trgm`, `unaccent` (латиница / общие диакритики). `ё` — только `normalize_ru`.

Запрос пользователя тоже прогонять через `normalize_ru` до `plainto_tsquery` / триграмм.

## Масштаб — кто что значит

Два независимых поля:

| | `scalable=true` | `scalable=false` |
|--|-----------------|------------------|
| `linear` | `amount * ratio` | amount как в БД |
| `gentle` | `amount * ratio^0.7` | amount как в БД |
| `whole` | linear + округление до целых (min 1) | amount как в БД |
| `manual` | не авто-масштаб; в UI «проверьте» | amount как в БД |

`fixed` из SAFETY = **`scalable=false`**, это не значение `scale_mode`.

`ratio` из **одного** источника за запрос: порции **или** якорь. Оба query-параметра сразу — ошибка API. На карточке рецепта те же формулы считает клиент (DEC-021).

Округление UI — [DEFAULTS.md](DEFAULTS.md). Счёт в Decimal. Next формулу не знает.

## ETL (контракт, не чек-лист)

Команда `import_v1`. Источник: корень `data/`, не рантайм Next.

- Одна транзакция: всё или ничего.
- Повторный запуск: upsert по `Recipe.slug` / `RecipeVariant(recipe, axis, code)` / `ContentDocument(type, slug)` / `Ingredient.canonical_id`. Дублей нет.
- `--dry-run`: отчёт, ноль записей.
- Ждать [DEFAULTS.md](DEFAULTS.md) «каталог V1»: **43** объекта в **19** файлах. Иное число — fail.
- Маппинг папок/category → VOCAB (`cook_method`, `equipment`). Папки корня не переименовывать. Казан vs форму не угадывать.
- Аллергены: **сид-словарь** `v1_ingredient_map` (строка V1 → `canonical_id` + списки аллергенов). Regex по падежам запрещён как основной путь. Нет ключа в сиде → импорт падает (`unknown` нельзя молча превратить в «нет»).
- Температуры: сид `v1_step_temperatures` для птицы/свинины/рыбы (в V1 JSON полей нет; **13** таких рецептов на 2026-09-05). Нет target там, где SAFETY требует — fail, не skip.
- Якорь: эвристика V1 → `is_anchor` на базе.
- `allowed_cuts=[]`. Не угадывать из title.
- `notes` blob → список: `NULL` → `[]`; нет `\n\n` → один пункт `{ "title": null, "text": "…" }`; иначе нарезка по `\n\n`, `title: null`. Заголовки не выдумывать. V1 `variations` в заметки не класть.
- V1 `variations[]` → `RecipeVariant` `axis=addon`, `has_delta=false`, `legacy_text` из `text`, `code` из транслита `title`.
- Сид замен `substitution_rules.json` → `SubstitutionRule` (upsert). Нет `canonical_id` в БД — пропустить строку, не падать.
- Нет `servings` / якоря — UI масштаба выключен. Не выдумывать 4 порции и `light`.
- Картинок нет — media не строить.

Сид-файлы появятся вместе с кодом импорта (не в этом документе). Пока кода нет — не заполнять «на глаз» в markdown.
