'use client';

import { usePathname } from 'next/navigation';
import { Suspense, useEffect } from 'react';
import { Footer, GuideStrip, Header, TabBar, isRecipeDetail } from './Chrome';
import { KeepScrollOnQuery } from '@/lib/keep-scroll';

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const recipe = isRecipeDetail(pathname);

  useEffect(() => {
    document.body.classList.toggle('is-recipe-page', recipe);
    return () => document.body.classList.remove('is-recipe-page');
  }, [recipe]);

  return (
    <>
      <Suspense fallback={null}>
        <KeepScrollOnQuery />
      </Suspense>
      <a className="skip-link" href="#main">
        К содержимому
      </a>
      <Header />
      <GuideStrip />
      <main id="main" className="wrap" tabIndex={-1}>
        {children}
      </main>
      <Footer />
      <TabBar />
    </>
  );
}
