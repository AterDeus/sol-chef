import { fetchCatalog } from '@/lib/api';
import { valuesOf } from '@/lib/filters';
import type { SearchParamsRecord } from '@/lib/types';
import { ErrorBanner } from '@/components/Feedback';
import { PageIntro } from '@/components/PageArt';
import { RecipesBook } from '@/components/RecipesBook';
import Link from 'next/link';

export const dynamic = 'force-dynamic';

export default async function RecipesPage({
  searchParams,
}: {
  searchParams: Promise<SearchParamsRecord>;
}) {
  const sp = await searchParams;
  const catalogSp = valuesOf(sp, 'without').length ? { without: sp.without } : {};
  const list = await fetchCatalog(catalogSp, { all: true });
  const recipes = list.ok ? list.data.results : [];

  return (
    <>
      <PageIntro
        scene="recipes"
        eyebrow="Книга"
        title="Рецепты"
        lede={
          <p className="lede">
            Сначала мясо, птица, овощи, рыба, гарниры, завтраки или десерты. В главе сразу все
            рецепты; способ и посуда только сужают список.{' '}
            <Link href="/calculator">Калькулятор</Link>
          </p>
        }
      />
      {list && !list.ok && <ErrorBanner message={list.detail} />}
      {list.ok && <RecipesBook recipes={recipes} sp={sp} />}
    </>
  );
}
