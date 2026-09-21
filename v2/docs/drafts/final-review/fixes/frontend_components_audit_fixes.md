# Правки по аудиту `frontend/components`

## Список проблем

1. Крупные компоненты смешивают UI, состояние, URL-навигацию, расчёты, доступность и бизнес-логику: `CookMode.tsx` (533 строки), `TipsView.tsx` (525), `RecipesBook.tsx` (330), `PrepKitView.tsx` (285), `IngredientsBlock.tsx` (271), `RecipeCard.tsx` (257), `CalculatorAsk.tsx` (248).
2. Повторяется логика работы с query params, URL и selection state; компоненты напрямую создают href или используют `router.push`, что размывает единый контракт фильтров.
3. Интерактивные фильтры реализованы через `<button>` + `router.push`, хотя состояние находится в URL; это ломает нативные возможности ссылок (открытие в новой вкладке, copy link, prefetch) и ухудшает progressive enhancement.
4. `CookMode` реализует диалог вручную вместо нативного `<dialog>` или проверенного dialog primitive; есть риски с focus trap, закрытием при backdrop click, aria, вложенными модалками и scroll lock.
5. Таймер в `CookMode` уменьшает значение раз в секунду через `setInterval`; после background throttling, sleep или долгого зависания вкладки показания будут неверными.
6. `CookMode` содержит разрозненные side effects и таймеры: timeout toast не очищается, wake-lock lifecycle не полностью привязан к закрытию/visibility, состояние старта и datetime input смешивают controlled/uncontrolled режимы.
7. В `CookMode` нет надёжной обработки пустого списка шагов: прогресс делит на `steps.length`, а UI может показать «Шаг 1 из 0».
8. `RecipeAxisSwitch` использует глобальную mutable-переменную `pending`, несколько `requestAnimationFrame` и ручной scroll restoration; при нескольких экземплярах, отменённой навигации или быстрых кликах возможно восстановление чужой позиции.
9. `IngredientsBlock` хранит расчётные данные в `number`, выполняет локальное масштабирование и KBJU на клиенте; возможны расхождения с backend Decimal-правилами, округлением и variant/prep-режимами.
10. Ввод масштаба теряет промежуточные состояния: невозможно нормально стереть значение или ввести `0,5`, если промежуточное значение невалидно; контролируемый input сразу отбрасывает ввод.
11. Компоненты используют индекс массива как key (`CookMode`, `PrepKitView`), а в отдельных местах ключи строятся из user/content text. При reorder/дублирующемся тексте React может сохранять состояние за неправильным элементом.
12. `PantryTextForm` дублирует `pathForHave` из `CalculatorAsk`, а `document.getElementById('pantry-text')` создаёт риск конфликтов идентификаторов и обходит ref-модель React.
13. `PantryTextForm` не отменяет предыдущий запрос и не проверяет `res.ok`; медленный предыдущий запрос может перезаписать результат нового, а non-JSON error превратится в общий catch.
14. В `RecipesBook` URL обновляется через debounce на каждый ввод, а одновременно фильтрация выполняется на клиенте по `recipes`. Это создаёт гонки между `q`, `qLive`, серверными props и `router.replace`.
15. В `RecipesBook` расчёт counts/filter pools выполняется повторно на каждом render и не изолирован от представления; на росте каталога появятся лишние CPU-операции и сложные регрессии.
16. `PrepKitView` многократно ищет slots через `Array.find()` внутри цикла дней, а tab state не синхронизирован с URL/историей браузера; ссылкой нельзя открыть конкретный раздел набора.
17. Статические справочники маршрутов и контентные массивы дублируются в `Chrome.tsx`, `Guides`, `PageArt`, а часть доступных guide routes захардкожена вместо получения из единого route/config source.
18. `PageArt` использует обычный `<img>`, а не `next/image`; нет управления `sizes`, приоритетом LCP и централизованной стратегии версионирования файлов.
19. В компонентах есть inline styles и ручная строковая сборка классов, что затрудняет единообразие дизайна и дальнейшую поддержку.
20. Отсутствует единый слой client data fetching/error handling и тесты доступности, поведения URL, таймеров, навигации и производительности интерактивных экранов.

## 1. Разделить container и presentation компоненты

### Проблема

Большие компоненты одновременно содержат доменные вычисления, navigation state и JSX. Это делает их трудно тестируемыми и опасными для локальных правок.

### Правка

Для каждого крупного экрана разделите минимум на три уровня:

```text
Feature container        URL/state/fetch orchestration
Feature hooks/selectors  derived data, actions, pure calculations
Presentational UI        props → JSX, без router/window/document
```

Пример для списка рецептов:

```text
features/recipes-book/
  RecipesBook.tsx              # container
  useRecipesBookState.ts       # URL state + debounce
  selectors.ts                 # filter/count/chapter calculations
  RecipesBookSearch.tsx
  RecipesBookFilters.tsx
  RecipesBookToc.tsx
  RecipesBookResults.tsx
  types.ts
```

Целевой public component должен быть коротким:

```tsx
export function RecipesBook({ recipes, searchParams }: Props) {
  const state = useRecipesBookState(searchParams);
  const model = useMemo(
    () => buildRecipesBookModel(recipes, state.filters),
    [recipes, state.filters],
  );

  return (
    <section>
      <RecipesBookSearch value={state.query} onChange={state.setQuery} />
      <RecipesBookFilters model={model} filters={state.filters} onToggle={state.toggle} />
      <RecipesBookResults model={model} />
    </section>
  );
}
```

`buildRecipesBookModel()` должен быть чистой функцией с unit-тестами на входные recipes + filter state.

## 2. Сделать URL фильтров единым источником истины

### Проблема

Сейчас фильтры управляются разными способами: `Link`, `FilterChip` с `router.push`, скрытые поля формы, `router.replace`, прямой `window.location.search`. Это увеличивает риск разных форматов URL, потери параметров и некорректной browser history.

### Правка

Создайте типизированный URL-state слой на feature. Он принимает `ReadonlyURLSearchParams`, возвращает typed state и детерминированно строит href/action.

```ts
// features/filters/urlState.ts
export type FilterValue = string | readonly string[] | null | undefined;

export function withSearchParam(
  pathname: string,
  params: ReadonlyURLSearchParams,
  key: string,
  value: FilterValue,
): string {
  const next = new URLSearchParams(params.toString());
  next.delete(key);
  const values = Array.isArray(value) ? value : value ? [value] : [];
  for (const item of [...new Set(values)].sort()) next.append(key, item);
  const query = next.toString();
  return query ? `${pathname}?${query}` : pathname;
}
```

Все persistent filter controls должны получать `href`. Для toggle-фильтров предпочитайте `<Link>`, потому что selection — навигационное состояние.

```tsx
import Link from 'next/link';

export function FilterLink({ href, selected, children }: Props) {
  return (
    <Link
      href={href}
      className={selected ? 'chip is-active' : 'chip'}
      aria-current={selected ? 'page' : undefined}
    >
      {children}
    </Link>
  );
}
```

`button` используйте только для локального состояния, которое не должно попадать в URL: открыть popover, запустить таймер, сменить вкладку в диалоге.

## 3. Заменить `FilterChip` на ссылку

### Проблема

Текущий `FilterChip` вызывает `router.push(href)` из button. Пользователь не может открыть фильтр средней кнопкой/в новой вкладке, а SSR fallback отсутствует.

### Правка

```tsx
// frontend/components/FilterChip.tsx
import Link from 'next/link';
import type { ReactNode } from 'react';

export function FilterChip({
  href,
  selected,
  children,
  ariaLabel,
  hint,
}: {
  href: string;
  selected: boolean;
  children: ReactNode;
  ariaLabel?: string;
  hint?: string;
}) {
  return (
    <Link
      href={href}
      className={selected ? 'chip is-active' : 'chip'}
      aria-label={ariaLabel}
      aria-current={selected ? 'page' : undefined}
      title={hint}
    >
      {children}
    </Link>
  );
}
```

Обновите все callers: `pressed` → `selected`. Не используйте `aria-pressed` у ссылки: это состояние toggle-button, а не страницы/навигации.

## 4. Разбить `CookMode` и использовать надёжный dialog

### Проблема

В одном файле собраны modal lifecycle, focus trap, wake lock, planning, stepper, timer, toast, подготовка и два разных представления списка шагов. Самодельный focus trap легко ломается и не обрабатывает все сценарии нативного dialog.

### Правка

Разбейте feature:

```text
features/cook-mode/
  CookModeDialog.tsx
  useCookSession.ts
  useCountdown.ts
  useWakeLock.ts
  useFocusRestore.ts              # только если не применён native dialog
  CookSetup.tsx
  CookStepper.tsx
  CookTimer.tsx
  CookStepOverview.tsx
  CookToast.tsx
```

Предпочтительный вариант — `<dialog>` c `showModal()` / `close()`.

```tsx
'use client';

import { useEffect, useRef } from 'react';

export function CookModeDialog({ open, onClose, children }: DialogProps) {
  const ref = useRef<HTMLDialogElement>(null);

  useEffect(() => {
    const dialog = ref.current;
    if (!dialog) return;
    if (open && !dialog.open) dialog.showModal();
    if (!open && dialog.open) dialog.close();
  }, [open]);

  return (
    <dialog
      ref={ref}
      className="cook-root"
      aria-labelledby="cook-dialog-title"
      onCancel={(event) => {
        event.preventDefault();
        onClose();
      }}
      onClose={onClose}
    >
      {children}
    </dialog>
  );
}
```

Если нужен одинаковый UX в неподдерживаемых браузерах, используйте зрелый компонент с a11y-гарантиями (`@radix-ui/react-dialog`), а не собственный focus trap.

## 5. Переписать таймер на дедлайн, а не decrement

### Проблема

Таймер `setInterval(... remaining - 1)` отстаёт или ускоряется при throttling вкладки, sleep и перегрузке main thread. Это особенно критично в cooking mode.

### Правка

Храните абсолютный `endsAtMs`; на каждом tick вычисляйте остаток из текущего времени. Состояние паузы хранит remaining milliseconds.

```ts
// features/cook-mode/useCountdown.ts
import { useEffect, useMemo, useState } from 'react';

export function useCountdown() {
  const [endsAtMs, setEndsAtMs] = useState<number | null>(null);
  const [pausedMs, setPausedMs] = useState<number | null>(null);
  const [now, setNow] = useState(Date.now());

  const remainingMs = useMemo(() => {
    if (endsAtMs !== null) return Math.max(0, endsAtMs - now);
    return pausedMs;
  }, [endsAtMs, pausedMs, now]);

  const running = endsAtMs !== null;

  useEffect(() => {
    if (!running) return;
    const tick = () => setNow(Date.now());
    tick();
    const timer = window.setInterval(tick, 250);
    return () => window.clearInterval(timer);
  }, [running]);

  useEffect(() => {
    if (running && remainingMs === 0) {
      setEndsAtMs(null);
      setPausedMs(0);
    }
  }, [running, remainingMs]);

  return {
    running,
    remainingSeconds: Math.ceil((remainingMs ?? 0) / 1000),
    start(seconds: number) {
      setEndsAtMs(Date.now() + seconds * 1000);
      setPausedMs(null);
    },
    pause() {
      setPausedMs(Math.max(0, (endsAtMs ?? Date.now()) - Date.now()));
      setEndsAtMs(null);
    },
    reset(seconds: number) {
      setEndsAtMs(null);
      setPausedMs(seconds * 1000);
    },
  };
}
```

Добавьте один эффект завершения, который воспроизводит toast/vibration ровно один раз, даже после возвращения вкладки из background.

## 6. Очистить side effects `CookMode`

### Проблема

`showToast` создаёт timeout без cleanup. Wake lock флаг `wantWake` может остаться true после неявного закрытия, а планируемое время хранится частично в controlled state, частично через `defaultValue` input.

### Правка

- Храните toast timeout в `useRef` и очищайте на unmount/замене сообщения.
- В `useWakeLock` централизуйте `request`, `release`, visibility listener и `desired` state.
- Сделайте `datetime-local` controlled: `value={toDatetimeLocal(new Date(startMs))}`.
- Проверяйте, что запланированное время не в прошлом до перехода в steps.
- Возвращайте состояние cooking session к исходному только после фактического закрытия dialog, а не в нескольких независимых эффектах.

```ts
function useToast() {
  const [message, setMessage] = useState<string | null>(null);
  const timeoutRef = useRef<number | null>(null);

  const show = useCallback((next: string) => {
    if (timeoutRef.current) window.clearTimeout(timeoutRef.current);
    setMessage(next);
    timeoutRef.current = window.setTimeout(() => setMessage(null), 4000);
  }, []);

  useEffect(() => () => {
    if (timeoutRef.current) window.clearTimeout(timeoutRef.current);
  }, []);

  return { message, show };
}
```

Отдельно обработайте `steps.length === 0`: не открывайте cooking dialog или покажите нормальное пустое состояние без расчёта прогресса.

## 7. Убрать глобальное состояние из `RecipeAxisSwitch`

### Проблема

`pending` находится на module scope. Любой экземпляр компонента использует одну и ту же переменную, а навигация может завершиться после размонтирования компонента или быть отменена.

### Правка

Сначала проверьте необходимость ручного восстановления: `Link scroll={false}` уже сохраняет scroll в ожидаемой позиции для многих сценариев. Если anchoring действительно нужен, храните snapshot в instance ref или в history state, а не в глобальной переменной.

```tsx
export function useAxisScrollAnchor() {
  const pendingRef = useRef<{ y: number; top: number; href: string } | null>(null);

  const capture = useCallback((element: HTMLElement, href: string) => {
    pendingRef.current = {
      y: window.scrollY,
      top: element.getBoundingClientRect().top,
      href,
    };
  }, []);

  const restore = useCallback(() => {
    const snapshot = pendingRef.current;
    pendingRef.current = null;
    if (!snapshot) return;
    // restore once after route state changes; cancel raf on unmount
  }, []);

  return { capture, restore };
}
```

Не используйте `aria-pressed` для `Link`. Для current axis передавайте `aria-current="page"` или отображайте selection как list/tab pattern целиком.

## 8. Вынести масштабирование рецепта в один источник правил

### Проблема

`IngredientsBlock` рассчитывает ratio и nutrition на клиенте. Backend уже имеет правила `Decimal`, `scale_mode`, rounding и nutrition. Дублирование неизбежно приведёт к расхождениям, особенно после новых режимов масштабирования и no-leftover/prep контекста.

### Правка

Выберите один вариант и применяйте его последовательно:

| Подход | Когда применять | Реализация |
|---|---|---|
| Серверный | Точный результат, shareable URL, source of truth | Изменение `servings`/`anchor_weight` обновляет query params, сервер возвращает готовые amounts/nutrition |
| Общая pure library | Мгновенный локальный preview без сети | Вынести алгоритмы в отдельный тестируемый пакет TypeScript и проверять contract tests against backend fixtures |

Для этого проекта предпочтителен серверный контракт: backend уже умеет масштабирование и возвращает display values. Локально храните только временное значение input до commit.

```tsx
function useScaleNavigation() {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();

  return (key: 'servings' | 'anchor_weight', value: string | null) => {
    const next = new URLSearchParams(searchParams.toString());
    if (value) next.set(key, value);
    else next.delete(key);
    router.replace(`${pathname}?${next}`, { scroll: false });
  };
}
```

Если локальная арифметика остаётся, используйте decimal library и единые fixture tests с backend response, а не `number`.

## 9. Исправить числовой input масштаба

### Проблема

Текущий `onChange` обновляет state только при полном валидном числе. Пользователь не может оставить поле пустым, поставить запятую в процессе ввода или набрать небольшое значение без прыжков UI.

### Правка

Храните raw string отдельно от committed numeric value; commit делайте по `blur`/Enter, а invalid state показывайте текстом и не отправляйте на сервер.

```tsx
function useDecimalInput(initial: number, onCommit: (value: string) => void) {
  const [raw, setRaw] = useState(String(initial));
  const [error, setError] = useState<string | null>(null);

  const commit = () => {
    const normalized = raw.trim().replace(',', '.');
    if (!/^\d+(\.\d+)?$/.test(normalized) || Number(normalized) <= 0) {
      setError('Введите число больше нуля');
      return;
    }
    setError(null);
    onCommit(normalized);
  };

  return { raw, setRaw, error, commit };
}
```

Не округляйте user input до каждого keystroke. Округление выполняйте в backend или при явном commit согласно единым domain правилам.

## 10. Исправить keys и модель идентичности

### Проблема

Индекс в качестве key опасен, если шаги/таймлайн могут изменяться, а key из текста ломается при дублях текста. Это особенно заметно при interactive checkbox/timer state.

### Правка

Добавьте стабильные id в API типы:

```ts
type RecipeStep = {
  id: string;
  position: number;
  text: string;
  // ...
};

type PrepTimelineItem = {
  id: string;
  kind: 'intro' | 'step';
  // ...
};
```

Используйте `key={step.id}` и храните completed steps как `Set<string>`, а не `Set<number>`. Если API пока не даёт id, временно применяйте детерминированный key из server id + position, но не из визуального текста.

## 11. Исправить `PantryTextForm`

### Проблема

Есть дублирующийся `pathForHave`, прямое обращение к DOM по глобальному ID и возможная race condition ответов API.

### Правка

- Вынесите `pathForHave` в `lib/pantry.ts` и используйте в CalculatorAsk/PantryTextForm.
- Используйте `useRef<HTMLTextAreaElement>` вместо `document.getElementById`.
- Отменяйте предыдущий запрос через `AbortController`.
- Проверяйте `response.ok`, безопасно парсите тело ошибки и игнорируйте `AbortError`.

```tsx
const controllerRef = useRef<AbortController | null>(null);
const textareaRef = useRef<HTMLTextAreaElement>(null);

async function resolvePantry(raw: string) {
  controllerRef.current?.abort();
  const controller = new AbortController();
  controllerRef.current = controller;

  const response = await clientFetch(`/api/ingredients/?text=${encodeURIComponent(raw)}`, {
    signal: controller.signal,
  });
  if (!response.ok) {
    throw new Error(`Resolve pantry failed: ${response.status}`);
  }
  return (await response.json()) as PantryResolveResponse;
}
```

В cleanup effect делайте `controllerRef.current?.abort()`.

## 12. Переработать поиск в `RecipesBook`

### Проблема

Поиск поддерживает параллельные состояния `q`, `qLive`, URL props и отложенный `router.replace`. При быстрой навигации, Back/Forward или обновлении server props поле может остаться несинхронизированным. Также URL изменяется ещё до явной отправки формы.

### Правка

Выберите один UX:

- **Submit-first**: URL меняется только по submit, простой и предсказуемый вариант.
- **Live search**: debounce выполняется в отдельном hook, синхронизируется с `useSearchParams`, отменяется при unmount и обязательно использует `startTransition`.

Для каталога с SSR filtering предпочтителен submit-first; быстрые фильтры и chapter navigation останутся ссылками.

```tsx
function RecipeSearchForm({ initialQuery }: { initialQuery: string }) {
  const [query, setQuery] = useState(initialQuery);

  useEffect(() => setQuery(initialQuery), [initialQuery]);

  return (
    <form action="/recipes" method="get" className="search-row">
      <label className="sr-only" htmlFor="recipe-search">Найти рецепт</label>
      <input id="recipe-search" type="search" name="q" value={query} onChange={(e) => setQuery(e.target.value)} />
      <button type="submit" className="btn-primary">Найти</button>
    </form>
  );
}
```

Если query должен сохранять другие параметры, строить action/href должен общий URL-state helper, а не `window.location`.

## 13. Мемоизировать и тестировать selectors каталога

### Проблема

`RecipesBook` выполняет несколько полных проходов по recipes: chapter count, pool, protein count, method count, equipment count, cards. Эти вычисления также находятся рядом с JSX, что усложняет понимание порядка фильтрации.

### Правка

Вынесите в чистый selector с одним документированным pipeline. Сначала фильтруйте, затем одним проходом создавайте counts.

```ts
export function buildRecipesBookModel(
  recipes: RecipeCardData[],
  filters: BookFilters,
): RecipesBookModel {
  const afterExtras = recipes.filter((recipe) => matchesCatalogExtras(recipe, filters));
  const chapter = resolveChapter(filters);
  const chapterPool = chapter ? afterExtras.filter(matchesChapter(chapter)) : afterExtras;
  const finalItems = applyBookFilters(chapterPool, filters);

  return {
    chapter,
    items: finalItems,
    chapterCounts: countChapters(afterExtras),
    proteinCounts: countProteins(chapterPool, chapter),
    methodCounts: countBy(finalItems, 'cook_method'),
    equipmentCounts: countBy(finalItems, 'equipment'),
  };
}
```

Добавьте unit tests: порядок фильтрации, multi-protein variant, пустой chapter, reset, result counts. Измерьте render на каталоге production-size до и после оптимизации.

## 14. Улучшить `PrepKitView`

### Проблема

В week grid на каждый день выполняется два `Array.find()` по slots; tab state сбрасывается при серверной навигации и не может быть адресован ссылкой.

### Правка

Создайте `slotsByDay` один раз и храните выбранную вкладку как `?tab=shop|sunday|meals` в URL, если пользователю важно возвращаться/делиться конкретным разделом.

```ts
const slotsByDay = useMemo(() => {
  const map = new Map<number, Partial<Record<'lunch' | 'dinner', PrepSlot>>>();
  for (const slot of kit.slots) {
    const day = map.get(slot.day) ?? {};
    day[slot.meal] = slot;
    map.set(slot.day, day);
  }
  return map;
}, [kit.slots]);
```

Для tabs соблюдайте ARIA tabs pattern полностью:

- `id` у tab и `aria-controls` на panel;
- `role="tabpanel"`, `aria-labelledby` у активной панели;
- keyboard navigation стрелками/Home/End либо замените tabs на обычные ссылки/segmented navigation, если вкладки ведут на URL.

## 15. Централизовать навигацию и guide configuration

### Проблема

Списки доступных guides/мяса/навигации повторяются в Header, Footer, GuideStrip и частично backend constants. При добавлении раздела можно обновить только один путь.

### Правка

Создайте один frontend config, независимый от JSX:

```ts
// frontend/lib/navigation.ts
export const GUIDE_LINKS = [
  { href: '/grains', label: 'Крупы', section: 'grains' },
  { href: '/meat/beef', label: 'Говядина', section: 'beef' },
  { href: '/meat/pork', label: 'Свинина', section: 'pork' },
  { href: '/meat/poultry', label: 'Птица', section: 'poultry' },
] as const;
```

`Header`, `Footer`, `GuideStrip` потребляют этот массив. Если доступность guide определяется backend content, отдавайте список опубликованных разделов отдельным endpoint или внедряйте его в server layout, а не поддерживайте список в двух приложениях вручную.

## 16. Перевести `PageArt` на Next Image

### Проблема

Обычный `<img>` не использует оптимизацию изображений Next.js и не задаёт responsive `sizes`; для hero art это влияет на LCP и трафик мобильных клиентов.

### Правка

```tsx
import Image from 'next/image';

export function PageArt({ scene, priority = false }: { scene: ArtScene; priority?: boolean }) {
  return (
    <div className="page-art" aria-hidden="true">
      <Image
        className="page-art__paint"
        src={ART_SRC[scene]}
        alt=""
        width={1024}
        height={518}
        priority={priority}
        sizes="(max-width: 768px) 100vw, 1024px"
      />
    </div>
  );
}
```

Не добавляйте `?v=9` в каждом компоненте. Для файлов в `public` используйте content-hashed filename при сборке/деплое либо централизованную константу версии. Для критичной иллюстрации передавайте `priority` только на реально LCP-страницах.

## 17. Убрать inline styles и систематизировать классы

### Проблема

В `CookMode` есть inline styles для flex, margins, borders; className собирается шаблонными строками во многих местах. Это затрудняет темы, responsive поведение и visual regression.

### Правка

Добавьте семантические классы в stylesheet/CSS module:

```tsx
<div className="cook-mode__title-wrap">...</div>
<div className="cook-timer-actions">...</div>
<label className="cook-step-check">...</label>
```

Для условных классов используйте `clsx`:

```tsx
import clsx from 'clsx';

className={clsx('cook-step-card', { 'is-done': done.has(step.id) })}
```

Не превращайте эту задачу в массовый rewrite CSS: меняйте стили рядом с декомпозицией `CookMode`, чтобы не смешивать функциональные и визуальные регрессии.

## 18. Добавить client data boundaries

### Проблема

`PantryTextForm` вручную вызывает fetch, а разные компоненты по-разному показывают ошибки/empty/loading состояния. Это затрудняет отмену запросов, retry, telemetry и тестирование.

### Правка

Для небольшого количества запросов достаточно typed fetch wrapper + feature hook. Не вводите глобальную библиотеку кэширования без потребности.

```ts
export class ApiError extends Error {
  constructor(public readonly status: number, message: string) {
    super(message);
  }
}

export async function fetchJson<T>(input: RequestInfo, init?: RequestInit): Promise<T> {
  const response = await fetch(input, init);
  if (!response.ok) throw new ApiError(response.status, `Request failed: ${response.status}`);
  return response.json() as Promise<T>;
}
```

Если client-side запросов станет много, используйте TanStack Query/SWR с ключами, abort signal, retry policy и boundaries. Не используйте одну библиотеку в одних компонентах и ручной `fetch` в других.

## 19. Тесты, которые нужно добавить

### Компонентные и unit tests

- URL helper сохраняет нецелевые параметры, удаляет page при новом поиске, дедуплицирует и стабильно сортирует multi-values.
- `buildRecipesBookModel` корректно применяет extras → chapter → protein → method → equipment и возвращает согласованные counts.
- `useCountdown` показывает корректный остаток после искусственного перехода времени, pause/resume/reset и завершение ровно один раз.
- Delta/масштабирование не расходятся с backend fixtures; decimal inputs принимают `0,5` до commit.
- Pantry resolver отменяет предыдущий запрос, не перезаписывает свежий ответ старым и показывает API error.
- Prep slot map корректно возвращает lunch/dinner без repeated find.

### Accessibility tests

- Cook dialog получает фокус при открытии, Esc закрывает его, фокус возвращается на trigger.
- В dialog невозможно tab-уйти в фон.
- Tabs имеют корректные roles/id/aria-controls/panels либо заменены ссылочной навигацией.
- Filter links имеют доступное имя и корректный текущий selected state.
- Все формы имеют связанные label; icon-only buttons имеют `aria-label`.

### E2E и performance

- Back/Forward корректно восстанавливает фильтры каталога, calculator и prep tab.
- Открытие фильтра в новой вкладке работает как навигация.
- Cooking timer остаётся корректным после background/sleep.
- Нет console errors при пустых steps/пустом shopping/неполном API payload.
- Профилировать production-size каталог: переключение фильтра и search не дают заметного UI lag.
- Lighthouse/real-user metric: LCP страницы с art, INP фильтров, CLS при server navigation.

## Рекомендуемый порядок внедрения

1. Исправить риски UX и данных: заменить FilterChip на Link, сделать query state единым, устранить глобальное состояние axis switch, добавить стабильные item IDs.
2. Переписать CookMode: native/проверенный dialog, deadline-based timer, выделенные hooks wake lock/toast/session, test пустых steps и a11y.
3. Выбрать source of truth для масштабирования и убрать неявное расхождение client `number` с backend Decimal.
4. Вынести pantry resolve в hook с AbortController и единым typed fetch/error layer.
5. Разбить RecipesBook, PrepKitView и CalculatorAsk на selectors/hooks/presentation; покрыть selectors тестами.
6. Централизовать navigation/guide config, обновить PageArt на `next/image`, удалить inline styles в рамках локальных refactor.
7. Настроить component/a11y/E2E/query-performance тесты и только после измерений вводить более сложное клиентское кэширование.
