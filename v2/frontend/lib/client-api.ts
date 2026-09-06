const FETCH_MS = 8000;
const DOWN = 'Не удалось связаться с сервером. Попробуйте позже.';

export function clientApiUrl(path: string): string {
  const base = (process.env.NEXT_PUBLIC_API_URL || '').replace(/\/$/, '');
  return `${base}${path}`;
}

function parseDetail(payload: unknown, fallback: string): string {
  if (payload && typeof payload === 'object') {
    const rec = payload as { detail?: unknown };
    if (typeof rec.detail === 'string' && rec.detail.trim()) return rec.detail;
  }
  return fallback;
}

async function readJson(res: Response): Promise<unknown> {
  const text = await res.text();
  if (!text) return null;
  try {
    return JSON.parse(text);
  } catch {
    return null;
  }
}

export async function clientFetch(path: string, init: RequestInit = {}): Promise<Response> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), FETCH_MS);
  try {
    return await fetch(clientApiUrl(path), {
      ...init,
      signal: init.signal ?? controller.signal,
    });
  } finally {
    clearTimeout(timer);
  }
}

export type ClientResult<T> =
  | { ok: true; data: T; status: number }
  | { ok: false; status: number; detail: string };

export async function fetchRecipeClient<T>(
  slug: string,
  opts: {
    anchor_weight?: number;
    servings?: number;
    variant?: string | null;
    equipment?: string | null;
  },
): Promise<ClientResult<T>> {
  const qs = new URLSearchParams();
  if (opts.anchor_weight != null) qs.set('anchor_weight', String(opts.anchor_weight));
  if (opts.servings != null) qs.set('servings', String(opts.servings));
  if (opts.variant) qs.set('variant', opts.variant);
  if (opts.equipment) qs.set('equipment', opts.equipment);
  const suffix = qs.toString() ? `?${qs.toString()}` : '';
  try {
    const res = await clientFetch(`/api/recipes/${encodeURIComponent(slug)}/${suffix}`, {
      cache: 'no-store',
    });
    const body = await readJson(res);
    if (!res.ok) {
      return {
        ok: false,
        status: res.status,
        detail: parseDetail(body, 'Не удалось обновить количества.'),
      };
    }
    return { ok: true, data: body as T, status: res.status };
  } catch {
    return { ok: false, status: 0, detail: DOWN };
  }
}
