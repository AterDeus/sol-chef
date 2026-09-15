const STORAGE_KEY = 'sol-chef-scheduled-alerts';
const POLL_MS = 15000;

let pollTimer = null;

function loadAlerts() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    const list = raw ? JSON.parse(raw) : [];
    return Array.isArray(list) ? list : [];
  } catch {
    return [];
  }
}

function saveAlerts(list) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(list));
}

function alertId(recipeId, kind, extra) {
  return `${recipeId}:${kind}:${extra}`;
}

export async function requestNotificationPermission() {
  if (!('Notification' in window)) return 'unsupported';
  if (Notification.permission === 'granted') return 'granted';
  if (Notification.permission === 'denied') return 'denied';
  return Notification.requestPermission();
}

export function canNotify() {
  return 'Notification' in window && Notification.permission === 'granted';
}

function showBrowserNotification(title, body, tag) {
  if (!canNotify()) return false;
  try {
    const n = new Notification(title, {
      body,
      tag: tag || title,
      icon: 'assets/icon-192.png',
      badge: 'assets/icon-192.png',
    });
    n.onclick = () => {
      window.focus();
      n.close();
    };
    return true;
  } catch {
    return false;
  }
}

export function scheduleAlert({ id, recipeId, recipeTitle, type, fireAt, title, body }) {
  const list = loadAlerts();
  const entry = {
    id,
    recipeId,
    recipeTitle,
    type,
    fireAt,
    title,
    body,
    fired: false,
    created: Date.now(),
  };
  const idx = list.findIndex(a => a.id === id);
  if (idx >= 0) list[idx] = entry;
  else list.push(entry);
  saveAlerts(list);
  return entry;
}

export function cancelAlertsForRecipe(recipeId) {
  const list = loadAlerts().filter(a => a.recipeId !== recipeId);
  saveAlerts(list);
}

export function cancelAlert(id) {
  const list = loadAlerts().filter(a => a.id !== id);
  saveAlerts(list);
}

export function getAlertsForRecipe(recipeId) {
  return loadAlerts().filter(a => a.recipeId === recipeId && !a.fired);
}

export function processDueAlerts(onInApp) {
  const now = Date.now();
  const list = loadAlerts();
  let changed = false;

  for (const alert of list) {
    if (alert.fired || alert.fireAt > now) continue;
    alert.fired = true;
    changed = true;

    const shown = showBrowserNotification(alert.title, alert.body, alert.id);
    if (onInApp) {
      onInApp(alert, shown);
    } else if (!shown) {
      console.info('[sol-chef]', alert.title, alert.body);
    }
  }

  if (changed) {
    saveAlerts(list.filter(a => !a.fired || a.fireAt > now - 86400000));
  }
}

export function schedulePrepAlerts(recipe, cookStartMs) {
  if (!recipe.prep?.length) return [];

  cancelAlertsForRecipe(recipe.id);
  const scheduled = [];

  for (let i = 0; i < recipe.prep.length; i++) {
    const item = recipe.prep[i];
    const beforeMin = (Number(item.before_min) || 0) + (Number(item.before_hours) || 0) * 60;
    if (!item.text || beforeMin <= 0) continue;

    const fireAt = cookStartMs - beforeMin * 60 * 1000;
    const id = alertId(recipe.id, 'prep', i);

    scheduled.push(scheduleAlert({
      id,
      recipeId: recipe.id,
      recipeTitle: recipe.title,
      type: 'prep',
      fireAt,
      title: `Подготовка: ${recipe.title}`,
      body: item.text,
    }));
  }

  return scheduled;
}

export function scheduleTimerAlert(recipeId, recipeTitle, timerId, fireAt, label) {
  return scheduleAlert({
    id: alertId(recipeId, 'timer', timerId),
    recipeId,
    recipeTitle,
    type: 'timer',
    fireAt,
    title: label ? `Таймер: ${label}` : 'Таймер готов',
    body: recipeTitle,
  });
}

export function cancelTimerAlert(recipeId, timerId) {
  cancelAlert(alertId(recipeId, 'timer', timerId));
}

export function startAlertPoller(onInApp) {
  if (pollTimer) return;
  processDueAlerts(onInApp);
  pollTimer = setInterval(() => processDueAlerts(onInApp), POLL_MS);
  document.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'visible') processDueAlerts(onInApp);
  });
}

export function buildPrepAlertId(recipeId, index) {
  return alertId(recipeId, 'prep', index);
}
