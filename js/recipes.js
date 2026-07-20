import { escapeHtml, escapeAttr, safeHref, fetchJson } from './utils.js';

const SOURCE_LABELS = {
  video: '🎥 видео',
  article: '📄 статья',
};

let allRecipes = [];
let activeTags = new Set();

function isValidRecipe(r) {
  return Boolean(
    r &&
    r.id &&
    r.title &&
    r.source_url &&
    r.summary &&
    Array.isArray(r.tags) &&
    r.tags.length > 0
  );
}

function sortRecipes(list) {
  return [...list].sort((a, b) => {
    if (a.added && b.added) return b.added.localeCompare(a.added);
    if (a.added) return -1;
    if (b.added) return 1;
    return (a.title || '').localeCompare(b.title || '', 'ru');
  });
}

function prepareRecipes(raw) {
  if (!Array.isArray(raw)) return [];
  const valid = raw.filter(isValidRecipe);
  if (valid.length < raw.length) {
    console.warn(`Пропущено рецептов с неполными данными: ${raw.length - valid.length}`);
  }
  return sortRecipes(valid);
}

function recipeSearchText(r) {
  const parts = [
    r.title,
    r.summary,
    r.source_name,
    r.category,
    ...(r.tags || []),
    ...(r.ingredients || []),
    ...(r.steps || []),
    r.notes,
  ];
  return parts.filter(Boolean).join(' ').toLowerCase();
}

function filterRecipes(list, query, tags) {
  const q = (query || '').trim().toLowerCase();
  return list.filter(r => {
    const tagMatch = tags.size === 0 || (r.tags || []).some(t => tags.has(t));
    if (!tagMatch) return false;
    if (!q) return true;
    return recipeSearchText(r).includes(q);
  });
}

function renderRecipeCard(r) {
  const title = escapeHtml(r.title);
  const url = safeHref(r.source_url);
  const summary = escapeHtml(r.summary);
  const sourceName = escapeHtml(r.source_name || '');
  const badge = escapeHtml(SOURCE_LABELS[r.source_type] || '🔗 источник');
  const tags = (r.tags || []).map(t => `<span class="tag">${escapeHtml(t)}</span>`).join('');
  const detailLink = `recipe.html?id=${encodeURIComponent(r.id)}`;
  return `
    <div class="recipe-card">
      <h3><a href="${detailLink}">${title}</a></h3>
      <div class="recipe-meta">
        <span class="src-badge">${badge}</span>
        ${tags}
      </div>
      <p class="summary">${summary}</p>
      <div class="recipe-card-footer">
        <div class="source-name">${sourceName}</div>
        <a class="recipe-source-link" href="${url}" target="_blank" rel="noopener">Источник</a>
      </div>
    </div>`;
}

function renderRecipes(list, total) {
  const container = document.getElementById('recipe-list');
  const countEl = document.getElementById('recipe-count');
  const totalCount = total ?? list.length;

  if (countEl) {
    if (totalCount === 0) {
      countEl.textContent = '';
    } else if (list.length === totalCount) {
      countEl.textContent = `Всего рецептов: ${totalCount}`;
    } else {
      countEl.textContent = `Показано ${list.length} из ${totalCount}`;
    }
  }

  if (!list || list.length === 0) {
    const query = document.getElementById('recipe-search')?.value.trim();
    const hasFilters = query || activeTags.size > 0;
    const msg = hasFilters
      ? 'Ничего не найдено — попробуйте другой запрос или снимите фильтры.'
      : 'Рецептов пока нет — первый появится здесь.';
    container.innerHTML = `<div class="empty-state">${msg}</div>`;
    return;
  }
  container.innerHTML = list.map(renderRecipeCard).join('');
}

function renderTagFilters(recipes) {
  const container = document.getElementById('recipe-tag-filters');
  if (!container) return;

  const tagCounts = new Map();
  recipes.forEach(r => {
    (r.tags || []).forEach(t => {
      tagCounts.set(t, (tagCounts.get(t) || 0) + 1);
    });
  });

  const tags = [...tagCounts.keys()].sort((a, b) => a.localeCompare(b, 'ru'));
  if (tags.length === 0) {
    container.innerHTML = '';
    return;
  }

  container.innerHTML = tags.map(tag => {
    const active = activeTags.has(tag) ? ' active' : '';
    const count = tagCounts.get(tag);
    return `<button type="button" class="tag-filter${active}" data-tag="${escapeAttr(tag)}">${escapeHtml(tag)} <span class="tag-count">${count}</span></button>`;
  }).join('');

  container.querySelectorAll('.tag-filter').forEach(btn => {
    btn.addEventListener('click', () => {
      const tag = btn.dataset.tag;
      if (activeTags.has(tag)) activeTags.delete(tag);
      else activeTags.add(tag);
      applyRecipeFilters();
      renderTagFilters(allRecipes);
    });
  });
}

function applyRecipeFilters() {
  const query = document.getElementById('recipe-search')?.value || '';
  const filtered = filterRecipes(allRecipes, query, activeTags);
  renderRecipes(filtered, allRecipes.length);
}

function initRecipeToolbar() {
  const search = document.getElementById('recipe-search');
  if (search) search.addEventListener('input', applyRecipeFilters);
}

export function loadRecipes() {
  fetchJson('data/recipes.json')
    .then(prepareRecipes)
    .then(recipes => {
      allRecipes = recipes;
      initRecipeToolbar();
      renderTagFilters(allRecipes);
      applyRecipeFilters();
    })
    .catch(() => {
      const el = document.getElementById('recipe-list');
      if (el) {
        el.innerHTML = '<div class="empty-state">Не получилось загрузить рецепты. Если открываете файл локально двойным кликом — браузер блокирует загрузку JSON. Работает после публикации на GitHub Pages (или через локальный сервер).</div>';
      }
    });
}
