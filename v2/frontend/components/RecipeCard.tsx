import Link from 'next/link';
import type { AlternativeSolution, RecipeCardData } from '@/lib/types';
import { recipeHref } from '@/lib/filters';
import {
  ALLERGEN,
  COOK_METHOD,
  DISH_TYPE,
  EQUIPMENT,
  PROTEIN_BASE,
  labelOf,
} from '@/lib/vocab';

function AllergenDots({ recipe }: { recipe: RecipeCardData }) {
  const { contains, may_contain, unknown } = recipe.allergens ?? {
    contains: [],
    may_contain: [],
    unknown: [],
  };
  if (!contains.length && !may_contain.length && !unknown.length) return null;

  return (
    <div className="allergen-dots" aria-label="Аллергены">
      {contains.map((code) => (
        <span key={`c-${code}`} className="allergen-dot allergen-dot--contains">
          <i aria-hidden />
          {labelOf(ALLERGEN, code)}
        </span>
      ))}
      {may_contain.map((code) => (
        <span key={`m-${code}`} className="allergen-dot allergen-dot--may">
          <i aria-hidden />
          следы: {labelOf(ALLERGEN, code)}
        </span>
      ))}
      {unknown.map((code) => (
        <span key={`u-${code}`} className="allergen-dot allergen-dot--unknown">
          <i aria-hidden />
          неизвестно: {labelOf(ALLERGEN, code)}
        </span>
      ))}
    </div>
  );
}

export function RecipeCard({ recipe }: { recipe: RecipeCardData }) {
  const tags = [
    labelOf(PROTEIN_BASE, recipe.protein_base),
    labelOf(COOK_METHOD, recipe.cook_method),
    labelOf(DISH_TYPE, recipe.dish_type),
  ];
  const href = recipeHref(recipe.slug, {
    variant: recipe.applied_axes?.variant,
    equipment: recipe.applied_axes?.equipment,
  });

  return (
    <article className="recipe-card">
      <h3>
        <Link href={href}>{recipe.title}</Link>
      </h3>
      <div className="recipe-meta">
        {tags.map((tag) => (
          <span key={tag} className="tag">
            {tag}
          </span>
        ))}
      </div>
      {recipe.why && recipe.why.length > 0 && (
        <ul className="why-list">
          {recipe.why.map((line) => (
            <li key={line}>{line}</li>
          ))}
        </ul>
      )}
      <AllergenDots recipe={recipe} />
    </article>
  );
}

export function RecipeGrid({ recipes }: { recipes: RecipeCardData[] }) {
  return (
    <div className="recipe-grid">
      {recipes.map((recipe) => (
        <RecipeCard key={recipe.slug} recipe={recipe} />
      ))}
    </div>
  );
}

export function SolutionBoard({
  featured,
  alternatives,
}: {
  featured: RecipeCardData;
  alternatives: AlternativeSolution[];
}) {
  const href = recipeHref(featured.slug, {
    variant: featured.applied_axes?.variant,
    equipment: featured.applied_axes?.equipment,
  });
  const shopping = featured.shopping_delta ?? [];
  const substitutions = featured.substitutions ?? [];
  const method = labelOf(COOK_METHOD, featured.cook_method);
  const gear = featured.equipment ? labelOf(EQUIPMENT, featured.equipment) : null;

  return (
    <div className="solution-board">
      <section className="solution-featured" aria-labelledby="featured-title">
        <p className="eyebrow">Я бы приготовил</p>
        <h2 id="featured-title">
          <Link href={href}>{featured.title}</Link>
        </h2>
        <div className="recipe-meta">
          <span className="tag">{labelOf(PROTEIN_BASE, featured.protein_base)}</span>
          <span className="tag">{method}</span>
          {gear ? <span className="tag">{gear}</span> : null}
          {featured.step_count ? <span className="tag">{featured.step_count} шагов</span> : null}
        </div>
        {shopping.length === 0 && featured.bucket === 'now' ? (
          <p className="solution-featured__status">Всё основное уже есть</p>
        ) : null}
        {shopping.length > 0 ? (
          <p className="solution-featured__status">
            Нужно докупить: {shopping.map((item) => item.title).join(', ')}
          </p>
        ) : null}
        {substitutions.length > 0 ? (
          <p className="solution-featured__status">
            Можно заменить:{' '}
            {substitutions.map((item) => `${item.from_title} → ${item.to_title}`).join('; ')}
          </p>
        ) : null}
        {featured.why && featured.why.length > 0 ? (
          <>
            <h3 className="solution-why-title">Почему именно это</h3>
            <ul className="why-list why-list--checks">
              {featured.why.map((line) => (
                <li key={line}>{line}</li>
              ))}
            </ul>
          </>
        ) : null}
        <p className="solution-featured__actions">
          <Link className="btn-primary" href={href}>
            Приготовить
          </Link>
        </p>
      </section>
      {alternatives.length > 0 ? (
        <section className="solution-alts" aria-labelledby="alts-title">
          <h2 id="alts-title">Ещё варианты</h2>
          <ul>
            {alternatives.map((item) => {
              const altHref = recipeHref(item.slug, {
                variant: item.applied_axes?.variant,
                equipment: item.applied_axes?.equipment,
              });
              return (
                <li key={`${item.label}-${item.slug}`}>
                  <span className="tag">{item.label}</span>
                  <Link href={altHref}>{item.title}</Link>
                  {item.why?.[0] ? <span className="solution-alts__why">{item.why[0]}</span> : null}
                </li>
              );
            })}
          </ul>
        </section>
      ) : null}
    </div>
  );
}

export function SolutionBuckets({
  now,
  almost,
  best,
}: {
  now: RecipeCardData[];
  almost: RecipeCardData[];
  best: RecipeCardData[];
}) {
  const sections = [
    { id: 'now', title: 'Можно сейчас', items: now },
    { id: 'almost', title: 'Нужно докупить 1–2', items: almost },
    { id: 'best', title: 'Лучше, если купить', items: best },
  ];
  return (
    <div className="solution-buckets">
      {sections.map((section) =>
        section.items.length === 0 ? null : (
          <section key={section.id} className="solution-bucket" aria-labelledby={`bucket-${section.id}`}>
            <h2 id={`bucket-${section.id}`} className="solution-bucket__title">
              {section.title}
            </h2>
            <RecipeGrid recipes={section.items} />
          </section>
        ),
      )}
    </div>
  );
}
