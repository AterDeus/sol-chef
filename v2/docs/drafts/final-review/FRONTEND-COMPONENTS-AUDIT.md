# Внешний аудит `frontend/components` — разбор по канону

Источник: [fixes/frontend_components_audit_fixes.md](fixes/frontend_components_audit_fixes.md) (чат 2026-09-20). Дамп кода: [FRONTEND-COMPONENTS.md](FRONTEND-COMPONENTS.md).

Канон экранов: [UX-PROPOSAL.md](../../UX-PROPOSAL.md). Масштаб: [DEFAULTS.md](../../DEFAULTS.md), [API.md](../../API.md) DEC-021. Фильтры URL уже есть: `frontend/lib/filters.ts`.

Код не менять из этого файла, пока человек не скажет «стартуй».

---

## Вердикт коротко

Аудит попал в реальные дыры UX: `FilterChip` — кнопка вместо ссылки; таймер готовки тикает `remaining - 1`; у `CookMode` самодельный диалог и дырявые side effects; глобальный `pending` у осей; ввод масштаба глотает промежуточный текст; pantry fetch без отмены и без `res.ok`.

Часть предложений **уже канон или уже сделана** (клиентский порт формулы «У меня»; слой `setHref`/`toggleHref`; живой поиск книги). Часть **ломает принятый экран** (масштаб через `router.replace` на каждый ввод; поиск только по Submit). Крупный split на `features/*` и TanStack Query — не этот срез.

Спринт сейчас — DNS/HTTPS cutover. Это бэклог качества после домена, не блокер релиза.

---

## P0 — чинить, не ломая канон

| # | Аудит | По канону / коду | Решение |
|---|--------|------------------|---------|
| 3 | `FilterChip` = `<button>` + `router.push` | Правда. Href уже строится в `lib/filters.ts` (`toggleHref` / `setHref`, с `DROP_WHEN` и CSV). Чип просто не ссылка. TESTING E11/E12, UX: фильтр = навигация. | Заменить на `<Link>`, `pressed` → `selected`, `aria-current="page"`. Не писать новый `withSearchParam`: он не знает `DROP_WHEN` (глава сбрасывает основу/способ/посуду) и сломает книгу. Тот же паттерн: чекбокс «Без вчерашнего» в `PrepKitView` — `router.push` вместо ссылки. |
| 5 | Таймер `setInterval(remaining - 1)` | Правда. После sleep/throttling вкладки показания врут. UX-PROPOSAL: старт/пауза/сброс, тост если нет вибрации. | Хранить `endsAtMs`, остаток = `max(0, endsAt - Date.now())`. Пауза — remaining ms. Один сигнал завершения. Не трогать UX кнопок ±. |
| 6 | Toast без cleanup, wake lock, datetime mixed | Правда. `showToast` ставит timeout без отмены; `datetime-local` — `defaultValue`, не `value={startMs}`; пустой `steps` даёт деление на 0 («Шаг 1 из 0»). | Toast в ref + unmount; wake `desired` сбрасывать на close; input controlled; при `steps.length === 0` не входить в шаги / не считать прогресс. `<dialog showModal>` вместо самодельного trap — да, native, **без Radix** (новая зависимость на cutover не нужна). |
| 10 | Числовой input масштаба | Правда. `onChange` пишет state только при валидном `n > 0` — нельзя стереть поле и набрать `0,5`. | Raw string + commit на blur/Enter. **Локально**, не в URL. DEFAULTS: «Запрос на каждый шаг слайдера не делать». |

---

## P1 — реальные баги, меньший вред

| # | Аудит | По канону | Решение |
|---|--------|-----------|---------|
| 8 | `pending` на module scope в `RecipeAxisSwitch` | Правда. На странице рецепта обычно один экземпляр, но гонка при быстрых кликах / Back возможна. TESTING E24: страница не прыгает наверх. | Instance `useRef`. `scroll={false}` уже стоит. Не убирать restore, пока E24 зелёный. У `Link`: оставить `aria-current`, убрать `aria-pressed`. |
| 11 | Pantry: дубль `pathForHave`, `getElementById`, нет abort/`res.ok` | Правда. `clientFetch` уже умеет timeout-abort 8 с, но предыдущий submit не отменяет. `id="pantry-text"` на калькуляторе один, конфликт id слабый. | Один `pathForHave` в `lib/`. `useRef` на textarea. Abort предыдущего + cleanup. Проверять `res.ok` (обёртка уже есть рядом: `fetchRecipeClient`). **Не** вводить TanStack Query: клиентских запросов один. |
| 14 | `PrepKitView`: `find` в цикле дней; вкладки не в URL | `find` на ~14 слотах — шум, не perf. Вкладки в UX-PROPOSAL есть, query `?tab=` **нет**. Шаринг раздела набора нигде не обещан. | `slotsByDay` — да, дёшево. `?tab=` — только если человек хочет ссылку на «Воскресенье». Пока не делать. ARIA tabs: сейчас `role="tablist"` без `aria-controls`/панелей — поправить разметку, не обязательно URL. |
| 7 | Пустые шаги / keys из индекса | `RecipeStep` в API **без id** (только text/timer/temps). Шаги не reorder’ятся в сессии. Ключ из текста prep ломается при дублях. | Пока `key={\`${index}-${item.text.slice(0,24)}\`}` или позиция после assemble. Новый `step.id` в Django — отдельный контракт API, не «заодно». Completed — `Set` по индексу ок, пока шаги статичны. |

---

## Не внедрять «заодно»

| Аудит | Почему нет |
|--------|------------|
| §1 Split всех экранов на `features/recipes-book/` + container/hooks/UI | CookMode 533 и TipsView 525 правда толстые. RecipesBook 330 — фильтры + сетка, не god-object. RecipeCard 257 — четыре экспорта в одном файле. **Не** плодить `features/` на cutover: это переезд папок, регресс E2E, без новой функции. Дробить CookMode — да, когда чиним таймер/dialog, в текущем `components/`. |
| §2 Новый универсальный URL-state вместо текущего | Слой уже есть: `FILTER_KEYS`, CSV, `toggleHref`, `setHref`+`DROP_WHEN`, `toggleHaveGroupHref`, `recipeHref`. Предложенный `withSearchParam` сортирует multi-values и не сбрасывает зависимые ключи — разъедется с книгой и калькулятором. Чинить call sites (`FilterChip` → `Link`), не хелпер. |
| §8 «Предпочтителен серверный контракт» масштаба | **Ломает канон.** DEFAULTS / API DEC-021 / UX-PROPOSAL: «У меня» считает на клиенте (`lib/scale.ts` ≡ Django), слайдер без запроса. Query `anchor_weight`/`servings` — шаринг и тесты, не каждый клик ±. Второй вариант аудита (одна TS-библиотека + contract tests против pytest) — как раз то, что уже задумано. Дыра: `number` vs Django `Decimal`. Лечить fixture-тестами порта, не `router.replace`. |
| §12 Submit-first поиск книги | **Откат недавнего UX.** STATUS 2026-09-20: книга — живой поиск. Форма submit уже есть, плюс debounce 250 мс в URL. Гонка `q` / `qLive` / Back — чинить синхронизацию с `useSearchParams` + `startTransition`, не убирать live. |
| §16 `next/image` на PageArt | Декор `aria-hidden`, `loading=eager` только на главной. `output: 'standalone'`, в `next.config` нет `images`. `?v=9` — запах, вынести константу. `next/image` + `sharp` в prod-образе — отдельная проверка Docker, не блокер LCP cutover. |
| §18 TanStack Query / SWR | Аудит сам пишет: не вводить без нужды. Один fetch pantry. |
| `@radix-ui/react-dialog` | Native `<dialog>` достаточно. Новая UI-библиотека на 8 ГБ ВМ не нужна. |
| Стабильные `id` шагов в API | Меняет сериализатор Django и, возможно, ETL. Пока ключи из позиции. |
| `?tab=` у набора | Новая IA шаринга. Человек не просил. |
| Центральный endpoint опубликованных guides | Справочник — четыре статических маршрута. Дубли Header/Footer/GuideStrip — вынести массив в `lib/navigation.ts`, без бэкенда. |
| Массовый вынос inline styles + clsx | Вместе с правкой CookMode, не отдельным CSS rewrite. |

---

## Что аудит завысил

- **«Нет единого слоя URL».** Есть `lib/filters.ts` (~236 строк) и `lib/catalog.ts`. Компоненты ещё зовут `router.push`/`window.location` точечно (поиск книги, pantry, leftover checkbox) — это call-site баги, не отсутствие контракта.
- **«Каталог на каждом render считает counts заново».** 255 карточек, несколько проходов — не CPU-кризис. Вынести `buildRecipesBookModel` как чистую функцию с тестами — полезно и дёшево; мемоизация «на росте каталога» не срочно.
- **TipsView 525 строк** в списке проблем, но правок нет. Там masonry + `history.replaceState` + клиентский `?q=` (TESTING E28). Не смешивать с FilterChip.
- **Keys из индекса в CookMode** опасны при reorder; шаги готовки не переставляются. Реальный риск — чекбоксы prep/tips при дублях текста.

---

## Масштаб и числа — отдельно от UI-рефактора

Канон уже выбрал порт, не roundtrip:

```text
Django apply_mode / roundScaled  ≡  frontend/lib/scale.ts
Django nutrition Decimal         ≡  frontend/lib/nutrition.ts  (number)
```

Аудит прав, что `number` разъедется с `Decimal` на краях. Неправ, что лечится серверным запросом на каждый ввод.

Порядок:

1. Починить ввод (raw string) — UX.
2. Сверить порт с pytest-фикстурами DEFAULTS (г/мл шаги, `gentle = ratio^0.7`, КБЖУ до `roundScaled`). TESTING grep «в бандле нет `ratio ** 0.7`» **устарел**: формула в `lib/scale.ts` — канон DEFAULTS, не запрет.
3. Не копировать V1 `1+(ratio-1)*0.5`. В коде уже `GENTLE_EXPONENT = 0.7`.

---

## Рекомендуемый порядок, если стартовать

Не «7 этапов архитектуры». Три коротких пакета:

1. **Ссылки и ввод.** `FilterChip` → `Link`; leftover toggle ссылкой; decimal input «У меня»; `pathForHave` + abort pantry; `pending` осей в ref.
2. **CookMode без смены экрана.** Native dialog, deadline-таймер, toast/wake cleanup, пустые шаги. При разбиении файла — те же классы UX-PROPOSAL (setup / шаги / обзор / ±).
3. **Книга без смены UX.** Чистый `buildRecipesBookModel` + тесты порядка фильтров; live search синхронизировать с URL, не переводить на submit-only.

Тесты: unit на `filters.ts` и selector книги — да. a11y dialog и E2E background-timer — когда появится фронтовый раннер (сейчас TESTING — pytest + смоук HTTP, vitest/playwright нет). Не ставить Playwright «чтобы закрыть аудит».

---

## Вне канона этого среза

- DNS / HTTPS / пуш `main` — CURRENT_SPRINT, этот аудит не блокирует.
- Волны рецептов и оверлей осей — не смешивать.
- Публичный Next `app/api` по-прежнему нельзя; pantry ходит в Django через `clientFetch` / `NEXT_PUBLIC_API_URL`.
