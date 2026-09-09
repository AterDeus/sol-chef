import { fetchGuide } from '@/lib/api';
import type { GrainsPayload } from '@/lib/types';
import { EmptyState, ErrorBanner } from '@/components/Feedback';
import { GrainsView } from '@/components/Guides';
import { PageIntro } from '@/components/PageArt';

export const revalidate = 60;

export default async function GrainsPage() {
  const result = await fetchGuide('grains');
  const payload = result.ok ? ((result.data.payload ?? {}) as GrainsPayload) : null;

  return (
    <>
      <PageIntro
        scene="grains"
        eyebrow="Справочник"
        title={result.ok ? result.data.title : 'Крупы'}
        lede={
          payload && (payload.intro_lead || payload.intro) ? (
            <p className="lede">
              {payload.intro_lead ? <strong>{payload.intro_lead} </strong> : null}
              {payload.intro}
            </p>
          ) : undefined
        }
      />
      {!result.ok && result.status === 404 && (
        <EmptyState>Справочник круп пока пуст.</EmptyState>
      )}
      {!result.ok && result.status !== 404 && <ErrorBanner message={result.detail} />}
      {result.ok && payload && <GrainsView payload={payload} omitLead />}
    </>
  );
}
