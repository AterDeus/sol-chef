import { escapeHtml, escapeAttr, safeHref, triedBadgeHtml } from './utils.js';
import { loadAllRecipes } from './recipe-data.js';

const SOURCE_LABELS = {
  video: '🎥 видео',
  article: '📄 статья',
};

const PRIMARY_TAG_COUNT = 6;

let allRecipes = [];
let activeTags = new Set();
let tagsExpanded = false;

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
  const triedMark = triedBadgeHtml(r.tried);
  return `
    <div class="recipe-card">
      <h3 class="recipe-card__title"><a href="${detailLink}">${title}</a>${triedMark}</h3>
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

function collectTagCounts(recipes) {
  const tagCounts = new Map();
  recipes.forEach(r => {
    (r.tags || []).forEach(t => {
      tagCounts.set(t, (tagCounts.get(t) || 0) + 1);
    });
  });
  return tagCounts;
}

function sortTagsByPopularity(tagCounts) {
  return [...tagCounts.entries()].sort((a, b) => {
    if (b[1] !== a[1]) return b[1] - a[1];
    return a[0].localeCompare(b[0], 'ru');
  });
}

function renderTagButton(tag, count) {
  const active = activeTags.has(tag) ? ' active' : '';
  return `<button type="button" class="tag-filter${active}" data-tag="${escapeAttr(tag)}">${escapeHtml(tag)} <span class="tag-count">${count}</span></button>`;
}

function bindTagButtons(container) {
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

function setTagsExpanded(expanded) {
  tagsExpanded = expanded;
  const wrap = document.getElementById('recipe-tag-filters-wrap');
  const toggle = document.getElementById('tag-filters-toggle');
  const extraWrap = document.getElementById('recipe-tag-filters-extra-wrap');
  if (!wrap || !toggle || !extraWrap) return;
  wrap.classList.toggle('is-expanded', expanded);
  extraWrap.classList.toggle('is-open', expanded);
  toggle.setAttribute('aria-expanded', expanded ? 'true' : 'false');
  toggle.setAttribute('aria-label', expanded ? 'Скрыть теги' : 'Показать все теги');
}

function renderTagFilters(recipes) {
  const primaryEl = document.getElementById('recipe-tag-filters-primary');
  const extraEl = document.getElementById('recipe-tag-filters-extra');
  const toggle = document.getElementById('tag-filters-toggle');
  if (!primaryEl || !extraEl) return;

  const tagCounts = collectTagCounts(recipes);
  const sorted = sortTagsByPopularity(tagCounts);

  if (sorted.length === 0) {
    primaryEl.innerHTML = '';
    extraEl.innerHTML = '';
    if (toggle) toggle.hidden = true;
    setTagsExpanded(false);
    return;
  }

  const primaryTags = sorted.slice(0, PRIMARY_TAG_COUNT);
  const primarySet = new Set(primaryTags.map(([tag]) => tag));
  const extraTags = sorted.filter(([tag]) => !primarySet.has(tag));

  for (const [tag] of extraTags) {
    if (activeTags.has(tag)) {
      tagsExpanded = true;
      break;
    }
  }

  primaryEl.innerHTML = primaryTags
    .map(([tag, count]) => renderTagButton(tag, count))
    .join('');

  extraEl.innerHTML = extraTags
    .map(([tag, count]) => renderTagButton(tag, count))
    .join('');

  if (toggle) {
    toggle.hidden = extraTags.length === 0;
  }

  setTagsExpanded(tagsExpanded && extraTags.length > 0);
  bindTagButtons(primaryEl);
  bindTagButtons(extraEl);
}

function applyRecipeFilters() {
  const query = document.getElementById('recipe-search')?.value || '';
  const filtered = filterRecipes(allRecipes, query, activeTags);
  renderRecipes(filtered, allRecipes.length);
}

function initRecipeToolbar() {
  const search = document.getElementById('recipe-search');
  if (search) search.addEventListener('input', applyRecipeFilters);

  const toggle = document.getElementById('tag-filters-toggle');
  toggle?.addEventListener('click', () => {
    setTagsExpanded(!tagsExpanded);
  });
}

export function loadRecipes() {
  loadAllRecipes()
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
