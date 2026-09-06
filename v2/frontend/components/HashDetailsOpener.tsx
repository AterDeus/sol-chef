'use client';

import { useEffect } from 'react';

/** Opens a matching `<details id>` when the URL hash points at it. */
export function HashDetailsOpener() {
  useEffect(() => {
    const openFromHash = () => {
      const id = decodeURIComponent(window.location.hash.replace(/^#/, ''));
      if (!id) return;
      const el = document.getElementById(id);
      if (el instanceof HTMLDetailsElement) {
        el.open = true;
      }
    };
    openFromHash();
    window.addEventListener('hashchange', openFromHash);
    return () => window.removeEventListener('hashchange', openFromHash);
  }, []);
  return null;
}
