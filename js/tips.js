import { escapeHtml, fetchJson } from './utils.js';

function renderTips(data) {
  const container = document.getElementById('tips-list');
  const introEl = document.getElementById('tips-intro');
  if (!container) return;

  if (!data || !Array.isArray(data.sections) || data.sections.length === 0) {
    container.innerHTML = '<div class="empty-state">Советы не загрузились.</div>';
    return;
  }

  if (introEl && data.intro) {
    introEl.innerHTML = `<b>100 приёмов из видео Энди Кукса</b>, ${escapeHtml(data.intro)}`;
  }

  container.innerHTML = data.sections.map(section => {
    const items = (section.items || []).map(item => `<li>${escapeHtml(item)}</li>`).join('');
    return `
      <details class="acc-item">
        <summary><span class="num">${escapeHtml(section.id)}</span> ${escapeHtml(section.title)}<span class="chev">▾</span></summary>
        <div class="acc-body"><ul>${items}</ul></div>
      </details>`;
  }).join('');
}

export function loadTips() {
  fetchJson('data/tips.json')
    .then(renderTips)
    .catch(() => {
      const container = document.getElementById('tips-list');
      if (container) {
        container.innerHTML = '<div class="empty-state">Не получилось загрузить советы.</div>';
      }
    });
}
