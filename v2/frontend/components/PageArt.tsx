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

const ART_SRC_MOBILE: Record<ArtScene, string> = {
  home: '/art/main-bg-m.png',
  calculator: '/art/pantry-m.png',
  grains: '/art/grains-m.png',
  meat: '/art/main-bg-m.png',
  beef: '/art/main-bg-m.png',
  pork: '/art/pork-m.png',
  poultry: '/art/poultry-m.png',
  tips: '/art/tools-m.png',
  prep: '/art/prep-m.png',
  recipes: '/art/recipes-m.png',
};

const ART_VERSION = '10';

export function PageArt({ scene }: { scene: ArtScene }) {
  return (
    <div className="page-art" aria-hidden>
      <picture>
        <source media="(max-width: 768px)" srcSet={`${ART_SRC_MOBILE[scene]}?v=${ART_VERSION}`} />
        <img
          className="page-art__paint"
          src={`${ART_SRC[scene]}?v=${ART_VERSION}`}
          alt=""
          width={1024}
          height={518}
          decoding="async"
          loading={scene === 'home' ? 'eager' : 'lazy'}
        />
      </picture>
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
      </div>
      {showArt ? <PageArt scene={scene} /> : null}
      {lede || actions ? (
        <div className="page-intro__body">
          {lede}
          {actions}
        </div>
      ) : null}
    </header>
  );
}
