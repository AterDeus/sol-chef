import type { RecipeStep, SearchParamsRecord } from '@/lib/types';
import { applyStepChoice, exclusiveStepGroup, rewriteSafetyCopy } from '@/lib/steps';
import { toURLSearchParams, valuesOf } from '@/lib/filters';
import { FilterChip } from '@/components/FilterChip';

function pieceHref(slug: string, sp: SearchParamsRecord, piece: string): string {
  const qs = toURLSearchParams(sp);
  qs.set('piece', piece);
  const suffix = qs.toString() ? `?${qs.toString()}` : '';
  return `/recipes/${slug}${suffix}`;
}

export function RecipeSteps({
  slug,
  steps,
  sp,
}: {
  slug: string;
  steps: RecipeStep[];
  sp: SearchParamsRecord;
}) {
  const group = exclusiveStepGroup(steps);
  const requested = valuesOf(sp, 'piece')[0] || null;
  const selected = group
    ? (group.choices.find((item) => item.id === requested)?.id ?? group.choices[0].id)
    : null;
  const visible = applyStepChoice(steps, selected);

  return (
    <section className="recipe-section">
      <h2>Шаги</h2>
      {group ? (
        <fieldset className="filter-block recipe-piece">
          <legend className="filter-legend">Какое мясо кладёте</legend>
          <p className="recipe-piece__hint">Один отруб на кастрюлю. Показывается только нужный шаг.</p>
          <div className="chip-row">
            {group.choices.map((choice) => (
              <FilterChip
                key={choice.id}
                href={pieceHref(slug, sp, choice.id)}
                pressed={selected === choice.id}
              >
                {choice.label}
              </FilterChip>
            ))}
          </div>
        </fieldset>
      ) : null}
      <ol className="recipe-steps">
        {visible.map((step, index) => (
          <li key={`${index}-${step.text.slice(0, 24)}`} className="recipe-step">
            <p>{rewriteSafetyCopy(step.text)}</p>
            {step.target_internal_temperature_c != null && (
              <span className="temp-chip">цель {step.target_internal_temperature_c} °C</span>
            )}
            {step.pull_internal_temperature_c != null && (
              <span className="temp-chip">снятие {step.pull_internal_temperature_c} °C</span>
            )}
            {step.hold_seconds != null && (
              <span className="temp-chip">выдержка {step.hold_seconds} с</span>
            )}
          </li>
        ))}
      </ol>
    </section>
  );
}