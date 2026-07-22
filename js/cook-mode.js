import { escapeHtml } from './utils.js';
import { spriteIconHtml } from './icons.js';
import {
  normalizeSteps,
  normalizePrep,
  formatDuration,
  formatDurationShort,
  prepFireTime,
  prepIconHtml,
  formatDateTime,
  formatRelativeToNow,
} from './step-utils.js';
import {
  requestNotificationPermission,
  canNotify,
  schedulePrepAlerts,
  scheduleTimerAlert,
  cancelTimerAlert,
  cancelAlertsForRecipe,
  getAlertsForRecipe,
  processDueAlerts,
} from './notifications.js';

const PREP_TYPE_LABELS = {
  thaw: 'Разморозка',
  fridge: 'Холодильник',
  room_temp: 'Комнат. темп.',
  marinate: 'Маринад',
  soak: 'Замачивание',
  custom: 'Подготовка',
};

export function initCookMode(recipe, rootEl) {
  if (!rootEl || !recipe.steps?.length) return null;

  const steps = normalizeSteps(recipe.steps);
  const prep = normalizePrep(recipe.prep);
  if (!steps.length) return null;

  const state = {
    phase: 'setup',
    cookStartMs: Date.now(),
    stepIndex: 0,
    completed: new Set(),
    wakeLock: null,
    timers: new Map(),
    timerIntervals: new Map(),
    timerDurations: new Map(),
  };

  rootEl.innerHTML = '';

  const shell = document.createElement('div');
  shell.className = 'cook-mode';
  shell.setAttribute('role', 'dialog');
  shell.setAttribute('aria-modal', 'true');
  shell.setAttribute('aria-label', `Режим готовки: ${recipe.title}`);

  shell.innerHTML = `
    <header class="cook-mode__header">
      <button type="button" class="cook-mode__close" aria-label="Закрыть режим готовки">${spriteIconHtml('x', 'ui-icon ui-icon--cook-ctrl')}</button>
      <div class="cook-mode__header-text">
        <div class="cook-mode__eyebrow">Режим готовки</div>
        <div class="cook-mode__title">${escapeHtml(recipe.title)}</div>
      </div>
      <button type="button" class="cook-mode__wake" aria-pressed="false" title="Не гасить экран">${spriteIconHtml('sun', 'ui-icon ui-icon--cook-ctrl')}</button>
    </header>
    <div class="cook-mode__body" id="cook-mode-body"></div>
    <div class="cook-mode__toast" id="cook-mode-toast" hidden></div>
  `;

  const bodyEl = shell.querySelector('#cook-mode-body');
  const toastEl = shell.querySelector('#cook-mode-toast');
  let toastTimer = null;

  function showToast(message, durationMs = 4000) {
    toastEl.textContent = message;
    toastEl.hidden = false;
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => { toastEl.hidden = true; }, durationMs);
  }

  function onInAppAlert(alert) {
    showToast(`${alert.title}: ${alert.body}`, 6000);
    if (navigator.vibrate) navigator.vibrate([200, 100, 200]);
  }

  processDueAlerts(onInAppAlert);

  function renderSetup() {
    state.phase = 'setup';
    const now = new Date();
    const defaultLocal = new Date(now.getTime() + 3600000);
    const localValue = toDatetimeLocal(defaultLocal);

    let prepHtml = '';
    if (prep.length) {
      const rows = prep.map(p => {
        const fireMs = prepFireTime(state.cookStartMs, p.before_min);
        return `
          <li class="cook-prep-item" data-before="${p.before_min}">
            <span class="cook-prep-item__icon">${prepIconHtml(p.type)}</span>
            <div class="cook-prep-item__body">
              <span class="cook-prep-item__type">${escapeHtml(PREP_TYPE_LABELS[p.type] || 'Подготовка')}</span>
              <p class="cook-prep-item__text">${escapeHtml(p.text)}</p>
              <span class="cook-prep-item__when">за ${formatDuration(p.before_min * 60)} до старта · <time class="cook-prep-fire">${formatDateTime(fireMs)}</time></span>
            </div>
          </li>`;
      }).join('');

      prepHtml = `
        <section class="cook-setup__section">
          <h2 class="cook-setup__heading">Заранее</h2>
          <p class="cook-setup__hint">Напоминания о разморозке, достаньте из холодильника, маринаде</p>
          <ul class="cook-prep-list">${rows}</ul>
        </section>`;
    }

    bodyEl.innerHTML = `
      <div class="cook-setup">
        <section class="cook-setup__section">
          <h2 class="cook-setup__heading">Когда начнёте?</h2>
          <div class="cook-start-options">
            <button type="button" class="cook-start-btn cook-start-btn--now is-active" data-start="now">Сейчас</button>
            <button type="button" class="cook-start-btn" data-start="plan">Запланировать</button>
          </div>
          <label class="cook-datetime-wrap" id="cook-datetime-wrap" hidden>
            <span class="cook-datetime-label">Время начала готовки</span>
            <input type="datetime-local" class="cook-datetime" id="cook-datetime" value="${localValue}">
          </label>
        </section>
        ${prepHtml}
        <section class="cook-setup__section cook-setup__summary">
          <div class="cook-summary-stat"><span class="cook-summary-stat__n">${steps.length}</span> шагов</div>
          <div class="cook-summary-stat"><span class="cook-summary-stat__n">${steps.filter(s => s.timer_sec).length}</span> с таймером</div>
        </section>
        <div class="cook-setup__actions">
          <button type="button" class="btn-primary cook-mode__start" id="cook-begin">Начать готовку</button>
          ${prep.length ? '<button type="button" class="btn-secondary" id="cook-schedule-prep">Только напоминания</button>' : ''}
        </div>
        <p class="cook-notify-hint" id="cook-notify-hint"></p>
      </div>`;

    wireSetupEvents();
    updatePrepTimes();
    updateNotifyHint();
  }

  function wireSetupEvents() {
    const nowBtn = bodyEl.querySelector('[data-start="now"]');
    const planBtn = bodyEl.querySelector('[data-start="plan"]');
    const dtWrap = bodyEl.querySelector('#cook-datetime-wrap');
    const dtInput = bodyEl.querySelector('#cook-datetime');

    nowBtn?.addEventListener('click', () => {
      nowBtn.classList.add('is-active');
      planBtn?.classList.remove('is-active');
      dtWrap.hidden = true;
      state.cookStartMs = Date.now();
      updatePrepTimes();
    });

    planBtn?.addEventListener('click', () => {
      planBtn.classList.add('is-active');
      nowBtn?.classList.remove('is-active');
      dtWrap.hidden = false;
      syncCookStartFromInput();
    });

    dtInput?.addEventListener('change', () => {
      syncCookStartFromInput();
      updatePrepTimes();
    });

    bodyEl.querySelector('#cook-begin')?.addEventListener('click', async () => {
      await ensureNotifyPermission();
      if (prep.length) schedulePrepAlerts(recipe, state.cookStartMs);
      if (state.cookStartMs > Date.now() + 60000) {
        showToast(`Готовка запланирована на ${formatDateTime(state.cookStartMs)}`);
      }
      state.stepIndex = 0;
      renderSteps();
    });

    bodyEl.querySelector('#cook-schedule-prep')?.addEventListener('click', async () => {
      await ensureNotifyPermission();
      schedulePrepAlerts(recipe, state.cookStartMs);
      showToast(`Напоминания запланированы (${prep.length})`);
      updateNotifyHint();
    });
  }

  function syncCookStartFromInput() {
    const dtInput = bodyEl.querySelector('#cook-datetime');
    if (!dtInput?.value) return;
    const parsed = new Date(dtInput.value);
    if (!Number.isNaN(parsed.getTime())) {
      state.cookStartMs = parsed.getTime();
    }
  }

  function updatePrepTimes() {
    bodyEl.querySelectorAll('.cook-prep-item').forEach(el => {
      const beforeMin = Number(el.dataset.before);
      const fireMs = prepFireTime(state.cookStartMs, beforeMin);
      const timeEl = el.querySelector('.cook-prep-fire');
      if (timeEl) {
        timeEl.textContent = formatDateTime(fireMs);
        timeEl.dataset.relative = formatRelativeToNow(fireMs);
      }
    });
  }

  async function ensureNotifyPermission() {
    const status = await requestNotificationPermission();
    updateNotifyHint(status);
    return status;
  }

  function updateNotifyHint(forcedStatus) {
    const hint = bodyEl.querySelector('#cook-notify-hint') || rootEl.querySelector('#cook-notify-hint');
    if (!hint) return;

    const status = forcedStatus || (canNotify() ? 'granted' : Notification?.permission || 'default');
    const pending = getAlertsForRecipe(recipe.id).length;

    if (status === 'unsupported') {
      hint.textContent = 'Браузер не поддерживает уведомления — напоминания покажем на экране.';
    } else if (status === 'denied') {
      hint.textContent = 'Уведомления заблокированы. Разрешите в настройках браузера для напоминаний в фоне.';
    } else if (status !== 'granted') {
      hint.textContent = 'При старте запросим разрешение на уведомления (разморозка, таймеры).';
    } else if (pending) {
      hint.textContent = `Активных напоминаний: ${pending}`;
    } else {
      hint.textContent = 'Уведомления включены.';
    }
  }

  function getTimerDuration(timerId, step) {
    return state.timerDurations.get(timerId) ?? step.timer_sec;
  }

  function timerAdjustStep(step) {
    return step.timer_sec >= 3600 ? 300 : step.timer_sec >= 600 ? 60 : 30;
  }

  function renderTimerBlock(step, timerId) {
    const activeTimer = state.timers.get(timerId);
    const timerRunning = state.timerIntervals.has(timerId);
    const durationSec = getTimerDuration(timerId, step);
    const label = step.timer_label || formatDuration(durationSec);
    const displaySec = activeTimer?.remaining ?? durationSec;
    const stepSec = timerAdjustStep(step);
    const noteBlock = step.timer_note
      ? `<p class="cook-step-timer__note">${escapeHtml(step.timer_note)}</p>`
      : '';
    const adjustBlock = timerRunning
      ? ''
      : `<div class="cook-step-timer__adjust">
          <button type="button" class="btn-secondary cook-timer-minus" aria-label="Уменьшить">−${formatDuration(stepSec)}</button>
          <button type="button" class="btn-secondary cook-timer-plus" aria-label="Увеличить">+${formatDuration(stepSec)}</button>
        </div>`;
    const cont = activeTimer?.remaining != null && activeTimer.remaining < durationSec;

    return `
        <div class="cook-step-timer ${timerRunning ? 'is-running' : ''}" data-timer-id="${timerId}">
          <div class="cook-step-timer__label">${escapeHtml(label)}</div>
          <div class="cook-step-timer__display" aria-live="polite">${formatDurationShort(displaySec)}</div>
          ${noteBlock}
          ${adjustBlock}
          <div class="cook-step-timer__actions">
            ${timerRunning
              ? '<button type="button" class="btn-secondary cook-timer-pause">Пауза</button><button type="button" class="btn-secondary cook-timer-reset">Сброс</button>'
              : `<button type="button" class="btn-primary cook-timer-start">${spriteIconHtml('play', 'ui-icon ui-icon--inline')} ${cont ? 'Продолжить' : 'Старт'} ${formatDuration(durationSec)}</button>`
            }
          </div>
        </div>`;
  }

  function renderSteps() {
    state.phase = 'steps';
    const step = steps[state.stepIndex];
    const progress = ((state.stepIndex + 1) / steps.length) * 100;
    const isDone = state.completed.has(state.stepIndex);
    const timerId = `step-${state.stepIndex}`;

    let timerBlock = '';
    if (step.timer_sec > 0) {
      timerBlock = renderTimerBlock(step, timerId);
    }

    bodyEl.innerHTML = `
      <div class="cook-steps">
        <div class="cook-progress" aria-hidden="true">
          <div class="cook-progress__bar" style="width:${progress}%"></div>
        </div>
        <div class="cook-progress__label">Шаг ${state.stepIndex + 1} из ${steps.length}</div>

        <article class="cook-step-card ${isDone ? 'is-done' : ''}">
          <p class="cook-step-text">${escapeHtml(step.text)}</p>
          ${timerBlock}
        </article>

        <label class="cook-step-check">
          <input type="checkbox" class="cook-step-check__input" ${isDone ? 'checked' : ''}>
          <span>Шаг выполнен</span>
        </label>

        <nav class="cook-step-nav">
          <button type="button" class="btn-secondary cook-step-prev" ${state.stepIndex === 0 ? 'disabled' : ''}>← Назад</button>
          <button type="button" class="btn-primary cook-step-next">${state.stepIndex >= steps.length - 1 ? 'Готово' : 'Далее →'}</button>
        </nav>

        <details class="cook-step-overview">
          <summary>Все шаги</summary>
          <ol class="cook-step-overview__list">
            ${steps.map((s, i) => `
              <li class="${i === state.stepIndex ? 'is-current' : ''} ${state.completed.has(i) ? 'is-done' : ''}">
                <button type="button" class="cook-step-jump" data-step="${i}">${escapeHtml(s.text.slice(0, 80))}${s.text.length > 80 ? '…' : ''}</button>
              </li>`).join('')}
          </ol>
        </details>
      </div>`;

    wireStepEvents(step, timerId);
  }

  function wireStepEvents(step, timerId) {
    bodyEl.querySelector('.cook-step-check__input')?.addEventListener('change', (e) => {
      if (e.target.checked) state.completed.add(state.stepIndex);
      else state.completed.delete(state.stepIndex);
      bodyEl.querySelector('.cook-step-card')?.classList.toggle('is-done', e.target.checked);
    });

    bodyEl.querySelector('.cook-step-prev')?.addEventListener('click', () => {
      if (state.stepIndex > 0) {
        state.stepIndex -= 1;
        renderSteps();
      }
    });

    bodyEl.querySelector('.cook-step-next')?.addEventListener('click', () => {
      state.completed.add(state.stepIndex);
      if (state.stepIndex < steps.length - 1) {
        state.stepIndex += 1;
        renderSteps();
      } else {
        renderComplete();
      }
    });

    bodyEl.querySelectorAll('.cook-step-jump').forEach(btn => {
      btn.addEventListener('click', () => {
        state.stepIndex = Number(btn.dataset.step);
        renderSteps();
      });
    });

    bodyEl.querySelector('.cook-timer-start')?.addEventListener('click', () => startTimer(timerId, step));
    bodyEl.querySelector('.cook-timer-pause')?.addEventListener('click', () => pauseTimer(timerId));
    bodyEl.querySelector('.cook-timer-reset')?.addEventListener('click', () => resetTimer(timerId, step));
    bodyEl.querySelector('.cook-timer-minus')?.addEventListener('click', () => adjustTimerDuration(timerId, step, -timerAdjustStep(step)));
    bodyEl.querySelector('.cook-timer-plus')?.addEventListener('click', () => adjustTimerDuration(timerId, step, timerAdjustStep(step)));
  }

  function adjustTimerDuration(timerId, step, deltaSec) {
    if (state.timerIntervals.has(timerId)) return;
    const next = Math.max(30, getTimerDuration(timerId, step) + deltaSec);
    state.timerDurations.set(timerId, next);
    state.timers.delete(timerId);
    const block = bodyEl.querySelector('.cook-step-timer');
    if (!block) return;
    block.querySelector('.cook-step-timer__display').textContent = formatDurationShort(next);
    const startBtn = block.querySelector('.cook-timer-start');
    if (startBtn) {
      startBtn.innerHTML = `${spriteIconHtml('play', 'ui-icon ui-icon--inline')} Старт ${formatDuration(next)}`;
    }
  }

  function startTimer(timerId, step) {
    pauseTimer(timerId);
    const durationSec = getTimerDuration(timerId, step);
    let remaining = state.timers.get(timerId)?.remaining ?? durationSec;
    const endAt = Date.now() + remaining * 1000;

    scheduleTimerAlert(
      recipe.id,
      recipe.title,
      timerId,
      endAt,
      step.timer_label || `Шаг ${state.stepIndex + 1}`
    );

    const interval = setInterval(() => {
      remaining = Math.max(0, Math.ceil((endAt - Date.now()) / 1000));
      state.timers.set(timerId, { remaining, endAt });
      const display = bodyEl.querySelector('.cook-step-timer__display');
      if (display) display.textContent = formatDurationShort(remaining);

      if (remaining <= 0) {
        pauseTimer(timerId);
        cancelTimerAlert(recipe.id, timerId);
        showToast(`Таймер: ${step.timer_label || 'готово'}`, 8000);
        if (navigator.vibrate) navigator.vibrate([300, 100, 300, 100, 300]);
        bodyEl.querySelector('.cook-step-timer')?.classList.remove('is-running');
        bodyEl.querySelector('.cook-step-timer')?.classList.add('is-finished');
        const adjustEl = bodyEl.querySelector('.cook-step-timer__adjust');
        if (adjustEl) adjustEl.hidden = false;
      }
    }, 250);

    state.timerIntervals.set(timerId, interval);
    const block = bodyEl.querySelector('.cook-step-timer');
    block?.classList.add('is-running');
    const adjust = block?.querySelector('.cook-step-timer__adjust');
    if (adjust) adjust.hidden = true;
    const actions = block?.querySelector('.cook-step-timer__actions');
    if (actions) {
      actions.innerHTML = `
        <button type="button" class="btn-secondary cook-timer-pause">Пауза</button>
        <button type="button" class="btn-secondary cook-timer-reset">Сброс</button>`;
      actions.querySelector('.cook-timer-pause')?.addEventListener('click', () => {
        pauseTimer(timerId);
        updateTimerControls(timerId, false, step);
      });
      actions.querySelector('.cook-timer-reset')?.addEventListener('click', () => resetTimer(timerId, step));
    }
  }

  function updateTimerControls(timerId, running, step) {
    const block = bodyEl.querySelector('.cook-step-timer');
    if (!block) return;
    block.classList.toggle('is-running', running);
    const actions = block.querySelector('.cook-step-timer__actions');
    if (!actions) return;
    const activeTimer = state.timers.get(timerId);
    const durationSec = getTimerDuration(timerId, step);
    if (running) {
      actions.innerHTML = `
        <button type="button" class="btn-secondary cook-timer-pause">Пауза</button>
        <button type="button" class="btn-secondary cook-timer-reset">Сброс</button>`;
      actions.querySelector('.cook-timer-pause')?.addEventListener('click', () => {
        pauseTimer(timerId);
        updateTimerControls(timerId, false, step);
      });
      actions.querySelector('.cook-timer-reset')?.addEventListener('click', () => resetTimer(timerId, step));
    } else {
      const cont = activeTimer?.remaining != null && activeTimer.remaining < durationSec;
      const adjust = block.querySelector('.cook-step-timer__adjust');
      if (adjust) adjust.hidden = false;
      actions.innerHTML = `<button type="button" class="btn-primary cook-timer-start">${spriteIconHtml('play', 'ui-icon ui-icon--inline')} ${cont ? 'Продолжить' : 'Старт'} ${formatDuration(durationSec)}</button>`;
      actions.querySelector('.cook-timer-start')?.addEventListener('click', () => startTimer(timerId, step));
    }
  }

  function pauseTimer(timerId) {
    const interval = state.timerIntervals.get(timerId);
    if (interval) {
      clearInterval(interval);
      state.timerIntervals.delete(timerId);
    }
    cancelTimerAlert(recipe.id, timerId);
  }

  function resetTimer(timerId, step) {
    pauseTimer(timerId);
    state.timers.delete(timerId);
    state.timerDurations.delete(timerId);
    renderSteps();
  }

  function renderComplete() {
    state.phase = 'done';
    bodyEl.innerHTML = `
      <div class="cook-complete">
        <div class="cook-complete__icon" aria-hidden="true">${spriteIconHtml('circle-check', 'ui-icon ui-icon--complete')}</div>
        <h2 class="cook-complete__title">Готово!</h2>
        <p class="cook-complete__text">${escapeHtml(recipe.title)} — все шаги пройдены.</p>
        <button type="button" class="btn-primary" id="cook-finish-close">Закрыть</button>
      </div>`;
    bodyEl.querySelector('#cook-finish-close')?.addEventListener('click', close);
    releaseWakeLock();
  }

  async function toggleWakeLock() {
    const btn = shell.querySelector('.cook-mode__wake');
    if (state.wakeLock) {
      await releaseWakeLock();
      btn?.setAttribute('aria-pressed', 'false');
      return;
    }
    if (!('wakeLock' in navigator)) {
      showToast('Экран не блокируется — браузер не поддерживает Wake Lock');
      return;
    }
    try {
      state.wakeLock = await navigator.wakeLock.request('screen');
      btn?.setAttribute('aria-pressed', 'true');
      state.wakeLock.addEventListener('release', () => {
        state.wakeLock = null;
        btn?.setAttribute('aria-pressed', 'false');
      });
    } catch {
      showToast('Не удалось удержать экран включённым');
    }
  }

  async function releaseWakeLock() {
    if (state.wakeLock) {
      await state.wakeLock.release();
      state.wakeLock = null;
    }
  }

  function close() {
    for (const id of state.timerIntervals.keys()) pauseTimer(id);
    releaseWakeLock();
    rootEl.hidden = true;
    rootEl.innerHTML = '';
    document.body.classList.remove('cook-mode-open');
  }

  function open() {
    rootEl.hidden = false;
    rootEl.innerHTML = '';
    rootEl.appendChild(shell);
    document.body.classList.add('cook-mode-open');
    renderSetup();
  }

  shell.querySelector('.cook-mode__close')?.addEventListener('click', close);
  shell.querySelector('.cook-mode__wake')?.addEventListener('click', toggleWakeLock);

  document.addEventListener('visibilitychange', async () => {
    if (document.visibilityState === 'visible' && state.wakeLock === null) {
      const btn = shell.querySelector('.cook-mode__wake');
      if (btn?.getAttribute('aria-pressed') === 'true') toggleWakeLock();
    }
  });

  return { open, close };
}

function toDatetimeLocal(date) {
  const pad = n => String(n).padStart(2, '0');
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T${pad(date.getHours())}:${pad(date.getMinutes())}`;
}

export function renderPrepSection(prep, cookStartMs = Date.now() + 3600000) {
  const items = normalizePrep(prep);
  if (!items.length) return '';

  const rows = items.map(p => {
    const fireMs = prepFireTime(cookStartMs, p.before_min);
    return `
      <li class="recipe-prep-item">
        <span class="recipe-prep-item__icon">${prepIconHtml(p.type)}</span>
        <div class="recipe-prep-item__body">
          <span class="recipe-prep-item__type">${escapeHtml(PREP_TYPE_LABELS[p.type] || 'Подготовка')}</span>
          <p class="recipe-prep-item__text">${escapeHtml(p.text)}</p>
          <span class="recipe-prep-item__when">за ${formatDuration(p.before_min * 60)} до готовки</span>
        </div>
      </li>`;
  }).join('');

  return `
    <section class="recipe-section recipe-prep">
      <h2>Заранее</h2>
      <p class="recipe-prep-hint">Запланируйте в режиме готовки — пришлём напоминание</p>
      <ul class="recipe-prep-list">${rows}</ul>
    </section>`;
}

export function renderStepsWithTimers(steps) {
  const normalized = normalizeSteps(steps);
  if (!normalized.length) return '';

  const lis = normalized.map(s => {
    const timerBadge = s.timer_sec
      ? `<span class="step-timer-badge" title="Есть таймер">${spriteIconHtml('timer', 'ui-icon ui-icon--badge')} ${escapeHtml(s.timer_label || formatDuration(s.timer_sec))}</span>`
      : '';
    return `<li>${escapeHtml(s.text)}${timerBadge}</li>`;
  }).join('');

  return `<ol class="recipe-list recipe-list--steps">${lis}</ol>`;
}
