'use client';

import { useRouter } from 'next/navigation';
import type { ReactNode } from 'react';

export function FilterChip({
  href,
  pressed,
  children,
  ariaLabel,
}: {
  href: string;
  pressed: boolean;
  children: ReactNode;
  ariaLabel?: string;
}) {
  const router = useRouter();
  return (
    <button
      type="button"
      className={pressed ? 'chip is-active' : 'chip'}
      aria-pressed={pressed}
      aria-label={ariaLabel}
      onClick={() => router.push(href)}
    >
      {children}
    </button>
  );
}
