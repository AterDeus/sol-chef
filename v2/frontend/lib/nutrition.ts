import { applyMode } from '@/lib/scale';
import type {
  NutritionMacros,
  RecipeIngredient,
  RecipeNutrition,
} from '@/lib/types';

const SKIP_UNITS = new Set(['pinch', 'to_taste']);

export type NutritionContribution = NutritionMacros & { grams: number };

export type ComputeNutritionOptions = {
  ratio: number;
  servings?: number | null;
  yieldWeightG?: number | null;
};

function skippedFromNutrition(line: RecipeIngredient): boolean {
  if (line.optional === true) return true;
  if (line.nutrition_exclude === true) return true;
  if (SKIP_UNITS.has(line.unit)) return true;
  return false;
}

export function gramsAfterScale(line: RecipeIngredient, ratio: number): number | null {
  if (line.nutrition_line == null || line.amount == null) return null;
  const factor = line.nutrition_line.nutrition_factor ?? 1;
  return (
    applyMode(line.amount, ratio, line.scale_mode, line.scalable) *
    line.nutrition_line.grams_per_unit *
    factor
  );
}

export function contribute(
  line: RecipeIngredient,
  ratio: number,
): NutritionContribution | null {
  if (skippedFromNutrition(line)) return null;
  const grams = gramsAfterScale(line, ratio);
  if (grams == null) return null;
  const n = line.nutrition_line;
  if (n == null) return null;
  const factor = grams / 100;
  return {
    kcal: n.kcal_per_100g * factor,
    protein_g: n.protein_g_per_100g * factor,
    fat_g: n.fat_g_per_100g * factor,
    carbs_g: n.carbs_g_per_100g * factor,
    grams,
  };
}

function emptyMacros(): NutritionMacros {
  return { kcal: 0, protein_g: 0, fat_g: 0, carbs_g: 0 };
}

function addMacros(target: NutritionMacros, part: NutritionContribution): void {
  target.kcal += part.kcal;
  target.protein_g += part.protein_g;
  target.fat_g += part.fat_g;
  target.carbs_g += part.carbs_g;
}

function scaleMacros(source: NutritionMacros, factor: number): NutritionMacros {
  return {
    kcal: source.kcal * factor,
    protein_g: source.protein_g * factor,
    fat_g: source.fat_g * factor,
    carbs_g: source.carbs_g * factor,
  };
}

function integerServings(servings: number | null | undefined): number | null {
  if (servings == null || !Number.isFinite(servings)) return null;
  if (!Number.isInteger(servings) || servings < 1) return null;
  return servings;
}

export function computeNutrition(
  ingredients: RecipeIngredient[],
  { ratio, servings, yieldWeightG }: ComputeNutritionOptions,
): RecipeNutrition {
  const total = emptyMacros();
  let massG = 0;
  let anyContribution = false;
  let incomplete = false;
  const omitted: string[] = [];
  const safeRatio = Number.isFinite(ratio) ? ratio : 1;

  for (const line of ingredients) {
    if (skippedFromNutrition(line)) continue;
    const part = contribute(line, safeRatio);
    if (part == null) {
      incomplete = true;
      if (line.name) omitted.push(line.name);
      continue;
    }
    anyContribution = true;
    addMacros(total, part);
    massG += part.grams;
  }

  if (!anyContribution) {
    return {
      basis: 'raw_input',
      incomplete,
      omitted,
      total: null,
      per_100g_input: null,
      per_100g_cooked: null,
      per_serving: null,
    };
  }

  const per100 = massG > 0 ? scaleMacros(total, 100 / massG) : null;
  const nServings = integerServings(servings);
  const perServing = nServings != null ? scaleMacros(total, 1 / nServings) : null;
  const cookedMass =
    yieldWeightG != null && Number.isFinite(yieldWeightG) && yieldWeightG > 0
      ? yieldWeightG * safeRatio
      : null;
  const perCooked =
    cookedMass != null && cookedMass > 0 ? scaleMacros(total, 100 / cookedMass) : null;

  return {
    basis: 'raw_input',
    incomplete,
    omitted,
    total,
    per_100g_input: per100,
    per_100g_cooked: perCooked,
    per_serving: perServing,
  };
}

function formatWithComma(value: number, digits: number): string {
  if (!Number.isFinite(value)) return '';
  if (digits === 0) return String(Math.round(value));
  return value.toFixed(digits).replace('.', ',');
}

export function formatKcal(value: number): string {
  return formatWithComma(value, 0);
}

export function formatMacro(value: number): string {
  return formatWithComma(value, 1);
}
