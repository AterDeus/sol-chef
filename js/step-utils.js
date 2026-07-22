/** Нормализация шагов и подготовительных напоминаний рецепта. */

import { spriteIconHtml } from './icons.js';

const PREP_TYPES = new Set(['thaw', 'fridge', 'room_temp', 'marinate', 'soak', 'custom']);

const PREP_ICON_IDS = {
  thaw: 'snowflake',
  fridge: 'refrigerator',
  room_temp: 'thermometer',
  marinate: 'flask-conical',
  soak: 'droplets',
  custom: 'clipboard-list',
};

export function prepIconHtml(type) {
  const id = PREP_ICON_IDS[type] || PREP_ICON_IDS.custom;
  return spriteIconHtml(id, 'ui-icon ui-icon--prep');
}

export function normalizeStep(step, index) {
  if (typeof step === 'string') {
    return { index, text: step.trim(), timer_sec: 0, timer_label: '', timer_note: '' };
  }
  if (step && typeof step === 'object') {
    const timerMin = Number(step.timer_min) || 0;
    const timerSec = Number(step.timer_sec) || 0;
    const totalSec = timerMin * 60 + timerSec;
    return {
      index,
      text: String(step.text || '').trim(),
      timer_sec: totalSec > 0 ? totalSec : 0,
      timer_label: String(step.timer_label || '').trim(),
      timer_note: String(step.timer_note || '').trim(),
    };
  }
  return { index, text: '', timer_sec: 0, timer_label: '', timer_note: '' };
}

export function normalizeSteps(steps) {
  if (!Array.isArray(steps)) return [];
  return steps
    .map((s, i) => normalizeStep(s, i))
    .filter(s => s.text);
}

export function normalizePrepItem(item, index) {
  if (!item || typeof item !== 'object') return null;
  const text = String(item.text || '').trim();
  if (!text) return null;

  const beforeMin = Number(item.before_min) || 0;
  const beforeHours = Number(item.before_hours) || 0;
  const leadMin = beforeMin + beforeHours * 60;
  if (leadMin <= 0) return null;

  const type = PREP_TYPES.has(item.type) ? item.type : 'custom';
  return {
    index,
    text,
    before_min: leadMin,
    type,
  };
}

export function normalizePrep(prep) {
  if (!Array.isArray(prep)) return [];
  return prep
    .map((p, i) => normalizePrepItem(p, i))
    .filter(Boolean)
    .sort((a, b) => b.before_min - a.before_min);
}

export function formatDuration(sec) {
  const s = Math.max(0, Math.round(sec));
  const h = Math.floor(s / 3600);
  const m = Math.floor((s % 3600) / 60);
  const r = s % 60;
  if (h > 0 && m > 0) return `${h} ч ${m} мин`;
  if (h > 0) return `${h} ч`;
  if (m > 0 && r > 0) return `${m} мин ${r} сек`;
  if (m > 0) return `${m} мин`;
  return `${r} сек`;
}

export function formatDurationShort(sec) {
  const s = Math.max(0, Math.round(sec));
  const h = Math.floor(s / 3600);
  const m = Math.floor((s % 3600) / 60);
  const r = s % 60;
  if (h > 0) return `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}:${String(r).padStart(2, '0')}`;
  return `${String(m).padStart(2, '0')}:${String(r).padStart(2, '0')}`;
}

export function prepFireTime(cookStartMs, beforeMin) {
  return cookStartMs - beforeMin * 60 * 1000;
}

export function formatDateTime(ms) {
  return new Date(ms).toLocaleString('ru-RU', {
    day: 'numeric',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit',
  });
}

export function formatRelativeToNow(ms) {
  const diff = ms - Date.now();
  const abs = Math.abs(diff);
  const min = Math.round(abs / 60000);
  if (min < 1) return diff >= 0 ? 'скоро' : 'только что';
  if (min < 60) return diff >= 0 ? `через ${min} мин` : `${min} мин назад`;
  const h = Math.floor(min / 60);
  const rm = min % 60;
  const part = rm ? `${h} ч ${rm} мин` : `${h} ч`;
  return diff >= 0 ? `через ${part}` : `${part} назад`;
}
