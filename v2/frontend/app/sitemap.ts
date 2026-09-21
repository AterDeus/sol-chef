import type { MetadataRoute } from 'next';
import { fetchCatalog, fetchPrepKits } from '@/lib/api';
import { siteUrl } from '@/lib/site';
import { MEAT_CUTS } from '@/lib/vocab';

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const base = siteUrl();
  const staticRoutes: MetadataRoute.Sitemap = [
    { url: base, changeFrequency: 'daily', priority: 1 },
    { url: `${base}/calculator`, changeFrequency: 'weekly', priority: 0.9 },
    { url: `${base}/recipes`, changeFrequency: 'daily', priority: 0.9 },
    { url: `${base}/tips`, changeFrequency: 'weekly', priority: 0.6 },
    { url: `${base}/grains`, changeFrequency: 'monthly', priority: 0.5 },
    { url: `${base}/meat`, changeFrequency: 'monthly', priority: 0.5 },
    { url: `${base}/prep`, changeFrequency: 'weekly', priority: 0.7 },
    ...MEAT_CUTS.map((cut) => ({
      url: `${base}/meat/${cut}`,
      changeFrequency: 'monthly' as const,
      priority: 0.4,
    })),
  ];

  const [catalog, kits] = await Promise.all([
    fetchCatalog({}, { all: true }),
    fetchPrepKits(),
  ]);

  const recipes: MetadataRoute.Sitemap = catalog.ok
    ? catalog.data.results.map((recipe) => ({
        url: `${base}/recipes/${recipe.slug}`,
        changeFrequency: 'weekly',
        priority: 0.7,
      }))
    : [];

  const prep: MetadataRoute.Sitemap = kits.ok
    ? kits.data.results.map((kit) => ({
        url: `${base}/prep/${kit.slug}`,
        changeFrequency: 'weekly',
        priority: 0.6,
      }))
    : [];

  return [...staticRoutes, ...recipes, ...prep];
}
