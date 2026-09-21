'use client';

import { useEffect, useMemo, useState } from 'react';
import { NutritionBlock } from '@/components/NutritionBlock';
import { SpriteIcon } from '@/components/SpriteIcon';
import { computeNutrition } from '@/lib/nutrition';
import { formatDisplayAmount, scaleIngredients } from '@/lib/scale';
import type { RecipeIngredient, Scaling } from '@/lib/types';

function unitLabelOf(unit?: string): string {
  if (unit === 'ml' || unit === 'l') return 'мл';
  return 'г';
}

function formatFactor(ratio: number): string {
  if (!Number.isFinite(ratio) || Math.abs(ratio - 1) < 0.01) return '';
  if (Math.abs(ratio - Math.round(ratio * 10) / 10) < 0.01) {
    return `×${String(ratio).replace('.', ',')}`;
  }
  return `×${ratio.toFixed(2).replace('.', ',')}`;
}

function formatInput(value: number): string {
  if (!Number.isFinite(value)) return '';
  if (Number.isInteger(value)) return String(value);
  return String(Math.round(value * 1000) / 1000);
}

function parsePositive(raw: string): number | null {
  const n = Number(raw.replace(',', '.'));
  if (!Number.isFinite(n) || n <= 0) return null;
  return n;
}

function stepForBase(base: number): number {
  return base >= 500 ? 250 : 50;
}

function DecimalField({
  value,
  parse,
  className,
  onCommit,
  ...inputProps
}: {
  value: number;
  parse: (raw: string) => number | null;
  onCommit: (next: number) => void;
} & Omit<React.InputHTMLAttributes<HTMLInputElement>, 'value' | 'onChange' | 'onBlur'>) {
  const [raw, setRaw] = useState(() => formatInput(value));
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setRaw(formatInput(value));
    setError(null);
  }, [value]);

  const commit = () => {
    const next = parse(raw);
    if (next == null) {
      setError('Введите число больше нуля');
      setRaw(formatInput(value));
      return;
    }
    setError(null);
    onCommit(next);
  };

  return (
    <div className="recipe-scale__field">
      <input
        {...inputProps}
        className={className}
        value={raw}
        aria-invalid={error ? true : undefined}
        onChange={(event) => {
          setRaw(event.target.value);
          setError(null);
        }}
        onBlur={commit}
        onKeyDown={(event) => {
          if (event.key === 'Enter') {
            event.preventDefault();
            commit();
          }
        }}
      />
      {error ? (
        <p className="recipe-scale__error" role="alert">
          {error}
        </p>
      ) : null}
    </div>
  );
}

const KBJU_SKIP_TIP = 'КБЖУ для этой строки не считается.';

function NutritionSkipHint() {
  const [open, setOpen] = useState(false);
  return (
    <button
      type="button"
      className="recipe-list__kbju-hint"
      aria-label={KBJU_SKIP_TIP}
      aria-expanded={open}
      data-tip={KBJU_SKIP_TIP}
      onClick={() => setOpen((value) => !value)}
      onBlur={() => setOpen(false)}
    >
      <SpriteIcon name="info" size={16} />
    </button>
  );
}

type Props = {
  scaling: Scaling;
  ingredients: RecipeIngredient[];
  servingsBase?: number | null;
  yieldWeightG?: number | null;
  yieldKind?: 'estimated' | 'exact' | null;
  hasTimers?: boolean;
};

export function IngredientsBlock({
  scaling,
  ingredients,
  servingsBase = null,
  yieldWeightG = null,
  yieldKind = null,
  hasTimers = false,
}: Props) {
  const enabled = scaling.enabled === true;
  const mode = scaling.mode;
  const baseAnchor = scaling.base_anchor;
  const showAnchor = enabled && mode !== 'servings' && Boolean(baseAnchor);
  const showServings = enabled && mode === 'servings' && Boolean(servingsBase);
  const defaultWeight = baseAnchor?.amount ?? 0;
  const [anchorWeight, setAnchorWeight] = useState(
    scaling.applied?.anchor_weight ?? defaultWeight,
  );
  const [servings, setServings] = useState(scaling.applied?.servings ?? servingsBase ?? 1);

  const ratio = showServings
    ? servings / (servingsBase || 1)
    : showAnchor && defaultWeight > 0
      ? anchorWeight / defaultWeight
      : 1;
  const items = useMemo(() => scaleIngredients(ingredients, ratio), [ingredients, ratio]);
  const nutrition = useMemo(
    () =>
      computeNutrition(ingredients, {
        ratio,
        servings: showServings ? servings : servingsBase,
        yieldWeightG,
      }),
    [ingredients, ratio, showServings, servings, servingsBase, yieldWeightG],
  );

  const factorLabel = showAnchor ? formatFactor(ratio) : '';
  const showReset = showAnchor && Math.abs(ratio - 1) >= 0.01;
  const step = stepForBase(anchorWeight || defaultWeight);
  const unitLabel = unitLabelOf(baseAnchor?.unit);

  return (
    <>
      <section className="recipe-section recipe-ingredients">
        <h2>Ингредиенты</h2>
        {showAnchor && baseAnchor && (
          <div className="recipe-scale">
            <div className="recipe-scale__head">
              <span className="recipe-scale__label">У меня</span>
              {factorLabel ? <span className="recipe-scale__factor">{factorLabel}</span> : null}
            </div>
            <div className="recipe-scale__row">
              <button
                type="button"
                className="btn-secondary recipe-scale__step"
                aria-label="Уменьшить количество"
                onClick={() => setAnchorWeight((n) => Math.max(step, n - step))}
              >
                −
              </button>
              <DecimalField
                className="recipe-scale__input"
                type="text"
                inputMode="decimal"
                aria-label={`Количество, ${unitLabel}: ${baseAnchor.name}`}
                value={anchorWeight}
                parse={parsePositive}
                onCommit={setAnchorWeight}
              />
              <span className="recipe-scale__unit-label">{unitLabel}</span>
              <button
                type="button"
                className="btn-secondary recipe-scale__step"
                aria-label="Увеличить количество"
                onClick={() => setAnchorWeight((n) => n + step)}
              >
                +
              </button>
            </div>
            <p className="recipe-scale__meta">
              <span>
                {baseAnchor.name}
                {baseAnchor.unit
                  ? ` · в рецепте ${formatDisplayAmount(baseAnchor.amount, baseAnchor.unit)}`
                  : null}
              </span>
              {showReset && (
                <button
                  type="button"
                  className="recipe-scale__reset"
                  onClick={() => setAnchorWeight(defaultWeight)}
                >
                  Сброс
                </button>
              )}
            </p>
            {showReset && hasTimers && (
              <p className="recipe-scale__timer-hint">
                Время готовки не пересчитывается — ориентируйтесь на шаги и подстройте таймеры в
                режиме готовки.
              </p>
            )}
          </div>
        )}
        {showServings && (
          <div className="recipe-scale">
            <div className="recipe-scale__head">
              <span>Порции</span>
            </div>
            <div className="recipe-scale__row">
              <button
                type="button"
                className="btn-secondary"
                aria-label="Меньше порций"
                onClick={() => setServings((n) => Math.max(1, n - 1))}
              >
                −
              </button>
              <DecimalField
                className="recipe-scale__input"
                type="text"
                inputMode="numeric"
                aria-label="Число порций"
                value={servings}
                parse={(raw) => {
                  const next = Number(raw.replace(',', '.'));
                  if (!Number.isFinite(next) || next <= 0) return null;
                  return next;
                }}
                onCommit={setServings}
              />
              <button
                type="button"
                className="btn-secondary"
                aria-label="Больше порций"
                onClick={() => setServings((n) => n + 1)}
              >
                +
              </button>
            </div>
          </div>
        )}
        <ul className="recipe-list">
          {items.map((item, index) => (
            <li key={`${item.name}-${index}`}>
              <span className="amount">{item.display_amount}</span>
              <span>
                {item.name}
                {item.detail ? <span className="detail">{item.detail}</span> : null}
                {item.scale_mode === 'manual' ? (
                  <span className="manual-hint">проверьте по исходному рецепту</span>
                ) : null}
              </span>
              {item.nutrition_skip_hint ? <NutritionSkipHint /> : null}
            </li>
          ))}
        </ul>
      </section>
      <NutritionBlock nutrition={nutrition} yieldKind={yieldKind} />
    </>
  );
}
