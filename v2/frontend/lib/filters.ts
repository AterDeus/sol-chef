import type { PantryGroup, SearchParamsRecord } from './types';
import {
  bookChapterById,
  chapterIdForBase,
  HAVE_GROUP_BOOK_PRIORITY,
  HAVE_GROUP_TO_BOOK,
  type BookChapter,
} from './vocab';

export const FILTER_KEYS = [
  'protein_base',
  'cook_method',
  'dish_type',
  'equipment',
  'cuts',
  'without',
  'have',
  'have_group',
  'intent',
] as const;
export type FilterKey = (typeof FILTER_KEYS)[number];

/** First-level pantry chips. Keep in sync with HAVE_UI_GROUPS. Opens a picker, not inventory. */
const PICKER_ONLY_HAVE_GROUPS = new Set([
  'chicken',
  'meat',
  'fish',
  'veg',
  'grains',
  'eggs',
  'dairy',
  'other',
]);

const CSV_KEYS = new Set([
  'protein_base',
  'cook_method',
  'dish_type',
  'equipment',
  'cuts',
  'without',
  'have',
  'have_group',
  'intent',
  'use_case',
  'quick',
  'missed',
]);

export function valuesOf(sp: SearchParamsRecord, key: string): string[] {
  const raw = sp[key];
  if (raw == null || raw === '') return [];
  const list = Array.isArray(raw) ? raw : [raw];
  if (!CSV_KEYS.has(key)) {
    return list.map((item) => item.trim()).filter(Boolean);
  }
  return list
    .flatMap((item) => item.split(','))
    .map((item) => item.trim())
    .filter(Boolean);
}

export function toURLSearchParams(sp: SearchParamsRecord): URLSearchParams {
  const qs = new URLSearchParams();
  for (const [key, raw] of Object.entries(sp)) {
    if (raw == null || raw === '') continue;
    for (const item of valuesOf({ [key]: raw }, key)) {
      qs.append(key, item);
    }
  }
  return qs;
}

export function hasAnyQuery(sp: SearchParamsRecord): boolean {
  return toURLSearchParams(sp).toString().length > 0;
}

export function hasCalculatorQuery(sp: SearchParamsRecord): boolean {
  return FILTER_KEYS.some((key) => {
    const values = valuesOf(sp, key);
    if (values.length === 0) return false;
    if (key === 'have_group') {
      return values.some((id) => !PICKER_ONLY_HAVE_GROUPS.has(id));
    }
    return true;
  });
}

export function queryString(sp: SearchParamsRecord): string {
  return toURLSearchParams(sp).toString();
}

export function isSelected(sp: SearchParamsRecord, key: string, value: string): boolean {
  return valuesOf(sp, key).includes(value);
}

export function toggleHref(
  pathname: string,
  sp: SearchParamsRecord,
  key: string,
  value: string,
): string {
  const qs = toURLSearchParams(sp);
  const current = qs.getAll(key);
  qs.delete(key);
  if (current.includes(value)) {
    current.filter((item) => item !== value).forEach((item) => qs.append(key, item));
  } else {
    current.forEach((item) => qs.append(key, item));
    qs.append(key, value);
  }
  qs.delete('page');
  if (key === 'protein_base') {
    qs.delete('cuts');
  }
  const next = qs.toString();
  return next ? `${pathname}?${next}` : pathname;
}

const DROP_WHEN: Record<string, string[]> = {
  chapter: ['protein_base', 'cook_method', 'equipment', 'cuts', 'page'],
  protein_base: ['cook_method', 'equipment', 'cuts', 'page'],
  cook_method: ['equipment', 'page'],
  equipment: ['page'],
};

export function resolveBookChapter(sp: SearchParamsRecord): {
  chapter: BookChapter | null;
  selectedBases: string[];
} {
  const chapterId = valuesOf(sp, 'chapter')[0];
  const selected = valuesOf(sp, 'protein_base');
  let chapter = bookChapterById(chapterId) ?? null;
  if (!chapter && selected.length) {
    chapter = bookChapterById(chapterIdForBase(selected[0])) ?? null;
  }
  const selectedBases = chapter
    ? selected.filter((code) =>
        chapter.bases.length
          ? (chapter.bases as readonly string[]).includes(code)
          : true,
      )
    : selected;
  return { chapter, selectedBases };
}

export function setHref(
  pathname: string,
  sp: SearchParamsRecord,
  key: string,
  value: string | null,
): string {
  const qs = toURLSearchParams(sp);
  for (const drop of DROP_WHEN[key] ?? ['page']) {
    qs.delete(drop);
  }
  qs.delete(key);
  if (value) qs.set(key, value);
  const next = qs.toString();
  return next ? `${pathname}?${next}` : pathname;
}

export function withPage(pathname: string, sp: SearchParamsRecord, page: number): string {
  const qs = toURLSearchParams(sp);
  if (page <= 1) qs.delete('page');
  else qs.set('page', String(page));
  const next = qs.toString();
  return next ? `${pathname}?${next}` : pathname;
}

const CATALOG_FROM_CALCULATOR_KEYS = [
  'protein_base',
  'cook_method',
  'dish_type',
  'equipment',
  'cuts',
  'without',
] as const;

function groupIdsForHave(groups: PantryGroup[], canonicalId: string): string[] {
  const ids: string[] = [];
  for (const group of groups) {
    if (group.items?.some((item) => item.canonical_id === canonicalId)) {
      ids.push(group.id);
    }
    for (const child of group.children ?? []) {
      if (child.items?.some((item) => item.canonical_id === canonicalId)) {
        ids.push(child.id);
        ids.push(group.id);
      }
    }
  }
  return ids;
}

function bookFromHave(
  sp: SearchParamsRecord,
  groups: PantryGroup[],
): { chapter: string; protein_base?: string } | null {
  const ids = new Set<string>();
  for (const haveId of valuesOf(sp, 'have')) {
    for (const groupId of groupIdsForHave(groups, haveId)) ids.add(groupId);
  }
  for (const groupId of valuesOf(sp, 'have_group')) ids.add(groupId);
  for (const groupId of HAVE_GROUP_BOOK_PRIORITY) {
    if (ids.has(groupId) && HAVE_GROUP_TO_BOOK[groupId]) {
      return HAVE_GROUP_TO_BOOK[groupId];
    }
  }
  return null;
}

/** Book URL for «Посмотреть все подходящие». Drops have/intent; catalog rejects those. */
export function catalogHrefFromCalculator(
  sp: SearchParamsRecord,
  groups: PantryGroup[],
): string | null {
  const qs = new URLSearchParams();
  for (const key of CATALOG_FROM_CALCULATOR_KEYS) {
    for (const value of valuesOf(sp, key)) {
      qs.append(key, value);
    }
  }
  const mapped = bookFromHave(sp, groups);
  if (mapped) {
    if (!qs.has('chapter')) qs.set('chapter', mapped.chapter);
    const chapter = bookChapterById(mapped.chapter);
    const alreadyProtein = valuesOf(sp, 'protein_base').length > 0;
    if (mapped.protein_base && !alreadyProtein) {
      const n = chapter?.bases.length ?? 0;
      if (n !== 1) qs.append('protein_base', mapped.protein_base);
    }
  } else if (valuesOf(sp, 'protein_base').length && !qs.has('chapter')) {
    qs.set('chapter', chapterIdForBase(valuesOf(sp, 'protein_base')[0]));
  }
  const next = qs.toString();
  return next ? `/recipes?${next}` : null;
}

export function recipeHref(
  slug: string,
  opts: {
    variant?: string | null;
    equipment?: string | null;
    prep?: string | null;
    day?: number | string | null;
    meal?: string | null;
    servings?: number | string | null;
    noLeftover?: boolean;
    piece?: string | null;
  } = {},
): string {
  const qs = new URLSearchParams();
  if (opts.variant) qs.set('variant', opts.variant);
  if (opts.equipment) qs.set('equipment', opts.equipment);
  if (opts.prep) qs.set('prep', opts.prep);
  if (opts.day != null && opts.day !== '') qs.set('day', String(opts.day));
  if (opts.meal) qs.set('meal', opts.meal);
  if (opts.servings != null && opts.servings !== '') qs.set('servings', String(opts.servings));
  if (opts.noLeftover) qs.set('no_leftover', '1');
  if (opts.piece) qs.set('piece', opts.piece);
  const suffix = qs.toString() ? `?${qs.toString()}` : '';
  return `/recipes/${slug}${suffix}`;
}

function collectHaveIds(group: PantryGroup): string[] {
  const own = (group.items ?? []).map((item) => item.canonical_id);
  return [...own, ...(group.children ?? []).flatMap(collectHaveIds)];
}

function findGroup(groups: PantryGroup[], id: string): PantryGroup | undefined {
  for (const group of groups) {
    if (group.id === id) return group;
    const child = group.children?.find((item) => item.id === id);
    if (child) return child;
  }
  return undefined;
}

function findParent(groups: PantryGroup[], id: string): PantryGroup | undefined {
  return groups.find((group) => (group.children ?? []).some((child) => child.id === id));
}

/** Toggle a pantry group, keeping meat → species → cut nested. */
export function toggleHaveGroupHref(
  pathname: string,
  sp: SearchParamsRecord,
  groupId: string,
  tree: PantryGroup[],
): string {
  const qs = toURLSearchParams(sp);
  const current = qs.getAll('have_group');
  const node = findGroup(tree, groupId);
  const parent = findParent(tree, groupId);
  const childIds = new Set((node?.children ?? []).map((child) => child.id));
  const childSelected = [...childIds].some((id) => current.includes(id));
  const selected = current.includes(groupId);
  const turningOff = selected || (!parent && childSelected);
  const dropHave = new Set(node ? collectHaveIds(node) : []);

  let nextGroups = current.filter((id) => id !== groupId);
  if (turningOff) {
    nextGroups = nextGroups.filter((id) => !childIds.has(id));
    if (parent && !nextGroups.includes(parent.id)) {
      const siblings = (parent.children ?? []).map((child) => child.id);
      if (!siblings.some((id) => nextGroups.includes(id))) {
        nextGroups.push(parent.id);
      }
    }
  } else {
    nextGroups.push(groupId);
    if (parent) {
      nextGroups = nextGroups.filter((id) => id !== parent.id);
    }
  }

  qs.delete('have_group');
  nextGroups.forEach((id) => qs.append('have_group', id));

  if (turningOff && dropHave.size > 0) {
    const have = qs.getAll('have').filter((id) => !dropHave.has(id));
    qs.delete('have');
    have.forEach((id) => qs.append('have', id));
  }

  qs.delete('page');
  const next = qs.toString();
  return next ? `${pathname}?${next}` : pathname;
}
