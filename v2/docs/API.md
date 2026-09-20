# API 2.0 (срез)

Контракт HTTP между Next и Django. Схема полей — [DATA-MODEL.md](DATA-MODEL.md). Коды фильтров — [VOCAB.md](VOCAB.md). Веса выдачи — [DEFAULTS.md](DEFAULTS.md). OpenAPI (`drf-spectacular`) должен совпадать с этим файлом; при расхождении править оба.

Публичный REST в Next `app/api` запрещён. Браузер ходит на `/api/` того же origin (Caddy → Django).

Мутации (V2.1): cookie-сессия + CSRF (`X-CSRFToken`). Неавторизованный **POST/PUT/DELETE** личного → **`403`** `{ "detail": "…" }`, не `401` и не JWT. `GET /api/recipes/<slug>/me/` для гостя → **`200`** `{ "authenticated": false }`.

## Общее

- Без JWT, без CORS.
- JSON, ключи английские, тексты для UI — русские.
- Пагинация каталога: DRF page (`count`, `next`, `previous`, `results`). Размер страницы по умолчанию **20**. Query `page_size` — до **500** (оглавление книги). Query `sample=` (1–24) — случайные N карточек без пагинации (витрина); не сочетать с `page`.
- Ошибки: `{ "detail": "…" }` или `{ "errors": { "field": ["…"] } }`. `400` — плохой запрос, `404` — нет сущности.
- `healthz`: `GET /healthz` → `200` `{ "status": "ok" }` (не под `/api/`).

### URL для Next

Caddy: браузер → `http://localhost:8080/api/...`.

Внутри Node (SSR / Server Actions) **нельзя** `fetch('/api/...')` — нет внешнего origin.

| Переменная | Кто | Значение в Compose |
|------------|-----|-------------------|
| `INTERNAL_API_URL` | сервер Next | `http://backend:8000` |
| `NEXT_PUBLIC_API_URL` | браузер | пустая строка (относительный `/api`) |

SSR: `fetch(`${INTERNAL_API_URL}/api/recipes/${slug}/`)`. Публичные GET без Cookie (иначе Next не кэширует). CSRF и Cookie — на мутациях (в срезе мутаций нет).

Не звать `http://localhost:8080` из контейнера frontend — лишний круг через хост.

## Фильтры (каталог и рекомендации)

Query-ключи: `protein_base`, `cook_method`, `dish_type`, `equipment`, `cuts`, `without` (коды VOCAB). Поиск каталога: `q`. Калькулятор дополнительно: `have=` (`canonical_id` или русский алиас), `have_group=` (грубая группа), `intent=` (сценарий).

- Несколько значений **одного** ключа (повторы или CSV): **OR**.
- Разные ключи между собой: **AND**.
- Неизвестный код: `400`, не молчаливый ignore.
- `equipment=`: попадание, если код у базы **или** у `RecipeVariant` `axis=equipment` с `has_delta`.
- `cook_method=`: база **или** `cook_method_override` у варианта посуды с дельтой (семейство-тушение видно в «духовке», если есть такая ось).
- `protein_base=`: база **или** код ∈ `protein_bases_extra` **или** `protein_base_override` у addon с `has_delta` (шаурма из курицы видна в «говядине», если чип так помечен).
- `cuts=`: код ∈ `Recipe.allowed_cuts` (поле базы, не дельта).
- `without=`: аллерген; на **карточке каталога** — объединение базы и всех addon-дельт с `has_delta` (`contains` и `unknown`). Строки `optional` (гарнир / «для подачи») в это объединение не входят. Страница рецепта — аллергены **текущего** display.
- Пустая выдача — `200` и `results: []`, не `404`.
- В спринте 3–4 нет `energy=` (калораж). Нет `variant=` на каталоге (одна строка на slug). Каталог не принимает `have=` / `have_group=` / `intent=`. Нет query `kcal_max` — ни на каталоге, ни на карточке, ни на рекомендациях.

Пример: `?protein_base=poultry&protein_base=beef&cook_method=oven` → (птица **или** говядина) **и** духовка.

Жёсткий отсев рекомендаций (не балл): unpublished; аллерген `contains` или `unknown` по запросу «без X».

## Масштаб на карточке

`GET /api/recipes/<slug>/`

| Query | Правило |
|-------|---------|
| нет query | базовые количества из БД |
| `?servings=` | `ratio = servings / recipe.servings`; нет `recipe.servings` → как «масштаб выключен» |
| `?anchor_weight=` | граммы или мл в базовой единице якоря; `ratio = anchor_weight / base_anchor` |
| оба сразу | **`400`** |
| `?variant=` | `code` оси addon; нет ключа = база; чужой / неизвестный → **`400`** |
| `?equipment=` | код посуды из доступных семейства; нет ключа = `Recipe.equipment` базы; иначе **`400`** |
| рецепт без якоря и без servings | параметры игнорируются, `scaling.enabled=false`, `200` |
| `scalable=false` у рецепта | то же: `200`, количества базы, `enabled=false` |
| `?prep=` | слот набора; см. ниже. **Нельзя** вместе с `anchor_weight` (**400**) |
| `servings` с `prep` | `ratio = servings / PrepKit.servings_base`, не якорь карточки |

Сборка дельт **до** масштаба — [DATA-MODEL.md](DATA-MODEL.md). На карточке «У меня» Next считает количества локально (DEC-021). Query `anchor_weight` / `servings` остаются для шаринга и тестов. Ранжирование калькулятора на клиенте нет.

В спринте 2 нет `?energy=`.

Шаринг карточки: `/recipes/<slug>?variant=&equipment=` (не сегмент path; HUMAN 3.3). Из набора: `/recipes/<slug>?prep=<kit>&day=&meal=` (и `servings=`, если не база).

### Карточка с `prep=` (слой «На неделю»)

Слот ищется по набору, не «первый slug в kit». Шаги ответа — тело слота или выбранной alternative, не книга.

| Query | Поведение |
|-------|-----------|
| нет `prep` | тело с нуля, как сейчас |
| `prep` + **оба** `day` и `meal` | слот kit×day×meal. URL-slug = `slot.recipe` **или** `alternatives[].slug` этого слота; при `no_leftover=1` у `reheat` ещё `no_leftover.slug` → иначе **400** |
| `prep` без day/meal | ровно **один** слот kit, у которого `recipe.slug` = URL (alternatives не считаются); два и больше → **400**; ноль → **400** |
| только `day` или только `meal` | **400** |
| `prep` неизвестный / не published | **400** |
| `anchor_weight` вместе с `prep` | **400** |

Шаги: основное блюдо → `PrepSlot.steps`; замена → `alternatives[].steps` той же записи; `no_leftover=1` у reheat → `no_leftover.steps`, у источника leftover → `no_leftover.steps` если есть. `prep_context`: `kit` `{slug, title}`, `day`, `meal`, `mode`, `source`, `containers[]` (уже с масштабом qty), `alternatives` (без чужих steps в списке чипов — `slug`, `label`, `mode`), `no_leftover` bool. Страница без `prep` — ISR как сейчас; с `prep` — не класть контекст в статический HTML.

Не добавлять prep в `GET /api/recommendations/`.

## Эндпоинты среза

### `GET /api/recipes/`

Каталог. Query: фильтры + `q` + `page` + `page_size` (1–500, по умолчанию 20) или `sample` (1–24, случайные карточки, без `page`).

```json
{
  "count": 43,
  "next": null,
  "previous": null,
  "results": [
    {
      "slug": "stejk-na-skovorode-pan-searing",
      "title": "Стейк на сковороде (Pan-Searing)",
      "protein_base": "beef",
      "protein_bases": ["beef"],
      "protein_variants": [],
      "cook_method": "pan_fry",
      "dish_type": "main",
      "equipment": "skillet",
      "allowed_cuts": ["thick_rib", "tenderloin"],
      "summary": "…",
      "editorial_tested": false,
      "high_risk_flags": [],
      "allergens": {
        "contains": ["milk"],
        "may_contain": [],
        "unknown": []
      },
      "has_delta_variants": false,
      "scaling": { "enabled": false }
    }
  ]
}
```

`allergens` на карточке каталога — худший случай: база ∪ addon-дельт с `has_delta`. `unknown` не опускать. `has_delta_variants` — есть ли хотя бы один addon с `has_delta=true` (для бейджа, не для переключателя в сетке). `protein_bases` — домашняя основа ∪ `protein_bases_extra` ∪ override чипов с дельтой. `protein_variants` — `{code, title, protein_base}` только у тех addon, где задан override (книга ставит `?variant=`).

Каталог **не** отдаёт `nutrition` и `nutrition_line`.

### `GET /api/recipes/<slug>/`

Полный рецепт. 404 если нет / не `published`. С V2.1-C в теле есть `community_confirmed`. Счётчики «приготовили N» и среднее оценок — не здесь, а `GET …/engagement/` (не ISR).

```json
{
  "slug": "barhatnaya-govyadina-po-kitajski",
  "title": "Бархатная говядина по-китайски",
  "protein_base": "beef",
  "home_protein_base": "beef",
  "cook_method": "pan_fry",
  "dish_type": "main",
  "equipment": "skillet",
  "allowed_cuts": [],
  "applied_axes": { "variant": null, "equipment": "skillet" },
  "available_variants": [{ "code": "with_green_butter", "title": "С зелёным маслом", "axis": "addon", "has_delta": false, "protein_base": null }],
  "available_equipment": ["skillet"],
  "summary": "…",
  "source_name": "Личный повар",
  "source_url": "https://sol-chef.ru",
  "editorial_tested": false,
  "high_risk_flags": [],
  "caution_text": null,
  "allergens": {
    "contains": ["egg", "soy"],
    "may_contain": [],
    "unknown": []
  },
  "scaling": {
    "enabled": true,
    "mode": "anchor",
    "ratio": 1.2,
    "base_anchor": { "amount": 500, "unit": "g", "name": "говядина" },
    "applied": { "anchor_weight": 600 }
  },
  "servings": null,
  "yield_weight_g": null,
  "yield_kind": null,
  "ingredients": [
    {
      "name": "говядина",
      "amount": 600,
      "amount_max": null,
      "unit": "g",
      "detail": "лопатка, огузок или бедро",
      "scalable": true,
      "scale_mode": "linear",
      "is_anchor": true,
      "optional": false,
      "nutrition_exclude": false,
      "nutrition_skip_hint": false,
      "display_amount": "600 г",
      "nutrition_line": {
        "kcal_per_100g": 250,
        "protein_g_per_100g": 26.0,
        "fat_g_per_100g": 15.0,
        "carbs_g_per_100g": 0,
        "grams_per_unit": 1,
        "nutrition_factor": 1
      }
    }
  ],
  "steps": [
    {
      "text": "…",
      "timer_seconds": 300,
      "timer_label": "Отдых",
      "timer_note": null,
      "pull_internal_temperature_c": null,
      "target_internal_temperature_c": null,
      "hold_seconds": null
    }
  ],
  "variations": [{ "title": "…", "text": "…" }],
  "notes": [{ "title": null, "text": "…" }],
  "time_profile": { "total_minutes": 30, "active_minutes": 15 },
  "effort_level": 3,
  "washing_level": 2,
  "use_cases": ["one_pan", "budget"],
  "adaptations": [],
  "nutrition": {
    "basis": "raw_input",
    "incomplete": false,
    "total": { "kcal": 1840, "protein_g": 112.0, "fat_g": 126.0, "carbs_g": 48.0 },
    "per_100g_input": { "kcal": 214, "protein_g": 13.0, "fat_g": 14.7, "carbs_g": 5.6 },
    "per_100g_cooked": null,
    "per_serving": null
  }
}
```

`display_amount` — уже округлённая строка для UI (правила DEFAULTS). Клиент её показывает, не пересчитывает.

`nutrition` — ориентировочное КБЖУ после сборки и масштаба (DEC-022, DEC-023). Не колонка рецепта. Не называть поле `per_100g` или `per_100g_raw`. `basis` остаётся `"raw_input"`: kcal всё ещё с сырых канонов; готовое — только знаменатель `per_100g_cooked`.

| Поле | Смысл |
|------|--------|
| `basis` | всегда `"raw_input"` |
| `total` | сумма по учтённым строкам текущего display |
| `per_100g_input` | `total` на 100 г **входной** учтённой массы, не 100 г тарелки |
| `per_100g_cooked` | `total` на 100 г `(yield_weight_g * ratio)`; `null` если выхода нет. Не алиас input |
| `per_serving` | только если есть `servings`; иначе JSON `null` |
| `incomplete` | хотя бы одна обязательная строка не вошла из-за дыры справочника или единиц |

`yield_weight_g` / `yield_kind` — на карточке, не в каталоге. Нет выхода — оба `null`. `yield_kind`: `estimated` \| `exact`.

`nutrition_line` — проекция **этой** строки карточки, чтобы клиент после `scaleLine` воспроизвёл ту же формулу. Не справочник `Ingredient` наружу. Каталог и калькулятор объект не читают. Нет отдельного `/api/nutrition`.

- `nutrition_exclude` на строке обязателен (bool): клиент не ставит `incomplete` на исключённое масло жарки. `nutrition_line: null` — строка не участвует (`exclude` / `optional` / `pinch` / `to_taste` / нет данных). Клиент не считает. `nutrition_skip_hint` — иконка «КБЖУ не считается» у `to_taste`/`pinch`, только если канон жирный/сладкий (≥300 ккал или ≥20 г жира на 100 г). Соль, перец, паприка — `false` (DEC-024).
- `nutrition_factor` в проекции: нет ключа на строке = `1`. Клиент умножает граммы вклада на него.
- `grams_per_unit` — граммы **одной** текущей единицы этой строки (`tbsp`→14, `g`→1, `ml`→density). Не пачка `g_per_tsp`+`g_per_tbsp`+density.

`applied_axes` — какие оси собраны в этом ответе. `ingredients` / `steps` / `allergens` / `cook_method` / `high_risk_flags` / `nutrition` — уже display.

`available_variants` — ось addon. Переключатель состава только если `has_delta=true`. Иначе клиент показывает свёртку `variations` (`title` + `legacy_text`) и не меняет список. `protein_base` на варианте — `protein_base_override`, если чип меняет основу. `home_protein_base` — колонка семьи (чип «Курица»), `protein_base` в корне — display после сборки.

`available_equipment` — дефолт базы плюс коды вариантов посуды с дельтой. Один код — ряда посуды нет.

`notes` — список, не строка. `variations` в ответе — только legacy (`has_delta=false`), чтобы не дублировать дельты. `prep` — напоминания «Заранее»; нет действий — `[]`, ключа в JSON автора нет. `time_profile` / `effort_level` / `washing_level` / `use_cases` / `adaptations` — профиль и разрешённые операции; у ETL V1 минуты `null`, списки пустые. Ranking калькулятора эти поля в этом спринте не читает.

`scaling.mode`: `anchor` \| `servings` \| `off`.

`scale_mode: manual` у строки: amount как после сборки, плюс клиент показывает «проверьте по исходному рецепту».

`optional: true` — гарнир / подача / «по желанию». Строка в списке есть, в `allergens` блюда и в КБЖУ не входит.

### `GET /api/guides/grains/` · `GET /api/guides/tips/`

`ContentDocument` `type=guide`. 404 если строки нет.

```json
{
  "type": "guide",
  "slug": "grains",
  "title": "Крупы",
  "payload": {}
}
```

`payload` — JSON V1 как лежит в БД. Next не ходит в `data/grains.json`.

### `GET /api/guides/meat/<cut>/`

`cut` ∈ `beef` \| `pork` \| `poultry`. Иначе `404`. Тело как у гида, `type: "meat"`.

### `GET /api/ingredients/`

Грубые группы кладовки для первого экрана калькулятора. Не склад с граммами. Не полный VOCAB осей.

Без query: дерево. Первый ряд — грубые группы. У `meat` есть `children` (свинина / говядина / баранина / другое) и пустой `items`; отрубы витрины — в `children[].items`. Остальные группы сразу отдают полный список группы, не «likely 5».

```json
{
  "groups": [
    {
      "id": "chicken",
      "title": "Курица",
      "items": [{ "canonical_id": "chicken_thighs", "title": "куриные бёдра" }]
    },
    {
      "id": "meat",
      "title": "Мясо",
      "items": [],
      "children": [
        {
          "id": "beef",
          "title": "Говядина",
          "items": [
            { "canonical_id": "beef_tenderloin", "title": "говяжья вырезка" },
            { "canonical_id": "beef_ribs", "title": "говяжьи рёбра" },
            { "canonical_id": "beef_round", "title": "мякоть" }
          ]
        }
      ]
    }
  ]
}
```

Каноны могут ещё не встречаться в рецептах.

`?text=курица,+гречка,+лук` — резолв без LLM. `свинина` → отрубы свинины. `масло` → `unknown`. Капуста принимается, даже если рецептов с ней ещё нет.

```json
{
  "items": [
    { "canonical_id": "chicken_thighs", "title": "куриные бёдра" },
    { "canonical_id": "buckwheat", "title": "гречка" },
    { "canonical_id": "onion", "title": "лук" }
  ],
  "unknown": []
}
```

Непонятные токены — в `unknown`, HTTP 200. Жёсткий `have=` на рекомендациях по-прежнему **400**, если канон/алиас неизвестен.

### `GET /api/recommendations/`

Калькулятор. Фильтры каталога плюс `have=`, `have_group=`, `intent=`. Без `q`. Без `kcal_max`. КБЖУ не отдаёт. Как считает — [CALCULATOR.md](CALCULATOR.md). На `featured` / `results` те же `protein_bases` и `protein_variants`, что у карточки каталога: книга без этого не покажет шаурму в говядине.

Неизвестный `have` / `have_group` / `intent` → **400**. `intent=` **не** отсекает рецепт (вес). `have=` не отсекает блюда, которые **используют** продукт из кладовки (нехватка — корзины). Блюда, которые «Есть» не берут, на `featured` / `alternatives` не попадают; если таких нет — `featured: null`. Жёсткий отсев — оси и «без чего».

```json
{
  "filters": {
    "protein_base": [],
    "cook_method": [],
    "have": ["chicken_thighs", "onion"],
    "have_group": ["chicken"],
    "intent": ["fast"]
  },
  "featured": {
    "slug": "classic-roast-chicken",
    "title": "…",
    "protein_base": "poultry",
    "protein_bases": ["poultry"],
    "protein_variants": [],
    "cook_method": "pan_fry",
    "dish_type": "main",
    "equipment": "skillet",
    "applied_axes": { "variant": null, "equipment": null },
    "bucket": "now",
    "why": ["можно приготовить сейчас", "быстрее на плите"],
    "score": 24,
    "shopping_delta": [],
    "substitutions": [],
    "allergens": { "contains": [], "may_contain": [], "unknown": [] },
    "high_risk_flags": ["poultry_temp"],
    "has_delta_variants": false,
    "step_count": 6
  },
  "alternatives": [
    {
      "label": "Проще",
      "slug": "…",
      "title": "…",
      "why": ["меньше стоять у плиты"],
      "applied_axes": { "variant": null, "equipment": "oven" }
    }
  ],
  "buckets": {
    "now": [],
    "almost": [],
    "best": []
  },
  "results": []
}
```

`score` для тестов; карточка Next его не показывает. Экран калькулятора рисует `featured` + `alternatives`, не сетку `results`. JSON `results` — доска (featured/альтернативы или корзины при `have=`), не все семейства каталога. Витрина `/` берёт случайную шестёрку из `GET /api/recipes/?sample=6`, не этот endpoint.

Без `have=` `buckets` пустые, `featured` — лучшее из ranked `results`. Заготовки (`dish_type` `sauce` / `preserve`) не featured, пока есть обычное блюдо. Клик: `/recipes/<slug>?equipment=&variant=` из `applied_axes`.

Пустые ниши после ETL V1 — штатный `featured: null`, `results: []`.

### `GET /api/prep-kits/`

Каталог наборов. Только `status=published`. Порядок: `position` по возрастанию, затем `slug`. **Без пагинации** в пилоте. Пустой список — **200** `{ "results": [] }`, не `404` и не «скоро».

```json
{
  "results": [
    {
      "slug": "nedelya-ptica",
      "title": "Птица на неделю",
      "summary": "…",
      "rhythm": "freezer",
      "position": 1,
      "metrics": {
        "slots_assemble": 8,
        "slots_finish": 4,
        "slots_reheat": 2,
        "unique_slugs": 10,
        "shopping_skus": 18,
        "components_count": 5,
        "t_sunday_active_min": 105,
        "t_sunday_wall_min": 180,
        "t_weekdays_active_min": 210,
        "t_scratch_active_min": 480
      }
    }
  ]
}
```

### `GET /api/prep-kits/<slug>/`

Полный набор. 404 если нет / не `published`. `?servings=` — линейный масштаб qty закупки, компонентов и контейнеров; число боксов и их `code`/`label` не менять. UI шлёт 1, 2 или 4 (база 2). Нет `servings_base` → масштаб выключен. `metrics` и `weekend_timeline` без пересчёта.

`?no_leftover=1` (также `true`/`yes`/`on`) — вариант без остатка: слот-источник на один приём, `reheat` заменяется `PrepSlot.no_leftover` (slug не из 14 основных ячеек набора), qty leftover-only боксов и уникальной закупки уменьшаются, `shopping_add` вливается. Без query — как в JSON. В корне ответа: `no_leftover` (bool), `has_leftovers` (в наборе есть `reheat`), `leftover_cost` `{dishes, shopping_add}` — цена плана для подписи переключателя. У контейнера морозилки ещё `thaw_pull`: `evening_before` \| `morning` (считает сервер из `unit` и кода компонента). Карточка рецепта: тот же query; slug слота = основное блюдо **или** `no_leftover.slug` этого слота при флаге.

`graph` — вид из слотов (кто ест компонент: weekend-слоты по контейнерам + каскад reheat), не ranking.

```json
{
  "slug": "nedelya-ptica",
  "title": "Птица на неделю",
  "summary": "…",
  "servings_base": 2,
  "scaling": { "enabled": true, "mode": "servings", "ratio": 1, "applied": { "servings": 2 } },
  "caution_text": "…",
  "rhythm": "freezer",
  "metrics": {},
  "allergens": { "contains": ["egg"], "unknown": [], "may_contain": [] },
  "shopping": [
    {
      "canonical_id": "chicken_thigh",
      "qty": 1400,
      "unit": "g",
      "title_ru": "Куриное бедро",
      "display_amount": "1400 г"
    }
  ],
  "components": [],
  "containers": [],
  "weekend_timeline": [],
  "slots": [],
  "graph": [
    {
      "code": "chicken_thigh_strips_parcook",
      "title": "Куриное бедро, полоски",
      "slots": [
        { "day": 1, "meal": "dinner", "slug": "lavash-s-kuritsej", "title": "Лаваш с курицей", "mode": "assemble" }
      ]
    }
  ]
}
```

У слота в ответе: `day`, `meal`, `slug`, `title`, `plate_title`, `plate_composition`, `mode`, `flavor`, `source`, `container_ids`, `containers` (развёрнутые боксы), `alternatives` (`slug`, `label`, `mode`, `container_ids`), минуты, `servings_cooked`, `feeds_slots`. `metrics.kcal_avg_per_serving` — ориентир по основным рецептам: из `kit.metrics`, если поле уже есть; иначе приложение считает один раз и записывает. Тела `steps` слота на каталоге набора можно отдать (cook открывается с карточки рецепта).

## Не в гостевом срезе (спринт 4)

Query `energy=`, `kcal_max`, чипы «15 мин / 30 мин» без поля времени в рецепте. JWT, webhooks, публичный Next `/api/`.

Аккаунты, CSRF-мутации, `/api/pantry/` как **факт наличия** — [ниже, V2.1](#v21-аккаунты). Граммы кладовки и загрузка фото — V2.2.

## V2.1 аккаунты

План: [ACCOUNTS.md](ACCOUNTS.md). Модели: [DATA-MODEL.md](DATA-MODEL.md). Не включать в OpenAPI среза, пока CURRENT_SPRINT не про A.

Все мутации ниже — CSRF. Письма и сессия — Django, не Next.

### CSRF и «кто я»

| Метод | URL | Кто | Смысл |
|-------|-----|-----|--------|
| `GET` | `/api/auth/csrf/` | все | выставить cookie CSRF, `{ "ok": true }` |
| `GET` | `/api/auth/me/` | все | `{ "authenticated": false }` или `{ "authenticated": true, "email": "…", "is_trusted": false }` |

### Вход / выход

| Метод | URL | Тело | Смысл |
|-------|-----|------|--------|
| `POST` | `/api/auth/request-code/` | `{ "email": "user@mail.ru" }` | валидация домена; письмо OTP+ссылка; всегда нейтральный успех (не светить, есть ли аккаунт), кроме **400** на зарубежный домен |
| `POST` | `/api/auth/verify-code/` | `{ "email", "code" }` | OTP; сессия; `next` не здесь — редирект делает страница |
| `POST` | `/api/auth/magic-login/` | `{ "token" }` | POST со страницы confirm, не GET |
| `POST` | `/api/auth/logout/` | — | сжечь сессию |
| `POST` | `/api/auth/delete-account/` | `{ "confirm": true }` | обезличивание; без confirm — 400 |

GET `/login/confirm?token=` **не** этот API и **не** логинит.

Зарубежный email → `400` `{ "detail": "Для входа используются только почтовые адреса в российских доменах" }`.

### Карточка: гидрация и память

| Метод | URL | Смысл |
|-------|-----|--------|
| `GET` | `/api/recipes/<slug>/me/` | гость: `{ "authenticated": false }`. Вошедший: `authenticated`, `favorite`, `my_rating` (1–5 \| null), `last_cooked_at` (ISO \| null) |
| `GET` | `/api/recipes/<slug>/engagement/` | публично, без PII: `{ "cooked_count", "rating_avg" (null если <3), "rating_count", "community_confirmed" }` |
| `PUT` | `/api/recipes/<slug>/favorite/` | `{ "favorite": true\|false }` |
| `POST` | `/api/recipes/<slug>/cooked/` | `{ "variant": code\|null, "equipment": code\|null, "scale_ratio": number\|null, "private_note": string }` → новая строка |
| `PUT` | `/api/recipes/<slug>/rate/` | `{ "score": 1..5 }` |

`cooked_count` — число `CookReport` со `status=approved`. Не класть engagement в ISR HTML.

### Комментарии и жалобы

| Метод | URL | Смысл |
|-------|-----|--------|
| `GET` | `/api/recipes/<slug>/comments/` | только `approved`; `{ "results": [ { "id", "body", "created_at" } ] }` — **без email и user id** |
| `POST` | `/api/recipes/<slug>/comments/` | `{ "body" }` → `pending` или `approved` по правилам |
| `POST` | `/api/recipes/<slug>/comments/<id>/delete/` | свой комментарий → `deleted` |
| `POST` | `/api/complaints/` | `{ "target": "comment"\|"recipe", "comment_id"?, "recipe_slug"?, "reason" }` |

### Кабинет

| Метод | URL | Смысл |
|-------|-----|--------|
| `GET` | `/api/me/favorites/` | список семейств, новые сверху; карточка как каталог (slug, title, оси) |
| `GET` | `/api/me/cooked/` | лента своих отчётов |
| `GET` | `/api/pantry/` | `{ "items": [ { "kind": "canonical"\|"have_group", "code": "…" } ] }` |
| `PUT` | `/api/pantry/` | полная замена набора (кнопка «Сохранить в кладовку»); граммов нет |

Неизвестный `kind` / `code` кладовки → `400`, как `have=`.
