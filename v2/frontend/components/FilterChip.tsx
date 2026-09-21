'use client';

import Link from 'next/link';
import type { ReactNode } from 'react';
import { captureScrollClick } from '@/lib/keep-scroll';

export function FilterChip({
  href,
  selected,
  children,
  ariaLabel,
  hint,
}: {
  href: string;
  selected: boolean;
  children: ReactNode;
  ariaLabel?: string;
  hint?: string;
}) {
  return (
    <Link
      href={href}
      scroll={false}
      className={selected ? 'chip is-active' : 'chip'}
      aria-label={ariaLabel}
      aria-current={selected ? 'page' : undefined}
      title={hint}
      onClick={captureScrollClick}
    >
      {children}
    </Link>
  );
}
