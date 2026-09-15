import { escapeHtml, triedBadgeHtml, safeHref, sanitizeVariationHtml } from './utils.js';
import { renderIngredientsSection, wireIngredientsScale } from './recipe-scale.js';
import { spriteIconHtml } from './icons.js';
import { loadAllRecipes } from './recipe-data.js';
import { initCookMode, renderPrepSection, renderStepsWithTimers } from './cook-mode.js';
import { startAlertPoller } from './notifications.js';
import { normalizePrep, normalizeSteps } from './step-utils.js';

let cookModeController = null;

function getRecipeId() {
  const params = new URLSearchParams(window.location.search);
  return (params.get('id') || '').trim();
}

function setOgMeta(property, content) {
  let el = document.querySelector(`meta[property="${property}"]`);
  if (!el) {
    el = document.createElement('meta');
    el.setAttribute('property', property);
    document.head.appendChild(el);
  }
  el.setAttribute('content', content);
}

function renderVariationsSection(variations) {
  if (!Array.isArray(variations) || variations.length === 0) return '';

  const count = variations.length;
  const countLabel = count === 1 ? '1 вариант' : count < 5 ? `${count} варианта` : `${count} вариантов`;
  const items = variations.map(v => `
    <article class="recipe-variation">
      <h3 class="recipe-variation__title">${escapeHtml(v.title)}</h3>
      <div class="recipe-variation__text">${sanitizeVariationHtml(v.text)}</div>
    </article>`).join('');

  return `
    <details class="recipe-variations acc-item">
      <summary>
        <span class="recipe-variations__heading">Вариации</span>
        <span class="recipe-variations__count">${countLabel}</span>
        <span class="chev">${spriteIconHtml('chevron-down', 'ui-icon ui-icon--chev')}</span>
      </summary>
      <div class="recipe-variations__body">${items}</div>
    </details>`;
}

function renderSourceLine(recipe) {
  const rawUrl = (recipe.source_url || '').trim();
  const name = (recipe.source_name || '').trim();
  if (!rawUrl && !name) return '';

  let href = '#';
  try {
    const u = new URL(rawUrl);
    if (u.protocol === 'http:' || u.protocol === 'https:') href = u.href;
  } catch (_) { /* invalid URL */ }

  const isExternal = href !== '#' && !href.includes('sol-chef.ru');
  const label = escapeHtml(name || 'Источник');

  if (isExternal) {
    return `<p class="recipe-source">Источник: <a class="recipe-source__link" href="${safeHref(rawUrl)}" target="_blank" rel="noopener">${label}</a></p>`;
  }
  if (name) {
    return `<p class="recipe-source">${label}</p>`;
  }
  return '';
}

function renderRecipe(recipe) {
  document.title = `${recipe.title} — sol-chef`;
  setOgMeta('og:title', `${recipe.title} — sol-chef`);
  setOgMeta('og:description', recipe.summary);

  document.getElementById('recipe-title').innerHTML =
    `${escapeHtml(recipe.title)}${triedBadgeHtml(recipe.tried)}`;

  const tags = (recipe.tags || []).map(t => `<span class="tag">${escapeHtml(t)}</span>`).join('');
  document.getElementById('recipe-meta-top').innerHTML = `
    ${tags}
  `;

  const hasSteps = normalizeSteps(recipe.steps).length > 0;
  const hasPrep = normalizePrep(recipe.prep).length > 0;

  let html = `<p class="recipe-lead">${escapeHtml(recipe.summary)}</p>`;
  html += renderSourceLine(recipe);

  if (hasPrep) {
    html += renderPrepSection(recipe.prep);
  }

  if (recipe.ingredients?.length) {
    html += renderIngredientsSection(recipe);
  }
  if (recipe.steps?.length) {
    html += `<section class="recipe-section"><h2>Шаги</h2>${renderStepsWithTimers(recipe.steps)}</section>`;
  }
  if (recipe.variations?.length) {
    html += renderVariationsSection(recipe.variations);
  }
  if (recipe.notes) {
    html += `<section class="recipe-section recipe-notes"><h2>Заметки</h2><p>${escapeHtml(recipe.notes)}</p></section>`;
  }

  html += `<div class="recipe-actions">`;
  if (hasSteps) {
    html += `<button type="button" class="btn-primary btn-cook" id="start-cook-mode">Режим готовки</button>`;
  }
  html += `<button type="button" class="btn-secondary" id="copy-link">Скопировать ссылку</button>`;
  html += `</div>`;

  document.getElementById('recipe-content').innerHTML = html;

  wireIngredientsScale(recipe);

  document.getElementById('copy-link')?.addEventListener('click', async () => {
    try {
      await navigator.clipboard.writeText(window.location.href);
      const btn = document.getElementById('copy-link');
      btn.textContent = 'Скопировано';
      setTimeout(() => { btn.textContent = 'Скопировать ссылку'; }, 2000);
    } catch (_) {
      prompt('Скопируйте ссылку:', window.location.href);
    }
  });

  const cookRoot = document.getElementById('cook-mode-root');
  if (hasSteps && cookRoot) {
    cookModeController = initCookMode(recipe, cookRoot);
    const openCook = () => cookModeController?.open();
    document.getElementById('start-cook-mode')?.addEventListener('click', openCook);
    const barBtn = document.getElementById('start-cook-mode-bar');
    if (barBtn) {
      barBtn.hidden = false;
      barBtn.addEventListener('click', openCook);
    }
  }
}

function showError(message) {
  document.getElementById('recipe-title').textContent = 'Рецепт не найден';
  document.getElementById('recipe-meta-top').innerHTML = '';
  document.getElementById('recipe-content').innerHTML = `
    <div class="empty-state">${escapeHtml(message)}</div>
    <p style="margin-top:16px"><a class="back-link" href="index.html#recipes">← К списку рецептов</a></p>`;
}

startAlertPoller((alert) => {
  if (document.hidden) return;
  const toast = document.getElementById('cook-mode-toast');
  if (toast) {
    toast.textContent = `${alert.title}: ${alert.body}`;
    toast.hidden = false;
    setTimeout(() => { toast.hidden = true; }, 6000);
  }
});

const id = getRecipeId();

const refLink = document.querySelector('[data-nav="reference"]');
if (refLink) {
  const refTab = localStorage.getItem('sol-chef-last-ref-tab') || 'grains';
  refLink.href = `index.html#${refTab}`;
}

if (!id) {
  showError('Не указан id рецепта. Пример: recipe.html?id=stejk-reverse-sear');
} else {
  loadAllRecipes()
    .then(list => {
      if (!Array.isArray(list)) throw new Error('invalid data');
      const recipe = list.find(r => r.id === id);
      if (!recipe) showError(`Рецепт «${id}» не найден в базе.`);
      else renderRecipe(recipe);
    })
    .catch(() => {
      showError('Не удалось загрузить данные. Откройте сайт через GitHub Pages или локальный сервер.');
    });
}
