import type { PantryGroup, SearchParamsRecord } from './types';

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
  protein_base: ['cook_method', 'equipment', 'cuts', 'page'],
  cook_method: ['equipment', 'page'],
  equipment: ['page'],
};

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

export function recipeHref(
  slug: string,
  opts: { variant?: string | null; equipment?: string | null } = {},
): string {
  const qs = new URLSearchParams();
  if (opts.variant) qs.set('variant', opts.variant);
  if (opts.equipment) qs.set('equipment', opts.equipment);
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
