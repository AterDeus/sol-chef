'use client';

import { useLayoutEffect, type MouseEvent } from 'react';
import { usePathname, useSearchParams } from 'next/navigation';

let pendingY: number | null = null;

function pinScroll(y: number) {
  const html = document.documentElement;
  const previous = html.style.scrollBehavior;
  html.style.scrollBehavior = 'auto';
  window.scrollTo(0, y);
  html.style.scrollBehavior = previous;
}

export function captureScrollClick(event: MouseEvent<HTMLAnchorElement>) {
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
  pendingY = window.scrollY;
}

/** Restore scroll after in-page query navigation (filter chips). */
export function KeepScrollOnQuery() {
  const pathname = usePathname();
  const search = useSearchParams();
  const key = `${pathname}?${search}`;

  useLayoutEffect(() => {
    if (pendingY == null) return;
    const y = pendingY;
    pendingY = null;
    pinScroll(y);
    let inner = 0;
    const outer = requestAnimationFrame(() => {
      pinScroll(y);
      inner = requestAnimationFrame(() => pinScroll(y));
    });
    return () => {
      cancelAnimationFrame(outer);
      cancelAnimationFrame(inner);
    };
  }, [key]);

  return null;
}
