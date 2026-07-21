import { escapeHtml, safeHref, fetchJson } from './utils.js';

const SOURCE_LABELS = {
  video: '🎥 видео',
  article: '📄 статья',
};

function getRecipeId() {
  const params = new URLSearchParams(window.location.search);
  return (params.get('id') || '').trim();
}

function renderList(items, ordered) {
  if (!items || items.length === 0) return '';
  const tag = ordered ? 'ol' : 'ul';
  const lis = items.map(i => `<li>${escapeHtml(i)}</li>`).join('');
  return `<${tag} class="recipe-list">${lis}</${tag}>`;
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

function renderRecipe(recipe) {
  document.title = `${recipe.title} — sol-chef`;
  setOgMeta('og:title', `${recipe.title} — sol-chef`);
  setOgMeta('og:description', recipe.summary);

  document.getElementById('recipe-title').textContent = recipe.title;

  const badge = escapeHtml(SOURCE_LABELS[recipe.source_type] || '🔗 источник');
  const tags = (recipe.tags || []).map(t => `<span class="tag">${escapeHtml(t)}</span>`).join('');
  document.getElementById('recipe-meta-top').innerHTML = `
    <span class="src-badge">${badge}</span>
    ${tags}
  `;

  const sourceUrl = safeHref(recipe.source_url);
  const sourceName = escapeHtml(recipe.source_name || 'Открыть источник');
  let html = `<p class="recipe-lead">${escapeHtml(recipe.summary)}</p>`;

  if (recipe.ingredients?.length) {
    html += `<section class="recipe-section"><h2>Ингредиенты</h2>${renderList(recipe.ingredients, false)}</section>`;
  }
  if (recipe.steps?.length) {
    html += `<section class="recipe-section"><h2>Шаги</h2>${renderList(recipe.steps, true)}</section>`;
  }
  if (recipe.notes) {
    html += `<section class="recipe-section recipe-notes"><h2>Заметки</h2><p>${escapeHtml(recipe.notes)}</p></section>`;
  }

  html += `
    <div class="recipe-actions">
      <a class="btn-primary" href="${sourceUrl}" target="_blank" rel="noopener">${sourceName}</a>
      <button type="button" class="btn-secondary" id="copy-link">Скопировать ссылку</button>
    </div>`;

  document.getElementById('recipe-content').innerHTML = html;

  const sourceBar = document.getElementById('recipe-source-bar');
  if (sourceBar && sourceUrl && sourceUrl !== '#') {
    sourceBar.href = sourceUrl;
    sourceBar.hidden = false;
    sourceBar.textContent = recipe.source_type === 'video' ? 'Видео' : 'Статья';
  }

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
}

function showError(message) {
  document.getElementById('recipe-title').textContent = 'Рецепт не найден';
  document.getElementById('recipe-meta-top').innerHTML = '';
  document.getElementById('recipe-content').innerHTML = `
    <div class="empty-state">${escapeHtml(message)}</div>
    <p style="margin-top:16px"><a class="back-link" href="index.html#recipes">← К списку рецептов</a></p>`;
}

const id = getRecipeId();

const refLink = document.querySelector('[data-nav="reference"]');
if (refLink) {
  const refTab = localStorage.getItem('sol-chef-last-ref-tab') || 'grains';
  refLink.href = `index.html#${refTab}`;
}

if (!id) {
  showError('Не указан id рецепта. Пример: recipe.html?id=stejk-reverse-sear');
} else {
  fetchJson('data/recipes.json')
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
