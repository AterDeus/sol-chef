/** Форматирование структурированных ингредиентов рецепта. */

const WEIGHT_UNITS = new Set(['г', 'кг']);
const VOLUME_UNITS = new Set(['мл', 'л']);

export function isIngredientScalable(item) {
  if (item == null || typeof item === 'string') return false;
  return item.scalable !== false;
}

export function getUnitPair(unit) {
  const u = String(unit || '').trim();
  if (u === 'г' || u === 'кг') return { small: 'г', large: 'кг', factor: 1000 };
  if (u === 'мл' || u === 'л') return { small: 'мл', large: 'л', factor: 1000 };
  return null;
}

export function toBaseAmount(amount, unit) {
  const n = Number(amount);
  if (!Number.isFinite(n)) return null;
  const u = String(unit || '').trim();
  if (u === 'кг') return { value: n * 1000, baseUnit: 'г' };
  if (u === 'л') return { value: n * 1000, baseUnit: 'мл' };
  return { value: n, baseUnit: u || 'г' };
}

function stepForUnit(unit) {
  const u = String(unit || '').trim();
  if (u === 'кг' || u === 'л') return 0.25;
  if (u === 'г' || u === 'мл') return 250;
  if (u === 'шт' || u === 'зубчик' || u === 'стебля' || u === 'порции') return 1;
  return 0.25;
}

const SCALE_MODES = new Set(['linear', 'gentle', 'whole']);

function ingredientName(item) {
  return String(item?.name || '').toLowerCase();
}

function isEggIngredient(item) {
  const name = ingredientName(item);
  return /яйц|белок/.test(name);
}

function detectScaleMode(item) {
  const explicit = String(item?.scale_mode || '').trim();
  if (SCALE_MODES.has(explicit)) return explicit;

  const name = ingredientName(item);
  if (isEggIngredient(item)) return 'whole';
  if (/сода|разрыхлител/.test(name)) return 'gentle';
  return 'linear';
}

export function effectiveScaleFactor(factor, mode) {
  if (mode === 'gentle') return 1 + (factor - 1) * 0.5;
  return factor;
}

export function roundScaled(n, unit, item = null) {
  if (!Number.isFinite(n)) return n;
  const u = String(unit || '').trim();
  const mode = item ? detectScaleMode(item) : 'linear';

  if (mode === 'whole' || (isEggIngredient(item) && (u === 'шт' || !u))) {
    return Math.max(1, Math.round(n));
  }

  if (u === 'г' || u === 'мл') {
    if (n >= 200) return Math.round(n / 10) * 10;
    if (n >= 50) return Math.round(n / 5) * 5;
    return Math.round(n);
  }
  if (u === 'кг' || u === 'л') return Math.round(n * 100) / 100;
  if (u === 'шт' || u === 'зубчик' || u === 'стебля' || u === 'порции') {
    const r = Math.round(n * 2) / 2;
    return Math.max(0.5, r);
  }
  if (u === 'ст. л.' || u === 'ч. л.') return Math.round(n * 4) / 4;
  return Math.round(n * 10) / 10;
}

export function findScaleAnchor(ingredients) {
  if (!Array.isArray(ingredients)) return null;

  const candidates = ingredients.filter(item =>
    isIngredientScalable(item) && item.amount != null && item.amount !== ''
  );
  if (!candidates.length) return null;

  const preferred = candidates.find(item => {
    const u = String(item.unit || '').trim();
    return WEIGHT_UNITS.has(u) || VOLUME_UNITS.has(u);
  });
  const item = preferred || candidates[0];
  const unit = String(item.unit || '').trim();
  const base = toBaseAmount(item.amount, unit);
  if (!base?.value) return null;

  return {
    name: String(item.name || '').trim(),
    originalAmount: Number(item.amount),
    originalUnit: unit,
    baseValue: base.value,
    baseUnit: base.baseUnit,
    step: stepForUnit(unit),
  };
}

export function computeScaleFactorFromBase(anchor, baseValue) {
  if (!anchor?.baseValue || !Number.isFinite(baseValue) || baseValue <= 0) return 1;
  return baseValue / anchor.baseValue;
}

export function computeScaleFactor(anchor, targetAmount) {
  if (!anchor) return 1;
  const target = Number(targetAmount);
  if (!Number.isFinite(target) || target <= 0) return 1;
  const base = toBaseAmount(anchor.originalAmount, anchor.originalUnit);
  const next = toBaseAmount(target, anchor.originalUnit);
  if (!base?.value || !next?.value) return 1;
  return next.value / base.value;
}

export function scaleIngredientItem(item, factor) {
  if (typeof item === 'string') return item;
  if (!isIngredientScalable(item) || item.amount == null || factor === 1) return item;

  const unit = String(item.unit || '').trim();
  const mode = detectScaleMode(item);
  const appliedFactor = effectiveScaleFactor(factor, mode);
  const scaled = {
    ...item,
    amount: roundScaled(Number(item.amount) * appliedFactor, unit, item),
  };
  if (item.amount_max != null) {
    scaled.amount_max = roundScaled(Number(item.amount_max) * appliedFactor, unit, item);
  }
  return scaled;
}

export function scaleIngredients(ingredients, factor) {
  if (!Array.isArray(ingredients) || factor === 1) return ingredients;
  return ingredients.map(item => scaleIngredientItem(item, factor));
}

export function formatScaleFactor(factor) {
  if (!Number.isFinite(factor) || Math.abs(factor - 1) < 0.01) return '';
  if (Math.abs(factor - Math.round(factor * 10) / 10) < 0.01) {
    return `×${String(factor).replace('.', ',')}`;
  }
  return `×${factor.toFixed(2).replace('.', ',')}`;
}

export function formatAnchorAmount(anchor) {
  if (!anchor) return '';
  const amountText = formatAmount(anchor.originalAmount);
  return anchor.originalUnit ? `${amountText} ${anchor.originalUnit}` : amountText;
}

export function formatAmount(value) {
  const n = Number(value);
  if (!Number.isFinite(n)) return '';
  if (n === 0.5) return '1/2';
  if (n === 0.25) return '1/4';
  if (n === 0.75) return '3/4';
  if (Number.isInteger(n)) return String(n);
  return String(n).replace('.', ',');
}

export function formatIngredient(item) {
  if (item == null) return '';
  if (typeof item === 'string') return item.trim();

  const name = String(item.name || '').trim();
  if (!name) return '';

  const parts = [name];
  const detail = String(item.detail || '').trim();
  if (detail) parts.push(detail);

  const unit = String(item.unit || '').trim();
  const hasAmount = item.amount != null && item.amount !== '';
  if (hasAmount) {
    const amountText = item.amount_max != null
      ? `${formatAmount(item.amount)}–${formatAmount(item.amount_max)}`
      : formatAmount(item.amount);
    parts.push(unit ? `${amountText} ${unit}` : amountText);
  }

  return parts.join(' ');
}

export function ingredientSearchText(item) {
  if (typeof item === 'string') return item;
  return formatIngredient(item);
}
