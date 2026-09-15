import type { TipItem, TipsPayload } from './types';
import { TIP_KIND, TIP_TAG, labelOf } from './vocab';

export type TipsQuery = {
  q: string;
  kind: string;
  section: string;
  tag: string;
};

export type NormalizedTip = {
  id: string;
  sectionId: string;
  sectionTitle: string;
  hint: string;
  explanation?: string;
  kind?: string;
  tags: string[];
};

export const TIP_KIND_CODES = Object.keys(TIP_KIND);
export const TIP_TAG_CODES = Object.keys(TIP_TAG);

export function padTipIndex(index: number): string {
  return String(index).padStart(2, '0');
}

export function tipDomId(id: string): string {
  return id.startsWith('tip-') ? id : `tip-${id}`;
}

export function tipHashHref(id: string): string {
  return `/tips#${tipDomId(id)}`;
}

export function normalizeSearch(value: string): string {
  return value.toLowerCase().replace(/ё/g, 'е').replace(/\s+/g, ' ').trim();
}

export function isKnownKind(code: string): boolean {
  return Boolean(code && TIP_KIND[code]);
}

export function isKnownTag(code: string): boolean {
  return Boolean(code && TIP_TAG[code]);
}

export function tipKindLabel(kind?: string): string | undefined {
  if (!kind) return undefined;
  return TIP_KIND[kind];
}

export function previewExplanation(text: string): string {
  const trimmed = text.trim();
  const match = trimmed.match(/^.+?[.!?…](?:["»“”']+)?(?=\s|$)/);
  return match ? match[0].trim() : trimmed;
}

function asRecord(item: TipItem): { hint: string; explanation?: string; id?: string; kind?: string; tags: string[] } {
  if (typeof item === 'string') {
    return { hint: item, tags: [] };
  }
  const tags = Array.isArray(item.tags) ? item.tags.filter((tag) => tag.length > 0) : [];
  return {
    hint: item.hint,
    explanation: item.explanation?.trim() || undefined,
    id: item.id?.trim() || undefined,
    kind: item.kind?.trim() || undefined,
    tags,
  };
}

export function resolveTipId(sectionId: string, item: TipItem, index: number): string {
  const rec = asRecord(item);
  if (rec.id) return rec.id.replace(/^tip-/, '');
  return `${sectionId}-${padTipIndex(index + 1)}`;
}

export function normalizeTip(
  section: { id: string; title: string },
  item: TipItem,
  index: number,
): NormalizedTip {
  const rec = asRecord(item);
  return {
    id: resolveTipId(section.id, item, index),
    sectionId: section.id,
    sectionTitle: section.title,
    hint: rec.hint,
    explanation: rec.explanation,
    kind: rec.kind,
    tags: rec.tags,
  };
}

export function flattenTips(payload: TipsPayload): NormalizedTip[] {
  const all: NormalizedTip[] = [];
  for (const section of payload.sections ?? []) {
    (section.items ?? []).forEach((item, index) => {
      all.push(normalizeTip(section, item, index));
    });
  }
  return all;
}

function searchBlob(tip: NormalizedTip): string {
  const kindLabel = tip.kind ? labelOf(TIP_KIND, tip.kind) : '';
  const tagLabels = tip.tags.map((tag) => labelOf(TIP_TAG, tag));
  return [tip.hint, tip.explanation ?? '', kindLabel, ...tagLabels, tip.sectionTitle].join(' ');
}

export function filterTips(items: NormalizedTip[], query: TipsQuery): NormalizedTip[] {
  const needle = normalizeSearch(query.q);
  return items.filter((tip) => {
    if (query.kind && tip.kind !== query.kind) return false;
    if (query.section && tip.sectionId !== query.section) return false;
    if (query.tag && !tip.tags.includes(query.tag)) return false;
    if (!needle) return true;
    return normalizeSearch(searchBlob(tip)).includes(needle);
  });
}

export function groupedTips(
  sections: Array<{ id: string; title: string }>,
  items: NormalizedTip[],
): Array<{ id: string; title: string; items: NormalizedTip[] }> {
  const buckets = new Map<string, NormalizedTip[]>();
  for (const item of items) {
    const list = buckets.get(item.sectionId);
    if (list) list.push(item);
    else buckets.set(item.sectionId, [item]);
  }
  return sections
    .map((section) => ({
      id: section.id,
      title: section.title,
      items: buckets.get(section.id) ?? [],
    }))
    .filter((section) => section.items.length > 0);
}

export function tagsInSet(items: NormalizedTip[]): string[] {
  const present = new Set<string>();
  for (const item of items) {
    for (const tag of item.tags) {
      if (isKnownTag(tag)) present.add(tag);
    }
  }
  return TIP_TAG_CODES.filter((code) => present.has(code));
}

export function sectionCounts(
  items: NormalizedTip[],
  query: TipsQuery,
  sectionIds: string[],
): Map<string, number> {
  const withoutSection = filterTips(items, { ...query, section: '' });
  const map = new Map<string, number>();
  for (const id of sectionIds) map.set(id, 0);
  for (const item of withoutSection) {
    map.set(item.sectionId, (map.get(item.sectionId) || 0) + 1);
  }
  return map;
}

export function tipsListHref(query: TipsQuery): string {
  const params = new URLSearchParams();
  const q = query.q.trim();
  if (q) params.set('q', q);
  if (query.kind && isKnownKind(query.kind)) params.set('kind', query.kind);
  if (query.section) params.set('section', query.section);
  if (query.tag && isKnownTag(query.tag)) params.set('tag', query.tag);
  const qs = params.toString();
  return qs ? `/tips?${qs}` : '/tips';
}
