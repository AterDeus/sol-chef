import { Suspense } from 'react';
import Link from 'next/link';
import { fetchPantryOptions, fetchRecommendations } from '@/lib/api';
import { catalogHrefFromCalculator, hasCalculatorQuery, valuesOf } from '@/lib/filters';
import type { PantryGroup, SearchParamsRecord } from '@/lib/types';
import { CalculatorAsk } from '@/components/CalculatorAsk';
import { EmptyState, ErrorBanner } from '@/components/Feedback';
import { PageIntro } from '@/components/PageArt';
import { SolutionBoard } from '@/components/RecipeCard';

export const dynamic = 'force-dynamic';

export default async function CalculatorPage({
  searchParams,
}: {
  searchParams: Promise<SearchParamsRecord>;
}) {
  const sp = await searchParams;
  const asked = hasCalculatorQuery(sp);
  const picking = valuesOf(sp, 'have_group').length > 0;
  const pantry = await fetchPantryOptions();
  const groups = pantry.ok ? pantry.data.groups : [];

  return (
    <>
      <PageIntro
        scene="calculator"
        showArt={!asked}
        eyebrow="Подбор"
        title="Калькулятор"
        lede={
          <p className="lede">
            Напишите, что есть дома, или выберите, что сейчас важнее. Система сама соберёт блюдо и
            подскажет, почему.
          </p>
        }
      />
      <CalculatorAsk sp={sp} groups={groups} />
      {asked && (
        <p style={{ marginBottom: 16 }}>
          <Link href="/calculator">Начать заново</Link>
          {' · '}
          <Link href="/recipes">Книга рецептов</Link>
        </p>
      )}
      {!asked && !picking && (
        <p className="calc-hint">Пока ничего не выбрано — напишите продукты или ткните сценарий.</p>
      )}
      {asked && (
        <Suspense fallback={<p className="calc-hint">Подбираем блюда из каталога…</p>}>
          <CalculatorResults sp={sp} groups={groups} />
        </Suspense>
      )}
    </>
  );
}

async function CalculatorResults({
  sp,
  groups,
}: {
  sp: SearchParamsRecord;
  groups: PantryGroup[];
}) {
  const rec = await fetchRecommendations(sp);
  const featured = rec.ok ? rec.data.featured : null;
  const alternatives = rec.ok ? rec.data.alternatives ?? [] : [];
  if (!rec.ok) {
    return <ErrorBanner message={rec.detail} />;
  }
  if (!featured) {
    return (
      <EmptyState>
        Ничего не подошло — снимите ограничение.{' '}
        <Link href="/recipes">Все рецепты</Link>
      </EmptyState>
    );
  }
  return (
    <SolutionBoard
      featured={featured}
      alternatives={alternatives}
      catalogHref={catalogHrefFromCalculator(sp, groups)}
    />
  );
}
