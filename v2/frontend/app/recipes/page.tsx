import Link from 'next/link';
import { fetchCatalog, fetchRecommendations } from '@/lib/api';
import { resolveBookChapter, setHref, valuesOf, withPage } from '@/lib/filters';
import type { RecipeCardData, SearchParamsRecord } from '@/lib/types';
import {
  BOOK_CHAPTERS,
  COOK_METHOD,
  PROTEIN_BASE,
  chapterIdForRecipe,
  equipmentLabel,
  labelOf,
} from '@/lib/vocab';
import { EmptyState, ErrorBanner } from '@/components/Feedback';
import { PageIntro } from '@/components/PageArt';
import { RecipeGrid } from '@/components/RecipeCard';

export const dynamic = 'force-dynamic';

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
    const id = chapterIdForRecipe(recipe.protein_base, recipe.dish_type);
    map.set(id, (map.get(id) || 0) + 1);
  }
  return map;
}

function inChapterPool(recipes: RecipeCardData[], chapterId: string): RecipeCardData[] {
  return recipes.filter(
    (recipe) => chapterIdForRecipe(recipe.protein_base, recipe.dish_type) === chapterId,
  );
}

function sortByVocab(codes: string[], order: readonly string[]): string[] {
  const rank = new Map(order.map((code, index) => [code, index]));
  return [...codes].sort((a, b) => (rank.get(a) ?? 99) - (rank.get(b) ?? 99));
}

function catalogWithChapter(
  sp: SearchParamsRecord,
  chapter: NonNullable<ReturnType<typeof resolveBookChapter>['chapter']>,
): SearchParamsRecord {
  const next: SearchParamsRecord = { ...sp };
  if (chapter.dishTypes.length && !valuesOf(sp, 'dish_type').length) {
    next.dish_type = [...chapter.dishTypes];
  }
  if (chapter.bases.length && !valuesOf(sp, 'protein_base').length) {
    next.protein_base = [...chapter.bases];
  }
  return next;
}

export default async function RecipesPage({
  searchParams,
}: {
  searchParams: Promise<SearchParamsRecord>;
}) {
  const sp = await searchParams;
  const q = valuesOf(sp, 'q')[0] ?? '';
  const { chapter, selectedBases } = resolveBookChapter(sp);
  const method = valuesOf(sp, 'cook_method')[0];
  const equipment = valuesOf(sp, 'equipment')[0];
  const searching = Boolean(q);
  const proteinFilter = selectedBases.length === 1 ? selectedBases : [];

  const rec = await fetchRecommendations(
    searching
      ? {}
      : {
          ...(valuesOf(sp, 'without').length ? { without: sp.without } : {}),
        },
  );
  const all = rec.ok ? rec.data.results : [];
  const chapterCounts = countChapters(all);
  const pool = chapter ? inChapterPool(all, chapter.id) : all;
  const proteinCounts = countBy(pool, 'protein_base');
  const proteinOrder =
    chapter && chapter.bases.length ? chapter.bases : Object.keys(PROTEIN_BASE);

  const catalogSp = searching && chapter ? catalogWithChapter(sp, chapter) : sp;
  const catalog = searching ? await fetchCatalog(catalogSp) : null;
  const rawSearch = searching ? (catalog?.ok ? catalog.data.results : []) : [];
  const searchResults =
    searching && chapter ? inChapterPool(rawSearch, chapter.id) : rawSearch;
  const count = searching
    ? chapter
      ? searchResults.length
      : catalog?.ok
        ? catalog.data.count
        : 0
    : 0;
  const page = Number(valuesOf(sp, 'page')[0] || '1') || 1;

  const chapterSp =
    chapter && !valuesOf(sp, 'chapter').length ? { ...sp, chapter: chapter.id } : sp;
  const inChapter = Boolean(chapter) && !searching;
  const afterProtein =
    inChapter && proteinFilter.length
      ? pool.filter((item) => proteinFilter.includes(item.protein_base))
      : pool;
  const methodCounts = inChapter ? countBy(afterProtein, 'cook_method') : new Map<string, number>();
  const afterMethod = inChapter && method ? afterProtein.filter((item) => item.cook_method === method) : afterProtein;
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
    : [];

  const crumbs = [
    chapter ? chapter.label : null,
    proteinFilter.length === 1 ? labelOf(PROTEIN_BASE, proteinFilter[0]) : null,
    method ? labelOf(COOK_METHOD, method) : null,
    equipment ? equipmentLabel(equipment) : null,
  ].filter(Boolean);

  return (
    <>
      <PageIntro
        scene="recipes"
        eyebrow="Книга"
        title="Рецепты"
        lede={
          <p className="lede">
            Сначала мясо, птица, овощи, рыба, гарниры, завтраки или десерты. В главе сразу все
            рецепты; способ и посуда только сужают список. <Link href="/calculator">Калькулятор</Link>
          </p>
        }
      />
      <form className="search-row" action="/recipes" method="get">
        {(['chapter', 'protein_base', 'cook_method', 'equipment', 'without'] as const).flatMap((key) =>
          valuesOf(chapterSp, key).map((value) => (
            <input key={`${key}-${value}`} type="hidden" name={key} value={value} />
          )),
        )}
        <input
          type="search"
          name="q"
          defaultValue={q}
          placeholder="Найти рецепт"
          aria-label="Поиск рецептов"
        />
        <button type="submit" className="btn-primary">
          Найти
        </button>
      </form>

      {searching && (
        <p style={{ marginBottom: 16 }}>
          {crumbs.length > 0 ? crumbs.join(' · ') : 'По всей книге'}
          {' · '}
          <Link href="/recipes">К оглавлению</Link>
        </p>
      )}

      {!searching && !chapter && (
        <section aria-label="Оглавление">
          <h2 className="filter-legend">Разделы</h2>
          {chapterCounts.size === 0 && rec.ok && (
            <EmptyState>Ничего не найдено</EmptyState>
          )}
          <div className="book-toc">
            {BOOK_CHAPTERS.filter((item) => (chapterCounts.get(item.id) || 0) > 0).map((item) => (
              <Link
                key={item.id}
                className="book-chapter"
                href={setHref('/recipes', sp, 'chapter', item.id)}
              >
                <span>{item.label}</span>
                <span className="book-chapter__n">{chapterCounts.get(item.id)}</span>
              </Link>
            ))}
          </div>
        </section>
      )}

      {!searching && chapter && (
        <>
          <p style={{ marginBottom: 16 }}>
            <Link href="/recipes">← Оглавление</Link>
            {' · '}
            {chapter.label}
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
              <Link
                key={code}
                href={setHref('/recipes', chapterSp, 'protein_base', active ? null : code)}
                className={active ? 'chip is-active' : 'chip'}
                aria-current={active ? 'true' : undefined}
              >
                {labelOf(PROTEIN_BASE, code)} · {n}
              </Link>
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
              .sort((a, b) => labelOf(COOK_METHOD, a[0]).localeCompare(labelOf(COOK_METHOD, b[0]), 'ru'))
              .map(([code, n]) => (
              <Link
                key={code}
                href={setHref('/recipes', chapterSp, 'cook_method', method === code ? null : code)}
                className={method === code ? 'chip is-active' : 'chip'}
                aria-current={method === code ? 'true' : undefined}
              >
                {labelOf(COOK_METHOD, code)} · {n}
              </Link>
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
                  <Link
                    key={code}
                    href={setHref('/recipes', chapterSp, 'equipment', equipment === code ? null : code)}
                    className={equipment === code ? 'chip is-active' : 'chip'}
                    aria-current={equipment === code ? 'true' : undefined}
                  >
                    {equipmentLabel(code)} · {n}
                  </Link>
                ))}
              </div>
            </fieldset>
          )}
        </>
      )}

      {!rec.ok && !searching && <ErrorBanner message={rec.detail} />}
      {searching && catalog && !catalog.ok && <ErrorBanner message={catalog.detail} />}

      {searching && searchResults.length === 0 && catalog?.ok && (
        <EmptyState>Ничего не найдено</EmptyState>
      )}
      {inChapter && rec.ok && cards.length === 0 && (
        <EmptyState>
          В этой главе ничего — снимите ограничение или выберите другую основу.{' '}
          <Link href="/recipes">К оглавлению</Link>
        </EmptyState>
      )}

      {searching && searchResults.length > 0 && (
        <>
          <p className="note" style={{ marginBottom: 12 }}>
            {count} {count === 1 ? 'рецепт' : count < 5 ? 'рецепта' : 'рецептов'}
          </p>
          <RecipeGrid recipes={searchResults} />
          <div className="pager">
            {catalog?.ok && catalog.data.previous && (
              <Link href={withPage('/recipes', sp, page - 1)} rel="prev">
                ← Назад
              </Link>
            )}
            {catalog?.ok && catalog.data.next && (
              <Link href={withPage('/recipes', sp, page + 1)} rel="next">
                Дальше →
              </Link>
            )}
          </div>
        </>
      )}

      {!searching && cards.length > 0 && (
        <>
          <p className="note" style={{ marginBottom: 12 }}>
            {cards.length}{' '}
            {cards.length === 1 ? 'рецепт' : cards.length < 5 ? 'рецепта' : 'рецептов'}
          </p>
          <RecipeGrid recipes={cards} />
        </>
      )}
    </>
  );
}
