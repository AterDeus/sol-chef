export function siteUrl(): string {
  const raw = (process.env.SITE_URL || process.env.NEXT_PUBLIC_SITE_URL || '')
    .trim()
    .replace(/\/$/, '');
  if (raw) {
    try {
      return new URL(raw).origin;
    } catch {
      /* fall through */
    }
  }
  return 'http://localhost:8080';
}
