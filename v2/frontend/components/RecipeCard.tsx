import Link from 'next/link';
import type { AlternativeSolution, RecipeCardData } from '@/lib/types';
import { effortLabel, minutesLabel, solutionTimeLabel } from '@/lib/catalog';
import { recipeHref } from '@/lib/filters';
import {
  COOK_METHOD,
  DISH_TYPE,
  PROTEIN_BASE,
  equipmentLabel,
  labelOf,
  pickGuestProteinVariant,
} from '@/lib/vocab';
import { AllergenNotice } from '@/components/AllergenNotice';

export type BookCardContext = {
  chapterId?: string;
  proteinFilter?: string[];
};

export function RecipeCard({
  recipe,
  book,
}: {
  recipe: RecipeCardData;
  book?: BookCardContext;
}) {
  const guest = book ? pickGuestProteinVariant(recipe, book) : null;
  const proteinCode = guest?.protein_base ?? recipe.protein_base;
  const time = minutesLabel(recipe.time_profile?.total_minutes);
  const effort = effortLabel(recipe.effort_level);
  const href = recipeHref(recipe.slug, {
    variant: guest?.code ?? recipe.applied_axes?.variant,
    equipment: recipe.applied_axes?.equipment,
  });

  return (
    <article className="recipe-card">
      <h3>
        <Link href={href} className="recipe-card__hit">
          {recipe.title}
        </Link>
      </h3>
      {recipe.summary ? <p className="recipe-card__summary">{recipe.summary}</p> : null}
      <dl className="recipe-card__facts">
        <div>
          <dt>Категория</dt>
          <dd>{labelOf(PROTEIN_BASE, proteinCode)}</dd>
        </div>
        {guest?.title ? (
          <div>
            <dt>Вариант</dt>
            <dd>{guest.title}</dd>
          </div>
        ) : null}
        <div>
          <dt>Способ</dt>
          <dd>{labelOf(COOK_METHOD, recipe.cook_method)}</dd>
        </div>
        <div>
          <dt>Тип блюда</dt>
          <dd>{labelOf(DISH_TYPE, recipe.dish_type)}</dd>
        </div>
        {time ? (
          <div>
            <dt>Время</dt>
            <dd>{time}</dd>
          </div>
        ) : null}
        {effort ? (
          <div>
            <dt>Сложность</dt>
            <dd>{effort}</dd>
          </div>
        ) : null}
        {recipe.requires_prep ? (
          <div>
            <dt>Заготовка</dt>
            <dd>Нужна готовая</dd>
          </div>
        ) : null}
      </dl>
      {recipe.why && recipe.why.length > 0 && (
        <ul className="why-list">
          {recipe.why.map((line) => (
            <li key={line}>{line}</li>
          ))}
        </ul>
      )}
      <AllergenNotice allergens={recipe.allergens} compact />
    </article>
  );
}

export function RecipeGrid({
  recipes,
  book,
}: {
  recipes: RecipeCardData[];
  book?: BookCardContext;
}) {
  return (
    <div className="recipe-grid">
      {recipes.map((recipe) => (
        <RecipeCard key={recipe.slug} recipe={recipe} book={book} />
      ))}
    </div>
  );
}

export function SolutionBoard({
  featured,
  alternatives,
  catalogHref,
}: {
  featured: RecipeCardData;
  alternatives: AlternativeSolution[];
  catalogHref?: string | null;
}) {
  const href = recipeHref(featured.slug, {
    variant: featured.applied_axes?.variant,
    equipment: featured.applied_axes?.equipment,
  });
  const shopping = featured.shopping_delta ?? [];
  const substitutions = featured.substitutions ?? [];
  const method = labelOf(COOK_METHOD, featured.cook_method);
  const gear =
    featured.equipment && featured.equipment !== featured.cook_method
      ? equipmentLabel(featured.equipment)
      : null;
  const time = solutionTimeLabel(featured.time_profile);
  const variantApplied = Boolean(featured.applied_axes?.variant);
  const nowComplete = shopping.length === 0 && featured.bucket === 'now';

  return (
    <div className="solution-board">
      <section className="solution-featured" aria-labelledby="featured-title">
        <p className="eyebrow">Я бы приготовил</p>
        <h2 id="featured-title">
          <Link href={href}>{featured.title}</Link>
        </h2>
        {variantApplied ? (
          <p className="solution-featured__axis">
            Основа: {labelOf(PROTEIN_BASE, featured.protein_base)}
          </p>
        ) : null}
        <dl className="recipe-card__facts">
          <div>
            <dt>Категория</dt>
            <dd>{labelOf(PROTEIN_BASE, featured.protein_base)}</dd>
          </div>
          <div>
            <dt>Способ</dt>
            <dd>{method}</dd>
          </div>
          {gear ? (
            <div>
              <dt>Посуда</dt>
              <dd>{gear}</dd>
            </div>
          ) : null}
          {time ? (
            <div>
              <dt>Время</dt>
              <dd>{time}</dd>
            </div>
          ) : null}
          {featured.step_count ? (
            <div>
              <dt>Шаги</dt>
              <dd>{featured.step_count}</dd>
            </div>
          ) : null}
        </dl>
        {featured.requires_prep ? (
          <p className="recipe-prep-needed">
            Нужна заготовка. Время на карточке — разогрев, не томление сырого мяса.
          </p>
        ) : null}
        <AllergenNotice allergens={featured.allergens} compact />
        {nowComplete && substitutions.length === 0 ? (
          <p className="solution-featured__status">Можно приготовить сейчас</p>
        ) : null}
        {nowComplete && substitutions.length > 0 ? (
          <p className="solution-featured__status">Можно приготовить с заменой</p>
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
              const altTime = solutionTimeLabel(item.time_profile);
              return (
                <li key={`${item.label}-${item.slug}`}>
                  <span className="tag">{item.label}</span>
                  <Link href={altHref}>{item.title}</Link>
                  {altTime ? (
                    <span className="solution-alts__why">{altTime}</span>
                  ) : item.why?.[0] ? (
                    <span className="solution-alts__why">{item.why[0]}</span>
                  ) : null}
                </li>
              );
            })}
          </ul>
          {catalogHref ? (
            <p className="solution-alts__more">
              <Link href={catalogHref}>Посмотреть все подходящие</Link>
            </p>
          ) : null}
        </section>
      ) : catalogHref ? (
        <p className="solution-alts__more">
          <Link href={catalogHref}>Посмотреть все подходящие</Link>
        </p>
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
