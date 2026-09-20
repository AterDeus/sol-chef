import type { SearchParamsRecord } from '@/lib/types';
import { isSelected, toggleHref } from '@/lib/filters';
import { FilterChip } from '@/components/FilterChip';

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
            <FilterChip
              key={code}
              href={toggleHref(pathname, sp, param, code)}
              pressed={selected}
            >
              {label}
            </FilterChip>
          );
        })}
      </div>
    </fieldset>
  );
}
