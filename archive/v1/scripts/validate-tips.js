#!/usr/bin/env node
'use strict';

const fs = require('fs');
const path = require('path');

const TIPS_FILE = path.join(__dirname, '..', 'data', 'tips.json');
const SECTION_ID_PATTERN = /^\d{2}$/;
const ITEM_ID_PATTERN = /^\d{2}-\d{2}$/;
const KIND = new Set(['technique', 'mistake', 'timing', 'accuracy', 'heat', 'storage']);
const TAGS = new Set([
  'prep',
  'knives',
  'skillet',
  'oven',
  'dough',
  'ingredients',
  'spices',
  'taste',
  'meat',
  'fish',
  'veg',
  'grains',
  'sauce',
  'storage',
  'safety',
]);
const ALLOWED_ITEM_KEYS = new Set(['id', 'hint', 'explanation', 'kind', 'tags']);

function fail(message){
  console.error(`ERROR: ${message}`);
  process.exitCode = 1;
}

let raw;
try {
  raw = fs.readFileSync(TIPS_FILE, 'utf8');
} catch {
  fail(`cannot read ${TIPS_FILE}`);
  process.exit(1);
}

let data;
try {
  data = JSON.parse(raw);
} catch (e){
  fail(`invalid JSON: ${e.message}`);
  process.exit(1);
}

if (!data || typeof data !== 'object' || Array.isArray(data)){
  fail('tips.json must be an object');
  process.exit(1);
}

if (!data.intro || typeof data.intro !== 'string'){
  fail('tips.json: missing intro string');
}

if (!Array.isArray(data.sections) || data.sections.length === 0){
  fail('tips.json: sections must be a non-empty array');
}

const sectionIds = new Set();
const itemIds = new Set();
let itemCount = 0;

data.sections.forEach((section, index) => {
  const prefix = `sections[${index}]`;
  if (!section || typeof section !== 'object'){
    fail(`${prefix}: must be an object`);
    return;
  }
  for (const field of ['id', 'title', 'items']){
    if (section[field] == null || section[field] === ''){
      fail(`${prefix}: missing "${field}"`);
    }
  }
  if (section.id && !SECTION_ID_PATTERN.test(section.id)){
    fail(`${prefix}: id must be two digits, got "${section.id}"`);
  }
  if (section.id){
    if (sectionIds.has(section.id)) fail(`duplicate section id "${section.id}"`);
    sectionIds.add(section.id);
  }
  if (!Array.isArray(section.items) || section.items.length === 0){
    fail(`${prefix}: items must be a non-empty array`);
    return;
  }
  section.items.forEach((item, i) => {
    const itemPrefix = `${prefix}.items[${i}]`;
    itemCount += 1;
    if (!item || typeof item !== 'object' || Array.isArray(item)){
      fail(`${itemPrefix}: must be an object`);
      return;
    }
    for (const key of Object.keys(item)){
      if (!ALLOWED_ITEM_KEYS.has(key)){
        fail(`${itemPrefix}: unexpected key "${key}"`);
      }
    }
    if (typeof item.id !== 'string' || !item.id){
      fail(`${itemPrefix}: missing "id"`);
    } else {
      if (!ITEM_ID_PATTERN.test(item.id)){
        fail(`${itemPrefix}: id must match NN-NN, got "${item.id}"`);
      }
      const expectedId = section.id
        ? `${section.id}-${String(i + 1).padStart(2, '0')}`
        : null;
      if (expectedId && item.id !== expectedId){
        fail(`${itemPrefix}: id must be "${expectedId}", got "${item.id}"`);
      }
      if (itemIds.has(item.id)) fail(`duplicate item id "${item.id}"`);
      itemIds.add(item.id);
    }
    if (typeof item.hint !== 'string' || !item.hint.trim()){
      fail(`${itemPrefix}: hint must be a non-empty string`);
    }
    if (item.explanation != null && typeof item.explanation !== 'string'){
      fail(`${itemPrefix}: explanation must be a string`);
    }
    if (typeof item.kind !== 'string' || !KIND.has(item.kind)){
      fail(`${itemPrefix}: kind must be one of ${[...KIND].join('|')}`);
    }
    if (!Array.isArray(item.tags)){
      fail(`${itemPrefix}: tags must be an array of 1–3 unique codes`);
      return;
    }
    if (item.tags.length < 1 || item.tags.length > 3){
      fail(`${itemPrefix}: tags must have 1–3 items, got ${item.tags.length}`);
    }
    const seenTags = new Set();
    item.tags.forEach((tag, ti) => {
      if (typeof tag !== 'string' || !TAGS.has(tag)){
        fail(`${itemPrefix}.tags[${ti}]: unknown tag "${tag}"`);
      }
      if (seenTags.has(tag)){
        fail(`${itemPrefix}: duplicate tag "${tag}"`);
      }
      seenTags.add(tag);
    });
  });
});

if (process.exitCode){
  console.error('\nTips validation failed.');
  process.exit(1);
}

console.log(`OK: ${data.sections.length} tip section(s), ${itemCount} item(s) validated.`);
