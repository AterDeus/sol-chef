import Link from 'next/link';
import type { Metadata } from 'next';
import { notFound } from 'next/navigation';
import { fetchRecipe } from '@/lib/api';
import { recipeHref, valuesOf } from '@/lib/filters';
import {
  COOK_METHOD,
  DISH_TYPE,
  PROTEIN_BASE,
  baseAddonChipLabel,
  equipmentLabel,
  labelOf,
} from '@/lib/vocab';
import { IngredientsBlock } from '@/components/IngredientsBlock';
import { AllergenNotice } from '@/components/AllergenNotice';
import { RecipeActions } from '@/components/RecipeActions';
import { RecipeAxisLink, RecipeAxisSwitch } from '@/components/RecipeAxisSwitch';
import { RecipeSteps } from '@/components/RecipeSteps';
import { ErrorBanner } from '@/components/Feedback';
import { minutesLabel } from '@/lib/catalog';
import { applyStepChoice, rewriteSafetyCopy } from '@/lib/steps';
import type { RecipeDetail, RecipeNote, SearchParamsRecord } from '@/lib/types';
import { PREP_DAY_RU, PREP_MEAL_RU, PREP_MODE_RU, PREP_PLACE_RU, kitHref } from '@/lib/prep';

type Props = {
  params: Promise<{ slug: string }>;
  searchParams: Promise<SearchParamsRecord>;
};

const PREP_LABELS: Record<string, string> = {
  thaw: 'Разморозка',
  fridge: 'Холодильник',
  room_temp: 'Комнат. темп.',
  marinate: 'Маринад',
  soak: 'Замачивание',
  custom: 'Подготовка',
};

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = await params;
  const result = await fetchRecipe(slug);
  if (!result.ok) return { title: 'Рецепт' };
  return {
    title: result.data.title,
    description: result.data.summary ?? undefined,
    alternates: { canonical: `/recipes/${slug}` },
    openGraph: {
      title: result.data.title,
      description: result.data.summary ?? undefined,
      type: 'article',
      locale: 'ru_RU',
    },
  };
}

function isoDurationMinutes(total: number | null | undefined): string | undefined {
  if (total == null || !Number.isFinite(total) || total <= 0) return undefined;
  return `PT${Math.round(total)}M`;
}

function RecipeJsonLd({ recipe }: { recipe: RecipeDetail }) {
  const data = {
    '@context': 'https://schema.org',
    '@type': 'Recipe',
    name: recipe.title,
    description: recipe.summary ?? undefined,
    totalTime: isoDurationMinutes(recipe.time_profile?.total_minutes),
    recipeYield: recipe.servings != null && recipe.servings > 0 ? recipe.servings : undefined,
    recipeCategory: labelOf(DISH_TYPE, recipe.dish_type) || undefined,
    recipeIngredient: (recipe.ingredients ?? []).map((item) =>
      [item.display_amount, item.name].filter(Boolean).join(' '),
    ),
    recipeInstructions: (recipe.steps ?? []).map((step) => ({
      '@type': 'HowToStep',
      text: step.text,
    })),
  };
  return (
    <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(data) }} />
  );
}

function notesList(notes: RecipeDetail['notes']): RecipeNote[] {
  if (!notes) return [];
  if (typeof notes === 'string') {
    return notes.trim() ? [{ title: null, text: notes }] : [];
  }
  return notes.filter((item) => item.text?.trim());
}

export default async function RecipePage({ params, searchParams }: Props) {
  const { slug } = await params;
  const sp = await searchParams;
  const variant = valuesOf(sp, 'variant')[0] || null;
  const equipment = valuesOf(sp, 'equipment')[0] || null;
  const prepKit = valuesOf(sp, 'prep')[0] || null;
  const day = valuesOf(sp, 'day')[0] || null;
  const meal = valuesOf(sp, 'meal')[0] || null;
  const servingsRaw = valuesOf(sp, 'servings')[0];
  const servings = servingsRaw ? Number(servingsRaw) : undefined;
  const noLeftover = ['1', 'true', 'yes', 'on'].includes(
    (valuesOf(sp, 'no_leftover')[0] || '').toLowerCase(),
  );
  const result = await fetchRecipe(slug, {
    variant,
    equipment,
    prep: prepKit,
    day,
    meal,
    servings: Number.isFinite(servings) ? servings : undefined,
    noLeftover,
  });

  if (!result.ok && result.status === 404) notFound();
  if (!result.ok) {
    return (
      <>
        <Link className="back-link" href="/recipes">
          ← К списку рецептов
        </Link>
        <h1>Рецепт</h1>
        <ErrorBanner message={result.detail} />
      </>
    );
  }

  const recipe = result.data;
  const prepContext = recipe.prep_context ?? null;
  const kitBack = prepContext
    ? kitHref(prepContext.kit.slug, {
        servings: Number.isFinite(servings) ? servings : null,
        noLeftover,
      })
    : '/recipes';
  const flags = recipe.high_risk_flags ?? [];
  const hasRisk = flags.length > 0;
  const allergens = recipe.allergens ?? { contains: [], may_contain: [], unknown: [] };
  const deltaVariants = (recipe.available_variants ?? []).filter((item) => item.has_delta);
  const equipmentCodes = recipe.available_equipment ?? [];
  const notes = notesList(recipe.notes);
  const prep = recipe.prep ?? [];
  const hasTimers = (recipe.steps ?? []).some((step) => (step.timer_seconds ?? 0) > 0);
  const appliedVariant = recipe.applied_axes?.variant ?? variant;
  const appliedEquipment = recipe.applied_axes?.equipment ?? recipe.equipment ?? equipment;
  const piece = valuesOf(sp, 'piece')[0] || null;
  const cookSteps = applyStepChoice(
    (recipe.steps ?? []).map((step) => ({
      ...step,
      text: rewriteSafetyCopy(step.text),
    })),
    piece,
  );
  const cookPrep = prep.map((item) => ({ ...item, text: rewriteSafetyCopy(item.text) }));

  return (
    <article className="recipe-page">
      {!prepContext && <RecipeJsonLd recipe={recipe} />}
      <Link className="back-link" href={prepContext ? kitBack : '/recipes'}>
        {prepContext ? `← ${prepContext.kit.title}` : '← К списку рецептов'}
      </Link>
      <h1>
        {recipe.title}
        {recipe.editorial_tested && <span className="tested-badge">Готовил сам</span>}
      </h1>
      <dl className="recipe-card__facts recipe-card__facts--page">
        <div>
          <dt>Категория</dt>
          <dd>{labelOf(PROTEIN_BASE, recipe.protein_base)}</dd>
        </div>
        <div>
          <dt>Способ</dt>
          <dd>{labelOf(COOK_METHOD, recipe.cook_method)}</dd>
        </div>
        <div>
          <dt>Тип блюда</dt>
          <dd>{labelOf(DISH_TYPE, recipe.dish_type)}</dd>
        </div>
        {recipe.equipment && recipe.equipment !== recipe.cook_method ? (
          <div>
            <dt>Посуда</dt>
            <dd>{equipmentLabel(recipe.equipment)}</dd>
          </div>
        ) : null}
        {minutesLabel(recipe.time_profile?.total_minutes) ? (
          <div>
            <dt>Время</dt>
            <dd>{minutesLabel(recipe.time_profile?.total_minutes)}</dd>
          </div>
        ) : null}
      </dl>

      {recipe.requires_prep ? (
        <p className="recipe-prep-needed">
          Нужна заготовка. Время на карточке — разогрев уже готового мяса, не три часа томления.
        </p>
      ) : null}

      {prepContext && (
        <div className="prep-recipe-banner">
          <span className="prep-mode">{PREP_MODE_RU[prepContext.mode]}</span>
          <span>
            {PREP_DAY_RU[prepContext.day]} · {PREP_MEAL_RU[prepContext.meal]} · {prepContext.kit.title}
          </span>
        </div>
      )}
      {prepContext && prepContext.containers.length > 0 && (
        <ul className="prep-boxes">
          {prepContext.containers.map((box) => (
            <li key={box.code} className="prep-box">
              <strong>{box.label}</strong> {box.component_title} · {box.display_amount}
              {box.place === 'freezer' ? ` · ${PREP_PLACE_RU[box.place]}` : ''}
            </li>
          ))}
        </ul>
      )}
      {prepContext && prepContext.alternatives.length > 0 && (
        <div className="chip-row" aria-label="Замены">
          {prepContext.alternatives.map((item) => (
            <Link
              key={item.slug}
              href={recipeHref(item.slug, {
                prep: prepContext.kit.slug,
                day: prepContext.day,
                meal: prepContext.meal,
                servings: servings,
                noLeftover,
              })}
              className={item.slug === slug ? 'chip is-active' : 'chip'}
            >
              {item.label}
            </Link>
          ))}
        </div>
      )}

      {hasRisk && (
        <div className="caution" role="alert">
          <strong>Осторожно</strong>
          <p>
            {recipe.caution_text ||
              'Соблюдайте температуру готовности и гигиену при работе с этим блюдом.'}
          </p>
        </div>
      )}

      <AllergenNotice allergens={allergens} />

      {recipe.summary && <p className="recipe-lead">{recipe.summary}</p>}
      {(recipe.source_name || recipe.source_url) && (
        <p className="recipe-source">
          {recipe.source_url ? (
            <>
              Источник:{' '}
              <a href={recipe.source_url} rel="noopener noreferrer">
                {recipe.source_name || recipe.source_url}
              </a>
            </>
          ) : (
            recipe.source_name
          )}
        </p>
      )}

      {prep.length > 0 && (
        <section className="recipe-section recipe-prep">
          <h2>Заранее</h2>
          <p className="recipe-prep-hint">
            {prepContext ? 'Разморозка из набора' : 'Запланируйте в режиме готовки'}
          </p>
          <ul className="recipe-prep-list">
            {prep.map((item, i) => (
              <li key={`${item.type}-${i}`}>
                <strong>{PREP_LABELS[item.type || 'custom'] || 'Подготовка'}.</strong>{' '}
                {rewriteSafetyCopy(item.text)}
              </li>
            ))}
          </ul>
        </section>
      )}

      {!prepContext && (deltaVariants.length > 0 || equipmentCodes.length > 1) && (
        <RecipeAxisSwitch applied={`${appliedVariant ?? ''}:${appliedEquipment ?? ''}`}>
          {deltaVariants.length > 0 && (
            <section className="recipe-section" aria-label="Вариации состава">
              <fieldset className="filter-block">
                <legend className="filter-legend">Вариация</legend>
                <div className="chip-row">
                  <RecipeAxisLink
                    href={recipeHref(recipe.slug, { equipment: appliedEquipment })}
                    className={!appliedVariant ? 'chip is-active' : 'chip'}
                    current={!appliedVariant}
                  >
                    {baseAddonChipLabel(
                      recipe.home_protein_base || recipe.protein_base,
                      deltaVariants,
                    )}
                  </RecipeAxisLink>
                  {deltaVariants.map((item) => (
                    <RecipeAxisLink
                      key={item.code}
                      href={recipeHref(recipe.slug, {
                        variant: item.code,
                        equipment: appliedEquipment,
                      })}
                      className={appliedVariant === item.code ? 'chip is-active' : 'chip'}
                      current={appliedVariant === item.code}
                    >
                      {item.title}
                    </RecipeAxisLink>
                  ))}
                </div>
              </fieldset>
            </section>
          )}

          {equipmentCodes.length > 1 && (
            <section className="recipe-section" aria-label="Посуда">
              <fieldset className="filter-block">
                <legend className="filter-legend">Посуда</legend>
                <div className="chip-row">
                  {equipmentCodes.map((code) => (
                    <RecipeAxisLink
                      key={code}
                      href={recipeHref(recipe.slug, { variant: appliedVariant, equipment: code })}
                      className={appliedEquipment === code ? 'chip is-active' : 'chip'}
                      current={appliedEquipment === code}
                    >
                      {equipmentLabel(code)}
                    </RecipeAxisLink>
                  ))}
                </div>
              </fieldset>
            </section>
          )}
        </RecipeAxisSwitch>
      )}

      {!prepContext && (recipe.ingredients ?? []).length > 0 && (
        <IngredientsBlock
          scaling={recipe.scaling ?? { enabled: false }}
          ingredients={recipe.ingredients}
          servingsBase={recipe.servings}
          yieldWeightG={recipe.yield_weight_g}
          yieldKind={recipe.yield_kind}
          hasTimers={hasTimers}
        />
      )}

      {(recipe.steps ?? []).length > 0 && (
        <RecipeSteps slug={recipe.slug} steps={recipe.steps ?? []} sp={sp} />
      )}

      {(recipe.variations ?? []).some((item) => item.text?.trim()) && (
        <section className="recipe-section" aria-label="Текстовые вариации">
          <h2>Вариации</h2>
          <ul className="recipe-notes">
            {recipe.variations
              .filter((item) => item.text?.trim())
              .map((item) => (
                <li key={item.title || item.text}>
                  {item.title ? <strong>{item.title}. </strong> : null}
                  {item.text}
                </li>
              ))}
          </ul>
        </section>
      )}

      {notes.length > 0 && (
        <section className="recipe-section">
          <h2>Заметки</h2>
          <ul className="recipe-notes">
            {notes.map((item, index) => (
              <li key={index}>
                {item.title ? <strong>{item.title}. </strong> : null}
                {rewriteSafetyCopy(item.text)}
              </li>
            ))}
          </ul>
        </section>
      )}

      <RecipeActions
        title={recipe.title}
        steps={cookSteps}
        prep={cookPrep}
        backHref={prepContext ? kitBack : '/recipes'}
        backLabel={prepContext ? '← На неделю' : '← Рецепты'}
      />
    </article>
  );
}
