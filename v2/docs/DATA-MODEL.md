# Модель данных 2.0

Контракт схемы. Коды полей — [VOCAB.md](VOCAB.md). Safety-инварианты — [SAFETY.md](SAFETY.md). Числа — [DEFAULTS.md](DEFAULTS.md). HTTP — [API.md](API.md). Задача сессии — [../CURRENT_SPRINT.md](../CURRENT_SPRINT.md).

Агент не выдумывает поля «на будущее», кроме явно помеченных *позже*.

## Приложения Django

| App | Модели |
|-----|--------|
| `recipes` | `Recipe`, `RecipeVariant`, `RecipeRevision`, `Ingredient`, `RecipeIngredient`, `RecipeStep`, `SubstitutionRule` |
| `content` | `ContentDocument` |
| `prep` | `PrepKit`, `PrepComponent`, `PrepContainer`, `PrepSlot` — слой «На неделю»; не раздувать `recipes` |
| `accounts` | V2.1: `User`, `AuthToken`, `Favorite`, `CookReport`, `PantryItem`, `RecipeRating`, `RecipeComment`, `Complaint` |

Сессии Django — в Postgres (не Redis). `AUTH_USER_MODEL = "accounts.User"`. Гостевой срез без этих таблиц живёт; миграции аккаунтов — спринт V2.1-A ([ACCOUNTS.md](ACCOUNTS.md)). Кладовка с граммами и фото — V2.2, не колонки «про запас».

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
| `yield_weight_g` | decimal | да | граммы готового на **базе** рецепта; нет / null = нет `per_100g_cooked` |
| `yield_kind` | enum | да | `estimated` (дефолт, если есть выход) \| `exact`; без выхода — null |
| `summary` | text | да | лид |
| `source_name` | text | да | |
| `source_url` | URL | да | |
| `source_type` | text | да | `video` / `article` / … |
| `editorial_tested` | bool | нет | только человек; ETL: `false` |
| `community_confirmed` | bool | нет | сервис аккаунтов: ≥3 разных user с approved `CookReport`; ETL: `false`; агент не ставит |
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

Нет поля `scalable_rule`. Нет колонки `variations` на `Recipe` (это `RecipeVariant`). Нет `scale_mode=fixed`. Нет колонки `Recipe.nutrition` — КБЖУ не канон рецепта, а производное display после сборки и масштаба (DEC-022, DEC-023). `yield_weight_g` — редакционная масса готового, не сумма входных граммов. Не выдумывать выход на каталоге. Не подписывать `per_100g_input` как «на 100 г готового».

Карточка 2.0 — три уровня, не квота вариантов:

- **A (обязательный):** id, title, summary, оси VOCAB, equipment, ingredients, steps, scale_mode/scalable, safety, provenance.
- **B (профиль):** `time_*`, `effort_level`, `washing_level`, `use_cases`. У оверлея обязателен. Таймеры шагов профиль не заменяют.
- **C (адаптивность):** `variants` 0–10 и `adaptations` только если есть реальная альтернатива или разрешённая операция. Не заполнять ради числа.

`energy_profile` — только калоражная ось (`standard` / написанный `light`/`rich`). Не решать через него «быстро / просто / мало посуды».

Вариант ≠ адаптация. Variant — редакционная версия блюда (чип, дельта состава). Adaptation — заранее разрешённая операция движка; runtime не фантазирует «наверное можно в духовке».

`new_ingredients` в JSON автора — **заявка** на канон, не второй реестр и не корзина. После регистрации в `Ingredient` блок из утверждённого рецепта исчезает. Аллергены строки рецепта не источник истины — только таблица `Ingredient`. Строки с одним `choice_group` — взаимоисключающий выбор; заявка канона на обе ветки не значит, что обе покупают.

### Инварианты рецепта

- `scalable=false` → query `servings` / `anchor_weight` не меняют количества.
- `servings IS NULL` и нет строки `is_anchor=true` **после сборки варианта** → масштабирование выключено. ETL **не** подставляет 4 порции.
- High-risk без `caution_text` → нельзя `published`. Вариант с флагом и `published` → `caution_text` базы или `caution_text_override`.
- `editorial_tested` агент не ставит.
- `community_confirmed` агент и ETL не ставят; только сервис по cook report.
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

КБЖУ display — после assemble и `apply_mode`, без `roundScaled` количеств (DEC-022). Не колонка `Recipe`. Выход в знаменателе `per_100g_cooked` — `yield_weight_g * ratio`, всегда linear, не `gentle`.

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

Источник правды аллергена и нутриентов на 100 г — эта таблица, не подстрока в рецепте и не копия `allergens_*` в каждом JSON. Оверлей ссылается `canonical_id`. `new_ingredients` — заявка: канона нет → зарегистрировать здесь → убрать блок из утверждённого файла.

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
| `kcal_per_100g` | decimal | да | энергия **источника**, не Atwater 4/9/4 |
| `protein_g_per_100g` | decimal | да | |
| `fat_g_per_100g` | decimal | да | |
| `carbs_g_per_100g` | decimal | да | как в источнике; сахар отдельно не в MVP |
| `nutrition_basis` | enum | да, если макросы null | в MVP только `raw_100g`; обязателен, если нутриенты заполнены |
| `nutrition_source` | enum | да | `fooddata_central` \| `ru_table` \| `packaging_typical` \| `editorial` |
| `nutrition_source_id` | text | да | устойчивый id источника (FDC); у `editorial` обычно `null` |
| `g_per_tsp` | decimal | да | типовая масса 1 ч. л. **этого** канона |
| `g_per_tbsp` | decimal | да | то же, ст. л. |
| `g_per_pcs` | decimal | да | то же, шт |
| `g_per_clove` | decimal | да | то же, зубчик |
| `g_per_bunch` | decimal | да | то же, пучок |
| `g_per_slice` | decimal | да | то же, ломтик |

Четыре макроса + `kcal`: все заполнены или все null. Валидатор сида.

`g_per_*` — редакционная оценка типовой массы единицы **этого** канона (яйцо ≈ 50 г, зубчик чеснока ≈ 5 г), не глобальная таблица «ст. л. = 15 г». Нет своего `g_per_*` у нужного unit — строка вне суммы КБЖУ, `incomplete`.

`nutrition_basis` в MVP — только `raw_100g` (типовой сырой продукт в том виде, как в рецепте). Значений `cooked_100g` / `prepared_100g` нет. `nutrition_source_id` не обязателен: заполнять, когда id стабилен; не выдумывать ключ для editorial.

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
| `nutrition_exclude` | bool | нет | дефолт `false`; строка не входит **ни** в числитель КБЖУ, **ни** в массу `per_100g_input` |
| `nutrition_factor` | decimal 0.01–1 | да | доля вклада строки (жир, который остался в сковороде). Нет ключа / null = 1. Ноль запрещён — это `nutrition_exclude`. Не вместе с exclude |
| `choice_group` | text | да | «A или B»: одна ветка в закупке и в display, не сумма веток |
| `display_name` | text | да | как в V1, если отличается от канона |

`unit` ∈ `to_taste` \| `pinch` → `amount` должен быть `NULL`, `scalable=false`. `nutrition_factor` не вместе с `nutrition_exclude`.

### КБЖУ (производное display)

Не колонка `Recipe`. Считать после сборки варианта и `apply_mode`, до округления UI количеств (DEC-022).

Nutrition использует **то же resolved `amount`**, что display после `apply_mode`. Для диапазона `amount` … `amount_max` берёт `amount` (низ). `amount_max` в расчёт не входит.

Не входит ни в числитель, ни в массу `per_100g_input`: `optional: true`; `unit` ∈ `to_taste` \| `pinch`; `nutrition_exclude: true`. `nutrition_exclude` — целиком или никак. Частичный вклад — `nutrition_factor` (множитель граммов вклада и массы входа, дефолт 1). `to_taste` / `pinch` можно на жирных канонах (масло, мёд): валидатор не бьёт (DEC-024); UI-иконка только у жирного/сладкого, не у соли.

Граммы строки: `g` — `amount`; `kg` — ×1000; `ml`/`l` — через `density_g_per_ml` (нет плотности → `incomplete`, не «как вода»); `tsp`/`tbsp`/`pcs`/`clove`/`bunch`/`slice` — `amount * g_per_<unit>` этого канона (нет → `incomplete`, глобальную ложку не подставлять). Затем × `nutrition_factor`. `pinch`/`to_taste` не переводятся и **не** делают `incomplete`. Вода/бульон, которые остаются в блюде: макросы 0, в знаменателе `per_100g_input` — да.

`per_100g_cooked` — только если задан `yield_weight_g` > 0: `total` на 100 г `(yield_weight_g * ratio)`. `ratio` всегда linear, даже если якорь масла `gentle`. Нет выхода → JSON `null`, ячейки в UI нет. Это **новое поле**, не переименование `per_100g_input`.

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

## Аккаунты (V2.1)

План и инварианты — [ACCOUNTS.md](ACCOUNTS.md). Не в гостевом срезе. Фото и граммы кладовки — *позже* (V2.2), колонок не заводить.

### `User`

`AbstractBaseUser` + `PermissionsMixin`. Логин — почта. Пароль в UI нет (`set_unusable_password`).

| Поле | Тип | Null | Смысл |
|------|-----|------|--------|
| `email` | email, unique | нет | пока `deleted_at` пуст; после удаления — необратимый хеш-плейсхолдер, не рабочий адрес |
| `is_active` | bool | нет | |
| `is_staff` | bool | нет | админка |
| `is_trusted` | bool | нет | только staff; вес cook report 2×, не `editorial_tested` |
| `approved_comments_count` | int ≥0 | нет | сколько **опубликованных** своих комментариев; порог премодерации DEFAULTS |
| `created_at` | timestamptz | нет | |
| `deleted_at` | timestamptz | да | soft-delete; сессии сжечь |

Удаление: `deleted_at=now()`, email заменить на неколлизящий хеш, `is_active=false`. Избранное и кладовка — физически DELETE. Оценка / комментарий / cook report: `user` SET_NULL; комментарии → `status=deleted`.

### `AuthToken`

Один ряд = одна попытка входа (письмо). Сырой link-token и OTP **в БД не хранить** — только SHA-256 (hex 64).

| Поле | Тип | Null | Смысл |
|------|-----|------|--------|
| `user` | FK User | нет | CASCADE |
| `link_token_hash` | char 64 | нет | хеш токена из URL |
| `otp_hash` | char 64 | нет | хеш 6-значного кода |
| `attempts_left` | 0–5 | нет | старт 5; 0 = нельзя verify |
| `created_at` | timestamptz | нет | |
| `expires_at` | timestamptz | нет | created + 15 мин |
| `used_at` | timestamptz | да | успех; повторно нельзя |

GET `/login/confirm?token=` **не** пишет `used_at`. POST успеха — `used_at`, сессия.

### `Favorite`

| Поле | Тип | Null | Смысл |
|------|-----|------|--------|
| `user` | FK User | нет | CASCADE |
| `recipe` | FK Recipe | нет | CASCADE, если рецепт сняли |
| `created_at` | timestamptz | нет | сортировка кабинета |

Unique `(user, recipe)`.

### `CookReport`

Каждая готовка — новая строка.

| Поле | Тип | Null | Смысл |
|------|-----|------|--------|
| `user` | FK User | да | SET_NULL при удалении аккаунта |
| `recipe` | FK Recipe | нет | |
| `variant_code` | text | да | `RecipeVariant.code` оси addon; null = база |
| `equipment_code` | VOCAB | да | посуда display; null = база рецепта |
| `scale_ratio` | decimal | да | факт «У меня» / порций, если человек сохранил; не кладовка |
| `private_note` | text | да | только автору; не комментарий |
| `cooked_at` | timestamptz | нет | |
| `status` | enum | нет | `pending` \| `approved` \| `rejected`. V2.1 без фото: сразу `approved` |

Фото — *позже*. `community_confirmed` на рецепте: count distinct `user_id` где `status=approved` и `user_id IS NOT NULL` ≥ 3.

### `PantryItem`

Факт наличия, не граммы.

| Поле | Тип | Null | Смысл |
|------|-----|------|--------|
| `user` | FK User | нет | CASCADE |
| `kind` | enum | нет | `canonical` \| `have_group` |
| `code` | text | нет | `canonical_id` или код группы калькулятора |

Unique `(user, kind, code)`. Неизвестные коды — 400 как у `have=` / `have_group=`.

### `RecipeRating`

| Поле | Тип | Null | Смысл |
|------|-----|------|--------|
| `user` | FK User | да | SET_NULL |
| `recipe` | FK Recipe | нет | |
| `score` | 1–5 | нет | |
| `updated_at` | timestamptz | нет | |

Unique `(user, recipe)` пока user не null. После удаления аккаунта оценка остаётся в среднем без PII.

### `RecipeComment`

| Поле | Тип | Null | Смысл |
|------|-----|------|--------|
| `user` | FK User | да | SET_NULL |
| `recipe` | FK Recipe | нет | |
| `body` | text | нет | plaintext, max DEFAULTS; без HTML/markdown |
| `status` | enum | нет | `pending` \| `approved` \| `rejected` \| `deleted` |
| `created_at` | timestamptz | нет | |

Первые 5 `approved` пользователя когда-либо — следующие без стоп-слов сразу `approved`. Стоп-слова — файл в репо (`apps/accounts/stopwords.txt`), правит человек, не LLM.

Публичная подпись **не** хранится: UI всегда «Участник · дата». Email и ник не отдавать.

### `Complaint`

| Поле | Тип | Null | Смысл |
|------|-----|------|--------|
| `user` | FK User | да | SET_NULL |
| `target` | enum | нет | `comment` \| `recipe` |
| `comment` | FK Comment | да | если target=comment |
| `recipe` | FK Recipe | да | если target=recipe (ошибка карточки, не «не вкусно») |
| `reason` | text | нет | max DEFAULTS |
| `status` | enum | нет | `open` \| `resolved` \| `rejected` |
| `created_at` | timestamptz | нет | |

Ровно один из `comment` / `recipe` по `target`. Жалоба на рецепт ≠ комментарий.

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
- `community_confirmed` и `editorial_tested` при upsert **не затирать** живые значения (ETL пишет `false` только на INSERT).

Сид-файлы появятся вместе с кодом импорта (не в этом документе). Пока кода нет — не заполнять «на глаз» в markdown.

## `apps.prep` — набор на неделю

Не колонки на `Recipe`. Книжное тело шагов — только «с нуля». Будничное тело живёт на **слоте** этого набора (`PrepSlot.steps`), не на паре kit×recipe и не в `PrepRecipeBody`.

Два слота одного slug (борщ finish в пн / reheat во вт) — два разных `steps`.

Импорт: `manage.py import_prep_kit` (dry-run / import). Upsert по `PrepKit.slug`. JSON набора: `id` или `slug` → `slug`; `component.id` / `container.id` → `code`. Next JSON не читает. Не в корневой `data/`. Нет демо-наборов в фикстурах.

`mode` у published слота меняется только **полным re-import** набора. Нет PATCH слота.

### `PrepKit`

| Поле | Тип | Null | Смысл |
|------|-----|------|--------|
| `slug` | slug, unique | нет | URL `/prep/<slug>` |
| `title` | text | нет | |
| `summary` | text | да | |
| `servings_base` | positive int | да | база масштаба; нет → масштаб выключен |
| `caution_text` | text | да | обязателен при мясе/птице/рыбе в наборе (редакция) |
| `rhythm` | text | да | подпись ритма (`freezer`, `fridge_only`, …), не фильтр витрины |
| `status` | enum | нет | `draft` \| `published`. Список API — только `published` |
| `position` | int | нет | editorial порядок списка (возрастание, затем `slug`) |
| `metrics` | JSON | нет | целые минуты и счётчики; клиент **не** пересчитывает |
| `weekend_timeline` | JSON | нет | шкала вс; приложение не солвит заново |
| `shopping` | JSON | нет | `[{ canonical_id, qty, unit, title_ru }]` |
| `allergens` | JSON | нет | `{ contains, unknown, may_contain }` — худший случай набора |

Нет полей `weekend_protocol`, `qty_g`, `eaten_by`, `feeds_days`, `weekend_active_hours_estimated`.

### `PrepComponent`

Unique `(kit, code)`. Полуфабрикат после вс.

| Поле | Тип | Null | Смысл |
|------|-----|------|--------|
| `kit` | FK | нет | |
| `code` | slug | нет | из JSON `id` |
| `title` | text | нет | |
| `canonical_ids` | JSON list | нет | каноны VOCAB |
| `qty` | decimal | нет | выход на `servings_base` |
| `unit` | VOCAB unit | нет | |
| `weekend_steps` | JSON list | нет | **как** делать, не расписание |
| `parcook` | JSON | нет | |
| `storage` | JSON | нет | срок — редакционная оценка, не ГОСТ |

Какие боксы у компонента — строки `PrepContainer`, не копия `eaten_by`.

### `PrepContainer`

Unique `(kit, code)`. Физический бокс. Не 1:1 с компонентом.

| Поле | Тип | Null | Смысл |
|------|-----|------|--------|
| `kit` | FK | нет | |
| `code` | slug | нет | `c2` |
| `label` | text | нет | `№2` |
| `component` | FK | нет | |
| `qty` | decimal | нет | |
| `unit` | VOCAB unit | нет | тот же, что у компонента, для суммы |
| `place` | enum | нет | `fridge` \| `freezer` |
| `thaw_before_day` | 1–7 | да | достать к этому дню слота; null — не из морозилки |

### `PrepSlot`

Unique `(kit, day, meal)`. `day` ∈ 1…7 (1 = первый день после вс). `meal` ∈ `lunch` \| `dinner`.

| Поле | Тип | Null | Смысл |
|------|-----|------|--------|
| `kit` | FK | нет | |
| `day` | 1–7 | нет | |
| `meal` | enum | нет | |
| `recipe` | FK `Recipe` | нет | **основное** блюдо слота. Тарелка целиком — в `steps`. Второго FK (`side_recipe`) нет |
| `mode` | enum | нет | `assemble` \| `finish` \| `reheat` |
| `flavor` | text | да | короткий вкус; для UI тарелки дублирует `plate.title`, если оно есть |
| `plate` | JSON | да | `{title, composition}` — имя и состав **тарелки**, не slug книги |
| `source` | JSON | нет | ровно две формы, см. ниже |
| `container_ids` | JSON list | нет | коды боксов **этого** kit; у reheat `[]` |
| `alternatives` | JSON list | нет | 0–3 объекта, не массив slug |
| `no_leftover` | JSON | да | у `reheat` — замена слота; у источника leftover — шаги «на один раз». Пусто `{}` |
| `servings_cooked` | int | да | большая порция на слоте-источнике |
| `feeds_slots` | int | да | сколько слотов кормит, включая источник |
| `time_active_from_prep_min` | int | да | |
| `time_active_scratch_min` | int | да | |
| `steps` | JSON list | нет | редакционное тело **этого** применения; пустой запрещён у published |

`from_prep` как mode не писать.

#### `source` (ровно две формы)

```json
{ "kind": "weekend" }
```

```json
{ "kind": "slot", "day": 1, "meal": "lunch" }
```

Других ключей нет. `container_ids` **не** внутри `source`.

| `mode` | `source` | `container_ids` |
|--------|----------|-----------------|
| assemble / finish | только `weekend` | непустой список кодов **этого** kit |
| reheat | только `slot` | пусто. Источник — тот же kit, **вчера** (`source.day + 1 ===` этот `day`). Приём может отличаться. Не вперёд, не сам на себя, не «через два дня» |

#### `alternatives[]`

0–3 объекта:

```json
{
  "slug": "…",
  "label": "Лаваш с курицей",
  "mode": "assemble",
  "container_ids": ["c2", "c5"],
  "steps": [{ "text": "…" }]
}
```

`steps` обязательны (иначе cook mode замены нет). `slug` — published `Recipe`. `container_ids` — боксы этого kit. Не требуют новой закупки и вс. `reheat` у замены: `container_ids` пустой.

Фронт ничего не валидирует. Импорт — да.

#### `no_leftover`

У **`reheat`** — обязательный объект: чем становится слот при `?no_leftover=1`. Не alternative-чип: это **блюдо слота**. Published slug, которого **нет** среди основных slug 14 слотов этого kit (`assemble`/`finish`/`reheat`). `assemble`/`finish`; непустые `steps`. Боксы этого kit **или** пустые `container_ids` плюс непустой `shopping_add` (блюдо будня с закупки, не дубль ячейки). `shopping_add` — дельта закупки к базе набора (те же ключи, что у `shopping`).

```json
{
  "slug": "chechevitsa-s-ovoshchami",
  "mode": "finish",
  "container_ids": [],
  "steps": [{ "text": "…" }],
  "plate": { "title": "…", "composition": "…" },
  "shopping_add": [{ "canonical_id": "lentils", "qty": 200, "unit": "g", "title_ru": "Чечевица" }]
}
```

У **слота-источника** leftover (на него ссылается `reheat`) — необязательно `{ "steps": [{ "text": "…" }] }`: тело «съесть за этот приём», без «остаток на завтра».

При `?no_leftover=1` приложение: источник `feeds_slots=1`, `servings_cooked` = база набора; `reheat` подменяется объектом; боксы/компоненты, которые ест **только** этот leftover, и закупка с их уникальными `canonical_id` — × `1/feeds_slots`; `shopping_add` сливается в список.

### Инварианты импорта (иначе kit не `published`, транзакция откатывается)

- ровно 14 слотов: все пары day×meal;
- recipe слота, каждый `alternatives[].slug` и `no_leftover.slug` у reheat — `published`;
- `no_leftover.slug` у reheat не совпадает ни с одним основным slug 14 слотов этого kit;
- `container_ids` слота, замены и `no_leftover` принадлежат этому kit (у `no_leftover` список может быть пустым, если есть `shopping_add`);
- сумма `qty` контейнеров компонента = `qty` компонента (тот же `unit`);
- `source` сходится с `mode`;
- reheat: источник есть, тот же kit, `source.day + 1 === slot.day`, не этот слот;
- `steps` слота, каждой alternative и `no_leftover` у reheat непустые;
- у каждого `reheat` есть `no_leftover` с slug/mode/steps (боксы или `shopping_add`);
- нет запрещённых ключей (`weekend_protocol`, `qty_g`, `eaten_by`, `eaten_by_slots`, `feeds_days`, `weekend_active_hours_estimated`, `container_ids` внутри `source`).

Кто ест компонент — не поле: слоты `weekend` по контейнерам + каскад `reheat`.

### Масштаб набора

`ratio = servings / servings_base`. Линейно **qty** закупки, компонентов, контейнеров. Число и коды боксов не менять (№2 остаётся №2). Timeline, `steps`, `mode`, граф — без изменений. UI набора предлагает **1, 2 и 4** порции при `servings_base=2`. Нет `servings_base` → масштаб выключен. Минуты в `metrics` не пересчитывать.
