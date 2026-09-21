import type { RecipeCardData, SearchParamsRecord } from './types';
import { valuesOf } from './filters';
import { recipeProteinCodes } from './vocab';

export const QUICK_FILTERS = [
  { id: 'fast', label: 'до 30 минут', param: 'max_minutes', value: '30' },
  { id: 'skillet', label: 'сковорода', param: 'quick', value: 'skillet' },
  { id: 'oven', label: 'духовка', param: 'quick', value: 'oven' },
  { id: 'one_pan', label: 'одна кастрюля', param: 'use_case', value: 'one_pan' },
  { id: 'no_milk', label: 'без молока', param: 'without', value: 'milk' },
  { id: 'no_gluten', label: 'без глютена', param: 'without', value: 'gluten' },
  { id: 'veg', label: 'вегетарианское', param: 'diet', value: 'vegetarian' },
  { id: 'budget', label: 'бюджетно', param: 'use_case', value: 'budget' },
] as const;

const ANIMAL_PROTEIN = new Set([
  'beef',
  'pork',
  'poultry',
  'lamb',
  'offal',
  'seafood',
  'fish_white_sea',
  'fish_red_sea',
  'fish_river',
  'fish_canned',
]);

export function isVegetarianRecipe(recipe: RecipeCardData): boolean {
  return recipeProteinCodes(recipe).every((code) => !ANIMAL_PROTEIN.has(code));
}

function isSkilletRecipe(recipe: RecipeCardData): boolean {
  return recipe.cook_method === 'pan_fry' || recipe.equipment === 'skillet';
}

function isOvenRecipe(recipe: RecipeCardData): boolean {
  return recipe.cook_method === 'oven' || recipe.equipment === 'oven';
}

function matchQuick(recipe: RecipeCardData, code: string): boolean {
  if (code === 'skillet') return isSkilletRecipe(recipe);
  if (code === 'oven') return isOvenRecipe(recipe);
  return false;
}

export function normalizeCatalogQuery(value: string): string {
  return value.toLowerCase().replace(/ё/g, 'е').replace(/\s+/g, ' ').trim();
}

export function minutesLabel(total: number | null | undefined): string | null {
  if (total == null || !Number.isFinite(total) || total <= 0) return null;
  return `~${Math.round(total)} мин`;
}

export function effortLabel(level: number | null | undefined): string | null {
  if (level == null || !Number.isInteger(level) || level < 1 || level > 5) return null;
  if (level <= 2) return 'просто';
  if (level === 3) return 'средне';
  return 'сложнее';
}

export function solutionTimeLabel(
  profile?: { total_minutes: number | null; active_minutes: number | null } | null,
): string | null {
  const total = profile?.total_minutes;
  if (total == null || !Number.isFinite(total) || total <= 0) return null;
  const rounded = Math.round(total);
  const active = profile?.active_minutes;
  if (active != null && Number.isFinite(active) && active > 0 && active < total) {
    return `${rounded} мин, из них ${Math.round(active)} у плиты`;
  }
  return `${rounded} мин`;
}

export function hasQuickFilters(sp: SearchParamsRecord): boolean {
  return (
    valuesOf(sp, 'max_minutes').length > 0 ||
    valuesOf(sp, 'diet').length > 0 ||
    valuesOf(sp, 'use_case').length > 0 ||
    valuesOf(sp, 'quick').length > 0 ||
    valuesOf(sp, 'without').length > 0 ||
    valuesOf(sp, 'q').length > 0
  );
}

export function matchesCatalogExtras(recipe: RecipeCardData, sp: SearchParamsRecord): boolean {
  const maxMinutes = Number(valuesOf(sp, 'max_minutes')[0] || '');
  if (Number.isFinite(maxMinutes) && maxMinutes > 0) {
    const total = recipe.time_profile?.total_minutes;
    if (total == null || total > maxMinutes) return false;
  }
  if (valuesOf(sp, 'diet').includes('vegetarian') && !isVegetarianRecipe(recipe)) {
    return false;
  }
  const useCases = valuesOf(sp, 'use_case');
  if (useCases.length > 0) {
    const have = new Set(recipe.use_cases ?? []);
    if (!useCases.some((code) => have.has(code))) return false;
  }
  const quick = valuesOf(sp, 'quick');
  if (quick.length > 0 && !quick.some((code) => matchQuick(recipe, code))) {
    return false;
  }
  const q = normalizeCatalogQuery(valuesOf(sp, 'q')[0] ?? '');
  if (q) {
    const hay = normalizeCatalogQuery(`${recipe.title} ${recipe.summary ?? ''}`);
    if (!hay.includes(q)) return false;
  }
  return true;
}

export function activeFilterChips(
  sp: SearchParamsRecord,
): Array<{ key: string; value: string; label: string }> {
  const chips: Array<{ key: string; value: string; label: string }> = [];
  for (const item of QUICK_FILTERS) {
    if (valuesOf(sp, item.param).includes(item.value)) {
      chips.push({ key: item.param, value: item.value, label: item.label });
    }
  }
  return chips;
}
