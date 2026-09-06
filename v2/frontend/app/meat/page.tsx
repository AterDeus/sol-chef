import Link from 'next/link';
import { fetchMeatGuide } from '@/lib/api';
import { MEAT_CUTS, MEAT_CUT_LABEL } from '@/lib/vocab';
import { EmptyState, ErrorBanner } from '@/components/Feedback';

export const revalidate = 60;

export default async function MeatHubPage() {
  const results = await Promise.all(
    MEAT_CUTS.map(async (cut) => ({ cut, result: await fetchMeatGuide(cut) })),
  );
  const tiles = results.filter((item) => item.result.ok);
  const down = results.every((item) => !item.result.ok && item.result.status === 0);
  const anyError = results.some(
    (item) => !item.result.ok && item.result.status !== 404 && item.result.status !== 0,
  );

  return (
    <>
      <p className="eyebrow">Справочник</p>
      <h1>Мясо</h1>
      <p className="lede">Выберите белок — внутри температуры и типичные ошибки по отрубам.</p>
      {down && <ErrorBanner message="Не удалось связаться с сервером. Попробуйте позже." />}
      {!down && anyError && <ErrorBanner message="Часть справочников не загрузилась." />}
      {!down && tiles.length === 0 && (
        <EmptyState>Пока нет справочников по мясу.</EmptyState>
      )}
      {tiles.length > 0 && (
        <div className="hub-tiles">
          {tiles.map((tile) => (
            <Link key={tile.cut} className="hub-tile" href={`/meat/${tile.cut}`}>
              {MEAT_CUT_LABEL[tile.cut]}
            </Link>
          ))}
        </div>
      )}
    </>
  );
}
