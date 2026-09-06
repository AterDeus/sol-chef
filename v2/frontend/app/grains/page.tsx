import { fetchGuide } from '@/lib/api';
import type { GrainsPayload } from '@/lib/types';
import { EmptyState, ErrorBanner } from '@/components/Feedback';
import { GrainsView } from '@/components/Guides';

export const revalidate = 60;

export default async function GrainsPage() {
  const result = await fetchGuide('grains');

  return (
    <>
      <p className="eyebrow">Справочник</p>
      <h1>{result.ok ? result.data.title : 'Крупы'}</h1>
      {!result.ok && result.status === 404 && (
        <EmptyState>Справочник круп пока пуст.</EmptyState>
      )}
      {!result.ok && result.status !== 404 && <ErrorBanner message={result.detail} />}
      {result.ok && <GrainsView payload={(result.data.payload ?? {}) as GrainsPayload} />}
    </>
  );
}
