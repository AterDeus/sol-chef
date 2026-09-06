import type { Metadata } from 'next';
import { AppShell } from '@/components/AppShell';
import './globals.css';

export const metadata: Metadata = {
  title: {
    default: 'Кухонная шпаргалка',
    template: '%s — Кухонная шпаргалка',
  },
  description: 'Калькулятор рецептов, справочник круп и мяса, советы и книга рецептов.',
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
