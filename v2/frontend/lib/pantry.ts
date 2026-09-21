import type { PantryGroup } from './types';

/** Human path for a pantry canonical id, e.g. «Птица · Курица». */
export function pantryItemPath(groups: PantryGroup[], canonicalId: string): string {
  for (const group of groups) {
    const own = group.items?.find((item) => item.canonical_id === canonicalId);
    if (own) return `${group.title} · ${own.title}`;
    for (const child of group.children ?? []) {
      const nested = child.items?.find((item) => item.canonical_id === canonicalId);
      if (nested) return `${group.title} · ${child.title} · ${nested.title}`;
    }
  }
  return canonicalId;
}
