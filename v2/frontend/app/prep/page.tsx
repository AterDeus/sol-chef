import Link from 'next/link';
import { fetchPrepKits } from '@/lib/api';
import { EmptyState, ErrorBanner } from '@/components/Feedback';
import { PageIntro } from '@/components/PageArt';
import { formatMinutes, kitDurationMinutes, savingsMinutes } from '@/lib/prep';

export const dynamic = 'force-dynamic';

export default async function PrepCatalogPage() {
  const result = await fetchPrepKits();
  const kits = result.ok ? result.data.results : [];

  return (
    <>
      <PageIntro
        scene="prep"
        eyebrow="Заготовки"
        title="На неделю"
        lede={
          <p className="lede">
            Один выходной: закупка и полуфабрикаты. Будни — собрать тарелку за 10–20 минут.
          </p>
        }
      />
      {!result.ok && <ErrorBanner message={result.detail} />}
      {result.ok && kits.length === 0 && (
        <EmptyState>Наборы пока не загружены</EmptyState>
      )}
      {kits.length > 0 && (
        <div className="prep-kit-grid">
          {kits.map((kit) => {
            const duration = formatMinutes(kitDurationMinutes(kit.metrics));
            const saved = formatMinutes(savingsMinutes(kit.metrics));
            const kcal = kit.metrics.kcal_avg_per_serving;
            return (
              <article key={kit.slug} className="prep-kit-card">
                <h2>
                  <Link href={`/prep/${kit.slug}`}>{kit.title}</Link>
                </h2>
                {kit.summary && <p>{kit.summary}</p>}
                <p className="prep-kit-card__meta">
                  {[
                    duration ? `подготовка ${duration}` : null,
                    saved ? `экономия ${saved}` : null,
                    kcal ? `около ${kcal} ккал на блюдо` : null,
                  ]
                    .filter(Boolean)
                    .join(' · ')}
                </p>
              </article>
            );
          })}
        </div>
      )}
    </>
  );
}
