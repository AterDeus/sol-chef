#!/usr/bin/env node
'use strict';

const fs = require('fs');
const path = require('path');

const RECIPES_FILE = path.join(__dirname, '..', 'data', 'recipes.json');
const ID_PATTERN = /^[a-z0-9]+(?:-[a-z0-9]+)*$/;
const DATE_PATTERN = /^\d{4}-\d{2}-\d{2}$/;
const REQUIRED = ['id', 'title', 'source_url', 'summary', 'tags'];
const TAGS_MIN = 2;
const TAGS_MAX = 5;
const CATEGORIES = new Set([
  'птица',
  'говядина',
  'свинина',
  'крупы',
  'гарнир',
  'суп',
  'выпечка',
  'десерт',
  'соусы',
  'завтрак',
  'рыба',
]);
const ALLOWED_FIELDS = new Set([
  'id', 'title', 'source_type', 'source_url', 'source_name',
  'tags', 'category', 'summary', 'ingredients', 'steps', 'notes', 'added',
]);

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

  if (recipe.ingredients != null){
    if (!Array.isArray(recipe.ingredients)){
      fail(`${prefix}: ingredients must be an array`);
    } else {
      recipe.ingredients.forEach((item, i) => {
        if (typeof item !== 'string' || !item.trim()){
          fail(`${prefix}.ingredients[${i}]: must be a non-empty string`);
        }
      });
    }
  }

  if (recipe.steps != null){
    if (!Array.isArray(recipe.steps)){
      fail(`${prefix}: steps must be an array`);
    } else {
      recipe.steps.forEach((item, i) => {
        if (typeof item !== 'string' || !item.trim()){
          fail(`${prefix}.steps[${i}]: must be a non-empty string`);
        }
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

const options = parseArgs();
let validatedCount = 0;

if (options.mode === 'database'){
  const raw = readFileOrExit(RECIPES_FILE);
  const data = loadJson(raw, RECIPES_FILE);
  validateRecipeList(data, 'recipes');
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
