import Link from 'next/link';
import type { PantryGroup, SearchParamsRecord } from '@/lib/types';
import { isSelected, toggleHref, valuesOf } from '@/lib/filters';
import {
  ALLERGEN,
  COOK_METHOD,
  CUT,
  DISH_TYPE,
  EQUIPMENT,
  PROTEIN_BASE,
} from '@/lib/vocab';

export function ChipGroup({
  legend,
  map,
  param,
  pathname,
  sp,
  codes,
}: {
  legend: string;
  map: Record<string, string>;
  param: string;
  pathname: string;
  sp: SearchParamsRecord;
  codes?: string[];
}) {
  const entries = codes
    ? codes.filter((code) => map[code]).map((code) => [code, map[code]] as const)
    : Object.entries(map);
  if (entries.length === 0) return null;
  return (
    <fieldset className="filter-block">
      <legend className="filter-legend">{legend}</legend>
      <div className="chip-row">
        {entries.map(([code, label]) => {
          const selected = isSelected(sp, param, code);
          return (
            <Link
              key={code}
              href={toggleHref(pathname, sp, param, code)}
              className={selected ? 'chip is-active' : 'chip'}
              aria-current={selected ? 'true' : undefined}
            >
              {label}
            </Link>
          );
        })}
      </div>
    </fieldset>
  );
}

export function FilterPanel({
  pathname,
  sp,
  showDishType = false,
  proteinLegend = 'Основа',
  availableCuts = [],
  pantryGroups = [],
}: {
  pathname: string;
  sp: SearchParamsRecord;
  showDishType?: boolean;
  proteinLegend?: string;
  availableCuts?: string[];
  pantryGroups?: PantryGroup[];
}) {
  const showCuts = valuesOf(sp, 'protein_base').length > 0 && availableCuts.length > 0;

  return (
    <section aria-label="Фильтры">
      <ChipGroup
        legend={proteinLegend}
        map={PROTEIN_BASE}
        param="protein_base"
        pathname={pathname}
        sp={sp}
      />
      {showCuts && (
        <ChipGroup
          legend="Отруб"
          map={CUT}
          param="cuts"
          pathname={pathname}
          sp={sp}
          codes={availableCuts}
        />
      )}
      <ChipGroup legend="Способ" map={COOK_METHOD} param="cook_method" pathname={pathname} sp={sp} />
      <ChipGroup legend="Посуда" map={EQUIPMENT} param="equipment" pathname={pathname} sp={sp} />
      {showDishType && (
        <ChipGroup legend="Тип блюда" map={DISH_TYPE} param="dish_type" pathname={pathname} sp={sp} />
      )}
      <ChipGroup legend="Без чего" map={ALLERGEN} param="without" pathname={pathname} sp={sp} />
      {pantryGroups.map((group) => (
        <ChipGroup
          key={group.id}
          legend={group.id === pantryGroups[0]?.id ? `Есть · ${group.title}` : group.title}
          map={Object.fromEntries((group.items ?? []).map((item) => [item.canonical_id, item.title]))}
          param="have"
          pathname={pathname}
          sp={sp}
        />
      ))}
    </section>
  );
}
