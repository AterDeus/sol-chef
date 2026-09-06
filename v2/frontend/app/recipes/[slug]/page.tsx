import Link from 'next/link';
import type { Metadata } from 'next';
import { notFound } from 'next/navigation';
import { fetchRecipe } from '@/lib/api';
import { recipeHref, valuesOf } from '@/lib/filters';
import {
  ALLERGEN,
  COOK_METHOD,
  DISH_TYPE,
  EQUIPMENT,
  HIGH_RISK,
  PROTEIN_BASE,
  labelOf,
} from '@/lib/vocab';
import { IngredientsBlock } from '@/components/IngredientsBlock';
import { RecipeActions } from '@/components/RecipeActions';
import { ErrorBanner } from '@/components/Feedback';
import type { RecipeDetail, RecipeNote, SearchParamsRecord } from '@/lib/types';

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
  };
}

function RecipeJsonLd({ recipe }: { recipe: RecipeDetail }) {
  const data = {
    '@context': 'https://schema.org',
    '@type': 'Recipe',
    name: recipe.title,
    description: recipe.summary ?? undefined,
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
  const result = await fetchRecipe(slug, { variant, equipment });

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

  return (
    <article className="recipe-page">
      <RecipeJsonLd recipe={recipe} />
      <Link className="back-link" href="/recipes">
        ← К списку рецептов
      </Link>
      <h1>
        {recipe.title}
        {recipe.editorial_tested && <span className="tested-badge">Готовил сам</span>}
      </h1>
      <div className="recipe-meta" style={{ marginBottom: 16 }}>
        <span className="tag">{labelOf(PROTEIN_BASE, recipe.protein_base)}</span>
        <span className="tag">{labelOf(COOK_METHOD, recipe.cook_method)}</span>
        <span className="tag">{labelOf(DISH_TYPE, recipe.dish_type)}</span>
        {recipe.equipment && <span className="tag">{labelOf(EQUIPMENT, recipe.equipment)}</span>}
        {flags.map((flag) => (
          <span key={flag} className="tag">
            {labelOf(HIGH_RISK, flag)}
          </span>
        ))}
      </div>

      {hasRisk && (
        <div className="caution" role="status">
          <strong>Осторожно</strong>
          {recipe.caution_text || flags.map((flag) => labelOf(HIGH_RISK, flag)).join(' · ')}
        </div>
      )}

      {((allergens.contains?.length ?? 0) > 0 ||
        (allergens.may_contain?.length ?? 0) > 0 ||
        (allergens.unknown?.length ?? 0) > 0) && (
        <div className="allergen-dots" style={{ marginBottom: 20 }} aria-label="Аллергены">
          {(allergens.contains ?? []).map((code) => (
            <span key={`c-${code}`} className="allergen-dot allergen-dot--contains">
              <i aria-hidden />
              {labelOf(ALLERGEN, code)}
            </span>
          ))}
          {(allergens.may_contain ?? []).map((code) => (
            <span key={`m-${code}`} className="allergen-dot allergen-dot--may">
              <i aria-hidden />
              следы: {labelOf(ALLERGEN, code)}
            </span>
          ))}
          {(allergens.unknown ?? []).map((code) => (
            <span key={`u-${code}`} className="allergen-dot allergen-dot--unknown">
              <i aria-hidden />
              неизвестно: {labelOf(ALLERGEN, code)}
            </span>
          ))}
        </div>
      )}

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
          <p className="recipe-prep-hint">Запланируйте в режиме готовки</p>
          <ul className="recipe-prep-list">
            {prep.map((item, i) => (
              <li key={`${item.type}-${i}`}>
                <strong>{PREP_LABELS[item.type || 'custom'] || 'Подготовка'}.</strong> {item.text}
              </li>
            ))}
          </ul>
        </section>
      )}

      {deltaVariants.length > 0 && (
        <section className="recipe-section" aria-label="Вариации состава">
          <fieldset className="filter-block">
            <legend className="filter-legend">Вариация</legend>
            <div className="chip-row">
            <Link
              href={recipeHref(recipe.slug, { equipment: appliedEquipment })}
              className={!appliedVariant ? 'chip is-active' : 'chip'}
              aria-current={!appliedVariant ? 'true' : undefined}
            >
              Как в рецепте
            </Link>
            {deltaVariants.map((item) => (
              <Link
                key={item.code}
                href={recipeHref(recipe.slug, {
                  variant: item.code,
                  equipment: appliedEquipment,
                })}
                className={appliedVariant === item.code ? 'chip is-active' : 'chip'}
                aria-current={appliedVariant === item.code ? 'true' : undefined}
              >
                {item.title}
              </Link>
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
              <Link
                key={code}
                href={recipeHref(recipe.slug, { variant: appliedVariant, equipment: code })}
                className={appliedEquipment === code ? 'chip is-active' : 'chip'}
                aria-current={appliedEquipment === code ? 'true' : undefined}
              >
                {labelOf(EQUIPMENT, code)}
              </Link>
            ))}
            </div>
          </fieldset>
        </section>
      )}

      {(recipe.ingredients ?? []).length > 0 && (
        <IngredientsBlock
          scaling={recipe.scaling ?? { enabled: false }}
          ingredients={recipe.ingredients}
          servingsBase={recipe.servings}
          hasTimers={hasTimers}
        />
      )}

      {(recipe.steps ?? []).length > 0 && (
        <section className="recipe-section">
          <h2>Шаги</h2>
          <ol className="recipe-steps">
            {(recipe.steps ?? []).map((step, index) => (
              <li key={index} className="recipe-step">
                <p>{step.text}</p>
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
      )}

      {(recipe.variations ?? []).length > 0 && (
        <details className="recipe-variations">
          <summary>Вариации ({recipe.variations.length})</summary>
          {recipe.variations.map((item) => (
            <article key={item.title} style={{ marginBottom: 12 }}>
              <h3 style={{ fontSize: 17, marginBottom: 6 }}>{item.title}</h3>
              <p>{item.text}</p>
            </article>
          ))}
        </details>
      )}

      {notes.length > 0 && (
        <section className="recipe-section">
          <h2>Заметки</h2>
          <ul className="recipe-notes">
            {notes.map((item, index) => (
              <li key={index}>
                {item.title ? <strong>{item.title}. </strong> : null}
                {item.text}
              </li>
            ))}
          </ul>
        </section>
      )}

      <RecipeActions title={recipe.title} steps={recipe.steps ?? []} prep={prep} />
    </article>
  );
}
