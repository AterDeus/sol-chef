'use client';

import { useRouter } from 'next/navigation';
import { useState } from 'react';
import { clientFetch } from '@/lib/client-api';
import { FILTER_KEYS, toURLSearchParams } from '@/lib/filters';
import type { PantryResolveResponse, SearchParamsRecord } from '@/lib/types';

export function PantryTextForm({ sp }: { sp: SearchParamsRecord }) {
  const router = useRouter();
  const [text, setText] = useState('');
  const [unknown, setUnknown] = useState<string[]>([]);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');

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
      const missed = body.unknown ?? [];
      setUnknown(missed);
      if (items.length === 0) {
        setError(missed.length ? `Не поняли: ${missed.join(', ')}` : 'Не удалось разобрать продукты.');
        return;
      }
      const qs = toURLSearchParams(sp);
      qs.delete('have');
      for (const item of items) qs.append('have', item.canonical_id);
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
        name="have"
        rows={2}
        value={text}
        onChange={(event) => setText(event.target.value)}
        placeholder="курица, гречка, лук"
        autoComplete="off"
      />
      {FILTER_KEYS.filter((key) => key !== 'have').flatMap((key) => {
        const raw = sp[key];
        const list = raw == null || raw === '' ? [] : Array.isArray(raw) ? raw : [raw];
        return list.map((value) => (
          <input key={`${key}-${value}`} type="hidden" name={key} value={value} />
        ));
      })}
      <button type="submit" className="btn-primary" disabled={busy}>
        Найти из этого
      </button>
      {error ? <p className="calc-pantry__note">{error}</p> : null}
      {!error && unknown.length > 0 ? (
        <p className="calc-pantry__note">Не поняли: {unknown.join(', ')}. Остальное учли.</p>
      ) : null}
    </form>
  );
}
