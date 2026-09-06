import Link from 'next/link';
import { fetchCatalog, fetchRecommendations } from '@/lib/api';
import { setHref, valuesOf, withPage } from '@/lib/filters';
import type { RecipeCardData, SearchParamsRecord } from '@/lib/types';
import { COOK_METHOD, EQUIPMENT, PROTEIN_BASE, labelOf } from '@/lib/vocab';
import { EmptyState, ErrorBanner } from '@/components/Feedback';
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

export default async function RecipesPage({
  searchParams,
}: {
  searchParams: Promise<SearchParamsRecord>;
}) {
  const sp = await searchParams;
  const q = valuesOf(sp, 'q')[0] ?? '';
  const protein = valuesOf(sp, 'protein_base')[0];
  const method = valuesOf(sp, 'cook_method')[0];
  const equipment = valuesOf(sp, 'equipment')[0];
  const searching = Boolean(q);

  const rec = await fetchRecommendations(
    searching
      ? {}
      : {
          ...(protein ? { protein_base: protein } : {}),
          ...(valuesOf(sp, 'without').length ? { without: sp.without } : {}),
        },
  );
  const all = rec.ok ? rec.data.results : [];
  const proteinCounts = countBy(all, 'protein_base');

  const catalog = searching ? await fetchCatalog(sp) : null;
  const searchResults = searching ? (catalog?.ok ? catalog.data.results : []) : [];
  const count = searching ? (catalog?.ok ? catalog.data.count : 0) : 0;
  const page = Number(valuesOf(sp, 'page')[0] || '1') || 1;

  const inChapter = Boolean(protein) && !searching;
  const methodCounts = inChapter ? countBy(all, 'cook_method') : new Map<string, number>();
  const afterMethod = inChapter && method ? all.filter((item) => item.cook_method === method) : [];
  const equipmentCounts = inChapter && method ? countBy(afterMethod, 'equipment') : new Map<string, number>();
  const showEquipment = equipmentCounts.size > 1;
  const cards =
    inChapter && method
      ? showEquipment
        ? equipment
          ? afterMethod.filter((item) => item.equipment === equipment)
          : []
        : afterMethod
      : [];

  const crumbs = [
    protein ? labelOf(PROTEIN_BASE, protein) : null,
    method ? labelOf(COOK_METHOD, method) : null,
    equipment ? labelOf(EQUIPMENT, equipment) : null,
  ].filter(Boolean);

  return (
    <>
      <p className="eyebrow">Книга</p>
      <h1>Рецепты</h1>
      <p className="lede">
        Оглавление по основе блюда. Дальше — способ и посуда.{' '}
        <Link href="/calculator">Калькулятор</Link>
      </p>
      <form className="search-row" action="/recipes" method="get">
        {(['protein_base', 'cook_method', 'equipment', 'without'] as const).flatMap((key) =>
          valuesOf(sp, key).map((value) => (
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

      {!searching && !protein && (
        <section aria-label="Оглавление">
          <h2 className="filter-legend">Основа блюда</h2>
          {proteinCounts.size === 0 && rec.ok && (
            <EmptyState>Ничего не найдено</EmptyState>
          )}
          <div className="book-toc">
            {[...proteinCounts.entries()]
              .sort((a, b) => labelOf(PROTEIN_BASE, a[0]).localeCompare(labelOf(PROTEIN_BASE, b[0]), 'ru'))
              .map(([code, n]) => (
                <Link key={code} className="book-chapter" href={setHref('/recipes', sp, 'protein_base', code)}>
                  <span>{labelOf(PROTEIN_BASE, code)}</span>
                  <span className="book-chapter__n">{n}</span>
                </Link>
              ))}
          </div>
        </section>
      )}

      {!searching && protein && (
        <>
          <p style={{ marginBottom: 16 }}>
            <Link href="/recipes">← Оглавление</Link>
            {method ? (
              <>
                {' · '}
                <Link href={setHref('/recipes', sp, 'cook_method', null)}>
                  {labelOf(PROTEIN_BASE, protein)}
                </Link>
              </>
            ) : null}
          </p>
          <fieldset className="filter-block">
            <legend className="filter-legend">Способ</legend>
            <div className="chip-row">
            {[...methodCounts.entries()].map(([code, n]) => (
              <Link
                key={code}
                href={setHref('/recipes', sp, 'cook_method', method === code ? null : code)}
                className={method === code ? 'chip is-active' : 'chip'}
                aria-current={method === code ? 'true' : undefined}
              >
                {labelOf(COOK_METHOD, code)} · {n}
              </Link>
            ))}
            </div>
          </fieldset>
          {method && showEquipment && (
            <fieldset className="filter-block">
              <legend className="filter-legend">Посуда</legend>
              <div className="chip-row">
                {[...equipmentCounts.entries()].map(([code, n]) => (
                  <Link
                    key={code}
                    href={setHref('/recipes', sp, 'equipment', equipment === code ? null : code)}
                    className={equipment === code ? 'chip is-active' : 'chip'}
                    aria-current={equipment === code ? 'true' : undefined}
                  >
                    {labelOf(EQUIPMENT, code)} · {n}
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
      {inChapter && methodCounts.size === 0 && rec.ok && (
        <EmptyState>
          В этой главе ничего — снимите ограничение или выберите другую основу.{' '}
          <Link href="/recipes">К оглавлению</Link>
        </EmptyState>
      )}
      {inChapter && method && showEquipment && !equipment && (
        <p className="note">Выберите посуду, чтобы увидеть блюда.</p>
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

      {!searching && cards.length > 0 && <RecipeGrid recipes={cards} />}
    </>
  );
}
