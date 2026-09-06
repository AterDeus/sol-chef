import Link from 'next/link';
import { fetchPantryOptions, fetchRecommendations } from '@/lib/api';
import { hasAnyQuery } from '@/lib/filters';
import type { SearchParamsRecord } from '@/lib/types';
import { CalculatorAsk } from '@/components/CalculatorAsk';
import { EmptyState, ErrorBanner } from '@/components/Feedback';
import { SolutionBoard } from '@/components/RecipeCard';

export const dynamic = 'force-dynamic';

export default async function CalculatorPage({
  searchParams,
}: {
  searchParams: Promise<SearchParamsRecord>;
}) {
  const sp = await searchParams;
  const asked = hasAnyQuery(sp);
  const [rec, pantry] = await Promise.all([
    asked ? fetchRecommendations(sp) : Promise.resolve(null),
    fetchPantryOptions(),
  ]);
  const featured = rec?.ok ? rec.data.featured : null;
  const alternatives = rec?.ok ? rec.data.alternatives ?? [] : [];

  return (
    <>
      <p className="eyebrow">Подбор</p>
      <h1>Калькулятор</h1>
      <p className="lede">
        Напишите, что есть дома, или выберите, что сейчас важнее. Система сама соберёт блюдо и
        подскажет, почему.
      </p>
      <CalculatorAsk sp={sp} groups={pantry.ok ? pantry.data.groups : []} />
      {asked && (
        <p style={{ marginBottom: 16 }}>
          <Link href="/calculator">Начать заново</Link>
          {' · '}
          <Link href="/recipes">Книга рецептов</Link>
        </p>
      )}
      {rec && !rec.ok && <ErrorBanner message={rec.detail} />}
      {!asked && (
        <p className="calc-hint">Пока ничего не выбрано — напишите продукты или ткните сценарий.</p>
      )}
      {asked && rec?.ok && !featured && (
        <EmptyState>
          Ничего не подошло — снимите ограничение.{' '}
          <Link href="/recipes">Все рецепты</Link>
        </EmptyState>
      )}
      {asked && rec?.ok && featured && (
        <SolutionBoard featured={featured} alternatives={alternatives} />
      )}
    </>
  );
}
