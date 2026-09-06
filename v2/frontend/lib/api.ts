import { cookies } from 'next/headers';
import type {
  CatalogResponse,
  GuideDocument,
  PantryOptionsResponse,
  RecipeDetail,
  RecommendationsResponse,
  SearchParamsRecord,
} from './types';
import { queryString } from './filters';

const INTERNAL_API_URL = process.env.INTERNAL_API_URL || 'http://backend:8000';
const FETCH_MS = 8000;
const DOWN = 'Не удалось связаться с сервером. Попробуйте позже.';

export type ApiOk<T> = { ok: true; data: T; status: number };
export type ApiErr = { ok: false; status: number; detail: string };
export type ApiResult<T> = ApiOk<T> | ApiErr;

function serverApiUrl(path: string): string {
  const base = INTERNAL_API_URL.replace(/\/$/, '');
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

export async function serverFetch(path: string, init: RequestInit = {}): Promise<Response> {
  const cookieStore = await cookies();
  const cookieHeader = cookieStore.toString();
  const headers = new Headers(init.headers);
  if (cookieHeader && !headers.has('Cookie')) {
    headers.set('Cookie', cookieHeader);
  }
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), FETCH_MS);
  try {
    return await fetch(serverApiUrl(path), {
      ...init,
      headers,
      signal: init.signal ?? controller.signal,
    });
  } finally {
    clearTimeout(timer);
  }
}

async function getJson<T>(path: string, fallback: string): Promise<ApiResult<T>> {
  try {
    const res = await serverFetch(path, { cache: 'no-store' });
    const body = await readJson(res);
    if (!res.ok) {
      return {
        ok: false,
        status: res.status,
        detail: parseDetail(body, fallback),
      };
    }
    return { ok: true, data: body as T, status: res.status };
  } catch {
    return { ok: false, status: 0, detail: DOWN };
  }
}

export async function fetchRecommendations(
  sp: SearchParamsRecord = {},
): Promise<ApiResult<RecommendationsResponse>> {
  const qs = new URLSearchParams();
  for (const key of [
    'protein_base',
    'cook_method',
    'dish_type',
    'equipment',
    'cuts',
    'without',
    'have',
    'have_group',
    'intent',
  ] as const) {
    const raw = sp[key];
    if (raw == null || raw === '') continue;
    const list = Array.isArray(raw) ? raw : [raw];
    for (const item of list) {
      for (const part of item.split(',')) {
        const trimmed = part.trim();
        if (trimmed) qs.append(key, trimmed);
      }
    }
  }
  const suffix = qs.toString() ? `?${qs.toString()}` : '';
  return getJson<RecommendationsResponse>(
    `/api/recommendations/${suffix}`,
    'Не удалось загрузить подборку.',
  );
}

export async function fetchPantryOptions(): Promise<ApiResult<PantryOptionsResponse>> {
  return getJson<PantryOptionsResponse>('/api/ingredients/', 'Не удалось загрузить продукты.');
}

export async function fetchCatalog(
  sp: SearchParamsRecord = {},
): Promise<ApiResult<CatalogResponse>> {
  const qs = queryString(sp);
  const path = qs ? `/api/recipes/?${qs}` : '/api/recipes/';
  return getJson<CatalogResponse>(path, 'Не удалось загрузить каталог.');
}

export async function fetchRecipe(
  slug: string,
  opts?: {
    anchor_weight?: number;
    servings?: number;
    variant?: string | null;
    equipment?: string | null;
  },
): Promise<ApiResult<RecipeDetail>> {
  const qs = new URLSearchParams();
  if (opts?.anchor_weight != null) qs.set('anchor_weight', String(opts.anchor_weight));
  if (opts?.servings != null) qs.set('servings', String(opts.servings));
  if (opts?.variant) qs.set('variant', opts.variant);
  if (opts?.equipment) qs.set('equipment', opts.equipment);
  const suffix = qs.toString() ? `?${qs.toString()}` : '';
  return getJson<RecipeDetail>(
    `/api/recipes/${encodeURIComponent(slug)}/${suffix}`,
    'Рецепт не найден.',
  );
}

export async function fetchGuide(kind: 'grains' | 'tips'): Promise<ApiResult<GuideDocument>> {
  return getJson<GuideDocument>(`/api/guides/${kind}/`, 'Справочник не найден.');
}

export async function fetchMeatGuide(cut: string): Promise<ApiResult<GuideDocument>> {
  return getJson<GuideDocument>(
    `/api/guides/meat/${encodeURIComponent(cut)}/`,
    'Справочник не найден.',
  );
}
