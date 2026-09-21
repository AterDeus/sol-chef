'use client';

import type { ReactNode } from 'react';
import type { PantryGroup, SearchParamsRecord } from '@/lib/types';
import { isSelected, toggleHaveGroupHref, toggleHref, valuesOf } from '@/lib/filters';
import { pantryItemPath } from '@/lib/pantry';
import { captureScrollClick } from '@/lib/keep-scroll';
import { ALLERGEN, EQUIPMENT_FILTER, INTENT } from '@/lib/vocab';
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
        <FilterChip key={item.id} href={item.href} selected={item.selected}>
          {item.title}
        </FilterChip>
      ))}
    </div>
  );
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
              scroll={false}
              className="calc-picked__chip"
              aria-label={`Убрать: ${pantryItemPath(groups, id)}`}
              onClick={captureScrollClick}
            >
              <span>{pantryItemPath(groups, id)}</span>
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
        <Link
          href={closeHref}
          scroll={false}
          className="calc-branch__close"
          aria-label={closeLabel}
          onClick={captureScrollClick}
        >
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
                selected={selected}
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
              children.length === 0
                ? 'Отметьте, что лежит дома'
                : group.id === 'meat'
                  ? 'Сначала вид, потом отруб. Заготовки — отдельно'
                  : 'Сначала полка, потом продукт'
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
                    hint={
                      child.id === 'prep' ? 'Что уже готово дома' : 'Что именно купили'
                    }
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
                selected={selected}
                hint={
                  code === 'light' ? 'Полегче по составу, не по калориям' : undefined
                }
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
          <ChipGroup legend="Посуда" map={EQUIPMENT_FILTER} param="equipment" pathname="/calculator" sp={sp} />
        </div>
      </details>
    </section>
  );
}
