import type { RecipeIngredient } from '@/lib/types';

const GENTLE_EXPONENT = 0.7;

const UNIT_LABEL: Record<string, string> = {
  g: 'г',
  kg: 'кг',
  ml: 'мл',
  l: 'л',
  pcs: 'шт',
  tsp: 'ч. л.',
  tbsp: 'ст. л.',
  pinch: 'щепотка',
  clove: 'зубчик',
  bunch: 'пучок',
  slice: 'ломтик',
  to_taste: 'по вкусу',
};

function roundHalfUp(value: number, quantum: number): number {
  const n = value / quantum;
  const sign = n < 0 ? -1 : 1;
  const abs = Math.abs(n);
  const whole = Math.floor(abs + 1e-12);
  const frac = abs - whole;
  const rounded = frac >= 0.5 - 1e-12 ? whole + 1 : whole;
  return sign * rounded * quantum;
}

export function applyMode(
  amount: number,
  ratio: number,
  scaleMode: string,
  scalable: boolean,
): number {
  if (!scalable) return amount;
  if (scaleMode === 'manual') return amount;
  if (scaleMode === 'gentle') return amount * ratio ** GENTLE_EXPONENT;
  return amount * ratio;
}

export function roundScaled(amount: number, unit: string, whole = false): number {
  if (whole) return Math.max(1, roundHalfUp(amount, 1));
  if (unit === 'g' || unit === 'ml') {
    if (amount >= 200) return roundHalfUp(amount / 10, 1) * 10;
    if (amount >= 50) return roundHalfUp(amount / 5, 1) * 5;
    return roundHalfUp(amount, 1);
  }
  if (unit === 'kg' || unit === 'l') return roundHalfUp(amount, 0.01);
  if (unit === 'pcs' || unit === 'clove' || unit === 'bunch' || unit === 'slice') {
    return Math.max(0.5, roundHalfUp(amount, 0.5));
  }
  if (unit === 'tsp' || unit === 'tbsp') return roundHalfUp(amount, 0.25);
  return roundHalfUp(amount, 0.1);
}

function formatNumber(value: number): string {
  if (!Number.isFinite(value)) return '';
  if (Math.abs(value - Math.round(value)) < 1e-9) return String(Math.round(value));
  const text = value.toFixed(6).replace(/\.?0+$/, '');
  return text.replace('.', ',');
}

const SPOON_ML: Record<string, number> = { tsp: 5, tbsp: 15 };

function spoonMl(amount: number, unit: string): string {
  return formatNumber(roundHalfUp(amount * SPOON_ML[unit], 1));
}

export function formatDisplayAmount(
  amount: number | null,
  unit: string,
  amountMax: number | null = null,
): string {
  const label = UNIT_LABEL[unit] ?? unit;
  if (unit === 'to_taste' || unit === 'pinch' || amount == null) return label;
  let text = formatNumber(amount);
  if (amountMax != null) text = `${text}–${formatNumber(amountMax)}`;
  let shown = `${text} ${label}`;
  if (unit in SPOON_ML) {
    let hint = spoonMl(amount, unit);
    if (amountMax != null) hint = `${hint}–${spoonMl(amountMax, unit)}`;
    shown = `${shown} (~${hint} мл)`;
  }
  return shown;
}

export function scaleLine(
  line: RecipeIngredient,
  ratio: number,
): RecipeIngredient {
  if (line.amount == null) {
    return { ...line, display_amount: formatDisplayAmount(null, line.unit, line.amount_max) };
  }
  const whole = line.scale_mode === 'whole' && line.scalable;
  const raw = applyMode(line.amount, ratio, line.scale_mode, line.scalable);
  const amount = roundScaled(raw, line.unit, whole);
  let amountMax: number | null = null;
  if (line.amount_max != null) {
    amountMax = roundScaled(
      applyMode(line.amount_max, ratio, line.scale_mode, line.scalable),
      line.unit,
      whole,
    );
  }
  return {
    ...line,
    amount,
    amount_max: amountMax,
    display_amount: formatDisplayAmount(amount, line.unit, amountMax),
  };
}

export function scaleIngredients(
  lines: RecipeIngredient[],
  ratio: number,
): RecipeIngredient[] {
  if (!Number.isFinite(ratio) || Math.abs(ratio - 1) < 0.0001) return lines;
  return lines.map((line) => scaleLine(line, ratio));
}
