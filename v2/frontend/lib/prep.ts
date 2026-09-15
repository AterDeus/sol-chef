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
  pantry: 'Шкаф',
};

const PREP_DAY_GENITIVE = [
  '',
  'понедельника',
  'вторника',
  'среды',
  'четверга',
  'пятницы',
  'субботы',
  'воскресенья',
];

const DICED_COMPONENT_CODES = new Set([
  'roasted_vegetables',
  'roasted_pumpkin',
  'roasted_veg_near',
  'roasted_veg_pumpkin',
  'braised_cabbage',
]);

export type ThawPull = 'evening_before' | 'morning';

export type ThawBox = {
  label: string;
  place: string;
  thaw_before_day: number | null;
  thaw_pull?: ThawPull | null;
  unit?: string;
  component_code?: string;
};

export function thawPrevDayGenitive(day: number): string {
  if (day <= 1) return 'воскресенья';
  return PREP_DAY_GENITIVE[day - 1] || 'воскресенья';
}

export function thawPullMode(box: ThawBox): ThawPull | null {
  if (box.place !== 'freezer' || box.thaw_before_day == null) return null;
  if (box.thaw_pull === 'morning' || box.thaw_pull === 'evening_before') return box.thaw_pull;
  if (box.unit === 'ml') return 'evening_before';
  if (box.component_code && DICED_COMPONENT_CODES.has(box.component_code)) return 'morning';
  return 'evening_before';
}

export function formatThawColumn(box: ThawBox): string {
  const pull = thawPullMode(box);
  const day = box.thaw_before_day;
  if (!pull || day == null) return '—';
  const name = PREP_DAY_GENITIVE[day] || PREP_DAY_RU[day];
  if (pull === 'morning') return `утром ${name}`;
  return `вечером накануне ${name}`;
}

export function coldContainerCaption(
  containers: Array<{ place: string }>,
): string | null {
  const cold = containers.filter((box) => box.place === 'fridge' || box.place === 'freezer').length;
  const pantry = containers.filter((box) => box.place === 'pantry').length;
  if (cold <= 0) return null;
  const n = `${cold} ${ruCount(cold, 'контейнер', 'контейнера', 'контейнеров')}`;
  if (pantry > 0) return `${n} плюс банки в шкафу`;
  return n;
}

export function ruCount(n: number, one: string, few: string, many: string): string {
  const n10 = Math.abs(n) % 10;
  const n100 = Math.abs(n) % 100;
  if (n10 === 1 && n100 !== 11) return one;
  if (n10 >= 2 && n10 <= 4 && (n100 < 12 || n100 > 14)) return few;
  return many;
}

export function containerNumber(label: string | null | undefined): string | null {
  const match = (label || '').match(/№\s*(\d+)/);
  return match ? `№${match[1]}` : null;
}

export function formatContainerList(labels: string[]): string {
  const nums = labels.map((label) => containerNumber(label));
  if (labels.length > 0 && nums.every((num) => num != null)) {
    const word = nums.length === 1 ? 'контейнер' : 'контейнеры';
    let joined = nums[0] as string;
    if (nums.length === 2) joined = `${nums[0]} и ${nums[1]}`;
    else if (nums.length > 2) joined = `${nums.slice(0, -1).join(', ')} и ${nums[nums.length - 1]}`;
    return `${word} ${joined}`;
  }
  return labels.filter(Boolean).join(', ');
}

export function leftoverCostCaption(cost?: { dishes: number; shopping_add: number } | null): string | null {
  if (!cost || (cost.dishes <= 0 && cost.shopping_add <= 0)) return null;
  const dishes = `${cost.dishes} ${ruCount(cost.dishes, 'быстрое блюдо', 'быстрых блюда', 'быстрых блюд')}`;
  const shop = `${cost.shopping_add} ${ruCount(cost.shopping_add, 'позиция', 'позиции', 'позиций')} к закупке`;
  return `+${dishes}, +${shop}.`;
}

export function thawRemindersForDay(day: number, containers: ThawBox[]): string[] {
  const due = containers.filter((box) => box.place === 'freezer' && box.thaw_before_day === day);
  const evening = due.filter((box) => thawPullMode(box) === 'evening_before');
  const morning = due.filter((box) => thawPullMode(box) === 'morning');
  const names = (boxes: ThawBox[]) => formatContainerList(boxes.map((box) => box.label));
  const lines: string[] = [];
  if (evening.length > 0) {
    lines.push(
      `С вечера ${thawPrevDayGenitive(day)} достаньте из морозилки ${names(evening)} и переложите в холодильник.`,
    );
  }
  if (morning.length > 0) {
    lines.push(`Утром достаньте из морозилки ${names(morning)} и переложите в холодильник.`);
  }
  return lines;
}

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
