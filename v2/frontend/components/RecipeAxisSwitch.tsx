'use client';

import Link from 'next/link';
import { useLayoutEffect, type MouseEvent, type ReactNode } from 'react';

let pending: { y: number; top: number; href: string } | null = null;

function pinScroll(y: number) {
  const html = document.documentElement;
  const previous = html.style.scrollBehavior;
  html.style.scrollBehavior = 'auto';
  window.scrollTo(0, y);
  html.style.scrollBehavior = previous;
}

function restoreFrom(snapshot: { y: number; top: number; href: string }) {
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
  useLayoutEffect(() => {
    if (!pending) return;
    const snapshot = pending;
    pending = null;
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

  return <>{children}</>;
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
  return (
    <Link
      href={href}
      scroll={false}
      className={className}
      aria-current={current ? 'true' : undefined}
      aria-pressed={current}
      data-axis-href={href}
      onClick={(event: MouseEvent<HTMLAnchorElement>) => {
        if (
          event.defaultPrevented ||
          event.button !== 0 ||
          event.metaKey ||
          event.altKey ||
          event.ctrlKey ||
          event.shiftKey
        ) {
          return;
        }
        pending = {
          y: window.scrollY,
          top: event.currentTarget.getBoundingClientRect().top,
          href,
        };
      }}
    >
      {children}
    </Link>
  );
}
