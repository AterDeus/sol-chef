import type { PrepMetrics } from './types';

export const PREP_MODE_RU: Record<string, string> = {
  assemble: 'Собрать',
  finish: 'Доготовить',
  reheat: 'Разогреть',
};

export const PREP_MEAL_RU: Record<string, string> = {
  lunch: 'Обед',
  dinner: 'Ужин',
};

export const PREP_DAY_RU = ['', 'Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'];

export const PREP_PLACE_RU: Record<string, string> = {
  fridge: 'Холодильник',
  freezer: 'Морозилка',
};

/** Чипы на странице набора. База kit — 2; граммы линейно, шаги не переписываются. */
export const PREP_SERVING_OPTIONS = [1, 2, 4] as const;

export function formatServingsLabel(n: number): string {
  const abs = Math.abs(n);
  const mod100 = abs % 100;
  const mod10 = abs % 10;
  if (mod10 === 1 && mod100 !== 11) return `${n} порция`;
  if (mod10 >= 2 && mod10 <= 4 && (mod100 < 12 || mod100 > 14)) return `${n} порции`;
  return `${n} порций`;
}

export function formatMinutes(value: number | null | undefined): string | null {
  if (value == null || Number.isNaN(value)) return null;
  const n = Math.round(value);
  const hours = Math.floor(n / 60);
  const minutes = n % 60;
  if (hours && minutes) return `${hours} ч ${minutes} мин`;
  if (hours) return `${hours} ч`;
  return `${minutes} мин`;
}

export function savingsMinutes(metrics: PrepMetrics): number | null {
  const scratch = metrics.t_scratch_active_min;
  const sunday = metrics.t_sunday_active_min;
  const weekdays = metrics.t_weekdays_active_min;
  if (scratch == null || sunday == null || weekdays == null) return null;
  return scratch - (sunday + weekdays);
}

export function kitHref(
  slug: string,
  opts: {
    servings?: number | null;
    servingsBase?: number | null;
    noLeftover?: boolean;
  } = {},
): string {
  const qs = new URLSearchParams();
  const servings = opts.servings ?? null;
  const base = opts.servingsBase ?? null;
  if (servings != null && base != null && servings !== base) {
    qs.set('servings', String(servings));
  } else if (servings != null && base == null) {
    qs.set('servings', String(servings));
  }
  if (opts.noLeftover) qs.set('no_leftover', '1');
  const suffix = qs.toString() ? `?${qs.toString()}` : '';
  return `/prep/${slug}${suffix}`;
}

export function kitDurationMinutes(metrics: PrepMetrics): number | null {
  const wall = metrics.t_sunday_wall_min;
  const active = metrics.t_sunday_active_min;
  if (wall != null) return wall;
  if (active != null) return active;
  return null;
}
