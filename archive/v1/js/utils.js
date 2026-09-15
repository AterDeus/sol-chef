import { spriteIconHtml } from './icons.js';

export { spriteIconHtml } from './icons.js';

export function escapeHtml(text) {
  if (text == null) return '';
  return String(text)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

export function escapeAttr(text) {
  return String(text)
    .replace(/&/g, '&amp;')
    .replace(/"/g, '&quot;')
    .replace(/</g, '&lt;');
}

const VARIATION_HTML_TAGS = new Set([
  'P', 'BR', 'STRONG', 'B', 'EM', 'I', 'UL', 'OL', 'LI',
]);

function sanitizeVariationElement(el) {
  [...el.childNodes].forEach(child => {
    if (child.nodeType === Node.TEXT_NODE) return;
    if (child.nodeType !== Node.ELEMENT_NODE) {
      child.remove();
      return;
    }
    if (!VARIATION_HTML_TAGS.has(child.tagName)) {
      child.replaceWith(el.ownerDocument.createTextNode(child.textContent || ''));
      return;
    }
    [...child.attributes].forEach(attr => child.removeAttribute(attr.name));
    if (child.tagName !== 'BR') sanitizeVariationElement(child);
  });
}

/** Безопасный HTML для текста вариаций: только базовая разметка без атрибутов. */
export function sanitizeVariationHtml(raw) {
  if (raw == null) return '';
  const str = String(raw).trim();
  if (!str) return '';

  if (typeof DOMParser === 'undefined') {
    return escapeHtml(str);
  }

  const doc = new DOMParser().parseFromString(`<div>${str}</div>`, 'text/html');
  const root = doc.body.firstElementChild;
  if (!root) return escapeHtml(str);

  sanitizeVariationElement(root);
  const html = root.innerHTML.trim();
  return html || escapeHtml(str);
}

export function safeHref(url) {
  try {
    const u = new URL(url);
    if (u.protocol === 'http:' || u.protocol === 'https:') return escapeHtml(url);
  } catch (_) { /* invalid URL */ }
  return '#';
}

export function fetchJson(url) {
  return fetch(url).then(res => {
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return res.json();
  });
}

export function setMeta(name, content) {
  if (!content) return;
  let el = document.querySelector(`meta[name="${name}"]`);
  if (!el) {
    el = document.createElement('meta');
    el.setAttribute('name', name);
    document.head.appendChild(el);
  }
  el.setAttribute('content', content);
}

export function setOg(property, content) {
  if (!content) return;
  let el = document.querySelector(`meta[property="${property}"]`);
  if (!el) {
    el = document.createElement('meta');
    el.setAttribute('property', property);
    document.head.appendChild(el);
  }
  el.setAttribute('content', content);
}

export function triedBadgeHtml(tried) {
  if (!tried) return '';
  return `<span class="tried-badge" title="Опробовано" aria-label="Опробовано">${spriteIconHtml('check', 'ui-icon ui-icon--tried')}</span>`;
}

export function renderIntro(introEl, data) {
  if (!introEl || !data) return;
  if (data.intro_lead && data.intro) {
    introEl.innerHTML = `<b>${escapeHtml(data.intro_lead)}</b> ${escapeHtml(data.intro)}`;
  } else if (data.intro) {
    introEl.textContent = data.intro;
  }
}
