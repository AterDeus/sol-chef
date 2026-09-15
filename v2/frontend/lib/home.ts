import type { RecipeCardData, TipsPayload } from './types';
import { flattenTips as flattenAllTips } from './tips';

export const HOME_SAMPLE_SIZE = 6;

const TIP_SECTION_ICON: Record<string, string> = {
  '01': 'clipboard-list',
  '02': 'utensils',
  '03': 'flame',
  '04': 'droplets',
  '05': 'snowflake',
  '06': 'scale',
  '07': 'sun',
  '08': 'chef-hat',
  '09': 'beef',
  '10': 'circle-check',
  '11': 'drumstick',
  '12': 'wheat',
  '13': 'shopping-basket',
  '14': 'flask-conical',
  '15': 'timer',
  '16': 'book-open-text',
};

export function tipSectionIcon(sectionId: string): string {
  return TIP_SECTION_ICON[sectionId] ?? 'chef-hat';
}

export type FeaturedTip = {
  id: string;
  sectionId: string;
  sectionTitle: string;
  hint: string;
  explanation?: string;
};

function randomInt(maxExclusive: number): number {
  const buf = new Uint32Array(1);
  globalThis.crypto.getRandomValues(buf);
  return buf[0] % maxExclusive;
}

function withoutWhy(recipe: RecipeCardData): RecipeCardData {
  return {
    ...recipe,
    why: undefined,
    score: undefined,
    applied_axes: undefined,
    shopping_delta: undefined,
    substitutions: undefined,
    bucket: undefined,
  };
}

function sample<T>(items: T[], n: number): T[] {
  const copy = [...items];
  for (let i = copy.length - 1; i > 0; i -= 1) {
    const j = randomInt(i + 1);
    const current = copy[i];
    copy[i] = copy[j];
    copy[j] = current;
  }
  return copy.slice(0, Math.min(n, copy.length));
}

export function pickRandomRecipes(
  results: RecipeCardData[],
  n = HOME_SAMPLE_SIZE,
): RecipeCardData[] {
  return sample(results, n).map(withoutWhy);
}

export function flattenTips(payload: TipsPayload): FeaturedTip[] {
  return flattenAllTips(payload).map((tip) => ({
    id: tip.id,
    sectionId: tip.sectionId,
    sectionTitle: tip.sectionTitle,
    hint: tip.hint,
    explanation: tip.explanation,
  }));
}

export function pickRandomTips(payload: TipsPayload, n = HOME_SAMPLE_SIZE): FeaturedTip[] {
  return sample(flattenTips(payload), n);
}
