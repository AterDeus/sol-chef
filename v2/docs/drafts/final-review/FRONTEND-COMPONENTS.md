# Компоненты фронтенда sol-chef 2.0 — дамп для аудита

Снимок кода на 2026-09-20. Источник: `v2/frontend/components/`.
Страницы `app/` и стили сюда не входят — только React-компоненты.

Правило раскладки: **один файл = содержимое одного исходного `.tsx`**.
Заголовок блока — путь относительно `v2/`. Ниже — экспорты и полный исходник.
Вспомогательные функции без `export` живут в том же файле, что и публичный компонент.

## Оглавление

| # | Файл | Экспорты | Строк |
|---|------|----------|------:|
| 1 | `frontend/components/AllergenNotice.tsx` | `AllergenNotice` | 59 |
| 2 | `frontend/components/AppShell.tsx` | `AppShell` | 30 |
| 3 | `frontend/components/CalculatorAsk.tsx` | `CalculatorAsk` | 248 |
| 4 | `frontend/components/Chrome.tsx` | `navMatch`, `isRecipeDetail`, `isGuidePath`, `Header`, `GuideStrip`, `Footer`, `TabBar`, `RecipeTabBar` | 181 |
| 5 | `frontend/components/CookMode.tsx` | `CookMode` | 533 |
| 6 | `frontend/components/Feedback.tsx` | `EmptyState`, `ErrorBanner` | 17 |
| 7 | `frontend/components/FilterChip.tsx` | `FilterChip` | 32 |
| 8 | `frontend/components/FilterPanel.tsx` | `ChipGroup` | 43 |
| 9 | `frontend/components/Guides.tsx` | `GrainsView`, `MeatView` | 110 |
| 10 | `frontend/components/HashDetailsOpener.tsx` | `HashDetailsOpener` | 37 |
| 11 | `frontend/components/IngredientsBlock.tsx` | `IngredientsBlock` | 271 |
| 12 | `frontend/components/NutritionBlock.tsx` | `NutritionBlock` | 105 |
| 13 | `frontend/components/PageArt.tsx` | `PageArt`, `PageIntro` | 70 |
| 14 | `frontend/components/PantryTextForm.tsx` | `PantryTextForm` | 129 |
| 15 | `frontend/components/PrepKitView.tsx` | `PrepKitView` | 285 |
| 16 | `frontend/components/RecipeActions.tsx` | `CopyLinkButton`, `RecipeActions` | 70 |
| 17 | `frontend/components/RecipeAxisSwitch.tsx` | `RecipeAxisSwitch`, `RecipeAxisLink` | 94 |
| 18 | `frontend/components/RecipeCard.tsx` | `RecipeCard`, `RecipeGrid`, `SolutionBoard`, `SolutionBuckets` | 257 |
| 19 | `frontend/components/RecipesBook.tsx` | `RecipesBook` | 330 |
| 20 | `frontend/components/RecipeSteps.tsx` | `RecipeSteps` | 67 |
| 21 | `frontend/components/SpriteIcon.tsx` | `SpriteIcon` | 19 |
| 22 | `frontend/components/TipsView.tsx` | `TipsView` | 525 |

Всего файлов: **22**. Строк исходников: **3512**.

---

## 1. `frontend/components/AllergenNotice.tsx`

- Путь: `v2/frontend/components/AllergenNotice.tsx`
- Экспорты: AllergenNotice
- Строк: 59

```tsx
import type { Allergens } from '@/lib/types';
import {
  containsAllergenLabel,
  hasAllergens,
  mayContainAllergenLabel,
  unknownAllergenLabel,
} from '@/lib/allergens';

export function AllergenNotice({
  allergens,
  compact = false,
}: {
  allergens?: Allergens | null;
  compact?: boolean;
}) {
  if (!hasAllergens(allergens)) return null;
  const contains = allergens?.contains ?? [];
  const mayContain = allergens?.may_contain ?? [];
  const unknown = allergens?.unknown ?? [];

  return (
    <div
      className={compact ? 'allergen-notice allergen-notice--compact' : 'allergen-notice'}
      aria-label="Аллергены"
    >
      {contains.length > 0 || mayContain.length > 0 ? (
        <div className="allergen-notice__group">
          {!compact ? <p className="allergen-notice__kicker">Аллергены рецепта</p> : null}
          <ul>
            {contains.map((code) => (
              <li key={`c-${code}`} className="allergen-chip allergen-chip--contains">
                {containsAllergenLabel(code)}
              </li>
            ))}
            {mayContain.map((code) => (
              <li key={`m-${code}`} className="allergen-chip allergen-chip--may">
                {mayContainAllergenLabel(code)}
              </li>
            ))}
          </ul>
        </div>
      ) : null}
      {unknown.length > 0 ? (
        <div className="allergen-notice__group">
          {!compact ? (
            <p className="allergen-notice__kicker">Возможные аллергены в покупных продуктах</p>
          ) : null}
          <ul>
            {unknown.map((code) => (
              <li key={`u-${code}`} className="allergen-chip allergen-chip--unknown">
                {unknownAllergenLabel(code)}
              </li>
            ))}
          </ul>
        </div>
      ) : null}
    </div>
  );
}
```

---

## 2. `frontend/components/AppShell.tsx`

- Путь: `v2/frontend/components/AppShell.tsx`
- Экспорты: AppShell
- Строк: 30

```tsx
'use client';

import { usePathname } from 'next/navigation';
import { useEffect } from 'react';
import { Footer, GuideStrip, Header, TabBar, isRecipeDetail } from './Chrome';

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const recipe = isRecipeDetail(pathname);

  useEffect(() => {
    document.body.classList.toggle('is-recipe-page', recipe);
    return () => document.body.classList.remove('is-recipe-page');
  }, [recipe]);

  return (
    <>
      <a className="skip-link" href="#main">
        К содержимому
      </a>
      <Header />
      <GuideStrip />
      <main id="main" className="wrap" tabIndex={-1}>
        {children}
      </main>
      <Footer />
      <TabBar />
    </>
  );
}
```

---

## 3. `frontend/components/CalculatorAsk.tsx`

- Путь: `v2/frontend/components/CalculatorAsk.tsx`
- Экспорты: CalculatorAsk
- Строк: 248

```tsx
import type { ReactNode } from 'react';
import type { PantryGroup, SearchParamsRecord } from '@/lib/types';
import { isSelected, toggleHaveGroupHref, toggleHref, valuesOf } from '@/lib/filters';
import { ALLERGEN, EQUIPMENT, INTENT } from '@/lib/vocab';
import { ChipGroup } from '@/components/FilterPanel';
import { PantryTextForm } from '@/components/PantryTextForm';
import { SpriteIcon } from '@/components/SpriteIcon';
import { FilterChip } from '@/components/FilterChip';
import Link from 'next/link';

const INTENT_ORDER = ['fast', 'pantry', 'easy', 'batch', 'light', 'oven'] as const;

function groupOpen(sp: SearchParamsRecord, group: PantryGroup): boolean {
  if (isSelected(sp, 'have_group', group.id)) return true;
  return (group.children ?? []).some((child) => isSelected(sp, 'have_group', child.id));
}

function ChipRow({
  items,
}: {
  items: Array<{ id: string; title: string; href: string; selected: boolean }>;
}) {
  if (items.length === 0) return null;
  return (
    <div className="chip-row">
      {items.map((item) => (
        <FilterChip key={item.id} href={item.href} pressed={item.selected}>
          {item.title}
        </FilterChip>
      ))}
    </div>
  );
}

function pathForHave(groups: PantryGroup[], canonicalId: string): string {
  for (const group of groups) {
    const own = group.items?.find((item) => item.canonical_id === canonicalId);
    if (own) return `${group.title} · ${own.title}`;
    for (const child of group.children ?? []) {
      const nested = child.items?.find((item) => item.canonical_id === canonicalId);
      if (nested) return `${group.title} · ${child.title} · ${nested.title}`;
    }
  }
  return canonicalId;
}

function PickedBar({
  sp,
  groups,
}: {
  sp: SearchParamsRecord;
  groups: PantryGroup[];
}) {
  const have = valuesOf(sp, 'have');
  if (have.length === 0) return null;
  return (
    <div className="calc-picked">
      <p className="calc-picked__label">Выбрано</p>
      <ul className="calc-picked__list">
        {have.map((id) => (
          <li key={id}>
            <Link
              href={toggleHref('/calculator', sp, 'have', id)}
              className="calc-picked__chip"
              aria-label={`Убрать: ${pathForHave(groups, id)}`}
            >
              <span>{pathForHave(groups, id)}</span>
              <SpriteIcon name="x" size={14} />
            </Link>
          </li>
        ))}
      </ul>
    </div>
  );
}

function Branch({
  title,
  path,
  closeHref,
  closeLabel,
  hint,
  nested = false,
  children,
}: {
  title: string;
  path?: string;
  closeHref: string;
  closeLabel: string;
  hint?: string;
  nested?: boolean;
  children: ReactNode;
}) {
  return (
    <section
      className={nested ? 'calc-branch calc-branch--nested' : 'calc-branch'}
      aria-label={path ?? title}
    >
      <header className="calc-branch__head">
        <div>
          {path ? <p className="calc-branch__path">{path}</p> : null}
          <h3 className="calc-branch__title">{title}</h3>
          {hint ? <p className="calc-branch__hint">{hint}</p> : null}
        </div>
        <Link href={closeHref} className="calc-branch__close" aria-label={closeLabel}>
          <SpriteIcon name="x" size={18} />
          <span>Убрать</span>
        </Link>
      </header>
      {children}
    </section>
  );
}

export function CalculatorAsk({
  sp,
  groups,
}: {
  sp: SearchParamsRecord;
  groups: PantryGroup[];
}) {
  const extraOpen =
    valuesOf(sp, 'without').length > 0 ||
    valuesOf(sp, 'equipment').length > 0 ||
    valuesOf(sp, 'protein_base').length > 0 ||
    valuesOf(sp, 'cook_method').length > 0 ||
    valuesOf(sp, 'cuts').length > 0;
  const openGroups = groups.filter((group) => groupOpen(sp, group));

  return (
    <section className="calc-ask" aria-label="Ситуация">
      <PantryTextForm sp={sp} groups={groups} />

      <fieldset className="filter-block">
        <legend className="filter-legend">Что есть</legend>
        <p className="calc-ask__hint">
          Можно выбрать несколько групп сразу: курица, овощи, крупу и сценарий. Сначала группа,
          внутри неё — уточнение.
        </p>
        <div className="chip-row">
          {groups.map((group) => {
            const selected = groupOpen(sp, group);
            return (
              <FilterChip
                key={group.id}
                href={toggleHaveGroupHref('/calculator', sp, group.id, groups)}
                pressed={selected}
              >
                {group.title}
              </FilterChip>
            );
          })}
        </div>
      </fieldset>

      <PickedBar sp={sp} groups={groups} />

      {openGroups.map((group) => {
        const children = group.children ?? [];
        const selectedChildren = children.filter((child) => isSelected(sp, 'have_group', child.id));
        return (
          <Branch
            key={group.id}
            title={group.title}
            closeHref={toggleHaveGroupHref('/calculator', sp, group.id, groups)}
            closeLabel={`Убрать: ${group.title}`}
            hint={
              children.length > 0
                ? 'Сначала вид, потом отруб с витрины'
                : 'Отметьте, что лежит дома'
            }
          >
            {children.length > 0 ? (
              <>
                <ChipRow
                  items={children.map((child) => ({
                    id: child.id,
                    title: child.title,
                    href: toggleHaveGroupHref('/calculator', sp, child.id, groups),
                    selected: isSelected(sp, 'have_group', child.id),
                  }))}
                />
                {selectedChildren.map((child) => (
                  <Branch
                    key={child.id}
                    nested
                    title={child.title}
                    path={`${group.title} → ${child.title}`}
                    closeHref={toggleHaveGroupHref('/calculator', sp, child.id, groups)}
                    closeLabel={`Убрать: ${child.title}`}
                    hint="Что именно купили"
                  >
                    <ChipRow
                      items={(child.items ?? []).map((item) => ({
                        id: item.canonical_id,
                        title: item.title,
                        href: toggleHref('/calculator', sp, 'have', item.canonical_id),
                        selected: isSelected(sp, 'have', item.canonical_id),
                      }))}
                    />
                  </Branch>
                ))}
              </>
            ) : (
              <ChipRow
                items={(group.items ?? []).map((item) => ({
                  id: item.canonical_id,
                  title: item.title,
                  href: toggleHref('/calculator', sp, 'have', item.canonical_id),
                  selected: isSelected(sp, 'have', item.canonical_id),
                }))}
              />
            )}
          </Branch>
        );
      })}

      <fieldset className="filter-block">
        <legend className="filter-legend">Что сейчас важнее</legend>
        <div className="chip-row">
          {INTENT_ORDER.map((code) => {
            const selected = isSelected(sp, 'intent', code);
            return (
              <FilterChip
                key={code}
                href={toggleHref('/calculator', sp, 'intent', code)}
                pressed={selected}
                hint={
                  code === 'light' ? 'Полегче по составу, не по калориям' : undefined
                }
              >
                {INTENT[code]}
              </FilterChip>
            );
          })}
        </div>
      </fieldset>

      <details className="calc-extra" open={extraOpen || undefined}>
        <summary aria-controls="calc-extra-panel">Ещё условия</summary>
        <div id="calc-extra-panel">
          <ChipGroup legend="Без чего" map={ALLERGEN} param="without" pathname="/calculator" sp={sp} />
          <ChipGroup legend="Посуда" map={EQUIPMENT} param="equipment" pathname="/calculator" sp={sp} />
        </div>
      </details>
    </section>
  );
}
```

---

## 4. `frontend/components/Chrome.tsx`

- Путь: `v2/frontend/components/Chrome.tsx`
- Экспорты: navMatch, isRecipeDetail, isGuidePath, Header, GuideStrip, Footer, TabBar, RecipeTabBar
- Строк: 181

```tsx
'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { SpriteIcon } from '@/components/SpriteIcon';

const NAV = [
  { href: '/calculator', label: 'Калькулятор', match: 'calc', icon: 'list-filter' },
  { href: '/recipes', label: 'Рецепты', match: 'recipes', icon: 'book-open-text' },
  { href: '/prep', label: 'На неделю', match: 'prep', icon: 'refrigerator' },
  { href: '/grains', label: 'Справочник', match: 'guide', icon: 'wheat' },
  { href: '/tips', label: 'Советы', match: 'tips', icon: 'chef-hat' },
] as const;

export function navMatch(pathname: string): 'calc' | 'recipes' | 'prep' | 'guide' | 'tips' | null {
  if (pathname.startsWith('/calculator')) return 'calc';
  if (pathname.startsWith('/recipes')) return 'recipes';
  if (pathname.startsWith('/prep')) return 'prep';
  if (pathname.startsWith('/grains') || pathname.startsWith('/meat')) return 'guide';
  if (pathname.startsWith('/tips')) return 'tips';
  return null;
}

export function isRecipeDetail(pathname: string): boolean {
  return pathname.startsWith('/recipes/') && pathname !== '/recipes/';
}

export function isGuidePath(pathname: string): boolean {
  return pathname.startsWith('/grains') || pathname.startsWith('/meat');
}

export function Header() {
  const pathname = usePathname();
  const active = navMatch(pathname);

  return (
    <>
      <header className="site-header">
        <Link
          className="site-brand"
          href="/"
          aria-current={pathname === '/' ? 'page' : undefined}
        >
          <SpriteIcon name="chef-hat" size={22} />
          Кухонная шпаргалка
        </Link>
        <nav className="site-nav" aria-label="Основное меню">
          {NAV.map((item) => (
            <Link
              key={item.match}
              href={item.href}
              className={active === item.match ? 'is-active' : undefined}
              aria-current={active === item.match ? 'page' : undefined}
            >
              <SpriteIcon name={item.icon} size={20} />
              {item.label}
            </Link>
          ))}
        </nav>
      </header>
      {!isRecipeDetail(pathname) && (
        <div className="mobile-brand">
          <Link href="/">Кухонная шпаргалка</Link>
        </div>
      )}
    </>
  );
}

export function GuideStrip() {
  const pathname = usePathname();
  if (!isGuidePath(pathname)) return null;

  const items = [
    { href: '/grains', label: 'Крупы', on: pathname === '/grains' },
    { href: '/meat/beef', label: 'Говядина', on: pathname === '/meat/beef' },
    { href: '/meat/pork', label: 'Свинина', on: pathname === '/meat/pork' },
    { href: '/meat/poultry', label: 'Птица', on: pathname === '/meat/poultry' },
  ];

  return (
    <nav className="guide-strip" aria-label="Справочник">
      {items.map((item) => (
        <Link
          key={item.href}
          href={item.href}
          className={item.on ? 'is-active' : undefined}
          aria-current={item.on ? 'page' : undefined}
        >
          {item.label}
        </Link>
      ))}
    </nav>
  );
}

export function Footer() {
  const pathname = usePathname();
  if (isRecipeDetail(pathname)) return null;

  return (
    <footer className="site-footer">
      <nav className="site-footer__nav" aria-label="Справочник">
        <div className="site-footer__group">
          <p className="site-footer__label">Справочник</p>
          <Link href="/grains">Крупы</Link>
          <Link href="/meat/beef">Говядина</Link>
          <Link href="/meat/pork">Свинина</Link>
          <Link href="/meat/poultry">Птица</Link>
        </div>
        <div className="site-footer__group">
          <p className="site-footer__label">Книга</p>
          <Link href="/recipes">Все рецепты</Link>
          <Link href="/prep">На неделю</Link>
          <Link href="/tips">Советы шеф-поваров</Link>
        </div>
      </nav>
    </footer>
  );
}

const TABS: Array<{
  href: string;
  label: string;
  aria?: string;
  icon: string;
  match: 'calc' | 'recipes' | 'prep' | 'guide' | 'tips';
}> = [
  { href: '/calculator', label: 'Калькулятор', icon: 'list-filter', match: 'calc' },
  { href: '/recipes', label: 'Рецепты', icon: 'book-open-text', match: 'recipes' },
  { href: '/prep', label: 'На неделю', icon: 'refrigerator', match: 'prep' },
  { href: '/grains', label: 'Справка', aria: 'Справочник', icon: 'wheat', match: 'guide' },
  { href: '/tips', label: 'Советы', aria: 'Советы шеф-поваров', icon: 'chef-hat', match: 'tips' },
];

export function TabBar() {
  const pathname = usePathname();
  if (isRecipeDetail(pathname)) return null;
  const active = navMatch(pathname);

  return (
    <nav className="tabbar tabbar--main" aria-label="Нижнее меню">
      {TABS.map((tab) => (
        <Link
          key={tab.href}
          href={tab.href}
          aria-label={tab.aria}
          className={active === tab.match ? 'is-active' : undefined}
          aria-current={active === tab.match ? 'page' : undefined}
        >
          <SpriteIcon name={tab.icon} size={22} />
          {tab.label}
        </Link>
      ))}
    </nav>
  );
}

export function RecipeTabBar({
  onCook,
  backHref = '/recipes',
  backLabel = '← Рецепты',
}: {
  onCook: () => void;
  backHref?: string;
  backLabel?: string;
}) {
  return (
    <nav className="tabbar tabbar--recipe" aria-label="Меню рецепта">
      <Link href={backHref} aria-label={backLabel}>
        {backLabel}
      </Link>
      <Link href="/grains" aria-label="Справочник">
        Справка
      </Link>
      <button type="button" className="tabbar-cook" onClick={onCook}>
        Режим готовки
      </button>
    </nav>
  );
}
```

---

## 5. `frontend/components/CookMode.tsx`

- Путь: `v2/frontend/components/CookMode.tsx`
- Экспорты: CookMode
- Строк: 533

```tsx
'use client';

import { useCallback, useEffect, useRef, useState } from 'react';
import type { RecipePrep, RecipeStep } from '@/lib/types';
import { formatClock, formatDuration } from '@/lib/time';
import { SpriteIcon } from './SpriteIcon';

type WakeLockSentinelLike = {
  released: boolean;
  release: () => Promise<void>;
  addEventListener: (type: 'release', listener: () => void) => void;
};

const PREP_LABELS: Record<string, string> = {
  thaw: 'Разморозка',
  fridge: 'Холодильник',
  room_temp: 'Комнат. темп.',
  marinate: 'Маринад',
  soak: 'Замачивание',
  custom: 'Подготовка',
};

const FOCUSABLE =
  'a[href], button:not(:disabled), input:not(:disabled), select, textarea, summary, [tabindex]:not([tabindex="-1"])';

function toDatetimeLocal(date: Date): string {
  const pad = (n: number) => String(n).padStart(2, '0');
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T${pad(date.getHours())}:${pad(date.getMinutes())}`;
}

function timerAdjustStep(seconds: number): number {
  if (seconds >= 3600) return 300;
  if (seconds >= 600) return 60;
  return 30;
}

function normalizePrep(prep: RecipePrep[] | undefined): Array<{
  text: string;
  before_min: number;
  type: string;
}> {
  if (!prep?.length) return [];
  return prep
    .map((item) => {
      const text = (item.text || '').trim();
      const before = (item.before_min || 0) + (item.before_hours || 0) * 60;
      if (!text || before <= 0) return null;
      return { text, before_min: before, type: item.type || 'custom' };
    })
    .filter((item): item is { text: string; before_min: number; type: string } => Boolean(item))
    .sort((a, b) => b.before_min - a.before_min);
}

type Props = {
  title: string;
  steps: RecipeStep[];
  prep?: RecipePrep[];
  open: boolean;
  onClose: () => void;
};

export function CookMode({ title, steps, prep: rawPrep, open, onClose }: Props) {
  const prep = normalizePrep(rawPrep);
  const [phase, setPhase] = useState<'setup' | 'steps' | 'done'>('setup');
  const [index, setIndex] = useState(0);
  const [done, setDone] = useState<Set<number>>(new Set());
  const [remaining, setRemaining] = useState<number | null>(null);
  const [running, setRunning] = useState(false);
  const [duration, setDuration] = useState(0);
  const [plan, setPlan] = useState(false);
  const [startMs, setStartMs] = useState(() => Date.now());
  const [toast, setToast] = useState<string | null>(null);
  const [wakeOn, setWakeOn] = useState(false);
  const wakeRef = useRef<WakeLockSentinelLike | null>(null);
  const intervalRef = useRef<number | null>(null);
  const wantWake = useRef(false);
  const dialogRef = useRef<HTMLDivElement>(null);
  const closeBtnRef = useRef<HTMLButtonElement>(null);
  const restoreFocusRef = useRef<HTMLElement | null>(null);

  const step = steps[index];
  const timerSec = duration || step?.timer_seconds || 0;

  const showToast = (message: string) => {
    setToast(message);
    window.setTimeout(() => setToast(null), 4000);
  };

  const releaseWake = useCallback(async () => {
    if (wakeRef.current) {
      try {
        await wakeRef.current.release();
      } catch {
        /* ignore */
      }
      wakeRef.current = null;
    }
    setWakeOn(false);
  }, []);

  const requestWake = useCallback(async () => {
    const nav = navigator as Navigator & {
      wakeLock?: { request: (type: 'screen') => Promise<WakeLockSentinelLike> };
    };
    if (!nav.wakeLock) {
      showToast('Экран не блокируется — браузер не поддерживает Wake Lock');
      return;
    }
    try {
      const sentinel = await nav.wakeLock.request('screen');
      wakeRef.current = sentinel;
      setWakeOn(true);
      sentinel.addEventListener('release', () => {
        wakeRef.current = null;
        setWakeOn(false);
      });
    } catch {
      showToast('Не удалось удержать экран включённым');
    }
  }, []);

  useEffect(() => {
    if (!open) return;
    document.body.classList.add('cook-mode-open');
    wantWake.current = true;
    void requestWake();
    return () => {
      document.body.classList.remove('cook-mode-open');
      if (intervalRef.current) window.clearInterval(intervalRef.current);
      void releaseWake();
    };
  }, [open, requestWake, releaseWake]);

  useEffect(() => {
    const onVis = () => {
      if (document.visibilityState === 'visible' && wantWake.current && !wakeRef.current) {
        void requestWake();
      }
    };
    document.addEventListener('visibilitychange', onVis);
    return () => document.removeEventListener('visibilitychange', onVis);
  }, [requestWake]);

  useEffect(() => {
    if (!running) return;
    intervalRef.current = window.setInterval(() => {
      setRemaining((prev) => {
        if (prev == null) return prev;
        if (prev <= 1) {
          setRunning(false);
          showToast(`Таймер: ${step?.timer_label || 'готово'}`);
          if (navigator.vibrate) navigator.vibrate([300, 100, 300]);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
    return () => {
      if (intervalRef.current) window.clearInterval(intervalRef.current);
    };
  }, [running, step?.timer_label]);

  useEffect(() => {
    setDuration(step?.timer_seconds ?? 0);
    setRemaining(null);
    setRunning(false);
  }, [index, step?.timer_seconds]);

  const close = useCallback(() => {
    wantWake.current = false;
    setRunning(false);
    setPhase('setup');
    setIndex(0);
    setDone(new Set());
    onClose();
  }, [onClose]);
  const closeRef = useRef(close);
  closeRef.current = close;

  useEffect(() => {
    if (!open) return;

    restoreFocusRef.current =
      document.activeElement instanceof HTMLElement ? document.activeElement : null;

    const frame = window.requestAnimationFrame(() => {
      closeBtnRef.current?.focus();
    });

    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        event.preventDefault();
        closeRef.current();
        return;
      }
      if (event.key !== 'Tab') return;
      const root = dialogRef.current;
      if (!root) return;
      const nodes = Array.from(root.querySelectorAll<HTMLElement>(FOCUSABLE)).filter(
        (el) => el.getClientRects().length > 0,
      );
      if (nodes.length === 0) return;
      const first = nodes[0];
      const last = nodes[nodes.length - 1];
      if (event.shiftKey) {
        if (document.activeElement === first || document.activeElement === root) {
          event.preventDefault();
          last.focus();
        }
      } else if (document.activeElement === last) {
        event.preventDefault();
        first.focus();
      }
    };

    document.addEventListener('keydown', onKeyDown);
    return () => {
      window.cancelAnimationFrame(frame);
      document.removeEventListener('keydown', onKeyDown);
      restoreFocusRef.current?.focus();
    };
  }, [open]);

  if (!open) return null;

  const toggleWake = () => {
    if (wakeOn) {
      wantWake.current = false;
      void releaseWake();
    } else {
      wantWake.current = true;
      void requestWake();
    }
  };

  const startTimer = () => {
    setRemaining(remaining == null || remaining === 0 ? timerSec : remaining);
    setRunning(true);
  };

  const resetTimer = () => {
    setRunning(false);
    setRemaining(timerSec);
  };

  const adjust = timerAdjustStep(step?.timer_seconds || 0);
  const timedCount = steps.filter((item) => (item.timer_seconds ?? 0) > 0).length;

  const stepList = (
    <ol className="cook-step-overview__list">
      {steps.map((item, i) => (
        <li
          key={i}
          className={`${i === index ? 'is-current' : ''} ${done.has(i) ? 'is-done' : ''}`}
        >
          <button
            type="button"
            className="cook-step-jump"
            onClick={() => {
              setPhase('steps');
              setIndex(i);
            }}
          >
            {item.text.slice(0, 80)}
            {item.text.length > 80 ? '…' : ''}
          </button>
        </li>
      ))}
    </ol>
  );

  return (
    <div
      ref={dialogRef}
      className="cook-root"
      role="dialog"
      aria-modal="true"
      aria-labelledby="cook-dialog-title"
    >
      <header className="cook-mode__header">
        <button
          ref={closeBtnRef}
          type="button"
          className="cook-icon-btn"
          aria-label="Закрыть режим готовки"
          onClick={close}
        >
          <SpriteIcon name="x" size={22} />
        </button>
        <div style={{ flex: 1, minWidth: 0 }}>
          <div className="cook-mode__eyebrow">Режим готовки</div>
          <div className="cook-mode__title" id="cook-dialog-title">
            {title}
          </div>
        </div>
        <button
          type="button"
          className="cook-icon-btn"
          aria-label="Не гасить экран"
          aria-pressed={wakeOn}
          onClick={toggleWake}
        >
          <SpriteIcon name="sun" size={22} />
        </button>
      </header>
      <div className="cook-mode__body">
        {phase === 'done' ? (
          <div className="cook-complete">
            <h2>Готово!</h2>
            <p>{title} — все шаги пройдены.</p>
            <button type="button" className="btn-primary" onClick={close}>
              Закрыть
            </button>
          </div>
        ) : phase === 'setup' ? (
          <div className="cook-setup">
            <section className="cook-setup__section">
              <h2 className="cook-setup__heading">Когда начнёте?</h2>
              <div className="cook-start-options">
                <button
                  type="button"
                  className={`cook-start-btn${plan ? '' : ' is-active'}`}
                  aria-pressed={!plan}
                  onClick={() => {
                    setPlan(false);
                    setStartMs(Date.now());
                  }}
                >
                  Сейчас
                </button>
                <button
                  type="button"
                  className={`cook-start-btn${plan ? ' is-active' : ''}`}
                  aria-pressed={plan}
                  onClick={() => {
                    setPlan(true);
                    setStartMs(Date.now() + 3600000);
                  }}
                >
                  Запланировать
                </button>
              </div>
              {plan && (
                <label className="cook-datetime-wrap">
                  <span className="cook-datetime-label">Время начала готовки</span>
                  <input
                    type="datetime-local"
                    className="cook-datetime"
                    defaultValue={toDatetimeLocal(new Date(Date.now() + 3600000))}
                    onChange={(e) => {
                      const parsed = new Date(e.target.value);
                      if (!Number.isNaN(parsed.getTime())) setStartMs(parsed.getTime());
                    }}
                  />
                </label>
              )}
            </section>
            {prep.length > 0 && (
              <section className="cook-setup__section">
                <h2 className="cook-setup__heading">Заранее</h2>
                <p className="cook-setup__hint">
                  Напоминания о разморозке, достаньте из холодильника, маринаде
                </p>
                <ul className="cook-prep-list">
                  {prep.map((item) => (
                    <li key={`${item.type}-${item.text}`} className="cook-prep-item">
                      <div className="cook-prep-item__body">
                        <span className="cook-prep-item__type">
                          {PREP_LABELS[item.type] || 'Подготовка'}
                        </span>
                        <p className="cook-prep-item__text">{item.text}</p>
                        <span className="cook-prep-item__when">
                          за {formatDuration(item.before_min * 60)} до старта ·{' '}
                          {new Date(startMs - item.before_min * 60 * 1000).toLocaleString('ru-RU', {
                            day: 'numeric',
                            month: 'short',
                            hour: '2-digit',
                            minute: '2-digit',
                          })}
                        </span>
                      </div>
                    </li>
                  ))}
                </ul>
              </section>
            )}
            <section className="cook-setup__section cook-setup__summary">
              <div className="cook-summary-stat">
                <span className="cook-summary-stat__n">{steps.length}</span> шагов
              </div>
              <div className="cook-summary-stat">
                <span className="cook-summary-stat__n">{timedCount}</span> с таймером
              </div>
            </section>
            <div className="cook-setup__actions">
              <button type="button" className="btn-primary" onClick={() => setPhase('steps')}>
                Начать готовку
              </button>
              {prep.length > 0 && (
                <button
                  type="button"
                  className="btn-secondary"
                  onClick={() => showToast(`Напоминания: ${prep.length}`)}
                >
                  Только напоминания
                </button>
              )}
            </div>
          </div>
        ) : (
          <div className="cook-steps">
            <div className="cook-steps__main">
              <div className="cook-progress" aria-hidden>
                <div
                  className="cook-progress__bar"
                  style={{ width: `${((index + 1) / steps.length) * 100}%` }}
                />
              </div>
              <div className="cook-progress__label" aria-live="polite">
                Шаг {index + 1} из {steps.length}
              </div>
              <article className={`cook-step-card${done.has(index) ? ' is-done' : ''}`}>
                <p>{step?.text}</p>
                {step?.target_internal_temperature_c != null && (
                  <span className="temp-chip">цель {step.target_internal_temperature_c} °C</span>
                )}
                {step?.pull_internal_temperature_c != null && (
                  <span className="temp-chip">снятие {step.pull_internal_temperature_c} °C</span>
                )}
                {timerSec > 0 && (
                  <div className={`cook-step-timer${running ? ' is-running' : ''}`}>
                    <div>{step.timer_label || formatDuration(timerSec)}</div>
                    <div className="cook-step-timer__display" aria-live="polite">
                      {formatClock(remaining ?? timerSec)}
                    </div>
                    {step.timer_note && <p className="note">{step.timer_note}</p>}
                    {!running && (
                      <div className="cook-step-timer__adjust">
                        <button
                          type="button"
                          className="btn-secondary"
                          aria-label="Уменьшить"
                          onClick={() => setDuration((n) => Math.max(30, (n || timerSec) - adjust))}
                        >
                          −{formatDuration(adjust)}
                        </button>
                        <button
                          type="button"
                          className="btn-secondary"
                          aria-label="Увеличить"
                          onClick={() => setDuration((n) => (n || timerSec) + adjust)}
                        >
                          +{formatDuration(adjust)}
                        </button>
                      </div>
                    )}
                    <div className="recipe-actions" style={{ border: 'none', marginTop: 12, paddingTop: 0 }}>
                      {running ? (
                        <>
                          <button type="button" className="btn-secondary" onClick={() => setRunning(false)}>
                            Пауза
                          </button>
                          <button type="button" className="btn-secondary" onClick={resetTimer}>
                            Сброс
                          </button>
                        </>
                      ) : (
                        <button type="button" className="btn-primary" onClick={startTimer}>
                          {remaining != null && remaining < timerSec && remaining > 0
                            ? 'Продолжить'
                            : `Старт ${formatDuration(timerSec)}`}
                        </button>
                      )}
                    </div>
                  </div>
                )}
              </article>
              <label className="cook-step-check" style={{ display: 'flex', gap: 8, marginBottom: 12 }}>
                <input
                  type="checkbox"
                  checked={done.has(index)}
                  onChange={(e) => {
                    setDone((prev) => {
                      const next = new Set(prev);
                      if (e.target.checked) next.add(index);
                      else next.delete(index);
                      return next;
                    });
                  }}
                />
                Шаг выполнен
              </label>
              <nav className="cook-step-nav">
                <button
                  type="button"
                  className="btn-secondary"
                  disabled={index === 0}
                  onClick={() => setIndex((i) => Math.max(0, i - 1))}
                >
                  ← Назад
                </button>
                <button
                  type="button"
                  className="btn-primary"
                  onClick={() => {
                    setDone((prev) => new Set(prev).add(index));
                    if (index >= steps.length - 1) setPhase('done');
                    else setIndex((i) => i + 1);
                  }}
                >
                  {index >= steps.length - 1 ? 'Готово' : 'Далее →'}
                </button>
              </nav>
              <details className="cook-step-overview cook-step-overview--mobile">
                <summary>Все шаги</summary>
                {stepList}
              </details>
            </div>
            <aside className="cook-steps__rail" aria-label="Все шаги">
              <h2 className="cook-rail-title">Все шаги</h2>
              {stepList}
            </aside>
          </div>
        )}
      </div>
      {toast && (
        <div className="cook-mode__toast" role="status" aria-live="polite">
          {toast}
        </div>
      )}
    </div>
  );
}
```

---

## 6. `frontend/components/Feedback.tsx`

- Путь: `v2/frontend/components/Feedback.tsx`
- Экспорты: EmptyState, ErrorBanner
- Строк: 17

```tsx
import type { ReactNode } from 'react';

export function EmptyState({ children }: { children: ReactNode }) {
  return (
    <div className="empty-state" role="status">
      {children}
    </div>
  );
}

export function ErrorBanner({ message }: { message: string }) {
  return (
    <div className="error-banner" role="alert">
      {message}
    </div>
  );
}
```

---

## 7. `frontend/components/FilterChip.tsx`

- Путь: `v2/frontend/components/FilterChip.tsx`
- Экспорты: FilterChip
- Строк: 32

```tsx
'use client';

import { useRouter } from 'next/navigation';
import type { ReactNode } from 'react';

export function FilterChip({
  href,
  pressed,
  children,
  ariaLabel,
  hint,
}: {
  href: string;
  pressed: boolean;
  children: ReactNode;
  ariaLabel?: string;
  hint?: string;
}) {
  const router = useRouter();
  return (
    <button
      type="button"
      className={pressed ? 'chip is-active' : 'chip'}
      aria-pressed={pressed}
      aria-label={ariaLabel}
      title={hint}
      onClick={() => router.push(href)}
    >
      {children}
    </button>
  );
}
```

---

## 8. `frontend/components/FilterPanel.tsx`

- Путь: `v2/frontend/components/FilterPanel.tsx`
- Экспорты: ChipGroup
- Строк: 43

```tsx
import type { SearchParamsRecord } from '@/lib/types';
import { isSelected, toggleHref } from '@/lib/filters';
import { FilterChip } from '@/components/FilterChip';

export function ChipGroup({
  legend,
  map,
  param,
  pathname,
  sp,
  codes,
}: {
  legend: string;
  map: Record<string, string>;
  param: string;
  pathname: string;
  sp: SearchParamsRecord;
  codes?: string[];
}) {
  const entries = codes
    ? codes.filter((code) => map[code]).map((code) => [code, map[code]] as const)
    : Object.entries(map);
  if (entries.length === 0) return null;
  return (
    <fieldset className="filter-block">
      <legend className="filter-legend">{legend}</legend>
      <div className="chip-row">
        {entries.map(([code, label]) => {
          const selected = isSelected(sp, param, code);
          return (
            <FilterChip
              key={code}
              href={toggleHref(pathname, sp, param, code)}
              pressed={selected}
            >
              {label}
            </FilterChip>
          );
        })}
      </div>
    </fieldset>
  );
}
```

---

## 9. `frontend/components/Guides.tsx`

- Путь: `v2/frontend/components/Guides.tsx`
- Экспорты: GrainsView, MeatView
- Строк: 110

```tsx
import type { GrainsPayload, MeatPayload } from '@/lib/types';
import { EmptyState } from '@/components/Feedback';

export function GrainsView({
  payload,
  omitLead = false,
}: {
  payload: GrainsPayload;
  omitLead?: boolean;
}) {
  const rows = payload.rows ?? [];
  return (
    <>
      {!omitLead && (payload.intro_lead || payload.intro) && (
        <p className="lede">
          {payload.intro_lead ? <strong>{payload.intro_lead} </strong> : null}
          {payload.intro}
        </p>
      )}
      {rows.length === 0 ? (
        <EmptyState>Пока нет таблицы круп.</EmptyState>
      ) : (
        <>
          <table className="grains">
            <caption className="sr-only">Крупы: промывка, вода, время</caption>
            <thead>
              <tr>
                <th scope="col">Крупа</th>
                <th scope="col">Промывка</th>
                <th scope="col">Вода</th>
                <th scope="col">Время</th>
                <th scope="col">Нюанс</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((row) => (
                <tr key={row.name}>
                  <td className="name">{row.name}</td>
                  <td>{row.wash}</td>
                  <td className="ratio">{row.ratio}</td>
                  <td>{row.time}</td>
                  <td className="note">{row.note}</td>
                </tr>
              ))}
            </tbody>
          </table>
          <div className="grain-cards">
            {rows.map((row) => (
              <article key={row.name} className="grain-card">
                <h3>{row.name}</h3>
                <p>
                  <span className="ratio">{row.ratio}</span> · {row.time}
                </p>
                <p className="note">Промывка: {row.wash}</p>
                <p className="note">{row.note}</p>
              </article>
            ))}
          </div>
        </>
      )}
    </>
  );
}

export function MeatView({
  payload,
  omitLead = false,
}: {
  payload: MeatPayload;
  omitLead?: boolean;
}) {
  const methods = payload.methods ?? [];
  return (
    <>
      {!omitLead && (payload.intro_lead || payload.intro) && (
        <p className="lede">
          {payload.intro_lead ? <strong>{payload.intro_lead} </strong> : null}
          {payload.intro}
        </p>
      )}
      {methods.length === 0 ? (
        <EmptyState>Пока нет карточек по этому мясу.</EmptyState>
      ) : (
        methods.map((method) => (
          <section key={method.name} className="method-block">
            <div className="method-head">
              <h2>{method.name}</h2>
              <span className="sub">{method.sub}</span>
            </div>
            <div className="cards">
              {method.cards.map((card) => (
                <article key={card.title} className="card">
                  <h3>{card.title}</h3>
                  <div className="readout">
                    <span className="lbl">{card.readout_label}</span>
                    {card.readout_value}
                  </div>
                  <p>{card.text}</p>
                  <p className="pitfall">
                    <b>Ошибка:</b> {card.pitfall}
                  </p>
                </article>
              ))}
            </div>
          </section>
        ))
      )}
    </>
  );
}
```

---

## 10. `frontend/components/HashDetailsOpener.tsx`

- Путь: `v2/frontend/components/HashDetailsOpener.tsx`
- Экспорты: HashDetailsOpener
- Строк: 37

```tsx
'use client';

import { useEffect } from 'react';

/** Opens a matching `<details id>` (and ancestor details) when the URL hash points at it. */
export function HashDetailsOpener({
  watch,
  exclusive,
}: {
  watch?: unknown;
  exclusive?: string;
} = {}) {
  useEffect(() => {
    const openFromHash = () => {
      const id = decodeURIComponent(window.location.hash.replace(/^#/, ''));
      if (!id) return;
      const el = document.getElementById(id);
      if (!el) return;
      if (el instanceof HTMLDetailsElement && exclusive) {
        document.querySelectorAll(exclusive).forEach((node) => {
          if (node instanceof HTMLDetailsElement && node !== el) node.open = false;
        });
      }
      let node: HTMLElement | null = el;
      while (node) {
        if (node instanceof HTMLDetailsElement) {
          node.open = true;
        }
        node = node.parentElement;
      }
    };
    openFromHash();
    window.addEventListener('hashchange', openFromHash);
    return () => window.removeEventListener('hashchange', openFromHash);
  }, [watch, exclusive]);
  return null;
}
```

---

## 11. `frontend/components/IngredientsBlock.tsx`

- Путь: `v2/frontend/components/IngredientsBlock.tsx`
- Экспорты: IngredientsBlock
- Строк: 271

```tsx
'use client';

import { useId, useMemo, useState } from 'react';
import { NutritionBlock } from '@/components/NutritionBlock';
import { SpriteIcon } from '@/components/SpriteIcon';
import { computeNutrition } from '@/lib/nutrition';
import { formatDisplayAmount, scaleIngredients } from '@/lib/scale';
import type { RecipeIngredient, Scaling } from '@/lib/types';

type UnitPair = { small: string; large: string; factor: number };

function unitPairOf(unit?: string): UnitPair | null {
  if (unit === 'g' || unit === 'kg') return { small: 'г', large: 'кг', factor: 1000 };
  if (unit === 'ml' || unit === 'l') return { small: 'мл', large: 'л', factor: 1000 };
  return null;
}

function formatFactor(ratio: number): string {
  if (!Number.isFinite(ratio) || Math.abs(ratio - 1) < 0.01) return '';
  if (Math.abs(ratio - Math.round(ratio * 10) / 10) < 0.01) {
    return `×${String(ratio).replace('.', ',')}`;
  }
  return `×${ratio.toFixed(2).replace('.', ',')}`;
}

function formatInput(value: number): string {
  if (!Number.isFinite(value)) return '';
  if (Number.isInteger(value)) return String(value);
  return String(Math.round(value * 1000) / 1000);
}

function displayOf(base: number, pair: UnitPair | null, large: boolean): number {
  if (!pair || !large) return base;
  return Math.round((base / pair.factor) * 1000) / 1000;
}

function baseFromInput(raw: string, pair: UnitPair | null, large: boolean): number | null {
  const n = Number(raw.replace(',', '.'));
  if (!Number.isFinite(n) || n <= 0) return null;
  if (!pair || !large) return n;
  return n * pair.factor;
}

function stepForBase(base: number): number {
  return base >= 500 ? 250 : 50;
}

const KBJU_SKIP_TIP = 'КБЖУ для этой строки не считается.';

function NutritionSkipHint() {
  const [open, setOpen] = useState(false);
  return (
    <button
      type="button"
      className="recipe-list__kbju-hint"
      aria-label={KBJU_SKIP_TIP}
      aria-expanded={open}
      data-tip={KBJU_SKIP_TIP}
      onClick={() => setOpen((value) => !value)}
      onBlur={() => setOpen(false)}
    >
      <SpriteIcon name="info" size={16} />
    </button>
  );
}

type Props = {
  scaling: Scaling;
  ingredients: RecipeIngredient[];
  servingsBase?: number | null;
  yieldWeightG?: number | null;
  yieldKind?: 'estimated' | 'exact' | null;
  hasTimers?: boolean;
};

export function IngredientsBlock({
  scaling,
  ingredients,
  servingsBase = null,
  yieldWeightG = null,
  yieldKind = null,
  hasTimers = false,
}: Props) {
  const enabled = scaling.enabled === true;
  const mode = scaling.mode;
  const baseAnchor = scaling.base_anchor;
  const showAnchor = enabled && mode !== 'servings' && Boolean(baseAnchor);
  const showServings = enabled && mode === 'servings' && Boolean(servingsBase);
  const defaultWeight = baseAnchor?.amount ?? 0;
  const [anchorWeight, setAnchorWeight] = useState(
    scaling.applied?.anchor_weight ?? defaultWeight,
  );
  const [servings, setServings] = useState(scaling.applied?.servings ?? servingsBase ?? 1);
  const pair = useMemo(() => unitPairOf(baseAnchor?.unit), [baseAnchor?.unit]);
  const [useLarge, setUseLarge] = useState(baseAnchor?.unit === 'kg' || baseAnchor?.unit === 'l');
  const unitGroup = useId();

  const ratio = showServings
    ? servings / (servingsBase || 1)
    : showAnchor && defaultWeight > 0
      ? anchorWeight / defaultWeight
      : 1;
  const items = useMemo(() => scaleIngredients(ingredients, ratio), [ingredients, ratio]);
  const nutrition = useMemo(
    () =>
      computeNutrition(ingredients, {
        ratio,
        servings: showServings ? servings : servingsBase,
        yieldWeightG,
      }),
    [ingredients, ratio, showServings, servings, servingsBase, yieldWeightG],
  );

  const factorLabel = showAnchor ? formatFactor(ratio) : '';
  const showReset = showAnchor && Math.abs(ratio - 1) >= 0.01;
  const step = stepForBase(anchorWeight || defaultWeight);
  const displayValue = displayOf(anchorWeight, pair, useLarge);
  const displayStep = pair && useLarge ? step / pair.factor : step;

  return (
    <>
      <section className="recipe-section recipe-ingredients">
        <h2>Ингредиенты</h2>
        {showAnchor && baseAnchor && (
          <div className="recipe-scale">
            <div className="recipe-scale__head">
              <span className="recipe-scale__label">У меня</span>
              {factorLabel ? <span className="recipe-scale__factor">{factorLabel}</span> : null}
            </div>
            <div className="recipe-scale__row">
              <button
                type="button"
                className="btn-secondary recipe-scale__step"
                aria-label="Уменьшить количество"
                onClick={() => setAnchorWeight((n) => Math.max(step, n - step))}
              >
                −
              </button>
              <input
                className="recipe-scale__input"
                type="number"
                inputMode="decimal"
                min={pair && useLarge ? step / pair.factor : step}
                step={displayStep}
                value={formatInput(displayValue)}
                aria-label={`Количество: ${baseAnchor.name}`}
                onChange={(e) => {
                  const next = baseFromInput(e.target.value, pair, useLarge);
                  if (next != null) setAnchorWeight(next);
                }}
              />
              {pair && (
                <div
                  className={`recipe-scale__units${useLarge ? ' is-large' : ''}`}
                  role="radiogroup"
                  aria-label="Единица измерения"
                >
                  <label className="recipe-scale__unit">
                    <input
                      type="radio"
                      name={unitGroup}
                      checked={!useLarge}
                      onChange={() => setUseLarge(false)}
                    />
                    {pair.small}
                  </label>
                  <label className="recipe-scale__unit">
                    <input
                      type="radio"
                      name={unitGroup}
                      checked={useLarge}
                      onChange={() => setUseLarge(true)}
                    />
                    {pair.large}
                  </label>
                </div>
              )}
              <button
                type="button"
                className="btn-secondary recipe-scale__step"
                aria-label="Увеличить количество"
                onClick={() => setAnchorWeight((n) => n + step)}
              >
                +
              </button>
            </div>
            <p className="recipe-scale__meta">
              <span>
                {baseAnchor.name}
                {baseAnchor.unit
                  ? ` · в рецепте ${formatDisplayAmount(baseAnchor.amount, baseAnchor.unit)}`
                  : null}
              </span>
              {showReset && (
                <button
                  type="button"
                  className="recipe-scale__reset"
                  onClick={() => {
                    setAnchorWeight(defaultWeight);
                    setUseLarge(false);
                  }}
                >
                  Сброс
                </button>
              )}
            </p>
            {showReset && hasTimers && (
              <p className="recipe-scale__timer-hint">
                Время готовки не пересчитывается — ориентируйтесь на шаги и подстройте таймеры в
                режиме готовки.
              </p>
            )}
          </div>
        )}
        {showServings && (
          <div className="recipe-scale">
            <div className="recipe-scale__head">
              <span>Порции</span>
            </div>
            <div className="recipe-scale__row">
              <button
                type="button"
                className="btn-secondary"
                aria-label="Меньше порций"
                onClick={() => setServings((n) => Math.max(1, n - 1))}
              >
                −
              </button>
              <input
                className="recipe-scale__input"
                type="number"
                min={1}
                step={1}
                value={servings}
                aria-label="Число порций"
                onChange={(e) => {
                  const next = Number(e.target.value);
                  if (Number.isFinite(next) && next > 0) setServings(next);
                }}
              />
              <button
                type="button"
                className="btn-secondary"
                aria-label="Больше порций"
                onClick={() => setServings((n) => n + 1)}
              >
                +
              </button>
            </div>
          </div>
        )}
        <ul className="recipe-list">
          {items.map((item, index) => (
            <li key={`${item.name}-${index}`}>
              <span className="amount">{item.display_amount}</span>
              <span>
                {item.name}
                {item.detail ? <span className="detail">{item.detail}</span> : null}
                {item.scale_mode === 'manual' ? (
                  <span className="manual-hint">проверьте по исходному рецепту</span>
                ) : null}
              </span>
              {item.nutrition_skip_hint ? <NutritionSkipHint /> : null}
            </li>
          ))}
        </ul>
      </section>
      <NutritionBlock nutrition={nutrition} yieldKind={yieldKind} />
    </>
  );
}
```

---

## 12. `frontend/components/NutritionBlock.tsx`

- Путь: `v2/frontend/components/NutritionBlock.tsx`
- Экспорты: NutritionBlock
- Строк: 105

```tsx
'use client';

import { useId, useState } from 'react';
import { formatKcal, formatMacro } from '@/lib/nutrition';
import type { NutritionMacros, RecipeNutrition } from '@/lib/types';

type Cell = {
  key: string;
  label: string;
  macros: NutritionMacros;
};

const METHOD_TEXT =
  'Суммируем белки, жиры, углеводы и ккал продуктов с известной пищевой ценностью до готовки. Соль, специи «по вкусу» и строки «по желанию» не входят. Цифры ориентировочные: масло, бульон и конкретный бренд могут отличаться от справочника.';

function MacroCell({ label, macros }: { label: string; macros: NutritionMacros }) {
  return (
    <div className="recipe-nutrition__cell">
      <p className="recipe-nutrition__label">{label}</p>
      <p className="recipe-nutrition__kcal">
        {formatKcal(macros.kcal)} <span>ккал</span>
      </p>
      <p className="recipe-nutrition__macros">
        Б {formatMacro(macros.protein_g)} · Ж {formatMacro(macros.fat_g)} · У{' '}
        {formatMacro(macros.carbs_g)}
      </p>
    </div>
  );
}

export function NutritionBlock({
  nutrition,
  yieldKind = null,
}: {
  nutrition: RecipeNutrition;
  yieldKind?: 'estimated' | 'exact' | null;
}) {
  const methodId = useId();
  const [methodOpen, setMethodOpen] = useState(false);
  const cells: Cell[] = [];
  if (nutrition.total) {
    cells.push({ key: 'total', label: 'На рецепт', macros: nutrition.total });
  }
  if (nutrition.per_100g_input) {
    cells.push({
      key: 'per100',
      label: 'На 100 г продуктов (до готовки)',
      macros: nutrition.per_100g_input,
    });
  }
  if (nutrition.per_100g_cooked) {
    const estimated = yieldKind !== 'exact';
    cells.push({
      key: 'cooked',
      label: estimated ? 'На 100 г готового (оценка)' : 'На 100 г готового',
      macros: nutrition.per_100g_cooked,
    });
  }
  if (nutrition.per_serving) {
    cells.push({ key: 'serving', label: 'На порцию', macros: nutrition.per_serving });
  }
  if (cells.length === 0) return null;
  const omitted = (nutrition.omitted ?? []).filter(Boolean);
  const omittedText =
    omitted.length > 0
      ? omitted.join(', ')
      : 'масло, соль или бульон конкретного бренда';

  return (
    <section className="recipe-nutrition" aria-label="КБЖУ ориентировочно">
      <h2>КБЖУ ориентировочно</h2>
      {nutrition.incomplete && (
        <p className="recipe-nutrition__incomplete">
          Неполный расчёт: не учтены {omittedText}. Цифрам можно доверять как ориентиру, не как
          точной этикетке.
        </p>
      )}
      <p className="recipe-nutrition__disclaimer">
        Ориентировочно. Зависит от продукта и способа приготовления.{' '}
        <button
          type="button"
          className="recipe-nutrition__method-btn"
          aria-expanded={methodOpen}
          aria-controls={methodId}
          onClick={() => setMethodOpen((value) => !value)}
        >
          Как считаем
        </button>
      </p>
      {methodOpen ? (
        <p className="recipe-nutrition__method" id={methodId}>
          {METHOD_TEXT}
        </p>
      ) : null}
      <div
        className="recipe-nutrition__grid"
        data-cols={cells.length}
      >
        {cells.map((cell) => (
          <MacroCell key={cell.key} label={cell.label} macros={cell.macros} />
        ))}
      </div>
    </section>
  );
}
```

---

## 13. `frontend/components/PageArt.tsx`

- Путь: `v2/frontend/components/PageArt.tsx`
- Экспорты: PageArt, PageIntro
- Строк: 70

```tsx
import type { ReactNode } from 'react';

export type ArtScene =
  | 'home'
  | 'calculator'
  | 'grains'
  | 'meat'
  | 'beef'
  | 'pork'
  | 'poultry'
  | 'tips'
  | 'prep'
  | 'recipes';

const ART_SRC: Record<ArtScene, string> = {
  home: '/art/main-bg.png',
  calculator: '/art/pantry.png',
  grains: '/art/grains.png',
  meat: '/art/main-bg.png',
  beef: '/art/main-bg.png',
  pork: '/art/pork.png',
  poultry: '/art/poultry.png',
  tips: '/art/tools.png',
  prep: '/art/prep.png',
  recipes: '/art/recipes.png',
};

export function PageArt({ scene }: { scene: ArtScene }) {
  return (
    <div className="page-art" aria-hidden>
      <img
        className="page-art__paint"
        src={`${ART_SRC[scene]}?v=9`}
        alt=""
        width={1024}
        height={518}
        decoding="async"
        loading={scene === 'home' ? 'eager' : 'lazy'}
      />
    </div>
  );
}

export function PageIntro({
  eyebrow,
  title,
  lede,
  actions,
  scene,
  showArt = true,
}: {
  eyebrow: string;
  title: ReactNode;
  lede?: ReactNode;
  actions?: ReactNode;
  scene: ArtScene;
  showArt?: boolean;
}) {
  return (
    <header className={`page-intro${showArt ? '' : ' page-intro--no-art'} page-intro--${scene}`}>
      <div className="page-intro__copy">
        <p className="eyebrow">{eyebrow}</p>
        <h1>{title}</h1>
        {lede}
        {actions}
      </div>
      {showArt ? <PageArt scene={scene} /> : null}
    </header>
  );
}
```

---

## 14. `frontend/components/PantryTextForm.tsx`

- Путь: `v2/frontend/components/PantryTextForm.tsx`
- Экспорты: PantryTextForm
- Строк: 129

```tsx
'use client';

import { useRouter } from 'next/navigation';
import { useId, useState } from 'react';
import { clientFetch } from '@/lib/client-api';
import { FILTER_KEYS, toURLSearchParams, valuesOf } from '@/lib/filters';
import type { PantryGroup, PantryResolveResponse, SearchParamsRecord } from '@/lib/types';

function pathForHave(groups: PantryGroup[], canonicalId: string): string {
  for (const group of groups) {
    const own = group.items?.find((item) => item.canonical_id === canonicalId);
    if (own) return own.title;
    for (const child of group.children ?? []) {
      const nested = child.items?.find((item) => item.canonical_id === canonicalId);
      if (nested) return nested.title;
    }
  }
  return canonicalId;
}

export function PantryTextForm({
  sp,
  groups,
}: {
  sp: SearchParamsRecord;
  groups: PantryGroup[];
}) {
  const router = useRouter();
  const hintId = useId();
  const resultId = useId();
  const initialText = valuesOf(sp, 'pantry')[0] ?? '';
  const [text, setText] = useState(initialText);
  const [unknown, setUnknown] = useState<string[]>(valuesOf(sp, 'missed'));
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');

  const recognized = valuesOf(sp, 'have');
  const missed = unknown.length ? unknown : valuesOf(sp, 'missed');
  const showResult = recognized.length > 0 || missed.length > 0 || Boolean(error);

  async function onSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const raw = text.trim();
    if (!raw) return;
    setBusy(true);
    setError('');
    setUnknown([]);
    try {
      const res = await clientFetch(`/api/ingredients/?text=${encodeURIComponent(raw)}`);
      const body = (await res.json()) as PantryResolveResponse;
      const items = body.items ?? [];
      const missedItems = body.unknown ?? [];
      setUnknown(missedItems);
      if (items.length === 0) {
        setError(
          missedItems.length
            ? `Не распознали: ${missedItems.join(', ')}. Попробуйте названия через запятую, как в примере.`
            : 'Не удалось разобрать продукты.',
        );
        return;
      }
      const qs = toURLSearchParams(sp);
      qs.delete('have');
      qs.delete('missed');
      qs.delete('pantry');
      qs.set('pantry', raw);
      for (const item of items) qs.append('have', item.canonical_id);
      for (const item of missedItems) qs.append('missed', item);
      router.push(qs.toString() ? `/calculator?${qs.toString()}` : '/calculator');
    } catch {
      setError('Не удалось связаться с сервером. Попробуйте позже.');
    } finally {
      setBusy(false);
    }
  }

  return (
    <form className="calc-pantry" action="/calculator" method="get" onSubmit={onSubmit}>
      <label htmlFor="pantry-text">Что есть дома</label>
      <textarea
        id="pantry-text"
        name="pantry"
        rows={2}
        value={text}
        onChange={(event) => setText(event.target.value)}
        placeholder="курица, рис, лук, томаты"
        autoComplete="off"
        aria-describedby={hintId}
      />
      <p id={hintId} className="calc-pantry__hint">
        Перечислите продукты через запятую. Пример: курица, рис, лук, томаты.
      </p>
      {FILTER_KEYS.filter((key) => key !== 'have').flatMap((key) => {
        const raw = sp[key];
        const list = raw == null || raw === '' ? [] : Array.isArray(raw) ? raw : [raw];
        return list.map((value) => (
          <input key={`${key}-${value}`} type="hidden" name={key} value={value} />
        ));
      })}
      <button type="submit" className="btn-primary" disabled={busy}>
        Подобрать рецепты
      </button>
      {showResult ? (
        <div className="calc-pantry__result" id={resultId} role="status">
          {recognized.length > 0 ? (
            <p>
              <strong>Распознали:</strong>{' '}
              {recognized.map((id) => pathForHave(groups, id)).join(', ')}
            </p>
          ) : null}
          {missed.length > 0 ? (
            <p>
              <strong>Не распознали:</strong> {missed.join(', ')}. Можно исправить запрос в поле
              выше и подобрать снова.
            </p>
          ) : null}
          {error ? <p className="calc-pantry__note">{error}</p> : null}
          <button
            type="button"
            className="calc-pantry__edit"
            onClick={() => document.getElementById('pantry-text')?.focus()}
          >
            Изменить запрос
          </button>
        </div>
      ) : null}
    </form>
  );
}
```

---

## 15. `frontend/components/PrepKitView.tsx`

- Путь: `v2/frontend/components/PrepKitView.tsx`
- Экспорты: PrepKitView
- Строк: 285

```tsx
'use client';

import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useState } from 'react';
import type { PrepKitDetail, PrepSlot } from '@/lib/types';
import { recipeHref } from '@/lib/filters';
import { SpriteIcon } from '@/components/SpriteIcon';
import {
  PREP_DAY_RU,
  PREP_MEAL_RU,
  PREP_MODE_RU,
  PREP_PLACE_RU,
  PREP_SERVING_OPTIONS,
  formatServingsLabel,
  kitHref,
  leftoverCostCaption,
  thawRemindersForDay,
  coldContainerCaption,
  formatThawColumn,
} from '@/lib/prep';

const TABS = [
  { id: 'shop', label: 'Что купить', icon: 'shopping-basket' },
  { id: 'sunday', label: 'Подготовить в воскресенье', icon: 'refrigerator' },
  { id: 'meals', label: 'Блюда на неделю', icon: 'utensils' },
] as const;

function slotTitle(slot: PrepSlot): string {
  return slot.plate_title || slot.flavor || slot.title;
}

function stringList(value: unknown): string[] {
  if (!Array.isArray(value)) return [];
  return value.filter((item): item is string => typeof item === 'string' && item.trim() !== '');
}

function SundayIntro({ row, index }: { row: Record<string, unknown>; index: number }) {
  const gear = stringList(row.gear);
  const plan = stringList(row.plan);
  if (gear.length > 0 || plan.length > 0) {
    return (
      <div className="prep-sunday-intro">
        {gear.length > 0 && (
          <section className="prep-sunday-intro__col" aria-labelledby={`prep-gear-${index}`}>
            <h3 id={`prep-gear-${index}`}>Посуда</h3>
            <ul>
              {gear.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          </section>
        )}
        {plan.length > 0 && (
          <section className="prep-sunday-intro__col" aria-labelledby={`prep-plan-${index}`}>
            <h3 id={`prep-plan-${index}`}>Сегодня</h3>
            <ul>
              {plan.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          </section>
        )}
      </div>
    );
  }
  const hands = typeof row.hands === 'string' ? row.hands : '';
  if (!hands) return null;
  return <p className="lede">{hands}</p>;
}

export function PrepKitView({
  kit,
  servings,
  noLeftover,
}: {
  kit: PrepKitDetail;
  servings: number | null;
  noLeftover: boolean;
}) {
  const router = useRouter();
  const [tab, setTab] = useState<(typeof TABS)[number]['id']>('shop');
  const applied = servings ?? kit.servings_base ?? 2;
  const servingOptions = kit.servings_base ? PREP_SERVING_OPTIONS : [];
  const leftoverCaption = leftoverCostCaption(kit.leftover_cost);
  const showLeftoverToggle = Boolean(kit.has_leftovers);
  const boxCaption = coldContainerCaption(kit.containers);
  const intro = kit.weekend_timeline.filter((row) => row.kind === 'intro');
  const recipeSteps = kit.weekend_timeline.filter((row) => row.kind !== 'intro');
  const planHref = (nextServings: number | null, nextNoLeftover: boolean) =>
    kitHref(kit.slug, {
      servings: nextServings,
      servingsBase: kit.servings_base,
      noLeftover: nextNoLeftover,
    });

  return (
    <>
      {(servingOptions.length > 0 || showLeftoverToggle) && (
        <div className="prep-plan">
          {servingOptions.length > 0 && (
            <div className="prep-servings" aria-label="Порции">
              {servingOptions.map((n) => (
                <Link
                  key={n}
                  href={planHref(n, noLeftover)}
                  className={applied === n ? 'chip is-active' : 'chip'}
                >
                  {formatServingsLabel(n)}
                </Link>
              ))}
            </div>
          )}
          {showLeftoverToggle && (
            <label className="prep-toggle">
              <input
                type="checkbox"
                checked={noLeftover}
                onChange={() => router.push(planHref(servings, !noLeftover))}
              />
              Без вчерашнего
              <span>
                Блюдо на один приём; вместо разогрева — другое из набора. Меняет закупку и
                воскресенье.
                {leftoverCaption ? ` ${leftoverCaption}` : ''}
              </span>
            </label>
          )}
        </div>
      )}

      <div className="prep-tabs" role="tablist" aria-label="Разделы набора">
        {TABS.map((item) => (
          <button
            key={item.id}
            type="button"
            role="tab"
            aria-selected={tab === item.id}
            className={tab === item.id ? 'chip is-active' : 'chip'}
            onClick={() => setTab(item.id)}
          >
            <SpriteIcon name={item.icon} size={16} />
            {item.label}
          </button>
        ))}
      </div>

      {tab === 'shop' && (
        <section>
          <h2>Что купить</h2>
          {kit.shopping.length === 0 ? (
            <p>Список закупки пуст.</p>
          ) : (
            <table className="prep-table">
              <thead>
                <tr>
                  <th>Продукт</th>
                  <th>Количество</th>
                </tr>
              </thead>
              <tbody>
                {kit.shopping.map((row) => (
                  <tr key={row.canonical_id}>
                    <td>{row.title_ru || row.canonical_id}</td>
                    <td>{row.display_amount}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </section>
      )}

      {tab === 'sunday' && (
        <section>
          <h2>Рецепт воскресенья</h2>
          {intro.map((row, index) => (
            <SundayIntro key={`intro-${index}`} row={row} index={index} />
          ))}
          {recipeSteps.length > 0 && (
            <ol className="prep-recipe">
              {recipeSteps.map((row, index) => {
                const text = typeof row.hands === 'string' ? row.hands : '';
                return (
                  <li key={index}>
                    <span>{text}</span>
                  </li>
                );
              })}
            </ol>
          )}
          <h3>Куда разложить</h3>
          {boxCaption && <p className="lede">{boxCaption}</p>}
          <table className="prep-table">
            <thead>
              <tr>
                <th>Бокс</th>
                <th>Что</th>
                <th>Где</th>
                <th>Достать</th>
              </tr>
            </thead>
            <tbody>
              {kit.containers.map((box) => (
                <tr key={box.code}>
                  <td>
                    {box.label} · {box.display_amount}
                  </td>
                  <td>{box.component_title}</td>
                  <td>{PREP_PLACE_RU[box.place] || box.place}</td>
                  <td>{formatThawColumn(box)}</td>
                </tr>
              ))}
            </tbody>
          </table>
          {kit.components.length > 0 && (
            <details className="prep-details">
              <summary>Подробнее по каждой заготовке</summary>
              {kit.components.map((item) => (
                <div key={item.code}>
                  <p>
                    <strong>{item.title}</strong> · {item.display_amount}
                  </p>
                  <ul>
                    {(item.weekend_steps ?? []).map((step, index) => (
                      <li key={index}>{typeof step === 'string' ? step : String(step)}</li>
                    ))}
                  </ul>
                </div>
              ))}
            </details>
          )}
        </section>
      )}

      {tab === 'meals' && (
        <section>
          <h2>Блюда на неделю</h2>
          <div className="prep-slot-grid">
            {[1, 2, 3, 4, 5, 6, 7].map((day) => {
              const lunch = kit.slots.find((slot) => slot.day === day && slot.meal === 'lunch');
              const dinner = kit.slots.find((slot) => slot.day === day && slot.meal === 'dinner');
              const thawLines = thawRemindersForDay(day, kit.containers);
              return (
                <div key={day} className="prep-day">
                  <p className="prep-day__title">{PREP_DAY_RU[day]}</p>
                  {thawLines.map((line) => (
                    <p key={line} className="prep-day__thaw">
                      {line}
                    </p>
                  ))}
                  <div className="prep-slot-row">
                    {[lunch, dinner].map((slot) => {
                      if (!slot) return null;
                      return (
                        <Link
                          key={`${slot.day}-${slot.meal}`}
                          className="prep-slot"
                          href={recipeHref(slot.slug, {
                            prep: kit.slug,
                            day: slot.day,
                            meal: slot.meal,
                            servings: servings,
                            noLeftover,
                          })}
                        >
                          <span className="prep-mode">{PREP_MODE_RU[slot.mode]}</span>
                          <span className="prep-slot__meal">{PREP_MEAL_RU[slot.meal]}</span>
                          <strong>{slotTitle(slot)}</strong>
                          {slot.plate_composition && (
                            <span className="prep-slot__composition">{slot.plate_composition}</span>
                          )}
                        </Link>
                      );
                    })}
                  </div>
                </div>
              );
            })}
          </div>
        </section>
      )}
    </>
  );
}
```

---

## 16. `frontend/components/RecipeActions.tsx`

- Путь: `v2/frontend/components/RecipeActions.tsx`
- Экспорты: CopyLinkButton, RecipeActions
- Строк: 70

```tsx
'use client';

import { useState } from 'react';
import type { RecipePrep, RecipeStep } from '@/lib/types';
import { CookMode } from './CookMode';
import { RecipeTabBar } from './Chrome';

export function CopyLinkButton() {
  const [label, setLabel] = useState('Скопировать ссылку');

  return (
    <button
      type="button"
      className="btn-secondary"
      onClick={async () => {
        try {
          await navigator.clipboard.writeText(window.location.href);
          setLabel('Скопировано');
          window.setTimeout(() => setLabel('Скопировать ссылку'), 2000);
        } catch {
          window.prompt('Скопируйте ссылку:', window.location.href);
        }
      }}
    >
      {label}
    </button>
  );
}

export function RecipeActions({
  title,
  steps,
  prep,
  backHref,
  backLabel,
}: {
  title: string;
  steps: RecipeStep[];
  prep?: RecipePrep[];
  backHref?: string;
  backLabel?: string;
}) {
  const [open, setOpen] = useState(false);
  const hasSteps = steps.length > 0;

  return (
    <>
      <div className="recipe-actions">
        {hasSteps && (
          <button type="button" className="btn-primary btn-cook" onClick={() => setOpen(true)}>
            Режим готовки
          </button>
        )}
        <CopyLinkButton />
      </div>
      {hasSteps && (
        <RecipeTabBar onCook={() => setOpen(true)} backHref={backHref} backLabel={backLabel} />
      )}
      {hasSteps && (
        <CookMode
          title={title}
          steps={steps}
          prep={prep}
          open={open}
          onClose={() => setOpen(false)}
        />
      )}
    </>
  );
}
```

---

## 17. `frontend/components/RecipeAxisSwitch.tsx`

- Путь: `v2/frontend/components/RecipeAxisSwitch.tsx`
- Экспорты: RecipeAxisSwitch, RecipeAxisLink
- Строк: 94

```tsx
'use client';

import Link from 'next/link';
import { useLayoutEffect, type MouseEvent, type ReactNode } from 'react';

let pending: { y: number; top: number; href: string } | null = null;

function pinScroll(y: number) {
  const html = document.documentElement;
  const previous = html.style.scrollBehavior;
  html.style.scrollBehavior = 'auto';
  window.scrollTo(0, y);
  html.style.scrollBehavior = previous;
}

function restoreFrom(snapshot: { y: number; top: number; href: string }) {
  const chip = document.querySelector(`[data-axis-href="${CSS.escape(snapshot.href)}"]`);
  if (chip instanceof HTMLElement) {
    const drift = chip.getBoundingClientRect().top - snapshot.top;
    if (Math.abs(drift) > 1) {
      pinScroll(window.scrollY + drift);
    }
    return;
  }
  pinScroll(snapshot.y);
}

export function RecipeAxisSwitch({
  applied,
  children,
}: {
  applied: string;
  children: ReactNode;
}) {
  useLayoutEffect(() => {
    if (!pending) return;
    const snapshot = pending;
    pending = null;
    restoreFrom(snapshot);
    let inner = 0;
    const outer = requestAnimationFrame(() => {
      restoreFrom(snapshot);
      inner = requestAnimationFrame(() => restoreFrom(snapshot));
    });
    return () => {
      cancelAnimationFrame(outer);
      cancelAnimationFrame(inner);
    };
  }, [applied]);

  return <>{children}</>;
}

export function RecipeAxisLink({
  href,
  className,
  children,
  current,
}: {
  href: string;
  className?: string;
  children: ReactNode;
  current?: boolean;
}) {
  return (
    <Link
      href={href}
      scroll={false}
      className={className}
      aria-current={current ? 'true' : undefined}
      aria-pressed={current}
      data-axis-href={href}
      onClick={(event: MouseEvent<HTMLAnchorElement>) => {
        if (
          event.defaultPrevented ||
          event.button !== 0 ||
          event.metaKey ||
          event.altKey ||
          event.ctrlKey ||
          event.shiftKey
        ) {
          return;
        }
        pending = {
          y: window.scrollY,
          top: event.currentTarget.getBoundingClientRect().top,
          href,
        };
      }}
    >
      {children}
    </Link>
  );
}
```

---

## 18. `frontend/components/RecipeCard.tsx`

- Путь: `v2/frontend/components/RecipeCard.tsx`
- Экспорты: RecipeCard, RecipeGrid, SolutionBoard, SolutionBuckets
- Строк: 257

```tsx
import Link from 'next/link';
import type { AlternativeSolution, RecipeCardData } from '@/lib/types';
import { effortLabel, minutesLabel, solutionTimeLabel } from '@/lib/catalog';
import { recipeHref } from '@/lib/filters';
import {
  COOK_METHOD,
  DISH_TYPE,
  PROTEIN_BASE,
  equipmentLabel,
  labelOf,
  pickGuestProteinVariant,
} from '@/lib/vocab';
import { AllergenNotice } from '@/components/AllergenNotice';

export type BookCardContext = {
  chapterId?: string;
  proteinFilter?: string[];
};

export function RecipeCard({
  recipe,
  book,
}: {
  recipe: RecipeCardData;
  book?: BookCardContext;
}) {
  const guest = book ? pickGuestProteinVariant(recipe, book) : null;
  const proteinCode = guest?.protein_base ?? recipe.protein_base;
  const time = minutesLabel(recipe.time_profile?.total_minutes);
  const effort = effortLabel(recipe.effort_level);
  const href = recipeHref(recipe.slug, {
    variant: guest?.code ?? recipe.applied_axes?.variant,
    equipment: recipe.applied_axes?.equipment,
  });

  return (
    <article className="recipe-card">
      <h3>
        <Link href={href} className="recipe-card__hit">
          {recipe.title}
        </Link>
      </h3>
      {recipe.summary ? <p className="recipe-card__summary">{recipe.summary}</p> : null}
      <dl className="recipe-card__facts">
        <div>
          <dt>Категория</dt>
          <dd>{labelOf(PROTEIN_BASE, proteinCode)}</dd>
        </div>
        {guest?.title ? (
          <div>
            <dt>Вариант</dt>
            <dd>{guest.title}</dd>
          </div>
        ) : null}
        <div>
          <dt>Способ</dt>
          <dd>{labelOf(COOK_METHOD, recipe.cook_method)}</dd>
        </div>
        <div>
          <dt>Тип блюда</dt>
          <dd>{labelOf(DISH_TYPE, recipe.dish_type)}</dd>
        </div>
        {time ? (
          <div>
            <dt>Время</dt>
            <dd>{time}</dd>
          </div>
        ) : null}
        {effort ? (
          <div>
            <dt>Сложность</dt>
            <dd>{effort}</dd>
          </div>
        ) : null}
      </dl>
      {recipe.why && recipe.why.length > 0 && (
        <ul className="why-list">
          {recipe.why.map((line) => (
            <li key={line}>{line}</li>
          ))}
        </ul>
      )}
      <AllergenNotice allergens={recipe.allergens} compact />
    </article>
  );
}

export function RecipeGrid({
  recipes,
  book,
}: {
  recipes: RecipeCardData[];
  book?: BookCardContext;
}) {
  return (
    <div className="recipe-grid">
      {recipes.map((recipe) => (
        <RecipeCard key={recipe.slug} recipe={recipe} book={book} />
      ))}
    </div>
  );
}

export function SolutionBoard({
  featured,
  alternatives,
}: {
  featured: RecipeCardData;
  alternatives: AlternativeSolution[];
}) {
  const href = recipeHref(featured.slug, {
    variant: featured.applied_axes?.variant,
    equipment: featured.applied_axes?.equipment,
  });
  const shopping = featured.shopping_delta ?? [];
  const substitutions = featured.substitutions ?? [];
  const method = labelOf(COOK_METHOD, featured.cook_method);
  const gear =
    featured.equipment && featured.equipment !== featured.cook_method
      ? equipmentLabel(featured.equipment)
      : null;
  const time = solutionTimeLabel(featured.time_profile);
  const variantApplied = Boolean(featured.applied_axes?.variant);
  const nowComplete = shopping.length === 0 && featured.bucket === 'now';

  return (
    <div className="solution-board">
      <section className="solution-featured" aria-labelledby="featured-title">
        <p className="eyebrow">Я бы приготовил</p>
        <h2 id="featured-title">
          <Link href={href}>{featured.title}</Link>
        </h2>
        {variantApplied ? (
          <p className="solution-featured__axis">
            Основа: {labelOf(PROTEIN_BASE, featured.protein_base)}
          </p>
        ) : null}
        <dl className="recipe-card__facts">
          <div>
            <dt>Категория</dt>
            <dd>{labelOf(PROTEIN_BASE, featured.protein_base)}</dd>
          </div>
          <div>
            <dt>Способ</dt>
            <dd>{method}</dd>
          </div>
          {gear ? (
            <div>
              <dt>Посуда</dt>
              <dd>{gear}</dd>
            </div>
          ) : null}
          {time ? (
            <div>
              <dt>Время</dt>
              <dd>{time}</dd>
            </div>
          ) : null}
          {featured.step_count ? (
            <div>
              <dt>Шаги</dt>
              <dd>{featured.step_count}</dd>
            </div>
          ) : null}
        </dl>
        <AllergenNotice allergens={featured.allergens} compact />
        {nowComplete && substitutions.length === 0 ? (
          <p className="solution-featured__status">Можно приготовить сейчас</p>
        ) : null}
        {nowComplete && substitutions.length > 0 ? (
          <p className="solution-featured__status">Можно приготовить с заменой</p>
        ) : null}
        {shopping.length > 0 ? (
          <p className="solution-featured__status">
            Нужно докупить: {shopping.map((item) => item.title).join(', ')}
          </p>
        ) : null}
        {substitutions.length > 0 ? (
          <p className="solution-featured__status">
            Можно заменить:{' '}
            {substitutions.map((item) => `${item.from_title} → ${item.to_title}`).join('; ')}
          </p>
        ) : null}
        {featured.why && featured.why.length > 0 ? (
          <>
            <h3 className="solution-why-title">Почему именно это</h3>
            <ul className="why-list why-list--checks">
              {featured.why.map((line) => (
                <li key={line}>{line}</li>
              ))}
            </ul>
          </>
        ) : null}
        <p className="solution-featured__actions">
          <Link className="btn-primary" href={href}>
            Приготовить
          </Link>
        </p>
      </section>
      {alternatives.length > 0 ? (
        <section className="solution-alts" aria-labelledby="alts-title">
          <h2 id="alts-title">Ещё варианты</h2>
          <ul>
            {alternatives.map((item) => {
              const altHref = recipeHref(item.slug, {
                variant: item.applied_axes?.variant,
                equipment: item.applied_axes?.equipment,
              });
              const altTime = solutionTimeLabel(item.time_profile);
              return (
                <li key={`${item.label}-${item.slug}`}>
                  <span className="tag">{item.label}</span>
                  <Link href={altHref}>{item.title}</Link>
                  {altTime ? (
                    <span className="solution-alts__why">{altTime}</span>
                  ) : item.why?.[0] ? (
                    <span className="solution-alts__why">{item.why[0]}</span>
                  ) : null}
                </li>
              );
            })}
          </ul>
        </section>
      ) : null}
    </div>
  );
}

export function SolutionBuckets({
  now,
  almost,
  best,
}: {
  now: RecipeCardData[];
  almost: RecipeCardData[];
  best: RecipeCardData[];
}) {
  const sections = [
    { id: 'now', title: 'Можно сейчас', items: now },
    { id: 'almost', title: 'Нужно докупить 1–2', items: almost },
    { id: 'best', title: 'Лучше, если купить', items: best },
  ];
  return (
    <div className="solution-buckets">
      {sections.map((section) =>
        section.items.length === 0 ? null : (
          <section key={section.id} className="solution-bucket" aria-labelledby={`bucket-${section.id}`}>
            <h2 id={`bucket-${section.id}`} className="solution-bucket__title">
              {section.title}
            </h2>
            <RecipeGrid recipes={section.items} />
          </section>
        ),
      )}
    </div>
  );
}
```

---

## 19. `frontend/components/RecipesBook.tsx`

- Путь: `v2/frontend/components/RecipesBook.tsx`
- Экспорты: RecipesBook
- Строк: 330

```tsx
'use client';

import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useEffect, useMemo, useState } from 'react';
import type { RecipeCardData, SearchParamsRecord } from '@/lib/types';
import {
  resolveBookChapter,
  setHref,
  toggleHref,
  valuesOf,
} from '@/lib/filters';
import {
  BOOK_CHAPTERS,
  COOK_METHOD,
  PROTEIN_BASE,
  chapterIdsForRecipe,
  equipmentLabel,
  labelOf,
  recipeProteinCodes,
} from '@/lib/vocab';
import {
  QUICK_FILTERS,
  activeFilterChips,
  hasQuickFilters,
  matchesCatalogExtras,
} from '@/lib/catalog';
import { EmptyState } from '@/components/Feedback';
import { FilterChip } from '@/components/FilterChip';
import { RecipeGrid } from '@/components/RecipeCard';

function countBy(recipes: RecipeCardData[], key: keyof RecipeCardData): Map<string, number> {
  const map = new Map<string, number>();
  for (const recipe of recipes) {
    const value = recipe[key];
    if (typeof value !== 'string' || !value) continue;
    map.set(value, (map.get(value) || 0) + 1);
  }
  return map;
}

function countChapters(recipes: RecipeCardData[]): Map<string, number> {
  const map = new Map<string, number>();
  for (const recipe of recipes) {
    for (const id of chapterIdsForRecipe(recipe)) {
      map.set(id, (map.get(id) || 0) + 1);
    }
  }
  return map;
}

function inChapterPool(recipes: RecipeCardData[], chapterId: string): RecipeCardData[] {
  return recipes.filter((recipe) =>
    (chapterIdsForRecipe(recipe) as string[]).includes(chapterId),
  );
}

function countProteinBases(
  recipes: RecipeCardData[],
  allowed?: readonly string[],
): Map<string, number> {
  const map = new Map<string, number>();
  for (const recipe of recipes) {
    for (const code of recipeProteinCodes(recipe)) {
      if (allowed?.length && !allowed.includes(code)) continue;
      map.set(code, (map.get(code) || 0) + 1);
    }
  }
  return map;
}

function matchesProteinFilter(recipe: RecipeCardData, proteinFilter: string[]): boolean {
  return recipeProteinCodes(recipe).some((code) => proteinFilter.includes(code));
}

function sortByVocab(codes: string[], order: readonly string[]): string[] {
  const rank = new Map(order.map((code, index) => [code, index]));
  return [...codes].sort((a, b) => (rank.get(a) ?? 99) - (rank.get(b) ?? 99));
}

function ruCount(n: number): string {
  const mod10 = n % 10;
  const mod100 = n % 100;
  if (mod10 === 1 && mod100 !== 11) return `${n} рецепт`;
  if (mod10 >= 2 && mod10 <= 4 && (mod100 < 12 || mod100 > 14)) return `${n} рецепта`;
  return `${n} рецептов`;
}

export function RecipesBook({
  recipes,
  sp,
}: {
  recipes: RecipeCardData[];
  sp: SearchParamsRecord;
}) {
  const router = useRouter();
  const urlQ = valuesOf(sp, 'q')[0] ?? '';
  const [q, setQ] = useState(urlQ);
  const [qLive, setQLive] = useState(urlQ);

  useEffect(() => {
    const timer = window.setTimeout(() => {
      setQLive(q);
      const qs = new URLSearchParams(window.location.search);
      const trimmed = q.trim();
      if (trimmed) qs.set('q', trimmed);
      else qs.delete('q');
      qs.delete('page');
      const next = qs.toString() ? `/recipes?${qs.toString()}` : '/recipes';
      const now = `${window.location.pathname}${window.location.search}`;
      if (next !== now) router.replace(next, { scroll: false });
    }, 250);
    return () => window.clearTimeout(timer);
  }, [q, router]);

  const liveSp: SearchParamsRecord = { ...sp, q: qLive || undefined };
  const { chapter, selectedBases } = resolveBookChapter(liveSp);
  const method = valuesOf(liveSp, 'cook_method')[0];
  const equipment = valuesOf(liveSp, 'equipment')[0];
  const proteinFilter = selectedBases.length === 1 ? selectedBases : [];
  const extrasOn = hasQuickFilters(liveSp);
  const filteredExtras = useMemo(
    () => recipes.filter((recipe) => matchesCatalogExtras(recipe, liveSp)),
    [recipes, liveSp],
  );
  const chapterCounts = countChapters(filteredExtras);
  const pool = chapter ? inChapterPool(filteredExtras, chapter.id) : filteredExtras;
  const proteinCounts = countProteinBases(
    pool,
    chapter && chapter.bases.length ? chapter.bases : undefined,
  );
  const proteinOrder =
    chapter && chapter.bases.length ? chapter.bases : Object.keys(PROTEIN_BASE);
  const inChapter = Boolean(chapter);
  const afterProtein =
    inChapter && proteinFilter.length
      ? pool.filter((item) => matchesProteinFilter(item, proteinFilter))
      : pool;
  const book = chapter ? { chapterId: chapter.id, proteinFilter } : undefined;
  const methodCounts = inChapter ? countBy(afterProtein, 'cook_method') : new Map<string, number>();
  const afterMethod =
    inChapter && method ? afterProtein.filter((item) => item.cook_method === method) : afterProtein;
  const equipmentPool = inChapter ? (method ? afterMethod : afterProtein) : [];
  const equipmentCounts = inChapter ? countBy(equipmentPool, 'equipment') : new Map<string, number>();
  const showProtein =
    inChapter && chapter ? sortByVocab([...proteinCounts.keys()], proteinOrder).length > 1 : false;
  const showMethod = methodCounts.size > 1;
  const showEquipment = [...equipmentCounts.keys()].filter(Boolean).length > 1;
  const cards = inChapter
    ? afterProtein.filter((item) => {
        if (method && item.cook_method !== method) return false;
        if (equipment && item.equipment !== equipment) return false;
        return true;
      })
    : extrasOn
      ? filteredExtras
      : [];
  const showToc = !chapter && !extrasOn;
  const chapterSp =
    chapter && !valuesOf(liveSp, 'chapter').length ? { ...liveSp, chapter: chapter.id } : liveSp;
  const chips = activeFilterChips(liveSp);
  const resultCount = showToc ? 0 : cards.length;

  return (
    <>
      <form
        className="search-row"
        action="/recipes"
        method="get"
        onSubmit={(event) => {
          event.preventDefault();
          setQLive(q.trim());
        }}
      >
        <input
          type="search"
          name="q"
          value={q}
          placeholder="Найти рецепт"
          aria-label="Поиск рецептов"
          onChange={(event) => setQ(event.target.value)}
        />
        <button type="submit" className="btn-primary">
          Найти
        </button>
      </form>

      <fieldset className="filter-block">
        <legend className="filter-legend">Быстрые фильтры</legend>
        <div className="chip-row">
          {QUICK_FILTERS.map((item) => (
            <FilterChip
              key={item.id}
              href={toggleHref('/recipes', liveSp, item.param, item.value)}
              pressed={valuesOf(liveSp, item.param).includes(item.value)}
            >
              {item.label}
            </FilterChip>
          ))}
        </div>
      </fieldset>

      {chips.length > 0 ? (
        <div className="catalog-active">
          <p className="catalog-active__count">{ruCount(resultCount)}</p>
          <ul className="catalog-active__chips">
            {chips.map((chip) => (
              <li key={`${chip.key}-${chip.value}`}>
                <FilterChip
                  href={toggleHref('/recipes', liveSp, chip.key, chip.value)}
                  pressed
                  ariaLabel={`Снять фильтр: ${chip.label}`}
                >
                  {chip.label}
                  <span aria-hidden> ×</span>
                </FilterChip>
              </li>
            ))}
          </ul>
          <Link
            className="catalog-active__reset"
            href={chapter ? `/recipes?chapter=${chapter.id}` : '/recipes'}
          >
            Сбросить
          </Link>
        </div>
      ) : !showToc ? (
        <p className="catalog-active__count">{ruCount(resultCount)}</p>
      ) : null}

      {showToc && (
        <section aria-label="Оглавление">
          <h2 className="filter-legend">Разделы</h2>
          {chapterCounts.size === 0 && <EmptyState>Ничего не найдено</EmptyState>}
          <div className="book-toc">
            {BOOK_CHAPTERS.filter((item) => (chapterCounts.get(item.id) || 0) > 0).map((item) => (
              <Link
                key={item.id}
                className="book-chapter"
                href={setHref('/recipes', liveSp, 'chapter', item.id)}
              >
                <span>{item.label}</span>
                <span className="book-chapter__n">{chapterCounts.get(item.id)}</span>
              </Link>
            ))}
          </div>
        </section>
      )}

      {inChapter && (
        <>
          <p className="catalog-crumb">
            <Link href="/recipes">← Оглавление</Link>
            {' · '}
            {chapter?.label}
            {proteinFilter.length === 1 ? ` · ${labelOf(PROTEIN_BASE, proteinFilter[0])}` : ''}
          </p>
          {showProtein && (
            <fieldset className="filter-block">
              <legend className="filter-legend">Основа</legend>
              <div className="chip-row">
                {sortByVocab([...proteinCounts.keys()], proteinOrder).map((code) => {
                  const n = proteinCounts.get(code) || 0;
                  const active = proteinFilter.length === 1 && proteinFilter[0] === code;
                  return (
                    <FilterChip
                      key={code}
                      href={setHref('/recipes', chapterSp, 'protein_base', active ? null : code)}
                      pressed={active}
                    >
                      {labelOf(PROTEIN_BASE, code)} · {n}
                    </FilterChip>
                  );
                })}
              </div>
            </fieldset>
          )}
          {showMethod && (
            <fieldset className="filter-block">
              <legend className="filter-legend">Способ</legend>
              <div className="chip-row">
                {[...methodCounts.entries()]
                  .sort((a, b) =>
                    labelOf(COOK_METHOD, a[0]).localeCompare(labelOf(COOK_METHOD, b[0]), 'ru'),
                  )
                  .map(([code, n]) => (
                    <FilterChip
                      key={code}
                      href={setHref('/recipes', chapterSp, 'cook_method', method === code ? null : code)}
                      pressed={method === code}
                    >
                      {labelOf(COOK_METHOD, code)} · {n}
                    </FilterChip>
                  ))}
              </div>
            </fieldset>
          )}
          {showEquipment && (
            <fieldset className="filter-block">
              <legend className="filter-legend">Посуда</legend>
              <div className="chip-row">
                {[...equipmentCounts.entries()]
                  .filter(([code]) => Boolean(code))
                  .sort((a, b) => equipmentLabel(a[0]).localeCompare(equipmentLabel(b[0]), 'ru'))
                  .map(([code, n]) => (
                    <FilterChip
                      key={code}
                      href={setHref('/recipes', chapterSp, 'equipment', equipment === code ? null : code)}
                      pressed={equipment === code}
                    >
                      {equipmentLabel(code)} · {n}
                    </FilterChip>
                  ))}
              </div>
            </fieldset>
          )}
        </>
      )}

      {!showToc && cards.length === 0 && (
        <EmptyState>
          Ничего не найдено. Проверьте написание, снимите фильтр или откройте другой раздел.{' '}
          <Link href="/recipes">К оглавлению</Link>
        </EmptyState>
      )}

      {cards.length > 0 && <RecipeGrid recipes={cards} book={book} />}
    </>
  );
}
```

---

## 20. `frontend/components/RecipeSteps.tsx`

- Путь: `v2/frontend/components/RecipeSteps.tsx`
- Экспорты: RecipeSteps
- Строк: 67

```tsx
import type { RecipeStep, SearchParamsRecord } from '@/lib/types';
import { applyStepChoice, exclusiveStepGroup, rewriteSafetyCopy } from '@/lib/steps';
import { toURLSearchParams, valuesOf } from '@/lib/filters';
import { FilterChip } from '@/components/FilterChip';

function pieceHref(slug: string, sp: SearchParamsRecord, piece: string): string {
  const qs = toURLSearchParams(sp);
  qs.set('piece', piece);
  const suffix = qs.toString() ? `?${qs.toString()}` : '';
  return `/recipes/${slug}${suffix}`;
}

export function RecipeSteps({
  slug,
  steps,
  sp,
}: {
  slug: string;
  steps: RecipeStep[];
  sp: SearchParamsRecord;
}) {
  const group = exclusiveStepGroup(steps);
  const requested = valuesOf(sp, 'piece')[0] || null;
  const selected = group
    ? (group.choices.find((item) => item.id === requested)?.id ?? group.choices[0].id)
    : null;
  const visible = applyStepChoice(steps, selected);

  return (
    <section className="recipe-section">
      <h2>Шаги</h2>
      {group ? (
        <fieldset className="filter-block recipe-piece">
          <legend className="filter-legend">Какое мясо кладёте</legend>
          <p className="recipe-piece__hint">Один отруб на кастрюлю. Показывается только нужный шаг.</p>
          <div className="chip-row">
            {group.choices.map((choice) => (
              <FilterChip
                key={choice.id}
                href={pieceHref(slug, sp, choice.id)}
                pressed={selected === choice.id}
              >
                {choice.label}
              </FilterChip>
            ))}
          </div>
        </fieldset>
      ) : null}
      <ol className="recipe-steps">
        {visible.map((step, index) => (
          <li key={`${index}-${step.text.slice(0, 24)}`} className="recipe-step">
            <p>{rewriteSafetyCopy(step.text)}</p>
            {step.target_internal_temperature_c != null && (
              <span className="temp-chip">цель {step.target_internal_temperature_c} °C</span>
            )}
            {step.pull_internal_temperature_c != null && (
              <span className="temp-chip">снятие {step.pull_internal_temperature_c} °C</span>
            )}
            {step.hold_seconds != null && (
              <span className="temp-chip">выдержка {step.hold_seconds} с</span>
            )}
          </li>
        ))}
      </ol>
    </section>
  );
}
```

---

## 21. `frontend/components/SpriteIcon.tsx`

- Путь: `v2/frontend/components/SpriteIcon.tsx`
- Экспорты: SpriteIcon
- Строк: 19

```tsx
type Props = {
  name: string;
  className?: string;
  size?: number;
};

export function SpriteIcon({ name, className = 'ui-icon', size = 22 }: Props) {
  return (
    <svg
      className={className}
      width={size}
      height={size}
      aria-hidden
      focusable="false"
    >
      <use href={`/icons.svg?v=11#icon-${name}`} />
    </svg>
  );
}
```

---

## 22. `frontend/components/TipsView.tsx`

- Путь: `v2/frontend/components/TipsView.tsx`
- Экспорты: TipsView
- Строк: 525

```tsx
'use client';

import { useEffect, useId, useLayoutEffect, useMemo, useRef, useState, type ReactNode } from 'react';
import { EmptyState } from '@/components/Feedback';
import { HashDetailsOpener } from '@/components/HashDetailsOpener';
import {
  filterTips,
  flattenTips,
  groupedTips,
  isKnownKind,
  sectionCounts,
  tagsInSet,
  tipDomId,
  tipKindLabel,
  tipsListHref,
  type NormalizedTip,
  type TipsQuery,
} from '@/lib/tips';
import type { TipsPayload } from '@/lib/types';
import { TIP_KIND, TIP_TAG } from '@/lib/vocab';

function toggleCode(current: string, next: string): string {
  return current === next ? '' : next;
}

function syncTipsUrl(query: TipsQuery) {
  const next = `${tipsListHref(query)}${window.location.hash}`;
  const now = `${window.location.pathname}${window.location.search}${window.location.hash}`;
  if (now !== next) {
    window.history.replaceState(null, '', next);
  }
}

function collapsedTipHeight(card: HTMLDetailsElement): number {
  const summary = card.querySelector('summary');
  if (!(summary instanceof HTMLElement)) return 0;
  const border = getComputedStyle(card);
  return (
    summary.getBoundingClientRect().height +
    (Number.parseFloat(border.borderTopWidth) || 0) +
    (Number.parseFloat(border.borderBottomWidth) || 0)
  );
}

function syncTipSlotHeight(slot: HTMLElement, card: HTMLDetailsElement) {
  const height = collapsedTipHeight(card);
  if (height > 0) slot.style.setProperty('--tip-slot-h', `${height}px`);
}

function tipMotionMs(el: Element): number {
  const raw = getComputedStyle(el).getPropertyValue('--duration').trim();
  const n = Number.parseFloat(raw);
  if (!Number.isFinite(n) || n <= 0) return 350;
  return raw.endsWith('ms') ? n : n * 1000;
}

function cssVarPx(el: HTMLElement, name: string, fallback: number): number {
  const raw = getComputedStyle(el).getPropertyValue(name).trim();
  const n = Number.parseFloat(raw);
  if (!Number.isFinite(n)) return fallback;
  if (raw.endsWith('rem')) {
    const root = Number.parseFloat(getComputedStyle(el.ownerDocument.documentElement).fontSize) || 16;
    return n * root;
  }
  return n;
}

function layoutTipsMasonry(container: HTMLElement) {
  const items = Array.from(container.children).filter((node): node is HTMLElement => node instanceof HTMLElement);
  const gap = cssVarPx(container, '--tips-gap', 10);
  const minCol = cssVarPx(container, '--tips-col-min', 264);
  const width = container.clientWidth;
  if (!items.length || width <= 0) {
    container.style.height = '';
    return;
  }

  const cols = Math.max(1, Math.floor((width + gap) / (minCol + gap)));
  const colWidth = (width - gap * (cols - 1)) / cols;
  const heights = Array.from({ length: cols }, () => 0);

  for (const item of items) {
    item.style.position = 'absolute';
    item.style.width = `${colWidth}px`;
    const card = item.querySelector(':scope > details.tip-card');
    if (card instanceof HTMLDetailsElement) syncTipSlotHeight(item, card);
  }

  for (const item of items) {
    const col = heights.indexOf(Math.min(...heights));
    const height = item.getBoundingClientRect().height;
    item.style.left = `${col * (colWidth + gap)}px`;
    item.style.top = `${heights[col]}px`;
    heights[col] += height + gap;
  }

  const tallest = Math.max(0, ...heights);
  const nextHeight = `${Math.max(0, tallest - gap)}px`;
  const signature = `${width}|${cols}|${nextHeight}|${items.map((item) => item.style.top + item.style.left).join('|')}`;
  if (container.dataset.masonrySig === signature) return;
  container.dataset.masonrySig = signature;
  container.style.height = nextHeight;
}

function TipsMasonry({ children, layoutKey }: { children: ReactNode; layoutKey: string }) {
  const ref = useRef<HTMLDivElement>(null);

  useLayoutEffect(() => {
    const container = ref.current;
    if (!container) return undefined;

    const run = () => layoutTipsMasonry(container);
    run();
    container.classList.add('is-ready');

    const observer = new ResizeObserver(run);
    observer.observe(container);
    const seen = new Set<Element>();
    const watchKids = () => {
      for (const child of container.children) {
        if (child instanceof HTMLElement && !seen.has(child)) {
          seen.add(child);
          observer.observe(child);
        }
      }
    };
    watchKids();
    const mutations = new MutationObserver(() => {
      watchKids();
      run();
    });
    mutations.observe(container, { childList: true });

    return () => {
      observer.disconnect();
      mutations.disconnect();
    };
  }, [layoutKey]);

  return (
    <div className="tips-masonry" ref={ref}>
      {children}
    </div>
  );
}

function TipBadges({ tip }: { tip: NormalizedTip }) {
  const kindLabel = tipKindLabel(tip.kind);
  const tags = tip.tags
    .map((code) => ({ code, label: TIP_TAG[code] }))
    .filter((item) => item.label && item.label !== kindLabel);
  if (!kindLabel && tags.length === 0) return null;
  return (
    <p className="tip-card__badges">
      {kindLabel ? <span className="tip-badge tip-badge--kind">{kindLabel}</span> : null}
      {tags.map((item) => (
        <span key={item.code} className="tip-badge">
          {item.label}
        </span>
      ))}
    </p>
  );
}

function TipCard({
  tip,
  onOpen,
}: {
  tip: NormalizedTip;
  onOpen?: (el: HTMLDetailsElement) => void;
}) {
  if (!tip.explanation) {
    return (
      <article id={tipDomId(tip.id)} className="tip-slot tip-slot--static">
        <div className="tip-card tip-card--static">
          <div className="tip-card__face">
            <TipBadges tip={tip} />
            <p className="tip-card__hint">{tip.hint}</p>
          </div>
        </div>
      </article>
    );
  }

  return <ExpandableTipCard tip={tip} onOpen={onOpen} />;
}

function ExpandableTipCard({
  tip,
  onOpen,
}: {
  tip: NormalizedTip;
  onOpen?: (el: HTMLDetailsElement) => void;
}) {
  const slotRef = useRef<HTMLDivElement>(null);
  const cardRef = useRef<HTMLDetailsElement>(null);
  const raiseTimer = useRef(0);

  useEffect(() => () => window.clearTimeout(raiseTimer.current), []);

  useLayoutEffect(() => {
    const slot = slotRef.current;
    const card = cardRef.current;
    if (!slot || !card) return undefined;

    const sync = () => syncTipSlotHeight(slot, card);
    sync();

    const summary = card.querySelector('summary');
    const observer = new ResizeObserver(sync);
    observer.observe(slot);
    if (summary) observer.observe(summary);

    return () => observer.disconnect();
  }, [tip.hint, tip.kind, tip.tags.join(',')]);

  return (
    <div className="tip-slot" ref={slotRef}>
      <details
        ref={cardRef}
        id={tipDomId(tip.id)}
        className="tip-card"
        onToggle={(event) => {
          const card = event.currentTarget;
          const slot = slotRef.current;
          if (slot) syncTipSlotHeight(slot, card);
          window.clearTimeout(raiseTimer.current);
          if (card.open) {
            card.classList.add('tip-card--raised');
            onOpen?.(card);
            return;
          }
          const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
          raiseTimer.current = window.setTimeout(
            () => {
              if (!card.open) card.classList.remove('tip-card--raised');
            },
            reduce ? 0 : tipMotionMs(card) + 20,
          );
        }}
      >
        <summary>
          <div className="tip-card__face">
            <TipBadges tip={tip} />
            <p className="tip-card__hint">{tip.hint}</p>
          </div>
        </summary>
        <div className="tip-card__reveal">
          <div className="tip-card__clip">
            <div className="tip-card__panel">
              <p className="tip-card__body">{tip.explanation}</p>
            </div>
          </div>
        </div>
      </details>
    </div>
  );
}

function ChipButton({
  label,
  pressed,
  count,
  showCount,
  onClick,
}: {
  label: string;
  pressed: boolean;
  count?: number;
  showCount?: boolean;
  onClick: () => void;
}) {
  return (
    <button
      type="button"
      className={pressed ? 'chip is-active' : 'chip'}
      aria-pressed={pressed}
      onClick={onClick}
    >
      {label}
      {showCount ? <span className="chip__n">{count ?? 0}</span> : null}
    </button>
  );
}

export function TipsView({
  payload,
  omitLead = false,
  initialQ = '',
  initialKind = '',
  initialSection = '',
  initialTag = '',
}: {
  payload: TipsPayload;
  omitLead?: boolean;
  initialQ?: string;
  initialKind?: string;
  initialSection?: string;
  initialTag?: string;
}) {
  const searchId = useId();
  const [q, setQ] = useState(initialQ);
  const [qLive, setQLive] = useState(initialQ);
  const [kind, setKind] = useState(isKnownKind(initialKind) ? initialKind : '');
  const [section, setSection] = useState(initialSection);
  const [tag, setTag] = useState(initialTag);
  const sections = payload.sections ?? [];
  const all = useMemo(() => flattenTips(payload), [payload]);
  const query: TipsQuery = { q: qLive, kind, section, tag };
  const filtered = useMemo(() => filterTips(all, query), [all, qLive, kind, section, tag]);
  const groups = useMemo(() => groupedTips(sections, filtered), [sections, filtered]);
  const beforeTag = useMemo(
    () => filterTips(all, { q: qLive, kind, section, tag: '' }),
    [all, qLive, kind, section],
  );
  const tagCodes = useMemo(() => tagsInSet(beforeTag), [beforeTag]);
  const filtering = Boolean(qLive.trim() || kind || tag);
  const activeFilters = Boolean(qLive.trim() || kind || section || tag);
  const counts = useMemo(
    () => sectionCounts(all, query, sections.map((item) => item.id)),
    [all, qLive, kind, tag, section, sections],
  );
  const watch = filtered.map((item) => item.id).join(',');
  const resultsRef = useRef<HTMLDivElement>(null);
  const gridBooted = useRef(false);

  const closeOtherTips = (opened: HTMLDetailsElement) => {
    opened
      .closest('.tips-handbook')
      ?.querySelectorAll('details.tip-card')
      .forEach((node) => {
        if (node instanceof HTMLDetailsElement && node !== opened) node.open = false;
      });
  };

  useLayoutEffect(() => {
    const root = resultsRef.current;
    if (!root) return;
    const layoutAll = () => {
      root.querySelectorAll('.tips-masonry').forEach((node) => {
        if (!(node instanceof HTMLElement)) return;
        layoutTipsMasonry(node);
        node.classList.add('is-ready');
      });
    };
    layoutAll();
    root.classList.add('is-ready');
    root.setAttribute('aria-busy', 'false');
    layoutAll();
    if (gridBooted.current) return;
    gridBooted.current = true;
    const id = decodeURIComponent(window.location.hash.replace(/^#/, ''));
    if (!id) return;
    document.getElementById(id)?.scrollIntoView({ block: 'start' });
  }, [watch]);

  useEffect(() => {
    syncTipsUrl({ q: qLive, kind, section, tag });
  }, [qLive, kind, section, tag]);

  useEffect(() => {
    if (q === qLive) return undefined;
    const timer = window.setTimeout(() => {
      setQLive(q);
    }, 140);
    return () => window.clearTimeout(timer);
  }, [q, qLive]);

  if (all.length === 0) {
    return (
      <>
        {!omitLead && payload.intro ? <p className="lede">{payload.intro}</p> : null}
        <EmptyState>Пока нет советов.</EmptyState>
      </>
    );
  }

  return (
    <div className="tips-handbook">
      <HashDetailsOpener watch={watch} exclusive=".tips-handbook details.tip-card" />
      {!omitLead && payload.intro ? <p className="lede">{payload.intro}</p> : null}

      <form
        className="tips-search"
        action="/tips"
        method="get"
        onSubmit={(event) => {
          event.preventDefault();
          syncTipsUrl(query);
        }}
      >
        <label className="tips-search__label" htmlFor={searchId}>
          Что хотите узнать?
        </label>
        <div className="search-row">
          <input
            id={searchId}
            type="search"
            name="q"
            value={q}
            placeholder="Например: бисквит, мука, заморозка, духовка"
            autoComplete="off"
            onChange={(event) => setQ(event.target.value)}
          />
        </div>
        {kind ? <input type="hidden" name="kind" value={kind} /> : null}
        {section ? <input type="hidden" name="section" value={section} /> : null}
        {tag ? <input type="hidden" name="tag" value={tag} /> : null}
      </form>

      <fieldset className="filter-block">
        <legend className="filter-legend">Разделы</legend>
        <div className="chip-row tips-chips">
          {sections.map((item) => (
            <ChipButton
              key={item.id}
              label={item.title}
              pressed={section === item.id}
              count={counts.get(item.id) || 0}
              showCount={filtering}
              onClick={() => setSection((prev) => toggleCode(prev, item.id))}
            />
          ))}
        </div>
      </fieldset>

      <fieldset className="filter-block">
        <legend className="filter-legend">Тип</legend>
        <p className="filter-help">Выберите один тип совета. Повторное нажатие снимает фильтр.</p>
        <div className="chip-row tips-chips" role="group" aria-label="Тип совета">
          {Object.entries(TIP_KIND).map(([code, label]) => (
            <ChipButton
              key={code}
              label={label}
              pressed={kind === code}
              onClick={() => setKind((prev) => toggleCode(prev, code))}
            />
          ))}
        </div>
      </fieldset>

      {tagCodes.length > 0 ? (
        <fieldset className="filter-block">
          <legend className="filter-legend">Тема</legend>
          <p className="filter-help">Тема сужает список внутри выбранного раздела.</p>
          <div className="chip-row tips-chips" role="group" aria-label="Тема совета">
            {tagCodes.map((code) => (
              <ChipButton
                key={code}
                label={TIP_TAG[code]}
                pressed={tag === code}
                onClick={() => setTag((prev) => toggleCode(prev, code))}
              />
            ))}
          </div>
        </fieldset>
      ) : null}

      <div className="catalog-active">
        <p className="catalog-active__count">
          {filtered.length}{' '}
          {filtered.length === 1 ? 'совет' : filtered.length < 5 ? 'совета' : 'советов'}
        </p>
        {activeFilters ? (
          <button
            type="button"
            className="catalog-active__reset"
            onClick={() => {
              setQ('');
              setQLive('');
              setKind('');
              setSection('');
              setTag('');
            }}
          >
            Сбросить
          </button>
        ) : null}
      </div>

      {filtered.length === 0 ? (
        <EmptyState>Ничего не найдено</EmptyState>
      ) : (
        <div className="tips-results" ref={resultsRef} aria-busy="true">
          <div className="tips-loader" role="status">
            <span className="tips-loader__spin" aria-hidden="true" />
            Загружаем советы
          </div>
          {groups.map((group) => {
            const panelId = `tips-panel-${group.id}`;
            return (
            <details
              key={group.id}
              id={`tip-${group.id}`}
              className="tips-section"
              open={filtering || undefined}
            >
              <summary
                aria-controls={panelId}
                id={`tips-h-${group.id}`}
              >
                {group.title}
                {filtering ? <span className="tips-section__n">{group.items.length}</span> : null}
              </summary>
              <div id={panelId}>
              <TipsMasonry layoutKey={group.items.map((item) => item.id).join(',')}>
                {group.items.map((item) => (
                  <TipCard key={item.id} tip={item} onOpen={closeOtherTips} />
                ))}
              </TipsMasonry>
              </div>
            </details>
            );
          })}
        </div>
      )}
      <p className="tips-legal">
        Советы по безопасности еды носят общий характер и не заменяют официальные правила.{' '}
        <a href="https://www.rospotrebnadzor.ru/" rel="noopener noreferrer">
          Роспотребнадзор
        </a>
      </p>
    </div>
  );
}
```

---
