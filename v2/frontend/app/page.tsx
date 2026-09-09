import Link from 'next/link';
import { redirect } from 'next/navigation';
import { fetchGuide, fetchRecommendations } from '@/lib/api';
import { hasAnyQuery, queryString } from '@/lib/filters';
import { pickRandomRecipes, pickRandomTips, tipSectionIcon } from '@/lib/home';
import type { SearchParamsRecord, TipsPayload } from '@/lib/types';
import { EmptyState, ErrorBanner } from '@/components/Feedback';
import { PageIntro } from '@/components/PageArt';
import { RecipeGrid } from '@/components/RecipeCard';
import { SpriteIcon } from '@/components/SpriteIcon';

export const dynamic = 'force-dynamic';
export const fetchCache = 'force-no-store';

export default async function HomePage({
  searchParams,
}: {
  searchParams: Promise<SearchParamsRecord>;
}) {
  const sp = await searchParams;
  if (hasAnyQuery(sp)) {
    redirect(`/calculator?${queryString(sp)}`);
  }

  const [rec, tips] = await Promise.all([fetchRecommendations(), fetchGuide('tips')]);
  const recipes = rec.ok ? pickRandomRecipes(rec.data.results) : [];
  const featuredTips = tips.ok
    ? pickRandomTips((tips.data.payload ?? {}) as TipsPayload)
    : [];

  return (
    <>
      <PageIntro
        scene="home"
        eyebrow="Личная кулинарная шпаргалка"
        title="Кухонная шпаргалка"
        lede={
          <p className="lede">
            Рецепты, справочник круп и мяса, советы Энди. Калькулятор соберёт ужин из того, что есть,
            и того, что сейчас важнее.
          </p>
        }
        actions={
          <p className="home-actions">
            <Link className="btn-primary" href="/calculator">
              Подобрать блюдо
            </Link>
            <Link className="btn-secondary" href="/recipes">
              Все рецепты
            </Link>
          </p>
        }
      />

      <div className="section-head">
        <h2>Рецепты</h2>
        <Link href="/recipes">Все рецепты</Link>
      </div>
      {!rec.ok && <ErrorBanner message={rec.detail} />}
      {rec.ok && recipes.length === 0 && (
        <EmptyState>Рецепты пока не загружены.</EmptyState>
      )}
      {recipes.length > 0 && <RecipeGrid recipes={recipes} />}

      <div className="section-head">
        <h2>Советы</h2>
        <Link href="/tips">Все советы</Link>
      </div>
      {!tips.ok && tips.status === 404 && (
        <EmptyState>Советы пока не загружены.</EmptyState>
      )}
      {!tips.ok && tips.status !== 404 && <ErrorBanner message={tips.detail} />}
      {tips.ok && featuredTips.length === 0 && <EmptyState>Пока нет советов.</EmptyState>}
      {featuredTips.length > 0 && (
        <div className="home-tip-grid">
          {featuredTips.map((tip) => (
            <article key={`${tip.sectionId}:${tip.hint}`} className="home-tip">
              <SpriteIcon name={tipSectionIcon(tip.sectionId)} className="ui-icon home-tip__icon" size={22} />
              <p className="home-tip__section">{tip.sectionTitle}</p>
              <h3>
                <Link href={`/tips#tip-${tip.sectionId}`}>{tip.hint}</Link>
              </h3>
              {tip.explanation ? <p className="home-tip__expl">{tip.explanation}</p> : null}
            </article>
          ))}
        </div>
      )}
    </>
  );
}
