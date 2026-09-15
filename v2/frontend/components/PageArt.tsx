import type { ReactNode } from 'react';

export type ArtScene =
  | 'home'
  | 'calculator'
  | 'grains'
  | 'meat'
  | 'beef'
  | 'pork'
  | 'poultry'
  | 'tips'
  | 'prep'
  | 'recipes';

const ART_SRC: Record<ArtScene, string> = {
  home: '/art/main-bg.png',
  calculator: '/art/pantry.png',
  grains: '/art/grains.png',
  meat: '/art/main-bg.png',
  beef: '/art/main-bg.png',
  pork: '/art/pork.png',
  poultry: '/art/poultry.png',
  tips: '/art/tools.png',
  prep: '/art/prep.png',
  recipes: '/art/recipes.png',
};

export function PageArt({ scene }: { scene: ArtScene }) {
  return (
    <div className="page-art" aria-hidden>
      <img
        className="page-art__paint"
        src={`${ART_SRC[scene]}?v=9`}
        alt=""
        width={1024}
        height={518}
        decoding="async"
        loading={scene === 'home' ? 'eager' : 'lazy'}
      />
    </div>
  );
}

export function PageIntro({
  eyebrow,
  title,
  lede,
  actions,
  scene,
  showArt = true,
}: {
  eyebrow: string;
  title: ReactNode;
  lede?: ReactNode;
  actions?: ReactNode;
  scene: ArtScene;
  showArt?: boolean;
}) {
  return (
    <header className={`page-intro${showArt ? '' : ' page-intro--no-art'} page-intro--${scene}`}>
      <div className="page-intro__copy">
        <p className="eyebrow">{eyebrow}</p>
        <h1>{title}</h1>
        {lede}
        {actions}
      </div>
      {showArt ? <PageArt scene={scene} /> : null}
    </header>
  );
}
