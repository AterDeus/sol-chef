import {
  computeScaleFactorFromBase,
  findScaleAnchor,
  formatAnchorAmount,
  formatIngredient,
  formatScaleFactor,
  getUnitPair,
  scaleIngredients,
} from './ingredient-utils.js';
import { escapeHtml } from './utils.js';
import { normalizeSteps } from './step-utils.js';

const BASE_STEP = 250;

function scaleStorageKey(recipeId) {
  return `sol-chef-scale:${recipeId}`;
}

function scaleUnitStorageKey(recipeId) {
  return `sol-chef-scale-large:${recipeId}`;
}

function readSavedBaseValue(recipeId, fallback) {
  try {
    const raw = sessionStorage.getItem(scaleStorageKey(recipeId));
    const value = Number(raw);
    if (Number.isFinite(value) && value > 0) return value;
  } catch (_) { /* sessionStorage unavailable */ }
  return fallback;
}

function readSavedUseLargeUnit(recipeId) {
  try {
    return sessionStorage.getItem(scaleUnitStorageKey(recipeId)) === '1';
  } catch (_) {
    return false;
  }
}

function writeSavedBaseValue(recipeId, baseValue) {
  try {
    sessionStorage.setItem(scaleStorageKey(recipeId), String(baseValue));
  } catch (_) { /* ignore */ }
}

function writeSavedUseLargeUnit(recipeId, useLarge) {
  try {
    sessionStorage.setItem(scaleUnitStorageKey(recipeId), useLarge ? '1' : '0');
  } catch (_) { /* ignore */ }
}

function clearSavedScale(recipeId) {
  try {
    sessionStorage.removeItem(scaleStorageKey(recipeId));
    sessionStorage.removeItem(scaleUnitStorageKey(recipeId));
  } catch (_) { /* ignore */ }
}

function renderIngredientList(items) {
  return items.map(item => `<li>${escapeHtml(formatIngredient(item))}</li>`).join('');
}

function hasTimers(steps) {
  return normalizeSteps(steps).some(step => step.timer_sec > 0);
}

function renderUnitSwitch(unitPair, useLargeUnit) {
  if (!unitPair) return '';
  return `
    <label class="recipe-scale__unit-switch" title="Единица измерения">
      <span class="recipe-scale__unit-opt" data-unit-side="small">${escapeHtml(unitPair.small)}</span>
      <span class="recipe-scale__unit-track">
        <input
          type="checkbox"
          class="recipe-scale__unit-check"
          id="recipe-scale-unit-check"
          ${useLargeUnit ? 'checked' : ''}
          aria-label="Переключить ${escapeHtml(unitPair.small)} и ${escapeHtml(unitPair.large)}"
        >
        <span class="recipe-scale__unit-thumb" aria-hidden="true"></span>
      </span>
      <span class="recipe-scale__unit-opt" data-unit-side="large">${escapeHtml(unitPair.large)}</span>
    </label>`;
}

function displayValue(baseValue, unitPair, useLargeUnit) {
  if (!unitPair || !useLargeUnit) return baseValue;
  return Math.round((baseValue / unitPair.factor) * 1000) / 1000;
}

function baseValueFromInput(raw, unitPair, useLargeUnit) {
  const n = Number(raw);
  if (!Number.isFinite(n) || n <= 0) return null;
  if (!unitPair || !useLargeUnit) return n;
  return n * unitPair.factor;
}

function inputStep(unitPair, useLargeUnit, anchorStep) {
  if (!unitPair) return anchorStep;
  if (!useLargeUnit) return BASE_STEP;
  return BASE_STEP / unitPair.factor;
}

function stepBase(unitPair, anchorStep) {
  return unitPair ? BASE_STEP : anchorStep;
}

function formatInputValue(value) {
  const n = Number(value);
  if (!Number.isFinite(n)) return '';
  if (Number.isInteger(n)) return String(n);
  return String(Math.round(n * 1000) / 1000);
}

export function renderIngredientsSection(recipe) {
  const anchor = findScaleAnchor(recipe.ingredients);
  if (!recipe.ingredients?.length) return '';

  const unitPair = anchor ? getUnitPair(anchor.originalUnit) : null;
  const defaultBase = anchor?.baseValue ?? null;
  const targetBase = anchor ? readSavedBaseValue(recipe.id, defaultBase) : defaultBase;
  const useLargeUnit = anchor && unitPair ? readSavedUseLargeUnit(recipe.id) : false;
  const factor = anchor ? computeScaleFactorFromBase(anchor, targetBase) : 1;
  const scaledItems = anchor ? scaleIngredients(recipe.ingredients, factor) : recipe.ingredients;
  const factorLabel = formatScaleFactor(factor);
  const showReset = anchor && Math.abs(factor - 1) >= 0.01;
  const showTimerHint = showReset && hasTimers(recipe.steps);

  let scaleBlock = '';
  if (anchor) {
    const step = inputStep(unitPair, useLargeUnit, anchor.step);
    const minBase = Math.max(stepBase(unitPair, anchor.step), anchor.baseValue * 0.1);
    const minDisplay = displayValue(minBase, unitPair, useLargeUnit);
    scaleBlock = `
      <div class="recipe-scale" id="recipe-scale" data-recipe-id="${escapeHtml(recipe.id)}">
        <div class="recipe-scale__head">
          <span class="recipe-scale__label">У меня</span>
          ${factorLabel ? `<span class="recipe-scale__factor" id="recipe-scale-factor">${escapeHtml(factorLabel)}</span>` : '<span class="recipe-scale__factor" id="recipe-scale-factor" hidden></span>'}
        </div>
        <div class="recipe-scale__row">
          <button type="button" class="btn-secondary recipe-scale__step" data-delta="-1" aria-label="Меньше">−</button>
          <input
            type="number"
            class="recipe-scale__input"
            id="recipe-scale-input"
            value="${formatInputValue(displayValue(targetBase, unitPair, useLargeUnit))}"
            min="${minDisplay}"
            step="${step}"
            inputmode="decimal"
            aria-label="Количество ${escapeHtml(anchor.name)}"
          >
          ${renderUnitSwitch(unitPair, useLargeUnit)}
          <button type="button" class="btn-secondary recipe-scale__step" data-delta="1" aria-label="Больше">+</button>
        </div>
        <p class="recipe-scale__meta">
          <span id="recipe-scale-anchor">${escapeHtml(anchor.name)} · в рецепте ${escapeHtml(formatAnchorAmount(anchor))}</span>
          <button type="button" class="recipe-scale__reset" id="recipe-scale-reset" ${showReset ? '' : 'hidden'}>Сброс</button>
        </p>
        <p class="recipe-scale__timer-hint" id="recipe-scale-timer-hint" ${showTimerHint ? '' : 'hidden'}>
          Время готовки не пересчитывается — ориентируйтесь на шаги и подстройте таймеры в режиме готовки.
        </p>
      </div>`;
  }

  return `
    <section class="recipe-section recipe-ingredients">
      <h2>Ингредиенты</h2>
      ${scaleBlock}
      <ul class="recipe-list" id="recipe-ingredients-list">${renderIngredientList(scaledItems)}</ul>
    </section>`;
}

export function wireIngredientsScale(recipe) {
  const root = document.getElementById('recipe-scale');
  const listEl = document.getElementById('recipe-ingredients-list');
  const anchor = findScaleAnchor(recipe.ingredients);
  if (!root || !listEl || !anchor) return;

  const unitPair = getUnitPair(anchor.originalUnit);
  const inputEl = document.getElementById('recipe-scale-input');
  const factorEl = document.getElementById('recipe-scale-factor');
  const resetEl = document.getElementById('recipe-scale-reset');
  const timerHintEl = document.getElementById('recipe-scale-timer-hint');
  const unitCheckEl = document.getElementById('recipe-scale-unit-check');
  const unitSwitchEl = root.querySelector('.recipe-scale__unit-switch');
  const showTimerHint = hasTimers(recipe.steps);

  let useLargeUnit = unitCheckEl?.checked ?? false;

  function syncUnitSwitchUi() {
    if (!unitSwitchEl) return;
    unitSwitchEl.classList.toggle('is-large', useLargeUnit);
  }

  function syncInputConstraints() {
    const step = stepBase(unitPair, anchor.step);
    const minBase = Math.max(step, anchor.baseValue * 0.1);
    inputEl.step = String(inputStep(unitPair, useLargeUnit, anchor.step));
    inputEl.min = String(displayValue(minBase, unitPair, useLargeUnit));
  }

  function applyBaseValue(baseValue, persist = true) {
    let nextBase = Number(baseValue);
    if (!Number.isFinite(nextBase) || nextBase <= 0) {
      nextBase = anchor.baseValue;
    }

    const factor = computeScaleFactorFromBase(anchor, nextBase);
    listEl.innerHTML = renderIngredientList(scaleIngredients(recipe.ingredients, factor));

    inputEl.value = formatInputValue(displayValue(nextBase, unitPair, useLargeUnit));
    syncInputConstraints();
    syncUnitSwitchUi();

    const factorLabel = formatScaleFactor(factor);
    if (factorLabel) {
      factorEl.textContent = factorLabel;
      factorEl.hidden = false;
      resetEl.hidden = false;
      if (timerHintEl) timerHintEl.hidden = !showTimerHint;
    } else {
      factorEl.hidden = true;
      resetEl.hidden = true;
      if (timerHintEl) timerHintEl.hidden = true;
    }

    if (persist) {
      writeSavedBaseValue(recipe.id, nextBase);
      writeSavedUseLargeUnit(recipe.id, useLargeUnit);
    }
  }

  syncUnitSwitchUi();
  syncInputConstraints();

  inputEl.addEventListener('change', () => {
    const base = baseValueFromInput(inputEl.value.replace(',', '.'), unitPair, useLargeUnit);
    applyBaseValue(base ?? anchor.baseValue);
  });

  inputEl.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      inputEl.blur();
    }
  });

  root.querySelectorAll('.recipe-scale__step').forEach(btn => {
    btn.addEventListener('click', () => {
      const delta = Number(btn.dataset.delta) || 0;
      const currentBase = baseValueFromInput(inputEl.value.replace(',', '.'), unitPair, useLargeUnit)
        ?? anchor.baseValue;
      applyBaseValue(currentBase + delta * stepBase(unitPair, anchor.step));
    });
  });

  unitCheckEl?.addEventListener('change', () => {
    const currentBase = baseValueFromInput(inputEl.value.replace(',', '.'), unitPair, useLargeUnit)
      ?? anchor.baseValue;
    useLargeUnit = unitCheckEl.checked;
    applyBaseValue(currentBase);
  });

  resetEl?.addEventListener('click', () => {
    clearSavedScale(recipe.id);
    useLargeUnit = false;
    if (unitCheckEl) unitCheckEl.checked = false;
    applyBaseValue(anchor.baseValue, false);
  });
}
