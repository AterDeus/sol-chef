import type { RecipeCardData, TipItem, TipsPayload } from './types';

export const HOME_SAMPLE_SIZE = 6;

export type FeaturedTip = {
  sectionId: string;
  sectionTitle: string;
  hint: string;
  explanation?: string;
};

function tipHint(item: TipItem): string {
  return typeof item === 'string' ? item : item.hint;
}

function tipExplanation(item: TipItem): string | undefined {
  if (typeof item === 'string') return undefined;
  const text = item.explanation?.trim();
  return text || undefined;
}

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
  const all: FeaturedTip[] = [];
  for (const section of payload.sections ?? []) {
    for (const item of section.items) {
      all.push({
        sectionId: section.id,
        sectionTitle: section.title,
        hint: tipHint(item),
        explanation: tipExplanation(item),
      });
    }
  }
  return all;
}

export function pickRandomTips(payload: TipsPayload, n = HOME_SAMPLE_SIZE): FeaturedTip[] {
  return sample(flattenTips(payload), n);
}
