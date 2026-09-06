import { notFound, permanentRedirect } from 'next/navigation';

export default async function LegacyRecipeHtmlPage({
  searchParams,
}: {
  searchParams: Promise<{ id?: string | string[] }>;
}) {
  const sp = await searchParams;
  const raw = Array.isArray(sp.id) ? sp.id[0] : sp.id;
  const id = raw?.trim();
  if (!id) notFound();
  permanentRedirect(`/recipes/${encodeURIComponent(id)}`);
}
