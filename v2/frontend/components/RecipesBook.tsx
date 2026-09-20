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
