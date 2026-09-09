import { fetchGuide } from '@/lib/api';
import type { TipsPayload } from '@/lib/types';
import { EmptyState, ErrorBanner } from '@/components/Feedback';
import { TipsView } from '@/components/Guides';
import { PageIntro } from '@/components/PageArt';

export const revalidate = 60;

export default async function TipsPage() {
  const result = await fetchGuide('tips');
  const payload = result.ok ? ((result.data.payload ?? {}) as TipsPayload) : null;

  return (
    <>
      <PageIntro
        scene="tips"
        eyebrow="Советы Энди"
        title={result.ok ? result.data.title : 'Советы'}
        lede={payload?.intro ? <p className="lede">{payload.intro}</p> : undefined}
      />
      {!result.ok && result.status === 404 && (
        <EmptyState>Советы пока не загружены.</EmptyState>
      )}
      {!result.ok && result.status !== 404 && <ErrorBanner message={result.detail} />}
      {result.ok && payload && <TipsView payload={payload} omitLead />}
    </>
  );
}
