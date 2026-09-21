import { notFound } from 'next/navigation';
import type { Metadata } from 'next';
import { fetchPrepKit } from '@/lib/api';
import { ErrorBanner } from '@/components/Feedback';
import { PageIntro } from '@/components/PageArt';
import { PrepKitView } from '@/components/PrepKitView';
import { formatMinutes, kitDurationMinutes, savingsMinutes } from '@/lib/prep';
import { valuesOf } from '@/lib/filters';
import type { SearchParamsRecord } from '@/lib/types';
import Link from 'next/link';

export const dynamic = 'force-dynamic';

type Props = {
  params: Promise<{ slug: string }>;
  searchParams: Promise<SearchParamsRecord>;
};

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = await params;
  const result = await fetchPrepKit(slug);
  if (!result.ok) return { title: 'Набор' };
  return {
    title: result.data.title,
    description: result.data.summary ?? undefined,
    alternates: { canonical: `/prep/${slug}` },
  };
}

function num(raw: string | undefined): number | null {
  if (!raw) return null;
  const value = Number(raw);
  return Number.isFinite(value) && value > 0 ? value : null;
}

export default async function PrepKitPage({ params, searchParams }: Props) {
  const { slug } = await params;
  const sp = await searchParams;
  const servings = num(valuesOf(sp, 'servings')[0]);
  const noLeftover = ['1', 'true', 'yes', 'on'].includes(
    (valuesOf(sp, 'no_leftover')[0] || '').toLowerCase(),
  );
  const result = await fetchPrepKit(slug, {
    servings: servings ?? undefined,
    noLeftover,
  });

  if (!result.ok && result.status === 404) notFound();
  if (!result.ok) {
    return (
      <>
        <Link className="back-link" href="/prep">
          ← На неделю
        </Link>
        <h1>Набор</h1>
        <ErrorBanner message={result.detail} />
      </>
    );
  }

  const kit = result.data;
  const metrics = kit.metrics ?? {};
  const duration = formatMinutes(kitDurationMinutes(metrics));
  const saved = formatMinutes(savingsMinutes(metrics));
  const kcal = metrics.kcal_avg_per_serving;

  return (
    <>
      <Link className="back-link" href="/prep">
        ← На неделю
      </Link>
      <PageIntro
        scene="prep"
        eyebrow="На неделю"
        title={kit.title}
        showArt={false}
        lede={kit.summary ? <p className="lede">{kit.summary}</p> : undefined}
      />
      {kit.caution_text && (
        <div className="caution" role="status">
          <strong>Осторожно</strong>
          {kit.caution_text}
        </div>
      )}
      <div className="prep-metrics">
        {duration && (
          <div className="prep-metric">
            <strong>{duration}</strong>
            <span>длится подготовка в воскресенье</span>
          </div>
        )}
        {saved && (
          <div className="prep-metric">
            <strong>{saved}</strong>
            <span>экономия за неделю против готовки с нуля</span>
          </div>
        )}
        {kcal != null && (
          <div className="prep-metric">
            <strong>около {kcal} ккал</strong>
            <span>средний ориентир на блюдо</span>
          </div>
        )}
      </div>
      <PrepKitView kit={kit} servings={servings} noLeftover={noLeftover} />
    </>
  );
}
