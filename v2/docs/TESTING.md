# Проверки 2.0

«Готово» = этот список, не впечатление агента. Задача среза — [../CURRENT_SPRINT.md](../CURRENT_SPRINT.md). Контракты: [DATA-MODEL.md](DATA-MODEL.md), [API.md](API.md).

Compose в `v2/infra`. Unit — без него; E2E/acceptance — на поднятом срезе `:8080`.

## Unit (pytest, Django)

Формулы масштаба и КБЖУ — pytest Django. Клиентский порт КБЖУ ≡ Django (U33).

| id | Проверка |
|----|----------|
| U1 | `gentle`: `amount * ratio**0.7`, не `1+(ratio-1)*0.5` |
| U2 | `linear`: `amount * ratio` |
| U3 | `whole`: целое, min 1 |
| U4 | `manual` и `scalable=false`: amount не меняется |
| U5 | округление DEFAULTS (г/мл шаги, шт 0.5, ч.л. четверти) |
| U6 | `normalize_ru`: `ёлка` ≡ `елка` для поиска |
| U7 | аллерген: `unknown` не схлопывается в «нет» |
| U8 | оба `servings` и `anchor_weight` → отказ сервиса (как `400` API) |
| U9 | нет якоря и нет servings → scaling off, порции не выдумываются |
| U10 | сборка: addon `has_delta=true` меняет display; `has_delta=false` — состав базы |
| U11 | неизвестный `variant` / `equipment` / `cuts` → отказ как `400` |
| U12 | `notes` после ETL — список объектов, не строка |
| U13 | масштаб **после** дельты: якорь базы, добавленный ингредиент × ratio |
| U14 | строка «для подачи» / «по желанию» (`optional`) не входит в `allergens` блюда; обязательный йогурт — входит |
| U15 | способ `oven` у семейства-тушения с `cook_method_override` → решение с этой посудой, не база |
| U15b | основа `beef` у семьи-птицы с addon `protein_base_override=beef` → решение с этим чипом, не база |
| U16 | `have` закрывает ядро → `bucket=now`; одна нехватка → `almost`; `score` не попадает в `why` |
| U16b | ядро закрыто заменой → why «можно приготовить с заменой», не «сейчас» |
| U17 | замена `quality` ≥ 0.50 подставляется; `forbidden` и низкий quality — нет |
| U18 | неизвестный `have` → отказ как `400` |
| U19 | валидатор оверлея: эталон 0 ошибок; `gentle` у соды — ошибка; `sol-chef.ru` — ошибка; нет `time_profile` — ошибка; чужой `use_case` — ошибка |
| U20 | `have=beef_mince`: бонус «есть …» только если ядро фарша закрыто; стейк и масло не featured / не «Быстрее»; нет использующих — `featured is None` |
| U20b | замена закрывает ядро: why «есть» канон из кладовки (бёдра, рибай, лопатка, шалот, яйцо), не строка рецепта |
| U21 | два явных `have=`: блюдо из обоих выше блюда из одного; `have_group=meat,beef` не раскрывает весь `meat`; у говядины есть вырезка, рёбра, мякоть |
| U21c | `have_group=beef` не ставит featured заготовке `govyadina-na-volokna-s-garnirom`; ядро `shredded_beef` не в сырой говядине; без `have=shredded_beef` солвер её отбрасывает |
| U21d | `have_group=prep` раскрывает `shredded_beef`; солвер находит leftover; чипы вида без «говяжья», `beef` → «Любая говядина», с большой буквы |
| U21e | `have_group=other` не раскрывается; `canned` раскрывается без тунца; сухие бобовые без банок; сметана/масло не в соусах/жирах; `offal` в UI — «Субпродукты» |
| U22 | без `have=` масло/`sauce` с высоким баллом не featured и не «Быстрее», если есть блюдо; если в пуле только заготовки — они остаются |
| U39 | `intent=fast`: меньше `time_total_minutes` выше по баллу; блюдо с большим временем не отсекается |
| U40 | решение отдаёт `time_profile`; аллергены JSON — комбо, не обязательно худший случай семьи |
| U41 | пустой `GET /api/recommendations/` — `featured: null`, без queryset каталога |
| U42 | снимок оси: `snapshot_fits` как `combo_fits`; при `axis_snapshots` `assemble` не вызывается |
| U23 | сумма трёх строк в граммах: `(n/100)*g`; kcal с канона, не Atwater 4/9/4 |
| U24 | `gentle` на масле: nutrition после `apply_mode`, не `total * ratio` |
| U25 | нет `servings` → `per_serving is None` |
| U26 | вода супа в знаменателе `per_100g_input`, 0 в макросах; ккал не ноль из-за мяса |
| U27 | `nutrition_exclude`: не в числителе и не в массе |
| U28 | `optional` не в сумме КБЖУ (как U14 для аллергенов) |
| U29 | `tbsp` без `g_per_tbsp` → `incomplete`; глобальная 15 г не применяется |
| U30 | дельта `has_delta` меняет total; `has_delta=false` — база |
| U31 | ключ `kcal` в JSON автора → ошибка валидатора |
| U32 | `to_taste` соли не делает `incomplete` и без иконки; перец `pinch` без иконки; мёд `to_taste` — не incomplete, иконка есть; масло/мёд `to_taste` разрешены валидатором |
| U33 | клиентский порт ≡ U23–U24 |
| U34 | диапазон 1–2 tbsp: nutrition по `amount`=1, не по max и не по середине |
| U35 | JSON API не содержит ключа `per_100g` / `per_100g_raw`; без yield `per_100g_cooked` есть и равен `null` |
| U36 | `nutrition_factor=0.5` на масле уменьшает вклад вдвое; не авто-0.5 |
| U37 | `yield_weight_g=500`, `ratio=2`, `scaling_enabled=True` → знаменатель cooked 1000 г; `per_100g_cooked` ≠ `per_100g_input` |
| U38 | нет `yield_weight_g` → `per_100g_cooked is None` |
| U51 | `GET /api/prep-kits/` без наборов → 200 `{ "results": [] }` |
| U52 | список только `published`, порядок `position` затем `slug` |
| U53 | импорт: 14 слотов → kit `published` |
| U54 | импорт: чужой `container_ids` / unpublished / reheat вперёд / reheat не со вчера → отказ |
| U55 | рецепт без `prep` — книжные шаги |
| U56 | `prep` без day/meal при двух слотах одного slug → 400 |
| U57 | `prep`+day+meal → шаги этого слота, `mode` в `prep_context` |
| U58 | `servings` набора меняет qty контейнера №2, не число контейнеров; `servings=1` при базе 2 даёт половину |
| U59 | alternative.slug с тем же day/meal → `alternatives[].steps`, не 400 из‑за FK слота |
| U60 | `anchor_weight` + `prep` → 400 |
| U61 | `?no_leftover=1`: `reheat` → `no_leftover` блюдо (slug не из 14 слотов); без флага слот остаётся `reheat`; `prep`+day+meal на slug замены без флага → 400, с флагом — `no_leftover.steps`; импорт без `no_leftover` у reheat или с дублем сетки → отказ |

## Integration

| id | Проверка |
|----|----------|
| I1 | `import_v1 --dry-run` видит **43** рецепта (канон DEFAULTS) |
| I2 | `import_v1` в транзакции пишет 43 `Recipe`; повтор — upsert, count остаётся 43 |
| I3 | обрыв посередине (тест с ошибкой на N-й записи) → 0 частично записанных |
| I4 | нет ключа в сиде ингредиентов → команда падает |
| I5 | птица/свинина/рыба без target в сиде температур → падает |
| I6 | 5 `ContentDocument` (grains, tips, beef, pork, poultry) |
| I7 | `GET /api/recipes/?protein_base=poultry&cook_method=oven` — AND между ключами |
| I8 | два `protein_base` — OR внутри ключа |
| I8b | `GET /api/recipes/?protein_base=beef` отдаёт шаурму с `protein_base=poultry` и чипом `protein_base_override=beef` |
| I9 | `GET /api/recipes/<slug>/?anchor_weight=` меняет `display_amount`, не шаги/температуры |
| I10 | FTS: запрос с `е` находит заголовок с `ё` и наоборот |
| I11 | каталог не использует `__icontains` (grep по коду поиска) |
| I12 | `GET /api/recipes/?equipment=` AND с `protein_base`; неизвестный код → 400 |
| I12b | `GET /api/recipes/?equipment=air_fryer` попадает в семью, где ось посуды — `code=air_fryer` без сосуда; карточка несёт `cook_methods` с `air_fryer` |
| I13 | рецепт с только legacy-вариациями: `available_variants[].has_delta=false`, ингредиенты базы |
| I14 | `import_draft --check --path` зелёный на эталоне `tests/fixtures/gold_overlay.json` |
| I15 | `import_draft --accepted` без JSON — «Черновиков нет», код 0; битый файл в пачке пропускает; `--path` падает |
| I16 | `GET /api/recipes/?page_size=` сужает страницу; без параметра размер **20**; больше 500 режется до 500; `sample=` отдаёт N случайных, неверный sample → 400 |

## E2E (Playwright, через Caddy `:8080`)

| id | Маршрут | Что сделать |
|----|---------|-------------|
| E1 | `/` | витрина: вход в калькулятор, случайные рецепты и советы; без query и без ряда фильтров; повторная загрузка может дать другой набор |
| E2 | `/calculator?have_group=chicken&intent=fast` | одно главное решение + альтернативы; «почему»; ссылка несёт ось, если решение не база |
| E3 | `/calculator?protein_base=seafood` | empty-state «Ничего не подошло» (после ETL V1 пусто) |
| E4 | `/recipes` | книга, поиск |
| E5 | `/recipes/<slug>` с якорем | «У меня» меняет числа **без** перезагрузки всей страницы; числа с API |
| E6 | `/recipes/<slug>` без масштаба | нет ползунка, 200 |
| E7 | cook mode | таймеры шагов, Wake Lock не ломает страницу |
| E8 | `/grains` `/meat` `/meat/beef` `/tips` | контент из API, не 404 |
| E9 | `/recipe.html?id=stejk-na-skovorode-pan-searing` | 301/redirect на `/recipes/stejk-na-skovorode-pan-searing` |
| E10 | 390px | осторожно / «У меня» / cook mode видны |
| E11 | фильтр с 0 рецептов в книге | «Ничего не найдено», не заглушка «скоро» |
| E12 | `/recipes` | оглавление: мясо, птица, овощи, рыба и морепродукты, гарниры, завтраки, десерты, другое; яичница в завтраках; `/recipes?chapter=breakfasts` сразу сетка |
| E13 | `/calculator` | поле «что есть», грубые чипы, сценарии; нет полотна Основа/Способ/Посуда/Есть · мясо |
| E14 | рецепт, ≥1280 | cook mode: две колонки или видимая лента шагов; setup |
| E15 | рецепт с якорем | «У меня»: имя якоря, поле в граммах (или мл), сброс видны; нет г↔кг |
| E16 | шапка и таббар | иконка + подпись; favicon не дефолт Next |
| E17 | `/calculator?have=` | featured: сейчас / докупить словами; не процент совпадения |
| E17b | `/calculator?have=chicken_thighs` | why не «есть куриная грудка»; ссылка «Посмотреть все подходящие» ведёт на `/recipes?chapter=poultry` |
| E18 | карточка калькулятора | клик открывает `/recipes/<slug>` с осями решения |
| E19 | `/calculator?have=beef_mince` и `+intent=oven` | не reverse-sear / не масло; empty state, пока в каталоге нет блюда с фаршем |
| E20 | `/calculator` Мясо | карточка «Мясо»; говядина — вложенный блок с путём и короткими чипами; Полуфабрикаты — сосед вида; Субпродукты, не «Другое» |
| E20b | `/calculator` Другое | полки бобовые / консервы / заморозка / хлеб / соусы / масло; не плоский ряд; тунец не в консервах |
| E21 | `/calculator?intent=fast` | featured не взбитое масло и не другое `sauce`; обычное блюдо |
| E22 | `/recipes/barhatnaya-govyadina-po-kitajski` | блок КБЖУ; слайдер «У меня» и чип (если есть) двигают числа; не фильтр калькулятора `kcal_max` |
| E23 | `/recipes/<slug>` с legacy-вариациями | секция «Вариации» списком как заметки, не `<details>` / не `<summary>` |
| E24 | `/recipes/<slug>` чип вариации или посуды | страница не прыгает наверх; URL помнит оси |
| E25 | `/prep` | empty-state «Наборы пока не загружены», не «скоро»; пятый пункт шапки/таббара «На неделю» активен |
| E26 | `/prep/<slug>` неизвестный | 404 |
| E27 | рецепт с `?prep=` | контейнеры и глагол mode; cook mode по шагам слота, не книги |
| E28 | `/tips` | поле поиска; фильтр по `kind` прячет чужие карточки; `?q=` на клиенте (не Django FTS, не `__icontains`, без нового API); `#tip-06-01` открывает эту карточку |

В бандле frontend нет `Math.pow` / `ratio ** 0.7` вокруг количеств (grep).

## Регрессия V1

| id | Проверка |
|----|----------|
| R1 | из `archive/v1/` `python -m http.server 3456` открывает архивный V1 |
| R2 | не изменены файлы в `archive/v1/` (кроме явной просьбы про архив) |
| R3 | Next/Django не читают JSON архива в рантайме (только ETL) |

## Acceptance среза — PASS / FAIL

Отмечать при сдаче, не заранее.

| # | Критерий | |
|---|---------|--|
| A1 | `docker compose -f v2/infra/docker-compose.yml up --build` → http://localhost:8080 | |
| A2 | dry-run ETL = 43 | |
| A3 | import пишет 43 и 5 справочников | |
| A4 | витрина, калькулятор, каталог, рецепт с «У меня», cook mode | |
| A5 | крупы / мясо / советы открываются | |
| A6 | поиск ё/е | |
| A7 | 301 со старого URL | |
| A8 | `/admin/` отдаёт статику (WhiteNoise или runserver) | |
| A9 | архив V1 на `:3456` из `archive/v1/` (не прод) | |
| A10 | гость проходит книгу / калькулятор / cook mode **без входа**; нет печати и «скоро»; формула масштаба на карточке = Django, не V1 `0.5` |
| A11 | книга ≠ калькулятор (оглавление по смысловым разделам + список в главе vs задача) | |
| A12 | legacy-вариации не подменяют состав | |
| A13 | «У меня»: имя якоря, factor, сброс; единица всегда г/мл, без г↔кг | |
| A14 | cook mode desktop не телефонный столбец | |
| A15 | шапка и таббар: иконка + подпись; favicon V1 | |
| A16 | API `equipment` / `notes[]` / `applied_axes` | |
| A17 | ETL 43: варианты addon без дельты, `allowed_cuts=[]` | |
| A18 | V1 на `:3456` после правок 2.0 | |
| A19 | калькулятор открывает выбранную ось, не всегда базу | |
| A20 | калькулятор не вываливает VOCAB; книга — смысловые разделы, не алфавит | |
| A21 | `have=` даёт «докупить» названиями, не процентом; featured не сетка | |
| A22 | неизвестный `have` → 400 |
| A23 | `/prep` открывается; пустой список не «скоро»; шапка из пяти пунктов | |

Нет Compose — срез не готов, даже если документы полные.

## V2.1 аккаунты

Только когда CURRENT_SPRINT про A/B/C. Гостевой список выше после каждого среза — зелёный.

### Unit

| id | Проверка |
|----|----------|
| U40 | Gmail / `proton.me` → отказ валидатора; `user@mail.ru` проходит |
| U41 | GET confirm не ставит `used_at` и не создаёт сессию |
| U42 | POST magic-login и верный OTP создают сессию; 6-я попытка OTP мертва |
| U43 | в `AuthToken` нет сырого OTP / link token (только хеш 64) |
| U44 | unique избранного; повтор cooked — вторая строка |
| U45 | `PUT /pantry/` не принимает граммы и неизвестный `have` |
| U46 | среднее `null` при 2 оценках; число при 3 |
| U47 | 1-й комментарий пользователя — `pending`; 6-й без стоп-слова — `approved` |
| U48 | 3 разных user approved cook report → `community_confirmed`; два от одного — нет |
| U49 | удаление аккаунта: избранное стерто, комментарий `deleted`, email не рабочий |
| U50 | ETL upsert не затирает живой `community_confirmed` / `editorial_tested` |

### E2E

| id | Что сделать |
|----|-------------|
| E30 | книга и cook mode без сессии как E4–E7 |
| E31 | `/login` + письмо Mailpit: GET ссылки не в кабинете; POST — в |
| E32 | избранное на карточке переживает reload |
| E33 | «Готово!» без клика «я приготовил» не пишет отчёт |
| E34 | logout: калькулятор с `have=` в URL жив |
| E35 | шапка D+ без пятого таба; «Войти» справа |
| E36 | новый комментарий не требует пересборки HTML рецепта (ISR/тело без текста отзыва) |

### Acceptance V2.1

| # | Критерий |
|---|----------|
| Auth-A | Mailpit в compose; OTP и POST-ссылка; GET не логинит |
| Auth-B | избранное, готовил, кладовка-кнопка; гость на `have=` |
| Auth-C | оценки, премодерация 5, жалобы в Admin, порог community_confirmed |
