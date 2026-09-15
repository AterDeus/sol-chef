const STORAGE_TAB = 'sol-chef-last-tab';
const STORAGE_REF = 'sol-chef-last-ref-tab';
const DEFAULT_TAB = 'recipes';

const REF_TABS = new Set(['grains', 'beef', 'pork', 'bird']);
const ALL_TABS = new Set([...REF_TABS, 'tips', 'recipes']);

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
  const a = accentMap[key] || accentMap.walnut;
  root.style.setProperty('--accent', a.accent);
  root.style.setProperty('--accent-soft', a.soft);
}

function getSection(tabId) {
  if (REF_TABS.has(tabId)) return 'reference';
  if (tabId === 'recipes') return 'recipes';
  if (tabId === 'tips') return 'tips';
  return 'recipes';
}

function normalizeTabId(tabId) {
  return ALL_TABS.has(tabId) ? tabId : DEFAULT_TAB;
}

function scrollActiveIntoView(container) {
  if (!container || container.hidden) return;
  const active = container.querySelector('[data-tab].active, [data-section].active');
  active?.scrollIntoView({ inline: 'center', block: 'nearest', behavior: 'smooth' });
}

export function initTabs() {
  const panels = document.querySelectorAll('section.panel');
  const refSubnavWrap = document.getElementById('ref-subnav-wrap');
  const tabButtons = document.querySelectorAll('[data-tab]');
  const sectionButtons = document.querySelectorAll('.bottom-nav [data-section]');
  const desktopNav = document.querySelector('.tabs--desktop');
  const refSubnav = document.getElementById('ref-subnav');
  const tabIndicator = document.getElementById('tabs-indicator');

  function isDesktopTabs() {
    return window.matchMedia('(min-width: 769px)').matches;
  }

  function updateTabIndicator(tabId, { animate = true } = {}) {
    if (!desktopNav || !tabIndicator) return;

    if (!isDesktopTabs()) {
      tabIndicator.hidden = true;
      return;
    }

    const btn = desktopNav.querySelector(`button[data-tab="${tabId}"]`);
    if (!btn) {
      tabIndicator.hidden = true;
      return;
    }

    tabIndicator.hidden = false;

    if (!animate) {
      tabIndicator.classList.add('is-static');
    }

    tabIndicator.style.left = `${btn.offsetLeft}px`;
    tabIndicator.style.width = `${btn.offsetWidth}px`;

    if (!animate) {
      tabIndicator.offsetHeight;
      tabIndicator.classList.remove('is-static');
    }
  }

  function updateMobileChrome(section) {
    document.body.classList.toggle('ref-subnav-visible', section === 'reference');
    if (refSubnavWrap) {
      refSubnavWrap.hidden = section !== 'reference';
    }
    sectionButtons.forEach(btn => {
      btn.classList.toggle('active', btn.dataset.section === section);
    });
  }

  function activateTab(tabId, { persist = true, updateHash = true, animateIndicator = true } = {}) {
    const id = normalizeTabId(tabId);
    const panel = document.getElementById(id);
    if (!panel) return;

    tabButtons.forEach(btn => {
      btn.classList.toggle('active', btn.dataset.tab === id);
    });

    panels.forEach(p => p.classList.remove('active'));
    panel.classList.add('active');

    const accentBtn = document.querySelector(`[data-tab="${id}"]`);
    setAccent(accentBtn?.dataset.accent || 'walnut');
    updateTabIndicator(id, { animate: animateIndicator });

    const section = getSection(id);
    updateMobileChrome(section);

    if (persist) {
      localStorage.setItem(STORAGE_TAB, id);
      if (REF_TABS.has(id)) {
        localStorage.setItem(STORAGE_REF, id);
      }
    }

    if (updateHash) {
      history.replaceState(null, '', `#${id}`);
    }

    requestAnimationFrame(() => {
      scrollActiveIntoView(desktopNav);
      scrollActiveIntoView(refSubnav);
    });

    if (window.matchMedia('(max-width: 768px)').matches) {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  }

  tabButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      activateTab(btn.dataset.tab);
    });
  });

  sectionButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      if (btn.dataset.tab) {
        activateTab(btn.dataset.tab);
        return;
      }
      const refTab = localStorage.getItem(STORAGE_REF) || 'grains';
      activateTab(refTab);
    });
  });

  function resolveInitialTab() {
    const hash = window.location.hash.slice(1);
    if (hash && ALL_TABS.has(hash)) return hash;
    const stored = localStorage.getItem(STORAGE_TAB);
    if (stored && ALL_TABS.has(stored)) return stored;
    return DEFAULT_TAB;
  }

  window.addEventListener('hashchange', () => {
    const hash = window.location.hash.slice(1);
    if (hash && ALL_TABS.has(hash)) {
      activateTab(hash, { persist: true, updateHash: false });
    }
  });

  window.addEventListener('resize', () => {
    const active = desktopNav?.querySelector('button[data-tab].active');
    if (active) {
      updateTabIndicator(active.dataset.tab, { animate: false });
    }
  });

  if (desktopNav && tabIndicator && typeof ResizeObserver !== 'undefined') {
    const ro = new ResizeObserver(() => {
      const active = desktopNav.querySelector('button[data-tab].active');
      if (active) {
        updateTabIndicator(active.dataset.tab, { animate: false });
      }
    });
    ro.observe(desktopNav);
    desktopNav.querySelectorAll('button[data-tab]').forEach(btn => ro.observe(btn));
  }

  document.fonts?.ready?.then(() => {
    const active = desktopNav?.querySelector('button[data-tab].active');
    if (active) {
      updateTabIndicator(active.dataset.tab, { animate: false });
    }
  });

  activateTab(resolveInitialTab(), {
    updateHash: !window.location.hash,
    animateIndicator: false,
  });
}
