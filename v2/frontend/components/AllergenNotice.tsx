import type { Allergens } from '@/lib/types';
import {
  containsAllergenLabel,
  hasAllergens,
  mayContainAllergenLabel,
  unknownAllergenLabel,
} from '@/lib/allergens';

export function AllergenNotice({
  allergens,
  compact = false,
}: {
  allergens?: Allergens | null;
  compact?: boolean;
}) {
  if (!hasAllergens(allergens)) return null;
  const contains = allergens?.contains ?? [];
  const mayContain = allergens?.may_contain ?? [];
  const unknown = allergens?.unknown ?? [];
  const confirmed = [
    ...contains.map((code) => ({ key: `c-${code}`, text: containsAllergenLabel(code) })),
    ...mayContain.map((code) => ({ key: `m-${code}`, text: mayContainAllergenLabel(code) })),
  ];

  return (
    <div className={compact ? 'allergen-notice allergen-notice--compact' : 'allergen-notice'}>
      <p className="allergen-notice__title">Аллергены:</p>
      {confirmed.length > 0 ? (
        <ul className="allergen-notice__list">
          {confirmed.map((item) => (
            <li key={item.key}>{item.text}</li>
          ))}
        </ul>
      ) : null}
      {unknown.length > 0 ? (
        <ul className="allergen-notice__notes">
          {unknown.map((code) => (
            <li key={`u-${code}`}>{unknownAllergenLabel(code)}</li>
          ))}
        </ul>
      ) : null}
    </div>
  );
}
