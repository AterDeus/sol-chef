'use client';

import { useCallback, useEffect, useRef, useState } from 'react';
import type { RecipePrep, RecipeStep } from '@/lib/types';
import { formatClock, formatDuration } from '@/lib/time';
import { SpriteIcon } from './SpriteIcon';

type WakeLockSentinelLike = {
  released: boolean;
  release: () => Promise<void>;
  addEventListener: (type: 'release', listener: () => void) => void;
};

const PREP_LABELS: Record<string, string> = {
  thaw: 'Разморозка',
  fridge: 'Холодильник',
  room_temp: 'Комнат. темп.',
  marinate: 'Маринад',
  soak: 'Замачивание',
  custom: 'Подготовка',
};

const FOCUSABLE =
  'a[href], button:not(:disabled), input:not(:disabled), select, textarea, summary, [tabindex]:not([tabindex="-1"])';

function toDatetimeLocal(date: Date): string {
  const pad = (n: number) => String(n).padStart(2, '0');
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T${pad(date.getHours())}:${pad(date.getMinutes())}`;
}

function timerAdjustStep(seconds: number): number {
  if (seconds >= 3600) return 300;
  if (seconds >= 600) return 60;
  return 30;
}

function normalizePrep(prep: RecipePrep[] | undefined): Array<{
  text: string;
  before_min: number;
  type: string;
}> {
  if (!prep?.length) return [];
  return prep
    .map((item) => {
      const text = (item.text || '').trim();
      const before = (item.before_min || 0) + (item.before_hours || 0) * 60;
      if (!text || before <= 0) return null;
      return { text, before_min: before, type: item.type || 'custom' };
    })
    .filter((item): item is { text: string; before_min: number; type: string } => Boolean(item))
    .sort((a, b) => b.before_min - a.before_min);
}

type Props = {
  title: string;
  steps: RecipeStep[];
  prep?: RecipePrep[];
  open: boolean;
  onClose: () => void;
};

export function CookMode({ title, steps, prep: rawPrep, open, onClose }: Props) {
  const prep = normalizePrep(rawPrep);
  const [phase, setPhase] = useState<'setup' | 'steps' | 'done'>('setup');
  const [index, setIndex] = useState(0);
  const [done, setDone] = useState<Set<number>>(new Set());
  const [remaining, setRemaining] = useState<number | null>(null);
  const [running, setRunning] = useState(false);
  const [duration, setDuration] = useState(0);
  const [plan, setPlan] = useState(false);
  const [startMs, setStartMs] = useState(() => Date.now());
  const [toast, setToast] = useState<string | null>(null);
  const [wakeOn, setWakeOn] = useState(false);
  const wakeRef = useRef<WakeLockSentinelLike | null>(null);
  const intervalRef = useRef<number | null>(null);
  const wantWake = useRef(false);
  const dialogRef = useRef<HTMLDivElement>(null);
  const closeBtnRef = useRef<HTMLButtonElement>(null);
  const restoreFocusRef = useRef<HTMLElement | null>(null);

  const step = steps[index];
  const timerSec = duration || step?.timer_seconds || 0;

  const showToast = (message: string) => {
    setToast(message);
    window.setTimeout(() => setToast(null), 4000);
  };

  const releaseWake = useCallback(async () => {
    if (wakeRef.current) {
      try {
        await wakeRef.current.release();
      } catch {
        /* ignore */
      }
      wakeRef.current = null;
    }
    setWakeOn(false);
  }, []);

  const requestWake = useCallback(async () => {
    const nav = navigator as Navigator & {
      wakeLock?: { request: (type: 'screen') => Promise<WakeLockSentinelLike> };
    };
    if (!nav.wakeLock) {
      showToast('Экран не блокируется — браузер не поддерживает Wake Lock');
      return;
    }
    try {
      const sentinel = await nav.wakeLock.request('screen');
      wakeRef.current = sentinel;
      setWakeOn(true);
      sentinel.addEventListener('release', () => {
        wakeRef.current = null;
        setWakeOn(false);
      });
    } catch {
      showToast('Не удалось удержать экран включённым');
    }
  }, []);

  useEffect(() => {
    if (!open) return;
    document.body.classList.add('cook-mode-open');
    wantWake.current = true;
    void requestWake();
    return () => {
      document.body.classList.remove('cook-mode-open');
      if (intervalRef.current) window.clearInterval(intervalRef.current);
      void releaseWake();
    };
  }, [open, requestWake, releaseWake]);

  useEffect(() => {
    const onVis = () => {
      if (document.visibilityState === 'visible' && wantWake.current && !wakeRef.current) {
        void requestWake();
      }
    };
    document.addEventListener('visibilitychange', onVis);
    return () => document.removeEventListener('visibilitychange', onVis);
  }, [requestWake]);

  useEffect(() => {
    if (!running) return;
    intervalRef.current = window.setInterval(() => {
      setRemaining((prev) => {
        if (prev == null) return prev;
        if (prev <= 1) {
          setRunning(false);
          showToast(`Таймер: ${step?.timer_label || 'готово'}`);
          if (navigator.vibrate) navigator.vibrate([300, 100, 300]);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
    return () => {
      if (intervalRef.current) window.clearInterval(intervalRef.current);
    };
  }, [running, step?.timer_label]);

  useEffect(() => {
    setDuration(step?.timer_seconds ?? 0);
    setRemaining(null);
    setRunning(false);
  }, [index, step?.timer_seconds]);

  const close = useCallback(() => {
    wantWake.current = false;
    setRunning(false);
    setPhase('setup');
    setIndex(0);
    setDone(new Set());
    onClose();
  }, [onClose]);
  const closeRef = useRef(close);
  closeRef.current = close;

  useEffect(() => {
    if (!open) return;

    restoreFocusRef.current =
      document.activeElement instanceof HTMLElement ? document.activeElement : null;

    const frame = window.requestAnimationFrame(() => {
      closeBtnRef.current?.focus();
    });

    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        event.preventDefault();
        closeRef.current();
        return;
      }
      if (event.key !== 'Tab') return;
      const root = dialogRef.current;
      if (!root) return;
      const nodes = Array.from(root.querySelectorAll<HTMLElement>(FOCUSABLE)).filter(
        (el) => el.getClientRects().length > 0,
      );
      if (nodes.length === 0) return;
      const first = nodes[0];
      const last = nodes[nodes.length - 1];
      if (event.shiftKey) {
        if (document.activeElement === first || document.activeElement === root) {
          event.preventDefault();
          last.focus();
        }
      } else if (document.activeElement === last) {
        event.preventDefault();
        first.focus();
      }
    };

    document.addEventListener('keydown', onKeyDown);
    return () => {
      window.cancelAnimationFrame(frame);
      document.removeEventListener('keydown', onKeyDown);
      restoreFocusRef.current?.focus();
    };
  }, [open]);

  if (!open) return null;

  const toggleWake = () => {
    if (wakeOn) {
      wantWake.current = false;
      void releaseWake();
    } else {
      wantWake.current = true;
      void requestWake();
    }
  };

  const startTimer = () => {
    setRemaining(remaining == null || remaining === 0 ? timerSec : remaining);
    setRunning(true);
  };

  const resetTimer = () => {
    setRunning(false);
    setRemaining(timerSec);
  };

  const adjust = timerAdjustStep(step?.timer_seconds || 0);
  const timedCount = steps.filter((item) => (item.timer_seconds ?? 0) > 0).length;

  const stepList = (
    <ol className="cook-step-overview__list">
      {steps.map((item, i) => (
        <li
          key={i}
          className={`${i === index ? 'is-current' : ''} ${done.has(i) ? 'is-done' : ''}`}
        >
          <button
            type="button"
            className="cook-step-jump"
            onClick={() => {
              setPhase('steps');
              setIndex(i);
            }}
          >
            {item.text.slice(0, 80)}
            {item.text.length > 80 ? '…' : ''}
          </button>
        </li>
      ))}
    </ol>
  );

  return (
    <div
      ref={dialogRef}
      className="cook-root"
      role="dialog"
      aria-modal="true"
      aria-labelledby="cook-dialog-title"
    >
      <header className="cook-mode__header">
        <button
          ref={closeBtnRef}
          type="button"
          className="cook-icon-btn"
          aria-label="Закрыть режим готовки"
          onClick={close}
        >
          <SpriteIcon name="x" size={22} />
        </button>
        <div style={{ flex: 1, minWidth: 0 }}>
          <div className="cook-mode__eyebrow">Режим готовки</div>
          <div className="cook-mode__title" id="cook-dialog-title">
            {title}
          </div>
        </div>
        <button
          type="button"
          className="cook-icon-btn"
          aria-label="Не гасить экран"
          aria-pressed={wakeOn}
          onClick={toggleWake}
        >
          <SpriteIcon name="sun" size={22} />
        </button>
      </header>
      <div className="cook-mode__body">
        {phase === 'done' ? (
          <div className="cook-complete">
            <h2>Готово!</h2>
            <p>{title} — все шаги пройдены.</p>
            <button type="button" className="btn-primary" onClick={close}>
              Закрыть
            </button>
          </div>
        ) : phase === 'setup' ? (
          <div className="cook-setup">
            <section className="cook-setup__section">
              <h2 className="cook-setup__heading">Когда начнёте?</h2>
              <div className="cook-start-options">
                <button
                  type="button"
                  className={`cook-start-btn${plan ? '' : ' is-active'}`}
                  aria-pressed={!plan}
                  onClick={() => {
                    setPlan(false);
                    setStartMs(Date.now());
                  }}
                >
                  Сейчас
                </button>
                <button
                  type="button"
                  className={`cook-start-btn${plan ? ' is-active' : ''}`}
                  aria-pressed={plan}
                  onClick={() => {
                    setPlan(true);
                    setStartMs(Date.now() + 3600000);
                  }}
                >
                  Запланировать
                </button>
              </div>
              {plan && (
                <label className="cook-datetime-wrap">
                  <span className="cook-datetime-label">Время начала готовки</span>
                  <input
                    type="datetime-local"
                    className="cook-datetime"
                    defaultValue={toDatetimeLocal(new Date(Date.now() + 3600000))}
                    onChange={(e) => {
                      const parsed = new Date(e.target.value);
                      if (!Number.isNaN(parsed.getTime())) setStartMs(parsed.getTime());
                    }}
                  />
                </label>
              )}
            </section>
            {prep.length > 0 && (
              <section className="cook-setup__section">
                <h2 className="cook-setup__heading">Заранее</h2>
                <p className="cook-setup__hint">
                  Напоминания о разморозке, достаньте из холодильника, маринаде
                </p>
                <ul className="cook-prep-list">
                  {prep.map((item) => (
                    <li key={`${item.type}-${item.text}`} className="cook-prep-item">
                      <div className="cook-prep-item__body">
                        <span className="cook-prep-item__type">
                          {PREP_LABELS[item.type] || 'Подготовка'}
                        </span>
                        <p className="cook-prep-item__text">{item.text}</p>
                        <span className="cook-prep-item__when">
                          за {formatDuration(item.before_min * 60)} до старта ·{' '}
                          {new Date(startMs - item.before_min * 60 * 1000).toLocaleString('ru-RU', {
                            day: 'numeric',
                            month: 'short',
                            hour: '2-digit',
                            minute: '2-digit',
                          })}
                        </span>
                      </div>
                    </li>
                  ))}
                </ul>
              </section>
            )}
            <section className="cook-setup__section cook-setup__summary">
              <div className="cook-summary-stat">
                <span className="cook-summary-stat__n">{steps.length}</span> шагов
              </div>
              <div className="cook-summary-stat">
                <span className="cook-summary-stat__n">{timedCount}</span> с таймером
              </div>
            </section>
            <div className="cook-setup__actions">
              <button type="button" className="btn-primary" onClick={() => setPhase('steps')}>
                Начать готовку
              </button>
              {prep.length > 0 && (
                <button
                  type="button"
                  className="btn-secondary"
                  onClick={() => showToast(`Напоминания: ${prep.length}`)}
                >
                  Только напоминания
                </button>
              )}
            </div>
          </div>
        ) : (
          <div className="cook-steps">
            <div className="cook-steps__main">
              <div className="cook-progress" aria-hidden>
                <div
                  className="cook-progress__bar"
                  style={{ width: `${((index + 1) / steps.length) * 100}%` }}
                />
              </div>
              <div className="cook-progress__label" aria-live="polite">
                Шаг {index + 1} из {steps.length}
              </div>
              <article className={`cook-step-card${done.has(index) ? ' is-done' : ''}`}>
                <p>{step?.text}</p>
                {step?.target_internal_temperature_c != null && (
                  <span className="temp-chip">цель {step.target_internal_temperature_c} °C</span>
                )}
                {step?.pull_internal_temperature_c != null && (
                  <span className="temp-chip">снятие {step.pull_internal_temperature_c} °C</span>
                )}
                {timerSec > 0 && (
                  <div className={`cook-step-timer${running ? ' is-running' : ''}`}>
                    <div>{step.timer_label || formatDuration(timerSec)}</div>
                    <div className="cook-step-timer__display" aria-live="polite">
                      {formatClock(remaining ?? timerSec)}
                    </div>
                    {step.timer_note && <p className="note">{step.timer_note}</p>}
                    {!running && (
                      <div className="cook-step-timer__adjust">
                        <button
                          type="button"
                          className="btn-secondary"
                          aria-label="Уменьшить"
                          onClick={() => setDuration((n) => Math.max(30, (n || timerSec) - adjust))}
                        >
                          −{formatDuration(adjust)}
                        </button>
                        <button
                          type="button"
                          className="btn-secondary"
                          aria-label="Увеличить"
                          onClick={() => setDuration((n) => (n || timerSec) + adjust)}
                        >
                          +{formatDuration(adjust)}
                        </button>
                      </div>
                    )}
                    <div className="recipe-actions" style={{ border: 'none', marginTop: 12, paddingTop: 0 }}>
                      {running ? (
                        <>
                          <button type="button" className="btn-secondary" onClick={() => setRunning(false)}>
                            Пауза
                          </button>
                          <button type="button" className="btn-secondary" onClick={resetTimer}>
                            Сброс
                          </button>
                        </>
                      ) : (
                        <button type="button" className="btn-primary" onClick={startTimer}>
                          {remaining != null && remaining < timerSec && remaining > 0
                            ? 'Продолжить'
                            : `Старт ${formatDuration(timerSec)}`}
                        </button>
                      )}
                    </div>
                  </div>
                )}
              </article>
              <label className="cook-step-check" style={{ display: 'flex', gap: 8, marginBottom: 12 }}>
                <input
                  type="checkbox"
                  checked={done.has(index)}
                  onChange={(e) => {
                    setDone((prev) => {
                      const next = new Set(prev);
                      if (e.target.checked) next.add(index);
                      else next.delete(index);
                      return next;
                    });
                  }}
                />
                Шаг выполнен
              </label>
              <nav className="cook-step-nav">
                <button
                  type="button"
                  className="btn-secondary"
                  disabled={index === 0}
                  onClick={() => setIndex((i) => Math.max(0, i - 1))}
                >
                  ← Назад
                </button>
                <button
                  type="button"
                  className="btn-primary"
                  onClick={() => {
                    setDone((prev) => new Set(prev).add(index));
                    if (index >= steps.length - 1) setPhase('done');
                    else setIndex((i) => i + 1);
                  }}
                >
                  {index >= steps.length - 1 ? 'Готово' : 'Далее →'}
                </button>
              </nav>
              <details className="cook-step-overview cook-step-overview--mobile">
                <summary>Все шаги</summary>
                {stepList}
              </details>
            </div>
            <aside className="cook-steps__rail" aria-label="Все шаги">
              <h2 className="cook-rail-title">Все шаги</h2>
              {stepList}
            </aside>
          </div>
        )}
      </div>
      {toast && (
        <div className="cook-mode__toast" role="status" aria-live="polite">
          {toast}
        </div>
      )}
    </div>
  );
}
