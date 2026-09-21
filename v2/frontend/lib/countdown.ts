'use client';

import { useCallback, useEffect, useRef, useState } from 'react';

export function useCountdown(onComplete?: () => void) {
  const [endsAtMs, setEndsAtMs] = useState<number | null>(null);
  const [pausedMs, setPausedMs] = useState<number | null>(null);
  const [now, setNow] = useState(() => Date.now());
  const finishedRef = useRef(false);
  const endsAtRef = useRef(endsAtMs);
  const onCompleteRef = useRef(onComplete);
  endsAtRef.current = endsAtMs;
  onCompleteRef.current = onComplete;

  const remainingMs = endsAtMs != null ? Math.max(0, endsAtMs - now) : pausedMs;
  const running = endsAtMs != null;

  const startMs = useCallback((ms: number) => {
    finishedRef.current = false;
    setPausedMs(null);
    setEndsAtMs(Date.now() + Math.max(0, ms));
    setNow(Date.now());
  }, []);

  const pause = useCallback(() => {
    const end = endsAtRef.current;
    if (end == null) return;
    setPausedMs(Math.max(0, end - Date.now()));
    setEndsAtMs(null);
  }, []);

  const reset = useCallback((ms: number) => {
    finishedRef.current = false;
    setEndsAtMs(null);
    setPausedMs(Math.max(0, ms));
  }, []);

  const stop = useCallback(() => {
    finishedRef.current = false;
    setEndsAtMs(null);
    setPausedMs(null);
  }, []);

  useEffect(() => {
    if (!running) return undefined;
    const tick = () => setNow(Date.now());
    tick();
    const timer = window.setInterval(tick, 250);
    return () => window.clearInterval(timer);
  }, [running]);

  useEffect(() => {
    if (!running || remainingMs == null || remainingMs > 0) return;
    if (finishedRef.current) return;
    finishedRef.current = true;
    setEndsAtMs(null);
    setPausedMs(0);
    onCompleteRef.current?.();
  }, [running, remainingMs]);

  return {
    running,
    remainingMs,
    remainingSeconds: remainingMs == null ? null : Math.ceil(remainingMs / 1000),
    startMs,
    pause,
    reset,
    stop,
  };
}
