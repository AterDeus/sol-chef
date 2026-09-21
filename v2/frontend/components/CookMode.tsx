'use client';

import { useCallback, useEffect, useRef, useState } from 'react';
import type { RecipePrep, RecipeStep } from '@/lib/types';
import { useCountdown } from '@/lib/countdown';
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

function toDatetimeLocal(date: Date): string {
  const pad = (n: number) => String(n).padStart(2, '0');
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T${pad(date.getHours())}:${pad(date.getMinutes())}`;
}

function timerAdjustStep(seconds: number): number {
  if (seconds >= 3600) return 300;
  if (seconds >= 600) return 60;
  return 30;
}

function stepOutline(text: string): string {
  const trimmed = text.replace(/\s+/g, ' ').trim();
  const sentenceEnd = trimmed.search(/[.!?](\s|$)/);
  const sentence = sentenceEnd === -1 ? trimmed : trimmed.slice(0, sentenceEnd + 1);
  if (sentence.length <= 96) return sentence;
  const cut = sentence.slice(0, 96);
  const word = cut.lastIndexOf(' ');
  const base = (word > 40 ? cut.slice(0, word) : cut).trimEnd();
  return `${base}…`;
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

function useToast() {
  const [message, setMessage] = useState<string | null>(null);
  const timeoutRef = useRef<number | null>(null);

  const show = useCallback((next: string) => {
    if (timeoutRef.current) window.clearTimeout(timeoutRef.current);
    setMessage(next);
    timeoutRef.current = window.setTimeout(() => setMessage(null), 4000);
  }, []);

  useEffect(
    () => () => {
      if (timeoutRef.current) window.clearTimeout(timeoutRef.current);
    },
    [],
  );

  return { message, show };
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
  const [duration, setDuration] = useState(0);
  const [plan, setPlan] = useState(false);
  const [startMs, setStartMs] = useState(() => Date.now());
  const [wakeOn, setWakeOn] = useState(false);
  const { message: toast, show: showToast } = useToast();
  const step = steps[index];
  const countdown = useCountdown(() => {
    showToast(`Таймер: ${step?.timer_label || 'готово'}`);
    if (navigator.vibrate) navigator.vibrate([300, 100, 300]);
  });
  const wakeRef = useRef<WakeLockSentinelLike | null>(null);
  const wantWake = useRef(false);
  const dialogRef = useRef<HTMLDialogElement>(null);
  const closeBtnRef = useRef<HTMLButtonElement>(null);

  const timerSec = duration || step?.timer_seconds || 0;
  const remainingSeconds = countdown.remainingSeconds;
  const shownSeconds = remainingSeconds ?? timerSec;

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
  }, [showToast]);

  useEffect(() => {
    const dialog = dialogRef.current;
    if (!dialog) return;
    if (open && !dialog.open) {
      dialog.showModal();
      closeBtnRef.current?.focus();
    }
    if (!open && dialog.open) dialog.close();
  }, [open]);

  useEffect(() => {
    if (!open) return undefined;
    document.body.classList.add('cook-mode-open');
    wantWake.current = true;
    void requestWake();
    return () => {
      document.body.classList.remove('cook-mode-open');
      wantWake.current = false;
      countdown.stop();
      void releaseWake();
    };
  }, [open, requestWake, releaseWake, countdown.stop]);

  useEffect(() => {
    if (open) return;
    setPhase('setup');
    setIndex(0);
    setDone(new Set());
    setPlan(false);
    setStartMs(Date.now());
    setDuration(0);
  }, [open]);

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
    setDuration(step?.timer_seconds ?? 0);
    countdown.stop();
  }, [index, step?.timer_seconds, countdown.stop]);

  const close = useCallback(() => {
    wantWake.current = false;
    countdown.stop();
    onClose();
  }, [countdown.stop, onClose]);

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
    const ms =
      countdown.remainingMs == null || countdown.remainingMs === 0
        ? timerSec * 1000
        : countdown.remainingMs;
    countdown.startMs(ms);
  };

  const resetTimer = () => {
    countdown.reset(timerSec * 1000);
  };

  const beginCooking = () => {
    if (steps.length === 0) {
      showToast('В этом рецепте нет шагов для режима готовки');
      return;
    }
    if (plan && startMs < Date.now() - 60_000) {
      showToast('Время начала уже прошло — выберите другое или нажмите «Сейчас»');
      return;
    }
    setPhase('steps');
  };

  const adjust = timerAdjustStep(step?.timer_seconds || 0);
  const timedCount = steps.filter((item) => (item.timer_seconds ?? 0) > 0).length;
  const progressPct = steps.length > 0 ? ((index + 1) / steps.length) * 100 : 0;

  const stepList = (
    <ol className="cook-step-overview__list">
      {steps.map((item, i) => (
        <li
          key={`${i}-${item.text.slice(0, 24)}`}
          className={`${phase === 'steps' && i === index ? 'is-current' : ''} ${done.has(i) ? 'is-done' : ''}`}
        >
          <button
            type="button"
            className="cook-step-jump"
            onClick={() => {
              setPhase('steps');
              setIndex(i);
            }}
          >
            {stepOutline(item.text)}
          </button>
        </li>
      ))}
    </ol>
  );

  return (
    <dialog
      ref={dialogRef}
      className="cook-root"
      aria-labelledby="cook-dialog-title"
      onCancel={(event) => {
        event.preventDefault();
        onClose();
      }}
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
        <div className="cook-mode__title-wrap">
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
            <section className="cook-setup__section cook-setup__when">
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
                    value={toDatetimeLocal(new Date(startMs))}
                    onChange={(e) => {
                      const parsed = new Date(e.target.value);
                      if (!Number.isNaN(parsed.getTime())) setStartMs(parsed.getTime());
                    }}
                  />
                </label>
              )}
            </section>
            {prep.length > 0 ? (
              <aside className="cook-setup__aside" aria-label="Заранее">
                <section className="cook-setup__section">
                  <h2 className="cook-setup__heading">Заранее</h2>
                  <p className="cook-setup__hint">
                    Напоминания о разморозке, достаньте из холодильника, маринаде
                  </p>
                  <ul className="cook-prep-list">
                    {prep.map((item, i) => (
                      <li key={`${i}-${item.type}-${item.text.slice(0, 24)}`} className="cook-prep-item">
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
              </aside>
            ) : (
              <aside className="cook-setup__aside cook-setup__aside--outline" aria-label="Шаги">
                <h2 className="cook-setup__heading">Шаги</h2>
                {stepList}
              </aside>
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
              <button type="button" className="btn-primary" onClick={beginCooking}>
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
        ) : steps.length === 0 ? (
          <div className="cook-complete">
            <h2>Нет шагов</h2>
            <p>У этого рецепта нет шагов для режима готовки.</p>
            <button type="button" className="btn-primary" onClick={close}>
              Закрыть
            </button>
          </div>
        ) : (
          <div className="cook-steps">
            <div className="cook-steps__main">
              <div className="cook-progress" aria-hidden>
                <div className="cook-progress__bar" style={{ width: `${progressPct}%` }} />
              </div>
              <div className="cook-progress__label" aria-live="polite">
                Шаг {index + 1} из {steps.length}
              </div>
              <article className={`cook-step-card${done.has(index) ? ' is-done' : ''}`}>
                <p className="cook-step-card__text">{step?.text}</p>
                {step?.target_internal_temperature_c != null && (
                  <span className="temp-chip">цель {step.target_internal_temperature_c} °C</span>
                )}
                {step?.pull_internal_temperature_c != null && (
                  <span className="temp-chip">снятие {step.pull_internal_temperature_c} °C</span>
                )}
                {timerSec > 0 && (
                  <div className={`cook-step-timer${countdown.running ? ' is-running' : ''}`}>
                    <div>{step.timer_label || formatDuration(timerSec)}</div>
                    <div className="cook-step-timer__display" aria-live="polite">
                      {formatClock(shownSeconds)}
                    </div>
                    {step.timer_note && <p className="note">{step.timer_note}</p>}
                    {!countdown.running && (
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
                    <div className="cook-timer-actions">
                      {countdown.running ? (
                        <>
                          <button type="button" className="btn-secondary" onClick={countdown.pause}>
                            Пауза
                          </button>
                          <button type="button" className="btn-secondary" onClick={resetTimer}>
                            Сброс
                          </button>
                        </>
                      ) : (
                        <button type="button" className="btn-primary" onClick={startTimer}>
                          {remainingSeconds != null &&
                          remainingSeconds < timerSec &&
                          remainingSeconds > 0
                            ? 'Продолжить'
                            : `Старт ${formatDuration(timerSec)}`}
                        </button>
                      )}
                    </div>
                  </div>
                )}
              </article>
              <label className="cook-step-check">
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
    </dialog>
  );
}
