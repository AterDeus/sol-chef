import { fetchGuide } from '@/lib/api';
import type { TipsPayload } from '@/lib/types';
import { EmptyState, ErrorBanner } from '@/components/Feedback';
import { TipsView } from '@/components/Guides';

export const revalidate = 60;

export default async function TipsPage() {
  const result = await fetchGuide('tips');

  return (
    <>
      <p className="eyebrow">Советы Энди</p>
      <h1>{result.ok ? result.data.title : 'Советы'}</h1>
      {!result.ok && result.status === 404 && (
        <EmptyState>Советы пока не загружены.</EmptyState>
      )}
      {!result.ok && result.status !== 404 && <ErrorBanner message={result.detail} />}
      {result.ok && <TipsView payload={(result.data.payload ?? {}) as TipsPayload} />}
    </>
  );
}
