'use client';

import Link from 'next/link';
import {
  createContext,
  useCallback,
  useContext,
  useLayoutEffect,
  useRef,
  type MouseEvent,
  type MutableRefObject,
  type ReactNode,
} from 'react';

type AxisSnapshot = { y: number; top: number; href: string };

const AxisScrollContext = createContext<MutableRefObject<AxisSnapshot | null> | null>(null);

function pinScroll(y: number) {
  const html = document.documentElement;
  const previous = html.style.scrollBehavior;
  html.style.scrollBehavior = 'auto';
  window.scrollTo(0, y);
  html.style.scrollBehavior = previous;
}

function restoreFrom(snapshot: AxisSnapshot) {
  const chip = document.querySelector(`[data-axis-href="${CSS.escape(snapshot.href)}"]`);
  if (chip instanceof HTMLElement) {
    const drift = chip.getBoundingClientRect().top - snapshot.top;
    if (Math.abs(drift) > 1) {
      pinScroll(window.scrollY + drift);
    }
    return;
  }
  pinScroll(snapshot.y);
}

export function RecipeAxisSwitch({
  applied,
  children,
}: {
  applied: string;
  children: ReactNode;
}) {
  const pendingRef = useRef<AxisSnapshot | null>(null);

  useLayoutEffect(() => {
    const snapshot = pendingRef.current;
    if (!snapshot) return;
    pendingRef.current = null;
    restoreFrom(snapshot);
    let inner = 0;
    const outer = requestAnimationFrame(() => {
      restoreFrom(snapshot);
      inner = requestAnimationFrame(() => restoreFrom(snapshot));
    });
    return () => {
      cancelAnimationFrame(outer);
      cancelAnimationFrame(inner);
    };
  }, [applied]);

  return <AxisScrollContext.Provider value={pendingRef}>{children}</AxisScrollContext.Provider>;
}

export function RecipeAxisLink({
  href,
  className,
  children,
  current,
}: {
  href: string;
  className?: string;
  children: ReactNode;
  current?: boolean;
}) {
  const pendingRef = useContext(AxisScrollContext);
  const capture = useCallback(
    (event: MouseEvent<HTMLAnchorElement>) => {
      if (
        event.defaultPrevented ||
        event.button !== 0 ||
        event.metaKey ||
        event.altKey ||
        event.ctrlKey ||
        event.shiftKey ||
        !pendingRef
      ) {
        return;
      }
      pendingRef.current = {
        y: window.scrollY,
        top: event.currentTarget.getBoundingClientRect().top,
        href,
      };
    },
    [href, pendingRef],
  );

  return (
    <Link
      href={href}
      scroll={false}
      className={className}
      aria-current={current ? 'page' : undefined}
      data-axis-href={href}
      onClick={capture}
    >
      {children}
    </Link>
  );
}
