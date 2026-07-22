import { fetchJson } from './utils.js';

export async function loadAllRecipes() {
  const index = await fetchJson('data/recipes/index.json');
  const files = index?.files;
  if (!Array.isArray(files) || files.length === 0) {
    throw new Error('invalid recipe index');
  }
  const chunks = await Promise.all(files.map(path => fetchJson(path)));
  return chunks.flat();
}
