const accentMap = {
  gold:   { accent: '#C9A034', soft: '#C9A03433' },
  ember:  { accent: '#C15A1F', soft: '#C15A1F33' },
  pork:   { accent: '#C97C6B', soft: '#C97C6B33' },
  bird:   { accent: '#D6A24A', soft: '#D6A24A33' },
  sage:   { accent: '#7E9463', soft: '#7E946333' },
  walnut: { accent: '#A6763E', soft: '#A6763E33' },
};

function setAccent(key) {
  const root = document.documentElement;
  const a = accentMap[key] || accentMap.ember;
  root.style.setProperty('--accent', a.accent);
  root.style.setProperty('--accent-soft', a.soft);
}

export function initTabs() {
  const buttons = document.querySelectorAll('nav.tabs button');
  const panels = document.querySelectorAll('section.panel');

  function activateTab(tabId) {
    const btn = document.querySelector(`nav.tabs button[data-tab="${tabId}"]`);
    if (!btn) return;
    buttons.forEach(b => b.classList.remove('active'));
    panels.forEach(p => p.classList.remove('active'));
    btn.classList.add('active');
    document.getElementById(tabId).classList.add('active');
    setAccent(btn.dataset.accent);
  }

  buttons.forEach(btn => {
    btn.addEventListener('click', () => {
      activateTab(btn.dataset.tab);
      history.replaceState(null, '', `#${btn.dataset.tab}`);
    });
  });

  setAccent('gold');

  const applyHash = () => {
    const hash = window.location.hash.slice(1);
    if (hash) activateTab(hash);
  };

  window.addEventListener('hashchange', applyHash);
  applyHash();
}
