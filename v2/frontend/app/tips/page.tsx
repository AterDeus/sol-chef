import { fetchGuide } from '@/lib/api';
import { valuesOf } from '@/lib/filters';
import { isKnownKind, isKnownTag } from '@/lib/tips';
import type { SearchParamsRecord, TipsPayload } from '@/lib/types';
import { EmptyState, ErrorBanner } from '@/components/Feedback';
import { TipsView } from '@/components/TipsView';
import { PageIntro } from '@/components/PageArt';
import type { Metadata } from 'next';

export const revalidate = 60;

export const metadata: Metadata = {
  title: 'Советы',
  description: 'Практические советы по темам: техника, продукты, организация.',
};

export default async function TipsPage({
  searchParams,
}: {
  searchParams: Promise<SearchParamsRecord>;
}) {
  const sp = await searchParams;
  const result = await fetchGuide('tips');
  const payload = result.ok ? ((result.data.payload ?? {}) as TipsPayload) : null;
  const initialQ = valuesOf(sp, 'q')[0] ?? '';
  const kindRaw = valuesOf(sp, 'kind')[0] ?? '';
  const tagRaw = valuesOf(sp, 'tag')[0] ?? '';
  const initialKind = isKnownKind(kindRaw) ? kindRaw : '';
  const initialSection = valuesOf(sp, 'section')[0] ?? '';
  const initialTag = isKnownTag(tagRaw) ? tagRaw : '';

  return (
    <>
      <PageIntro
        scene="tips"
        eyebrow="Советы шеф-поваров"
        title="Советы"
        lede={
          <p className="lede">
            Советы сгруппированы по темам. По умолчанию разделы свёрнуты.
          </p>
        }
      />
      {!result.ok && result.status === 404 && (
        <EmptyState>Советы пока не загружены.</EmptyState>
      )}
      {!result.ok && result.status !== 404 && <ErrorBanner message={result.detail} />}
      {result.ok && payload && (
        <TipsView
          payload={payload}
          omitLead
          initialQ={initialQ}
          initialKind={initialKind}
          initialSection={initialSection}
          initialTag={initialTag}
        />
      )}
    </>
  );
}
