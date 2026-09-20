import type { ReactNode } from 'react';
import type { PantryGroup, SearchParamsRecord } from '@/lib/types';
import { isSelected, toggleHaveGroupHref, toggleHref, valuesOf } from '@/lib/filters';
import { ALLERGEN, EQUIPMENT, INTENT } from '@/lib/vocab';
import { ChipGroup } from '@/components/FilterPanel';
import { PantryTextForm } from '@/components/PantryTextForm';
import { SpriteIcon } from '@/components/SpriteIcon';
import { FilterChip } from '@/components/FilterChip';
import Link from 'next/link';

const INTENT_ORDER = ['fast', 'pantry', 'easy', 'batch', 'light', 'oven'] as const;

function groupOpen(sp: SearchParamsRecord, group: PantryGroup): boolean {
  if (isSelected(sp, 'have_group', group.id)) return true;
  return (group.children ?? []).some((child) => isSelected(sp, 'have_group', child.id));
}

function ChipRow({
  items,
}: {
  items: Array<{ id: string; title: string; href: string; selected: boolean }>;
}) {
  if (items.length === 0) return null;
  return (
    <div className="chip-row">
      {items.map((item) => (
        <FilterChip key={item.id} href={item.href} pressed={item.selected}>
          {item.title}
        </FilterChip>
      ))}
    </div>
  );
}

function pathForHave(groups: PantryGroup[], canonicalId: string): string {
  for (const group of groups) {
    const own = group.items?.find((item) => item.canonical_id === canonicalId);
    if (own) return `${group.title} · ${own.title}`;
    for (const child of group.children ?? []) {
      const nested = child.items?.find((item) => item.canonical_id === canonicalId);
      if (nested) return `${group.title} · ${child.title} · ${nested.title}`;
    }
  }
  return canonicalId;
}

function PickedBar({
  sp,
  groups,
}: {
  sp: SearchParamsRecord;
  groups: PantryGroup[];
}) {
  const have = valuesOf(sp, 'have');
  if (have.length === 0) return null;
  return (
    <div className="calc-picked">
      <p className="calc-picked__label">Выбрано</p>
      <ul className="calc-picked__list">
        {have.map((id) => (
          <li key={id}>
            <Link
              href={toggleHref('/calculator', sp, 'have', id)}
              className="calc-picked__chip"
              aria-label={`Убрать: ${pathForHave(groups, id)}`}
            >
              <span>{pathForHave(groups, id)}</span>
              <SpriteIcon name="x" size={14} />
            </Link>
          </li>
        ))}
      </ul>
    </div>
  );
}

function Branch({
  title,
  path,
  closeHref,
  closeLabel,
  hint,
  nested = false,
  children,
}: {
  title: string;
  path?: string;
  closeHref: string;
  closeLabel: string;
  hint?: string;
  nested?: boolean;
  children: ReactNode;
}) {
  return (
    <section
      className={nested ? 'calc-branch calc-branch--nested' : 'calc-branch'}
      aria-label={path ?? title}
    >
      <header className="calc-branch__head">
        <div>
          {path ? <p className="calc-branch__path">{path}</p> : null}
          <h3 className="calc-branch__title">{title}</h3>
          {hint ? <p className="calc-branch__hint">{hint}</p> : null}
        </div>
        <Link href={closeHref} className="calc-branch__close" aria-label={closeLabel}>
          <SpriteIcon name="x" size={18} />
          <span>Убрать</span>
        </Link>
      </header>
      {children}
    </section>
  );
}

export function CalculatorAsk({
  sp,
  groups,
}: {
  sp: SearchParamsRecord;
  groups: PantryGroup[];
}) {
  const extraOpen =
    valuesOf(sp, 'without').length > 0 ||
    valuesOf(sp, 'equipment').length > 0 ||
    valuesOf(sp, 'protein_base').length > 0 ||
    valuesOf(sp, 'cook_method').length > 0 ||
    valuesOf(sp, 'cuts').length > 0;
  const openGroups = groups.filter((group) => groupOpen(sp, group));

  return (
    <section className="calc-ask" aria-label="Ситуация">
      <PantryTextForm sp={sp} groups={groups} />

      <fieldset className="filter-block">
        <legend className="filter-legend">Что есть</legend>
        <p className="calc-ask__hint">
          Можно выбрать несколько групп сразу: курица, овощи, крупу и сценарий. Сначала группа,
          внутри неё — уточнение.
        </p>
        <div className="chip-row">
          {groups.map((group) => {
            const selected = groupOpen(sp, group);
            return (
              <FilterChip
                key={group.id}
                href={toggleHaveGroupHref('/calculator', sp, group.id, groups)}
                pressed={selected}
              >
                {group.title}
              </FilterChip>
            );
          })}
        </div>
      </fieldset>

      <PickedBar sp={sp} groups={groups} />

      {openGroups.map((group) => {
        const children = group.children ?? [];
        const selectedChildren = children.filter((child) => isSelected(sp, 'have_group', child.id));
        return (
          <Branch
            key={group.id}
            title={group.title}
            closeHref={toggleHaveGroupHref('/calculator', sp, group.id, groups)}
            closeLabel={`Убрать: ${group.title}`}
            hint={
              children.length > 0
                ? 'Сначала вид, потом отруб с витрины'
                : 'Отметьте, что лежит дома'
            }
          >
            {children.length > 0 ? (
              <>
                <ChipRow
                  items={children.map((child) => ({
                    id: child.id,
                    title: child.title,
                    href: toggleHaveGroupHref('/calculator', sp, child.id, groups),
                    selected: isSelected(sp, 'have_group', child.id),
                  }))}
                />
                {selectedChildren.map((child) => (
                  <Branch
                    key={child.id}
                    nested
                    title={child.title}
                    path={`${group.title} → ${child.title}`}
                    closeHref={toggleHaveGroupHref('/calculator', sp, child.id, groups)}
                    closeLabel={`Убрать: ${child.title}`}
                    hint="Что именно купили"
                  >
                    <ChipRow
                      items={(child.items ?? []).map((item) => ({
                        id: item.canonical_id,
                        title: item.title,
                        href: toggleHref('/calculator', sp, 'have', item.canonical_id),
                        selected: isSelected(sp, 'have', item.canonical_id),
                      }))}
                    />
                  </Branch>
                ))}
              </>
            ) : (
              <ChipRow
                items={(group.items ?? []).map((item) => ({
                  id: item.canonical_id,
                  title: item.title,
                  href: toggleHref('/calculator', sp, 'have', item.canonical_id),
                  selected: isSelected(sp, 'have', item.canonical_id),
                }))}
              />
            )}
          </Branch>
        );
      })}

      <fieldset className="filter-block">
        <legend className="filter-legend">Что сейчас важнее</legend>
        <div className="chip-row">
          {INTENT_ORDER.map((code) => {
            const selected = isSelected(sp, 'intent', code);
            return (
              <FilterChip
                key={code}
                href={toggleHref('/calculator', sp, 'intent', code)}
                pressed={selected}
              >
                {INTENT[code]}
              </FilterChip>
            );
          })}
        </div>
      </fieldset>

      <details className="calc-extra" open={extraOpen || undefined}>
        <summary aria-controls="calc-extra-panel">Ещё условия</summary>
        <div id="calc-extra-panel">
          <ChipGroup legend="Без чего" map={ALLERGEN} param="without" pathname="/calculator" sp={sp} />
          <ChipGroup legend="Посуда" map={EQUIPMENT} param="equipment" pathname="/calculator" sp={sp} />
        </div>
      </details>
    </section>
  );
}
