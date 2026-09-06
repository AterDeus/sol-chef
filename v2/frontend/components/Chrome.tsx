'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { SpriteIcon } from '@/components/SpriteIcon';

const NAV = [
  { href: '/calculator', label: 'Калькулятор', match: 'calc', icon: 'list-filter' },
  { href: '/recipes', label: 'Рецепты', match: 'recipes', icon: 'book-open-text' },
  { href: '/grains', label: 'Справочник', match: 'guide', icon: 'wheat' },
  { href: '/tips', label: 'Советы', match: 'tips', icon: 'chef-hat' },
] as const;

export function navMatch(pathname: string): 'calc' | 'recipes' | 'guide' | 'tips' | null {
  if (pathname.startsWith('/calculator')) return 'calc';
  if (pathname.startsWith('/recipes')) return 'recipes';
  if (pathname.startsWith('/grains') || pathname.startsWith('/meat')) return 'guide';
  if (pathname.startsWith('/tips')) return 'tips';
  return null;
}

export function isRecipeDetail(pathname: string): boolean {
  return pathname.startsWith('/recipes/') && pathname !== '/recipes/';
}

export function isGuidePath(pathname: string): boolean {
  return pathname.startsWith('/grains') || pathname.startsWith('/meat');
}

export function Header() {
  const pathname = usePathname();
  const active = navMatch(pathname);

  return (
    <>
      <header className="site-header">
        <Link
          className="site-brand"
          href="/"
          aria-current={pathname === '/' ? 'page' : undefined}
        >
          Кухонная шпаргалка
        </Link>
        <nav className="site-nav" aria-label="Основное меню">
          {NAV.map((item) => (
            <Link
              key={item.match}
              href={item.href}
              className={active === item.match ? 'is-active' : undefined}
              aria-current={active === item.match ? 'page' : undefined}
            >
              <SpriteIcon name={item.icon} size={18} />
              {item.label}
            </Link>
          ))}
        </nav>
      </header>
      {!isRecipeDetail(pathname) && (
        <div className="mobile-brand">
          <Link href="/">Кухонная шпаргалка</Link>
        </div>
      )}
    </>
  );
}

export function GuideStrip() {
  const pathname = usePathname();
  if (!isGuidePath(pathname)) return null;

  const items = [
    { href: '/grains', label: 'Крупы', on: pathname === '/grains' },
    { href: '/meat/beef', label: 'Говядина', on: pathname === '/meat/beef' },
    { href: '/meat/pork', label: 'Свинина', on: pathname === '/meat/pork' },
    { href: '/meat/poultry', label: 'Птица', on: pathname === '/meat/poultry' },
  ];

  return (
    <nav className="guide-strip" aria-label="Справочник">
      {items.map((item) => (
        <Link
          key={item.href}
          href={item.href}
          className={item.on ? 'is-active' : undefined}
          aria-current={item.on ? 'page' : undefined}
        >
          {item.label}
        </Link>
      ))}
    </nav>
  );
}

export function Footer() {
  const pathname = usePathname();
  if (isRecipeDetail(pathname)) return null;

  return (
    <footer className="site-footer">
      <Link href="/grains">Крупы</Link>
      <Link href="/meat/beef">Говядина</Link>
      <Link href="/meat/pork">Свинина</Link>
      <Link href="/meat/poultry">Птица</Link>
      <Link href="/tips">Советы Энди</Link>
      <Link href="/recipes">Все рецепты</Link>
    </footer>
  );
}

const TABS: Array<{
  href: string;
  label: string;
  aria?: string;
  icon: string;
  match: 'calc' | 'recipes' | 'guide' | 'tips';
}> = [
  { href: '/calculator', label: 'Калькулятор', icon: 'list-filter', match: 'calc' },
  { href: '/recipes', label: 'Рецепты', icon: 'book-open-text', match: 'recipes' },
  { href: '/grains', label: 'Справка', aria: 'Справочник', icon: 'wheat', match: 'guide' },
  { href: '/tips', label: 'Советы', aria: 'Советы Энди', icon: 'chef-hat', match: 'tips' },
];

export function TabBar() {
  const pathname = usePathname();
  if (isRecipeDetail(pathname)) return null;
  const active = navMatch(pathname);

  return (
    <nav className="tabbar tabbar--main" aria-label="Нижнее меню">
      {TABS.map((tab) => (
        <Link
          key={tab.href}
          href={tab.href}
          aria-label={tab.aria}
          className={active === tab.match ? 'is-active' : undefined}
          aria-current={active === tab.match ? 'page' : undefined}
        >
          <SpriteIcon name={tab.icon} size={22} />
          {tab.label}
        </Link>
      ))}
    </nav>
  );
}

export function RecipeTabBar({ onCook }: { onCook: () => void }) {
  return (
    <nav className="tabbar tabbar--recipe" aria-label="Меню рецепта">
      <Link href="/recipes" aria-label="Назад к рецептам">
        ← Рецепты
      </Link>
      <Link href="/grains" aria-label="Справочник">
        Справка
      </Link>
      <button type="button" className="tabbar-cook" onClick={onCook}>
        Режим готовки
      </button>
    </nav>
  );
}
