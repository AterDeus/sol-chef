import { notFound } from 'next/navigation';
import { fetchMeatGuide } from '@/lib/api';
import type { MeatPayload } from '@/lib/types';
import { MEAT_CUTS, MEAT_CUT_LABEL, type MeatCut } from '@/lib/vocab';
import { EmptyState, ErrorBanner } from '@/components/Feedback';
import { MeatView } from '@/components/Guides';
import { PageIntro } from '@/components/PageArt';

export const revalidate = 60;

function isCut(value: string): value is MeatCut {
  return (MEAT_CUTS as readonly string[]).includes(value);
}

export default async function MeatCutPage({
  params,
}: {
  params: Promise<{ cut: string }>;
}) {
  const { cut } = await params;
  if (!isCut(cut)) notFound();

  const result = await fetchMeatGuide(cut);
  const title = result.ok ? result.data.title : MEAT_CUT_LABEL[cut];
  const payload = result.ok ? ((result.data.payload ?? {}) as MeatPayload) : null;

  return (
    <>
      <PageIntro
        scene={cut}
        eyebrow="Справочник"
        title={title}
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
        <EmptyState>Справочник по этому мясу пока пуст.</EmptyState>
      )}
      {!result.ok && result.status !== 404 && <ErrorBanner message={result.detail} />}
      {result.ok && payload && <MeatView payload={payload} omitLead />}
    </>
  );
}
