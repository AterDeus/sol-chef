# Решения 2.0

Короткие ADR. Предложение агента сюда не пишется, пока человек не принял (HUMAN или явная фраза в чате). Статус в [STATUS.md](STATUS.md) эти решения не меняет.

Порядок при конфликте документов — [README.md](README.md).

## DEC-001 — Масштаб только в Django

Status: accepted · 2026-09-05

Все количества считает domain service Django (`gentle` = `ratio^0.7`). Next показывает поля API.

Отклонено: формула в React «для отзывчивости»; копия `roundScaled` из V1.

Следствие: слайдер «У меня» бьёт в `GET /api/recipes/<slug>/?anchor_weight=` (дебаунс), не в `Math.pow`.

## DEC-001 — Масштаб только в Django

Status: superseded · DEC-021 · 2026-09-06

Было: все количества считает Django, слайдер бьёт в API. Человек (чат 2026-09-06): надпись «Обновляем количества» и дёрганье списка мешают; пересчёт должен быть мгновенным.

## DEC-021 — «У меня» на карточке считает клиент

Status: accepted · чат 2026-09-06

На странице рецепта количества после «У меня» / порций считает Next (`lib/scale.ts`): та же `gentle = ratio^0.7` и округление DEFAULTS, что Django. Без запроса на каждый шаг, без статуса «обновляем».

API `?anchor_weight=` остаётся для шаринга и тестов. Ранжирование калькулятора — только Django. Формула V1 `1+(ratio-1)*0.5` запрещена.

## DEC-022 — Nutrition is derived from assembled/scaled ingredients

Status: accepted · чат 2026-09-06

Ориентировочное КБЖУ — производное display после сборки варианта и масштаба, не контент рецепта.

1. JSON рецепта автора не содержит `nutrition` / `kcal` / БЖУ.
2. Источник чисел на 100 г — `Ingredient` (сид), не строка рецепта.
3. Источник истины формулы — Django `services/nutrition.py`, Decimal, после assemble + `apply_mode`, без `roundScaled`.
4. Frontend после `scaleLine` воспроизводит ту же формулу по проекции `nutrition_line`. Это не второй источник истины и не API каталога.

Дополнительно: `kcal` суммируется с канонов, не считается Atwater 4/9/4; базис MVP — вход до готовки (`raw_input` / `nutrition_basis=raw_100g`); поле API — `per_100g_input` (не `per_100g`, не `per_100g_raw`); `nutrition_exclude` целиком из числителя и массы; для диапазона `amount`…`amount_max` nutrition берёт `amount` (низ).

HUMAN 2.15. Канон — DATA-MODEL / API / DEC-022.

## DEC-023 — Yield and nutrition_factor are editorial

Status: accepted · чат 2026-09-06 · HUMAN 2.16

Первый срез этапа 3 КБЖУ: готовое и частичный жир — только если редакция написала числа.

1. `yield_weight_g` — граммы готового на базе. Нет ключа → `per_100g_cooked: null`. Не алиас `per_100g_input`. Не выдумывать на каталоге.
2. Знаменатель cooked — `yield * ratio`, всегда linear, не `gentle`.
3. `nutrition_factor` 0.01–1 на строке, editorial. Нет ключа = 1. Ноль запрещён (`nutrition_exclude`). Не вместе с exclude. Авто-0.5 на масло жарки нет.
4. Фильтр `kcal_max`, автовыбор `light`, обязательные `servings`, `ingredient_role` — не этот срез.

## DEC-024 — Calorie-dense to_taste is allowed

Status: accepted · чат 2026-09-06 · HUMAN 2.17

`to_taste` / `pinch` на масле, мёде и прочих жирных канонах разрешены. Строка не входит в сумму КБЖУ и не ставит `incomplete`. На карточке иконка справа только если пропуск скрывает заметные ккал (канон ≥300 ккал/100 г или ≥20 г жира/100 г). Соль, перец, паприка — без иконки. Тултип: «КБЖУ для этой строки не считается.» Валидатор это не бьёт ни на оверлее 43, ни на новых волнах. Граммы у ядра блюда по-прежнему обязательны.

## DEC-002 — Один origin, без JWT и CORS

Status: accepted · 2026-09-05

Caddy: `/api` `/admin` `/static` `/healthz` → Django, остальное → Next. Браузер не ходит на другой origin.

SSR Next использует `INTERNAL_API_URL` (Docker DNS `backend:8000`), клиент — относительный `/api`.

## DEC-003 — Справочники как `ContentDocument`

Status: accepted · 2026-09-05

Крупы, мясо, советы — JSON в Postgres, не 10 реляционных таблиц в срезе. Ключ `(type, slug)`.

## DEC-004 — Нет runtime LLM

Status: accepted · 2026-09-05

В приложении нет вызова модели. Рецепты агентами — файлы и staging после «стартуй волну 1».

## DEC-005 — V2 только в `v2/`

Status: superseded · DEC-027 · 2026-09-12

Корень был живым V1 до cutover. JSON корня — сырьё ETL, не рантайм Next.

## DEC-027 — Cutover: V1 в архив, прод на ВМ

Status: accepted · чат 2026-09-12

1. Статический V1 переезжает в `archive/v1/`. Корень — монорепо; Next/Django по-прежнему только в `v2/`.
2. JSON архива — сырьё `import_v1`, не рантайм. Живой каталог (~135 карточек и наборы) — Postgres; на ВМ переносят дампом, не голым `import_v1`.
3. Домен `sol-chef.ru` уходит с GitHub Pages на ВМ Timeweb (Caddy 80/443). Операции — [CUTOVER.md](CUTOVER.md).
4. `main` с архивом не пушить, пока DNS не смотрит на V2: без корневых `index.html`/`CNAME` Pages отдаст не сайт.

## DEC-006 — Каркас D+

Status: accepted · HUMAN 3.2a · 2026-09-05

Главная `/` — витрина. Подбор и шаринг — `/calculator`. В UI пока «Калькулятор». Канон экранов — [UX-PROPOSAL.md](UX-PROPOSAL.md). `v2/preview/` не референс.

Query на `/` — редирект на `/calculator` с тем же query, не смена фильтров на главной.

## DEC-007 — `unknown` ≠ безопасность

Status: accepted · HUMAN 2.12

Калькулятор отсекает `contains` и `unknown`. Аллерген висит на `canonical_id`.

Для ETL V1 — сид-словарь имён, не regex по падежам.

## DEC-008 — Старые URL рецептов

Status: accepted · HUMAN 3.4

`/recipe.html?id=<slug>` → редирект на `/recipes/<slug>`. Делает страница Next (query `id` в `redirects()` App Router не матчится), не обязательно Caddy.

## DEC-009 — Пустых гидов нет

Status: accepted · D+

Нет страниц «скоро». Чип фильтра с 0 рецептов — empty-state. Гид — только если есть `ContentDocument`.

## DEC-010 — Живые поля на `Recipe`

Status: accepted · 2026-09-05

`title`, `slug`, словари, статус, FTS — на `Recipe`. `RecipeRevision` — история, не таблица каталога.

## DEC-011 — `ё` не через `unaccent`

Status: accepted · 2026-09-05

Стандартный `unaccent` не переводит `ё`→`е`. Функция `normalize_ru` + `to_tsvector('russian')` + `pg_trgm`. Подробности — DATA-MODEL.

## DEC-012 — Семейство на одном slug

Status: accepted · HUMAN 9.1 · 2026-09-05

Одно блюдо = один `Recipe.slug`. Добавки — `RecipeVariant` `axis=addon` с дельтами. Не четыре карточки в книге. V1 `title`+`text` → `has_delta=false`, состав не врать.

## DEC-013 — Посуда отдельной осью

Status: accepted · HUMAN 9.2 · 2026-09-05

`equipment` — свой словарь и свой переключатель, не в списке «с грибами». Коды — VOCAB. `cook_method` фильтр матчит и `cook_method_override` варианта посуды.

## DEC-014 — Отрубы — фильтр базы

Status: accepted · HUMAN 9.4 · 2026-09-05

`allowed_cuts` на рецепте, query `cuts=`. Не чип семейства. Подписи — бытовые РФ. ETL 43 не угадывает. Рыба/овощи в этот enum в спринте 2 не входят.

## DEC-015 — Спринт 2: заморозка развилок черновика

Status: accepted · фраза «следующий шаг» 2026-09-05

Пока человек не сказал иначе:

1. Якорь на базе; `replace` якорной строки наследует якорь.
2. Шаринг карточки — query `?variant=&equipment=` на `/recipes/<slug>`, не path.
3. Оси независимы (порядок сборки DATA-MODEL). Query `energy=` в спринте 2 нет.
4. Аддоны взаимоисключающие.
5. Аллергены карточки каталога — худший случай по addon-дельтам.
6. `step_delta.remove` нет; выкинуть этап — `replace` текста.
7. Граммы кладовки / автокорзина — V2.2. Простой `have=` без граммов — DEC-017.

## DEC-016 — Главная ≠ калькулятор

Status: accepted · чат 2026-09-05

`/` — короткий вход + случайные рецепты и советы на каждый запрос. Подбор — только `/calculator` (DEC-018: задача, не полотно фильтров). Пункт шапки «Калькулятор» ведёт на `/calculator`, логотип — на `/`. Канон — [UX-PROPOSAL.md](UX-PROPOSAL.md).

## DEC-017 — Калькулятор собирает CookingSolution

Status: accepted · чат 2026-09-05 («не откладываем. основа готова»)

Один slug + дельты, не клоны JSON. Выдача калькулятора — версия с осями, не семейство на базе. Простой pantry: `have=` без граммов и без аккаунта, в этом срезе. Три корзины только при `have=`. Граф замен в Postgres, не runtime LLM. Граммы, срок, корзина — V2.2.

Следствие: HUMAN 9.3 уточнён. Ссылка с карточки подбора несёт `?equipment=&variant=`.

## DEC-018 — Калькулятор = задача, не анкета VOCAB

Status: accepted · чат 2026-09-05 (скрин полотна фильтров)

Первый экран `/calculator` — «что есть» + сценарий (`intent`), не ряды основа/способ/посуда/40 продуктов. VOCAB и оси остаются во внутреннем query и в книге. Выдача — одно featured + альтернативы с «почему», не сетка каталога. Не решать это аккордеоном над старым полотном. Минут 15/30 нет, пока нет поля времени. Шапка D+ не менять.

## DEC-019 — Кладовка = словарь покупки, не VOCAB и не текущие 43

Status: accepted · чат 2026-09-05

Каноны супермаркета живут в `pantry_vocab.py` (`SHOPPING_GROUPS`, `HAVE_GROUPS`, `PANTRY_ASSUMED` / `PANTRY_COMMON`). Это не `protein_base`. UI показывает грубые группы и likely-позиции, не 150 кнопок. `рыба` не пустая. `свинина` ≠ `pork_neck`. `масло` не резолвится однозначно. `water_or_stock` — не товар.

## DEC-020 — Эталон оверлея: профиль, не квота вариантов

Status: accepted · чат 2026-09-06 (комментарий к бархатной говядине)

JSON `barhatnaya-govyadina-po-kitajski` — эталон карточки 2.0 для остальных 43.

1. Уровни A/B/C: обязательны классификация, состав, шаги, scale, safety; профиль времени/effort/washing/`use_cases`; адаптивность только где есть смысл.
2. `variants` 0–10, не квота «три штуки». Variant ≠ adaptation.
3. `adaptations[]` — заранее разрешённые операции калькулятора. Runtime не выдумывает смену посуды.
4. Аллергены и канон — таблица `Ingredient`. `new_ingredients` только заявка.
5. `use_cases` — фиксированный VOCAB, не теги V1.

Полные роли `required`/`substitutable` на каждой строке — ещё не в Postgres. Ranking `intent=` по минутам не переключали: у ETL V1 `time_*` null. Чипы 15/30 (DEC-018) по-прежнему не врать по всему каталогу.

## DEC-025 — Аккаунт поверх гостя

Status: accepted · чат 2026-09-07 (ТЗ по черновику ACCOUNTS)

1. Гость умеет книгу, калькулятор, «У меня», cook mode без входа. Аккаунт — сохранить и написать.
2. Passwordless: российские TLD, OTP+ссылка, GET не логинит, в БД только хеш, сессия Django в Postgres. Не JWT, не 401 на гидратации гостя (`200` `{authenticated:false}`; мутации `403`).
3. Четыре сущности: избранное, cook report, оценка, комментарий. Кладовка V2.1 — факт `canonical`/`have_group`, кнопка сохранить, не «У меня» и не кнопка на карточке рецепта.
4. ISR без PII и без летучих счётчиков. `community_confirmed` — поле `Recipe`, считает сервис (≥3 разных user).
5. Реализация тремя срезами A → B → C, затем V2.2 граммы и фото. Кастомный `User`, FK на `Recipe`, не slug как ключ.
6. D+: «Войти» в служебном хроме, не пятый таб.

Следствие: HUMAN 3.9 («аккаунт V2.2») читается как глубокая кладовка/корзина, не запрет войти в V2.1. HUMAN 12 — ответы в §10 HUMAN.

Хозяин плана: [ACCOUNTS.md](ACCOUNTS.md).

## DEC-026 — Слой «На неделю»

Status: accepted · чат 2026-09-09 (HUMAN §11 + старт кода)

1. Пятый таб шапки/таббара — **«На неделю»**, URL `/prep`. «Войти» не таб.
2. `Recipe` хранит только тело «с нуля». Будничные шаги — на `PrepSlot` (и `alternatives[].steps`), не `PrepRecipeBody`.
3. Гостю без входа. Пилот: готовые наборы, editorial замены. Солвер вс и сбор калькулятором — не в рантайме.
4. Пустой каталог — 200 и «Наборы пока не загружены». Демо-наборов в коде нет.

Канон: [DATA-MODEL.md](DATA-MODEL.md), [API.md](API.md), [UX-PROPOSAL.md](UX-PROPOSAL.md) §6.4–6.5. Черновики продукта: [drafts/WEEKLY-PREP.md](drafts/WEEKLY-PREP.md).

