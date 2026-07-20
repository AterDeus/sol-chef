import { escapeHtml, fetchJson, renderIntro } from './utils.js';

function renderMeatCard(card) {
  return `
    <div class="card">
      <h3>${escapeHtml(card.title)}</h3>
      <div class="readout"><span class="lbl">${escapeHtml(card.readout_label)}</span>${escapeHtml(card.readout_value)}</div>
      <p>${escapeHtml(card.text)}</p>
      <p class="pitfall"><b>Ошибка:</b> ${escapeHtml(card.pitfall)}</p>
    </div>`;
}

function renderMeatPanel(data, introId, contentId) {
  const introEl = document.getElementById(introId);
  const container = document.getElementById(contentId);
  if (!container) return;

  if (!data || !Array.isArray(data.methods)) {
    container.innerHTML = '<div class="empty-state">Не удалось загрузить данные.</div>';
    return;
  }

  renderIntro(introEl, data);
  container.innerHTML = data.methods.map(method => `
    <div class="method-block">
      <div class="method-head"><h2>${escapeHtml(method.name)}</h2><span class="sub">${escapeHtml(method.sub)}</span></div>
      <div class="cards">${(method.cards || []).map(renderMeatCard).join('')}</div>
    </div>`).join('');
}

function renderGrains(data) {
  const introEl = document.getElementById('grains-intro');
  const container = document.getElementById('grains-content');
  if (!container) return;

  if (!data || !Array.isArray(data.rows) || data.rows.length === 0) {
    container.innerHTML = '<div class="empty-state">Не удалось загрузить крупы.</div>';
    return;
  }

  renderIntro(introEl, data);

  const tableRows = data.rows.map(row => `
    <tr>
      <td class="name">${escapeHtml(row.name)}</td>
      <td class="note">${escapeHtml(row.wash)}</td>
      <td class="ratio">${escapeHtml(row.ratio)}</td>
      <td class="note">${escapeHtml(row.time)}</td>
      <td class="note">${escapeHtml(row.note)}</td>
    </tr>`).join('');

  const cardRows = data.rows.map(row => `
    <article class="grain-card">
      <h3 class="grain-card-name">${escapeHtml(row.name)}</h3>
      <dl class="grain-card-meta">
        <div><dt>Промывка</dt><dd>${escapeHtml(row.wash)}</dd></div>
        <div><dt>Вода : крупа</dt><dd class="ratio">${escapeHtml(row.ratio)}</dd></div>
        <div><dt>Время</dt><dd>${escapeHtml(row.time)}</dd></div>
      </dl>
      <p class="grain-card-note">${escapeHtml(row.note)}</p>
    </article>`).join('');

  container.innerHTML = `
    <table class="grains grains-table">
      <tr>
        <th>Крупа</th>
        <th>Промывка</th>
        <th>Вода : крупа</th>
        <th>Время</th>
        <th>Нюанс</th>
      </tr>
      ${tableRows}
    </table>
    <div class="grain-cards">${cardRows}</div>`;
}

const MEAT_PANELS = [
  ['data/meat-beef.json', 'beef-intro', 'beef-content'],
  ['data/meat-pork.json', 'pork-intro', 'pork-content'],
  ['data/meat-poultry.json', 'bird-intro', 'bird-content'],
];

export function loadReferenceData() {
  fetchJson('data/grains.json')
    .then(renderGrains)
    .catch(() => {
      const el = document.getElementById('grains-content');
      if (el) el.innerHTML = '<div class="empty-state">Не удалось загрузить крупы.</div>';
    });

  MEAT_PANELS.forEach(([url, introId, contentId]) => {
    fetchJson(url)
      .then(data => renderMeatPanel(data, introId, contentId))
      .catch(() => {
        const el = document.getElementById(contentId);
        if (el) el.innerHTML = '<div class="empty-state">Не удалось загрузить раздел.</div>';
      });
  });
}
