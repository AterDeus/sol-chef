import type { RecipeStep } from './types';

export type StepChoice = {
  id: string;
  label: string;
  indexes: number[];
};

export type ExclusiveStepGroup = {
  choices: StepChoice[];
  exclusiveIndexes: Set<number>;
};

function choiceFromText(text: string, index: number): StepChoice | null {
  if (!/пропуст/i.test(text)) return null;
  if (/грудк/i.test(text)) {
    return { id: 'breast', label: 'Грудка', indexes: [index] };
  }
  if (/бедр/i.test(text)) {
    return { id: 'thigh', label: 'Бедро', indexes: [index] };
  }
  return {
    id: `alt-${index}`,
    label: `Вариант ${index + 1}`,
    indexes: [index],
  };
}

export function exclusiveStepGroup(steps: RecipeStep[]): ExclusiveStepGroup | null {
  const found: StepChoice[] = [];
  for (let index = 0; index < steps.length; index += 1) {
    const choice = choiceFromText(steps[index]?.text ?? '', index);
    if (choice) found.push(choice);
  }
  if (found.length < 2) return null;
  const exclusiveIndexes = new Set(found.flatMap((item) => item.indexes));
  return { choices: found, exclusiveIndexes };
}

export function applyStepChoice(
  steps: RecipeStep[],
  piece: string | null | undefined,
): RecipeStep[] {
  const group = exclusiveStepGroup(steps);
  if (!group) return steps;
  const selected =
    group.choices.find((item) => item.id === piece) ?? group.choices[0];
  const keep = new Set(selected.indexes);
  return steps.filter((step, index) => {
    if (!group.exclusiveIndexes.has(index)) return true;
    return keep.has(index);
  });
}

export function rewriteSafetyCopy(text: string): string {
  return text.replace(
    /Курицу достать заранее, чтобы не класть ледяные куски[^.]*\.?/gi,
    'Если курица заморожена, безопасно разморозьте её в холодильнике; перед готовкой обсушите куски.',
  );
}
