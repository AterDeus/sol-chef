'use client';

import { useMemo, useState } from 'react';
import { NutritionBlock } from '@/components/NutritionBlock';
import { SpriteIcon } from '@/components/SpriteIcon';
import { computeNutrition } from '@/lib/nutrition';
import { scaleIngredients } from '@/lib/scale';
import type { RecipeIngredient, Scaling } from '@/lib/types';

type UnitPair = { small: string; large: string; factor: number };

function unitPairOf(unit?: string): UnitPair | null {
  if (unit === 'g' || unit === 'kg') return { small: 'г', large: 'кг', factor: 1000 };
  if (unit === 'ml' || unit === 'l') return { small: 'мл', large: 'л', factor: 1000 };
  return null;
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

function displayOf(base: number, pair: UnitPair | null, large: boolean): number {
  if (!pair || !large) return base;
  return Math.round((base / pair.factor) * 1000) / 1000;
}

function baseFromInput(raw: string, pair: UnitPair | null, large: boolean): number | null {
  const n = Number(raw.replace(',', '.'));
  if (!Number.isFinite(n) || n <= 0) return null;
  if (!pair || !large) return n;
  return n * pair.factor;
}

function stepForBase(base: number): number {
  return base >= 500 ? 250 : 50;
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
  const pair = useMemo(() => unitPairOf(baseAnchor?.unit), [baseAnchor?.unit]);
  const [useLarge, setUseLarge] = useState(baseAnchor?.unit === 'kg' || baseAnchor?.unit === 'l');

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
  const displayValue = displayOf(anchorWeight, pair, useLarge);
  const displayStep = pair && useLarge ? step / pair.factor : step;

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
                aria-label="Меньше"
                onClick={() => setAnchorWeight((n) => Math.max(step, n - step))}
              >
                −
              </button>
              <input
                className="recipe-scale__input"
                type="number"
                inputMode="decimal"
                min={pair && useLarge ? step / pair.factor : step}
                step={displayStep}
                value={formatInput(displayValue)}
                aria-label={`Количество: ${baseAnchor.name}`}
                onChange={(e) => {
                  const next = baseFromInput(e.target.value, pair, useLarge);
                  if (next != null) setAnchorWeight(next);
                }}
              />
              {pair && (
                <label className={`recipe-scale__unit-switch${useLarge ? ' is-large' : ''}`}>
                  <span className="recipe-scale__unit-opt" data-unit-side="small">
                    {pair.small}
                  </span>
                  <span className="recipe-scale__unit-track">
                    <input
                      type="checkbox"
                      className="recipe-scale__unit-check"
                      checked={useLarge}
                      aria-label={`Переключить ${pair.small} и ${pair.large}`}
                      onChange={(e) => setUseLarge(e.target.checked)}
                    />
                    <span className="recipe-scale__unit-thumb" aria-hidden />
                  </span>
                  <span className="recipe-scale__unit-opt" data-unit-side="large">
                    {pair.large}
                  </span>
                </label>
              )}
              <button
                type="button"
                className="btn-secondary recipe-scale__step"
                aria-label="Больше"
                onClick={() => setAnchorWeight((n) => n + step)}
              >
                +
              </button>
            </div>
            <p className="recipe-scale__meta">
              <span>
                {baseAnchor.name}
                {baseAnchor.unit ? ` · в рецепте ${baseAnchor.amount} ${baseAnchor.unit}` : null}
              </span>
              {showReset && (
                <button
                  type="button"
                  className="recipe-scale__reset"
                  onClick={() => {
                    setAnchorWeight(defaultWeight);
                    setUseLarge(false);
                  }}
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
              <input
                className="recipe-scale__input"
                type="number"
                min={1}
                step={1}
                value={servings}
                aria-label="Число порций"
                onChange={(e) => {
                  const next = Number(e.target.value);
                  if (Number.isFinite(next) && next > 0) setServings(next);
                }}
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
