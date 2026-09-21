import type { Allergens } from './types';
import { ALLERGEN, labelOf } from './vocab';

export function unknownAllergenLabel(code: string): string {
  if (code === 'celery') {
    return 'Проверьте состав бульона: возможен сельдерей';
  }
  if (code === 'egg') {
    return 'Проверьте состав печенья и готовых смесей: возможно яйцо';
  }
  return `Возможно содержит ${labelOf(ALLERGEN, code)} — зависит от покупного продукта`;
}

export function containsAllergenLabel(code: string): string {
  return labelOf(ALLERGEN, code);
}

export function mayContainAllergenLabel(code: string): string {
  return `следы: ${labelOf(ALLERGEN, code)}`;
}

export function hasAllergens(allergens?: Allergens | null): boolean {
  if (!allergens) return false;
  return (
    (allergens.contains?.length ?? 0) > 0 ||
    (allergens.may_contain?.length ?? 0) > 0 ||
    (allergens.unknown?.length ?? 0) > 0
  );
}
