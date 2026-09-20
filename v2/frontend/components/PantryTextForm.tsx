'use client';

import { useRouter } from 'next/navigation';
import { useId, useState } from 'react';
import { clientFetch } from '@/lib/client-api';
import { FILTER_KEYS, toURLSearchParams, valuesOf } from '@/lib/filters';
import type { PantryGroup, PantryResolveResponse, SearchParamsRecord } from '@/lib/types';

function pathForHave(groups: PantryGroup[], canonicalId: string): string {
  for (const group of groups) {
    const own = group.items?.find((item) => item.canonical_id === canonicalId);
    if (own) return own.title;
    for (const child of group.children ?? []) {
      const nested = child.items?.find((item) => item.canonical_id === canonicalId);
      if (nested) return nested.title;
    }
  }
  return canonicalId;
}

export function PantryTextForm({
  sp,
  groups,
}: {
  sp: SearchParamsRecord;
  groups: PantryGroup[];
}) {
  const router = useRouter();
  const hintId = useId();
  const resultId = useId();
  const initialText = valuesOf(sp, 'pantry')[0] ?? '';
  const [text, setText] = useState(initialText);
  const [unknown, setUnknown] = useState<string[]>(valuesOf(sp, 'missed'));
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');

  const recognized = valuesOf(sp, 'have');
  const missed = unknown.length ? unknown : valuesOf(sp, 'missed');
  const showResult = recognized.length > 0 || missed.length > 0 || Boolean(error);

  async function onSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const raw = text.trim();
    if (!raw) return;
    setBusy(true);
    setError('');
    setUnknown([]);
    try {
      const res = await clientFetch(`/api/ingredients/?text=${encodeURIComponent(raw)}`);
      const body = (await res.json()) as PantryResolveResponse;
      const items = body.items ?? [];
      const missedItems = body.unknown ?? [];
      setUnknown(missedItems);
      if (items.length === 0) {
        setError(
          missedItems.length
            ? `Не распознали: ${missedItems.join(', ')}. Попробуйте названия через запятую, как в примере.`
            : 'Не удалось разобрать продукты.',
        );
        return;
      }
      const qs = toURLSearchParams(sp);
      qs.delete('have');
      qs.delete('missed');
      qs.delete('pantry');
      qs.set('pantry', raw);
      for (const item of items) qs.append('have', item.canonical_id);
      for (const item of missedItems) qs.append('missed', item);
      router.push(qs.toString() ? `/calculator?${qs.toString()}` : '/calculator');
    } catch {
      setError('Не удалось связаться с сервером. Попробуйте позже.');
    } finally {
      setBusy(false);
    }
  }

  return (
    <form className="calc-pantry" action="/calculator" method="get" onSubmit={onSubmit}>
      <label htmlFor="pantry-text">Что есть дома</label>
      <textarea
        id="pantry-text"
        name="pantry"
        rows={2}
        value={text}
        onChange={(event) => setText(event.target.value)}
        placeholder="курица, рис, лук, томаты"
        autoComplete="off"
        aria-describedby={hintId}
      />
      <p id={hintId} className="calc-pantry__hint">
        Перечислите продукты через запятую. Пример: курица, рис, лук, томаты.
      </p>
      {FILTER_KEYS.filter((key) => key !== 'have').flatMap((key) => {
        const raw = sp[key];
        const list = raw == null || raw === '' ? [] : Array.isArray(raw) ? raw : [raw];
        return list.map((value) => (
          <input key={`${key}-${value}`} type="hidden" name={key} value={value} />
        ));
      })}
      <button type="submit" className="btn-primary" disabled={busy}>
        Подобрать рецепты
      </button>
      {showResult ? (
        <div className="calc-pantry__result" id={resultId} role="status">
          {recognized.length > 0 ? (
            <p>
              <strong>Распознали:</strong>{' '}
              {recognized.map((id) => pathForHave(groups, id)).join(', ')}
            </p>
          ) : null}
          {missed.length > 0 ? (
            <p>
              <strong>Не распознали:</strong> {missed.join(', ')}. Можно исправить запрос в поле
              выше и подобрать снова.
            </p>
          ) : null}
          {error ? <p className="calc-pantry__note">{error}</p> : null}
          <button
            type="button"
            className="calc-pantry__edit"
            onClick={() => document.getElementById('pantry-text')?.focus()}
          >
            Изменить запрос
          </button>
        </div>
      ) : null}
    </form>
  );
}
