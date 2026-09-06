'use client';

import { useState } from 'react';
import type { RecipePrep, RecipeStep } from '@/lib/types';
import { CookMode } from './CookMode';
import { RecipeTabBar } from './Chrome';

export function CopyLinkButton() {
  const [label, setLabel] = useState('Скопировать ссылку');

  return (
    <button
      type="button"
      className="btn-secondary"
      onClick={async () => {
        try {
          await navigator.clipboard.writeText(window.location.href);
          setLabel('Скопировано');
          window.setTimeout(() => setLabel('Скопировать ссылку'), 2000);
        } catch {
          window.prompt('Скопируйте ссылку:', window.location.href);
        }
      }}
    >
      {label}
    </button>
  );
}

export function RecipeActions({
  title,
  steps,
  prep,
}: {
  title: string;
  steps: RecipeStep[];
  prep?: RecipePrep[];
}) {
  const [open, setOpen] = useState(false);
  const hasSteps = steps.length > 0;

  return (
    <>
      <div className="recipe-actions">
        {hasSteps && (
          <button type="button" className="btn-primary btn-cook" onClick={() => setOpen(true)}>
            Режим готовки
          </button>
        )}
        <CopyLinkButton />
      </div>
      {hasSteps && <RecipeTabBar onCook={() => setOpen(true)} />}
      {hasSteps && (
        <CookMode
          title={title}
          steps={steps}
          prep={prep}
          open={open}
          onClose={() => setOpen(false)}
        />
      )}
    </>
  );
}
