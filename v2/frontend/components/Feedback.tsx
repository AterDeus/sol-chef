import type { ReactNode } from 'react';

export function EmptyState({ children }: { children: ReactNode }) {
  return (
    <div className="empty-state" role="status">
      {children}
    </div>
  );
}

export function ErrorBanner({ message }: { message: string }) {
  return (
    <div className="error-banner" role="alert">
      {message}
    </div>
  );
}
