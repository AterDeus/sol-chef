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

  return (
    <div
      className={compact ? 'allergen-notice allergen-notice--compact' : 'allergen-notice'}
      aria-label="Аллергены"
    >
      {contains.length > 0 || mayContain.length > 0 ? (
        <div className="allergen-notice__group">
          {!compact ? <p className="allergen-notice__kicker">Аллергены рецепта</p> : null}
          <ul>
            {contains.map((code) => (
              <li key={`c-${code}`} className="allergen-chip allergen-chip--contains">
                {containsAllergenLabel(code)}
              </li>
            ))}
            {mayContain.map((code) => (
              <li key={`m-${code}`} className="allergen-chip allergen-chip--may">
                {mayContainAllergenLabel(code)}
              </li>
            ))}
          </ul>
        </div>
      ) : null}
      {unknown.length > 0 ? (
        <div className="allergen-notice__group">
          {!compact ? (
            <p className="allergen-notice__kicker">Возможные аллергены в покупных продуктах</p>
          ) : null}
          <ul>
            {unknown.map((code) => (
              <li key={`u-${code}`} className="allergen-chip allergen-chip--unknown">
                {unknownAllergenLabel(code)}
              </li>
            ))}
          </ul>
        </div>
      ) : null}
    </div>
  );
}
