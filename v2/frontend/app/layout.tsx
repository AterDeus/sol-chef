import type { Metadata } from 'next';
import { AppShell } from '@/components/AppShell';
import { siteUrl } from '@/lib/site';
import './globals.css';

export const metadata: Metadata = {
  metadataBase: new URL(siteUrl()),
  title: {
    default: 'Кухонная шпаргалка',
    template: '%s — Кухонная шпаргалка',
  },
  description: 'Калькулятор рецептов, справочник круп и мяса, советы и книга рецептов.',
  openGraph: {
    type: 'website',
    locale: 'ru_RU',
    siteName: 'Кухонная шпаргалка',
  },
  icons: {
    icon: [{ url: '/favicon.svg', type: 'image/svg+xml' }],
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ru">
      <body>
        <AppShell>{children}</AppShell>
      </body>
    </html>
  );
}
