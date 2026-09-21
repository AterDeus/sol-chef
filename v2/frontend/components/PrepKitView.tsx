'use client';

import Link from 'next/link';
import { useMemo, useState } from 'react';
import type { PrepKitDetail, PrepSlot } from '@/lib/types';
import { recipeHref } from '@/lib/filters';
import { SpriteIcon } from '@/components/SpriteIcon';
import {
  PREP_DAY_RU,
  PREP_MEAL_RU,
  PREP_MODE_RU,
  PREP_PLACE_RU,
  PREP_SERVING_OPTIONS,
  formatServingsLabel,
  kitHref,
  leftoverCostCaption,
  thawRemindersForDay,
  coldContainerCaption,
  formatThawColumn,
} from '@/lib/prep';

const TABS = [
  { id: 'shop', label: 'Что купить', icon: 'shopping-basket' },
  { id: 'sunday', label: 'Подготовить в воскресенье', icon: 'refrigerator' },
  { id: 'meals', label: 'Блюда на неделю', icon: 'utensils' },
] as const;

function slotTitle(slot: PrepSlot): string {
  return slot.plate_title || slot.flavor || slot.title;
}

function stringList(value: unknown): string[] {
  if (!Array.isArray(value)) return [];
  return value.filter((item): item is string => typeof item === 'string' && item.trim() !== '');
}

function SundayIntro({ row, index }: { row: Record<string, unknown>; index: number }) {
  const gear = stringList(row.gear);
  const plan = stringList(row.plan);
  if (gear.length > 0 || plan.length > 0) {
    return (
      <div className="prep-sunday-intro">
        {gear.length > 0 && (
          <section className="prep-sunday-intro__col" aria-labelledby={`prep-gear-${index}`}>
            <h3 id={`prep-gear-${index}`}>Посуда</h3>
            <ul>
              {gear.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          </section>
        )}
        {plan.length > 0 && (
          <section className="prep-sunday-intro__col" aria-labelledby={`prep-plan-${index}`}>
            <h3 id={`prep-plan-${index}`}>Сегодня</h3>
            <ul>
              {plan.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          </section>
        )}
      </div>
    );
  }
  const hands = typeof row.hands === 'string' ? row.hands : '';
  if (!hands) return null;
  return <p className="lede">{hands}</p>;
}

export function PrepKitView({
  kit,
  servings,
  noLeftover,
}: {
  kit: PrepKitDetail;
  servings: number | null;
  noLeftover: boolean;
}) {
  const [tab, setTab] = useState<(typeof TABS)[number]['id']>('shop');
  const applied = servings ?? kit.servings_base ?? 2;
  const servingOptions = kit.servings_base ? PREP_SERVING_OPTIONS : [];
  const leftoverCaption = leftoverCostCaption(kit.leftover_cost);
  const showLeftoverToggle = Boolean(kit.has_leftovers);
  const boxCaption = coldContainerCaption(kit.containers);
  const intro = kit.weekend_timeline.filter((row) => row.kind === 'intro');
  const recipeSteps = kit.weekend_timeline.filter((row) => row.kind !== 'intro');
  const slotsByDay = useMemo(() => {
    const map = new Map<number, Partial<Record<'lunch' | 'dinner', PrepSlot>>>();
    for (const slot of kit.slots) {
      const day = map.get(slot.day) ?? {};
      day[slot.meal] = slot;
      map.set(slot.day, day);
    }
    return map;
  }, [kit.slots]);
  const planHref = (nextServings: number | null, nextNoLeftover: boolean) =>
    kitHref(kit.slug, {
      servings: nextServings,
      servingsBase: kit.servings_base,
      noLeftover: nextNoLeftover,
    });

  return (
    <>
      {(servingOptions.length > 0 || showLeftoverToggle) && (
        <div className="prep-plan">
          {servingOptions.length > 0 && (
            <div className="prep-servings" aria-label="Порции">
              {servingOptions.map((n) => (
                <Link
                  key={n}
                  href={planHref(n, noLeftover)}
                  className={applied === n ? 'chip is-active' : 'chip'}
                >
                  {formatServingsLabel(n)}
                </Link>
              ))}
            </div>
          )}
          {showLeftoverToggle && (
            <Link
              href={planHref(servings, !noLeftover)}
              className={`prep-toggle${noLeftover ? ' is-on' : ''}`}
              aria-current={noLeftover ? 'true' : undefined}
            >
              <span className="prep-toggle__mark" aria-hidden />
              Без вчерашнего
              <span>
                Блюдо на один приём; вместо разогрева — другое из набора. Меняет закупку и
                воскресенье.
                {leftoverCaption ? ` ${leftoverCaption}` : ''}
              </span>
            </Link>
          )}
        </div>
      )}

      <div className="prep-tabs" role="tablist" aria-label="Разделы набора">
        {TABS.map((item) => (
          <button
            key={item.id}
            type="button"
            role="tab"
            id={`prep-tab-${item.id}`}
            aria-controls={`prep-panel-${item.id}`}
            aria-selected={tab === item.id}
            tabIndex={tab === item.id ? 0 : -1}
            className={tab === item.id ? 'chip is-active' : 'chip'}
            onClick={() => setTab(item.id)}
          >
            <SpriteIcon name={item.icon} size={16} />
            {item.label}
          </button>
        ))}
      </div>

      {tab === 'shop' && (
        <section id="prep-panel-shop" role="tabpanel" aria-labelledby="prep-tab-shop">
          <h2>Что купить</h2>
          {kit.shopping.length === 0 ? (
            <p>Список закупки пуст.</p>
          ) : (
            <table className="prep-table">
              <thead>
                <tr>
                  <th>Продукт</th>
                  <th>Количество</th>
                </tr>
              </thead>
              <tbody>
                {kit.shopping.map((row) => (
                  <tr key={row.canonical_id}>
                    <td>{row.title_ru || row.canonical_id}</td>
                    <td>{row.display_amount}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </section>
      )}

      {tab === 'sunday' && (
        <section id="prep-panel-sunday" role="tabpanel" aria-labelledby="prep-tab-sunday">
          <h2>Рецепт воскресенья</h2>
          {intro.map((row, index) => (
            <SundayIntro key={`intro-${index}`} row={row} index={index} />
          ))}
          {recipeSteps.length > 0 && (
            <ol className="prep-recipe">
              {recipeSteps.map((row, index) => {
                const text = typeof row.hands === 'string' ? row.hands : '';
                return (
                  <li key={`${index}-${text.slice(0, 24)}`}>
                    <span>{text}</span>
                  </li>
                );
              })}
            </ol>
          )}
          <h3>Куда разложить</h3>
          {boxCaption && <p className="lede">{boxCaption}</p>}
          <table className="prep-table">
            <thead>
              <tr>
                <th>Бокс</th>
                <th>Что</th>
                <th>Где</th>
                <th>Достать</th>
              </tr>
            </thead>
            <tbody>
              {kit.containers.map((box) => (
                <tr key={box.code}>
                  <td>
                    {box.label} · {box.display_amount}
                  </td>
                  <td>{box.component_title}</td>
                  <td>{PREP_PLACE_RU[box.place] || box.place}</td>
                  <td>{formatThawColumn(box)}</td>
                </tr>
              ))}
            </tbody>
          </table>
          {kit.components.length > 0 && (
            <details className="prep-details">
              <summary>Подробнее по каждой заготовке</summary>
              {kit.components.map((item) => (
                <div key={item.code}>
                  <p>
                    <strong>{item.title}</strong> · {item.display_amount}
                  </p>
                  <ul>
                    {(item.weekend_steps ?? []).map((step, index) => {
                      const text = typeof step === 'string' ? step : String(step);
                      return <li key={`${index}-${text.slice(0, 24)}`}>{text}</li>;
                    })}
                  </ul>
                </div>
              ))}
            </details>
          )}
        </section>
      )}

      {tab === 'meals' && (
        <section id="prep-panel-meals" role="tabpanel" aria-labelledby="prep-tab-meals">
          <h2>Блюда на неделю</h2>
          <div className="prep-slot-grid">
            {[1, 2, 3, 4, 5, 6, 7].map((day) => {
              const lunch = slotsByDay.get(day)?.lunch;
              const dinner = slotsByDay.get(day)?.dinner;
              const thawLines = thawRemindersForDay(day, kit.containers);
              return (
                <div key={day} className="prep-day">
                  <p className="prep-day__title">{PREP_DAY_RU[day]}</p>
                  {thawLines.map((line) => (
                    <p key={line} className="prep-day__thaw">
                      {line}
                    </p>
                  ))}
                  <div className="prep-slot-row">
                    {[lunch, dinner].map((slot) => {
                      if (!slot) return null;
                      return (
                        <Link
                          key={`${slot.day}-${slot.meal}`}
                          className="prep-slot"
                          href={recipeHref(slot.slug, {
                            prep: kit.slug,
                            day: slot.day,
                            meal: slot.meal,
                            servings: servings,
                            noLeftover,
                          })}
                        >
                          <span className="prep-mode">{PREP_MODE_RU[slot.mode]}</span>
                          <span className="prep-slot__meal">{PREP_MEAL_RU[slot.meal]}</span>
                          <strong>{slotTitle(slot)}</strong>
                          {slot.plate_composition && (
                            <span className="prep-slot__composition">{slot.plate_composition}</span>
                          )}
                        </Link>
                      );
                    })}
                  </div>
                </div>
              );
            })}
          </div>
        </section>
      )}
    </>
  );
}
