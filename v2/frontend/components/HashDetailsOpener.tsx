'use client';

import { useEffect } from 'react';

/** Opens a matching `<details id>` (and ancestor details) when the URL hash points at it. */
export function HashDetailsOpener({
  watch,
  exclusive,
}: {
  watch?: unknown;
  exclusive?: string;
} = {}) {
  useEffect(() => {
    const openFromHash = () => {
      const id = decodeURIComponent(window.location.hash.replace(/^#/, ''));
      if (!id) return;
      const el = document.getElementById(id);
      if (!el) return;
      if (el instanceof HTMLDetailsElement && exclusive) {
        document.querySelectorAll(exclusive).forEach((node) => {
          if (node instanceof HTMLDetailsElement && node !== el) node.open = false;
        });
      }
      let node: HTMLElement | null = el;
      while (node) {
        if (node instanceof HTMLDetailsElement) {
          node.open = true;
        }
        node = node.parentElement;
      }
    };
    openFromHash();
    window.addEventListener('hashchange', openFromHash);
    return () => window.removeEventListener('hashchange', openFromHash);
  }, [watch, exclusive]);
  return null;
}
