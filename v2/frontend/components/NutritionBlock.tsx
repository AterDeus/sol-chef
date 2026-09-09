'use client';

import { formatKcal, formatMacro } from '@/lib/nutrition';
import type { NutritionMacros, RecipeNutrition } from '@/lib/types';

type Cell = {
  key: string;
  label: string;
  macros: NutritionMacros;
};

function MacroCell({ label, macros }: { label: string; macros: NutritionMacros }) {
  return (
    <div className="recipe-nutrition__cell">
      <p className="recipe-nutrition__label">{label}</p>
      <p className="recipe-nutrition__kcal">
        {formatKcal(macros.kcal)} <span>ккал</span>
      </p>
      <p className="recipe-nutrition__macros">
        Б {formatMacro(macros.protein_g)} · Ж {formatMacro(macros.fat_g)} · У{' '}
        {formatMacro(macros.carbs_g)}
      </p>
    </div>
  );
}

export function NutritionBlock({
  nutrition,
  yieldKind = null,
}: {
  nutrition: RecipeNutrition;
  yieldKind?: 'estimated' | 'exact' | null;
}) {
  const cells: Cell[] = [];
  if (nutrition.total) {
    cells.push({ key: 'total', label: 'На рецепт', macros: nutrition.total });
  }
  if (nutrition.per_100g_input) {
    cells.push({
      key: 'per100',
      label: 'На 100 г продуктов (до готовки)',
      macros: nutrition.per_100g_input,
    });
  }
  if (nutrition.per_100g_cooked) {
    const estimated = yieldKind !== 'exact';
    cells.push({
      key: 'cooked',
      label: estimated ? 'На 100 г готового (оценка)' : 'На 100 г готового',
      macros: nutrition.per_100g_cooked,
    });
  }
  if (nutrition.per_serving) {
    cells.push({ key: 'serving', label: 'На порцию', macros: nutrition.per_serving });
  }
  if (cells.length === 0) return null;

  return (
    <section className="recipe-nutrition" aria-label="КБЖУ ориентировочно">
      <h2>КБЖУ ориентировочно</h2>
      {nutrition.incomplete && (
        <p className="recipe-nutrition__incomplete">Неполный расчёт</p>
      )}
      <p className="recipe-nutrition__disclaimer">
        Ориентировочно. Зависит от продукта и способа приготовления.
      </p>
      <div
        className="recipe-nutrition__grid"
        data-cols={cells.length}
      >
        {cells.map((cell) => (
          <MacroCell key={cell.key} label={cell.label} macros={cell.macros} />
        ))}
      </div>
    </section>
  );
}
