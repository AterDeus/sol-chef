#!/usr/bin/env node
'use strict';

const fs = require('fs');
const path = require('path');

const RECIPES_DIR = path.join(__dirname, '..', 'data', 'recipes');
const RECIPES_INDEX = path.join(RECIPES_DIR, 'index.json');
const ID_PATTERN = /^[a-z0-9]+(?:-[a-z0-9]+)*$/;
const DATE_PATTERN = /^\d{4}-\d{2}-\d{2}$/;
const REQUIRED = ['id', 'title', 'source_url', 'summary', 'tags'];
const TAGS_MIN = 2;
const TAGS_MAX = 5;
const CATEGORIES = new Set([
  'птица',
  'говядина',
  'свинина',
  'баранина',
  'крупы',
  'рис',
  'гарнир',
  'паста',
  'суп',
  'выпечка',
  'десерт',
  'соусы',
  'завтрак',
  'рыба',
]);
const ALLOWED_FIELDS = new Set([
  'id', 'title', 'source_type', 'source_url', 'source_name',
  'tags', 'category', 'summary', 'ingredients', 'steps', 'prep', 'notes', 'variations', 'added', 'tried',
]);
const PREP_TYPES = new Set(['thaw', 'fridge', 'room_temp', 'marinate', 'soak', 'custom']);

function fail(message){
  console.error(`ERROR: ${message}`);
  process.exitCode = 1;
}

function readInput(pathOrStdin){
  if (pathOrStdin === '--stdin'){
    return fs.readFileSync(0, 'utf8');
  }
  return fs.readFileSync(pathOrStdin, 'utf8');
}

function unwrapMarkdownJson(raw){
  const trimmed = raw.trim();
  const fullFence = trimmed.match(/^```(?:json|JSON)?\s*\r?\n([\s\S]*?)\r?\n```\s*$/i);
  if (fullFence){
    return fullFence[1].trim();
  }
  const embeddedFence = trimmed.match(/```(?:json|JSON)?\s*\r?\n([\s\S]*?)\r?\n```/i);
  if (embeddedFence){
    return embeddedFence[1].trim();
  }
  return trimmed;
}

function parseArgs(){
  const args = process.argv.slice(2);
  if (args.length === 0){
    return { mode: 'database' };
  }
  if (args[0] === '--import'){
    const file = args[1];
    if (!file){
      fail('--import requires a file path');
      process.exit(1);
    }
    return { mode: 'import', source: file };
  }
  if (args[0] === '--stdin'){
    return { mode: 'import', source: '--stdin' };
  }
  fail(`unknown argument "${args[0]}" (use --import <file> or --stdin)`);
  process.exit(1);
}

function isErrorPayload(value){
  return value
    && typeof value === 'object'
    && !Array.isArray(value)
    && Object.prototype.hasOwnProperty.call(value, 'error');
}

function normalizeImportPayload(data){
  if (isErrorPayload(data)){
    fail('AI error payload — fix source and retry; do not add to data/recipes.json');
    if (typeof data.error === 'string' && data.error.trim()){
      console.error(`  message: ${data.error.trim()}`);
    }
    return null;
  }
  if (Array.isArray(data)){
    return data;
  }
  if (data && typeof data === 'object'){
    return [data];
  }
  fail('import payload must be a recipe object or an array of recipes');
  return null;
}

function validateTags(recipe, prefix){
  if (recipe.tags == null){
    return;
  }
  if (!Array.isArray(recipe.tags)){
    fail(`${prefix}: tags must be an array`);
    return;
  }
  if (recipe.tags.length < TAGS_MIN || recipe.tags.length > TAGS_MAX){
    fail(`${prefix}: tags must contain ${TAGS_MIN}–${TAGS_MAX} items (got ${recipe.tags.length})`);
  }
  const seen = new Set();
  recipe.tags.forEach((tag, i) => {
    if (typeof tag !== 'string' || !tag.trim()){
      fail(`${prefix}.tags[${i}]: must be a non-empty string`);
      return;
    }
    const normalized = tag.trim().toLowerCase();
    if (seen.has(normalized)){
      fail(`${prefix}.tags[${i}]: duplicate tag "${tag.trim()}"`);
    }
    seen.add(normalized);
  });
  if (recipe.category && seen.has(String(recipe.category).trim().toLowerCase())){
    fail(`${prefix}: tag duplicates category "${recipe.category}"`);
  }
}

function validateStep(item, path){
  if (typeof item === 'string'){
    if (!item.trim()){
      fail(`${path}: must be a non-empty string`);
    }
    return;
  }
  if (!item || typeof item !== 'object' || Array.isArray(item)){
    fail(`${path}: must be a string or step object`);
    return;
  }
  if (!item.text || typeof item.text !== 'string' || !item.text.trim()){
    fail(`${path}.text: required non-empty string`);
  }
  const allowed = new Set(['text', 'timer_min', 'timer_sec', 'timer_label', 'timer_note']);
  for (const key of Object.keys(item)){
    if (!allowed.has(key)){
      fail(`${path}: unknown field "${key}"`);
    }
  }
  if (item.timer_min != null && (typeof item.timer_min !== 'number' || item.timer_min < 0)){
    fail(`${path}.timer_min: must be a non-negative number`);
  }
  if (item.timer_sec != null && (typeof item.timer_sec !== 'number' || item.timer_sec < 0 || item.timer_sec > 3599)){
    fail(`${path}.timer_sec: must be 0–3599`);
  }
  const totalSec = (Number(item.timer_min) || 0) * 60 + (Number(item.timer_sec) || 0);
  if ((item.timer_min != null || item.timer_sec != null) && totalSec <= 0){
    fail(`${path}: timer_min/timer_sec must total more than 0 when set`);
  }
  if (item.timer_note != null && typeof item.timer_note !== 'string'){
    fail(`${path}.timer_note: must be a string`);
  }
}

function validatePrepItem(item, path){
  if (!item || typeof item !== 'object' || Array.isArray(item)){
    fail(`${path}: must be an object`);
    return;
  }
  if (!item.text || typeof item.text !== 'string' || !item.text.trim()){
    fail(`${path}.text: required non-empty string`);
  }
  const beforeMin = Number(item.before_min) || 0;
  const beforeHours = Number(item.before_hours) || 0;
  if (beforeMin + beforeHours <= 0){
    fail(`${path}: set before_min and/or before_hours (> 0)`);
  }
  if (item.before_min != null && (typeof item.before_min !== 'number' || item.before_min < 1)){
    fail(`${path}.before_min: must be >= 1`);
  }
  if (item.before_hours != null && (typeof item.before_hours !== 'number' || item.before_hours < 1)){
    fail(`${path}.before_hours: must be >= 1`);
  }
  if (item.type != null && !PREP_TYPES.has(item.type)){
    fail(`${path}.type: invalid value "${item.type}"`);
  }
  const allowed = new Set(['text', 'before_min', 'before_hours', 'type']);
  for (const key of Object.keys(item)){
    if (!allowed.has(key)){
      fail(`${path}: unknown field "${key}"`);
    }
  }
}

function validateIngredientItem(item, path){
  if (!item || typeof item !== 'object' || Array.isArray(item)){
    fail(`${path}: must be an object`);
    return;
  }
  if (!item.name || typeof item.name !== 'string' || !item.name.trim()){
    fail(`${path}.name: required non-empty string`);
  }
  const allowed = new Set(['name', 'amount', 'amount_max', 'unit', 'detail', 'scalable', 'scale_mode']);
  for (const key of Object.keys(item)){
    if (!allowed.has(key)){
      fail(`${path}: unknown field "${key}"`);
    }
  }
  if (item.amount != null && typeof item.amount !== 'number'){
    fail(`${path}.amount: must be a number`);
  }
  if (item.amount_max != null && typeof item.amount_max !== 'number'){
    fail(`${path}.amount_max: must be a number`);
  }
  if (item.amount_max != null && (item.amount == null || item.amount >= item.amount_max)){
    fail(`${path}.amount_max: must be greater than amount`);
  }
  if (item.unit != null && (typeof item.unit !== 'string' || !item.unit.trim())){
    fail(`${path}.unit: must be a non-empty string`);
  }
  if (item.detail != null && typeof item.detail !== 'string'){
    fail(`${path}.detail: must be a string`);
  }
  if (item.scalable != null && typeof item.scalable !== 'boolean'){
    fail(`${path}.scalable: must be a boolean`);
  }
  if (item.scale_mode != null){
    const modes = new Set(['linear', 'gentle', 'whole']);
    if (typeof item.scale_mode !== 'string' || !modes.has(item.scale_mode)){
      fail(`${path}.scale_mode: must be linear, gentle, or whole`);
    }
  }
}

const DISALLOWED_VARIATION_HTML = /<\s*(script|style|iframe|object|embed|link|meta|svg|math)\b|on\w+\s*=|javascript:/i;

function validateVariationItem(item, path){
  if (!item || typeof item !== 'object' || Array.isArray(item)){
    fail(`${path}: must be an object`);
    return;
  }
  if (!item.title || typeof item.title !== 'string' || !item.title.trim()){
    fail(`${path}.title: required non-empty string`);
  }
  if (!item.text || typeof item.text !== 'string' || !item.text.trim()){
    fail(`${path}.text: required non-empty string`);
  }
  if (DISALLOWED_VARIATION_HTML.test(item.text)){
    fail(`${path}.text: disallowed HTML (only p, br, strong, b, em, i, ul, ol, li without attributes)`);
  }
  const allowed = new Set(['title', 'text']);
  for (const key of Object.keys(item)){
    if (!allowed.has(key)){
      fail(`${path}: unknown field "${key}"`);
    }
  }
}

function validateRecipe(recipe, index, labelPrefix){
  const prefix = `${labelPrefix}[${index}]`;
  if (!recipe || typeof recipe !== 'object' || Array.isArray(recipe)){
    fail(`${prefix}: must be an object`);
    return;
  }

  for (const field of REQUIRED){
    if (recipe[field] == null || recipe[field] === ''){
      fail(`${prefix}: missing required field "${field}"`);
    }
  }

  if (recipe.id && !ID_PATTERN.test(recipe.id)){
    fail(`${prefix}: invalid id "${recipe.id}" (use lowercase latin and hyphens)`);
  }

  validateTags(recipe, prefix);

  if (recipe.source_type && !['video', 'article'].includes(recipe.source_type)){
    fail(`${prefix}: source_type must be "video" or "article"`);
  }

  if (recipe.category != null && recipe.category !== ''){
    if (!CATEGORIES.has(recipe.category)){
      fail(`${prefix}: invalid category "${recipe.category}" (allowed: ${[...CATEGORIES].join(', ')})`);
    }
  }

  if (recipe.source_url){
    try {
      const url = new URL(recipe.source_url);
      if (!['http:', 'https:'].includes(url.protocol)){
        fail(`${prefix}: source_url must be http or https`);
      }
    } catch {
      fail(`${prefix}: invalid source_url`);
    }
  }

  if (recipe.added && !DATE_PATTERN.test(recipe.added)){
    fail(`${prefix}: added must be YYYY-MM-DD`);
  }

  if (recipe.tried != null && typeof recipe.tried !== 'boolean'){
    fail(`${prefix}: tried must be a boolean`);
  }

  if (recipe.ingredients != null){
    if (!Array.isArray(recipe.ingredients)){
      fail(`${prefix}: ingredients must be an array`);
    } else {
      recipe.ingredients.forEach((item, i) => {
        validateIngredientItem(item, `${prefix}.ingredients[${i}]`);
      });
    }
  }

  if (recipe.steps != null){
    if (!Array.isArray(recipe.steps)){
      fail(`${prefix}: steps must be an array`);
    } else {
      recipe.steps.forEach((item, i) => {
        validateStep(item, `${prefix}.steps[${i}]`);
      });
    }
  }

  if (recipe.prep != null){
    if (!Array.isArray(recipe.prep)){
      fail(`${prefix}: prep must be an array`);
    } else {
      recipe.prep.forEach((item, i) => {
        validatePrepItem(item, `${prefix}.prep[${i}]`);
      });
    }
  }

  if (recipe.variations != null){
    if (!Array.isArray(recipe.variations)){
      fail(`${prefix}: variations must be an array`);
    } else if (recipe.variations.length === 0){
      fail(`${prefix}: variations must not be empty when set`);
    } else {
      recipe.variations.forEach((item, i) => {
        validateVariationItem(item, `${prefix}.variations[${i}]`);
      });
    }
  }

  for (const key of Object.keys(recipe)){
    if (!ALLOWED_FIELDS.has(key)){
      fail(`${prefix}: unknown field "${key}"`);
    }
  }
}

function validateRecipeList(recipes, labelPrefix){
  if (!Array.isArray(recipes)){
    fail(`${labelPrefix} must be a JSON array`);
    process.exit(1);
  }

  const ids = new Set();
  recipes.forEach((recipe, index) => {
    validateRecipe(recipe, index, labelPrefix);
    if (recipe.id){
      if (ids.has(recipe.id)){
        fail(`duplicate id "${recipe.id}"`);
      }
      ids.add(recipe.id);
    }
  });
}

function loadJson(raw, sourceLabel){
  try {
    return JSON.parse(raw);
  } catch (e){
    fail(`invalid JSON in ${sourceLabel}: ${e.message}`);
    process.exit(1);
  }
}

function readFileOrExit(filePath){
  try {
    return fs.readFileSync(filePath, 'utf8');
  } catch {
    fail(`cannot read ${filePath}`);
    process.exit(1);
  }
}

function loadRecipeDatabase(){
  const indexRaw = readFileOrExit(RECIPES_INDEX);
  const index = loadJson(indexRaw, RECIPES_INDEX);
  if (!index || !Array.isArray(index.files) || index.files.length === 0){
    fail('data/recipes/index.json must contain a non-empty "files" array');
    process.exit(1);
  }

  const recipes = [];
  for (const relPath of index.files){
    if (typeof relPath !== 'string' || !relPath.startsWith('data/recipes/') || !relPath.endsWith('.json')){
      fail(`invalid recipe file path in index: "${relPath}"`);
      continue;
    }
    const filePath = path.join(__dirname, '..', relPath);
    const raw = readFileOrExit(filePath);
    const chunk = loadJson(raw, filePath);
    if (!Array.isArray(chunk)){
      fail(`${relPath} must be a JSON array`);
      continue;
    }
    chunk.forEach((recipe, index) => {
      validateRecipe(recipe, index, relPath);
    });
    recipes.push(...chunk);
  }

  const ids = new Set();
  recipes.forEach(recipe => {
    if (recipe.id){
      if (ids.has(recipe.id)){
        fail(`duplicate id "${recipe.id}"`);
      }
      ids.add(recipe.id);
    }
  });

  return recipes;
}

const options = parseArgs();
let validatedCount = 0;

if (options.mode === 'database'){
  const data = loadRecipeDatabase();
  validatedCount = data.length;
} else {
  const raw = unwrapMarkdownJson(readInput(options.source));
  const data = loadJson(raw, options.source);
  const recipes = normalizeImportPayload(data);
  if (recipes){
    validateRecipeList(recipes, 'import');
    validatedCount = recipes.length;
  }
}

if (process.exitCode){
  console.error('\nValidation failed.');
  process.exit(1);
}

const suffix = options.mode === 'import' ? ' for import' : '';
console.log(`OK: ${validatedCount} recipe(s) validated${suffix}.`);
