#!/usr/bin/env node
'use strict';

const fs = require('fs');
const path = require('path');

const TIPS_FILE = path.join(__dirname, '..', 'data', 'tips.json');
const ID_PATTERN = /^\d{2}$/;

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

const ids = new Set();
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
  if (section.id && !ID_PATTERN.test(section.id)){
    fail(`${prefix}: id must be two digits, got "${section.id}"`);
  }
  if (section.id){
    if (ids.has(section.id)) fail(`duplicate section id "${section.id}"`);
    ids.add(section.id);
  }
  if (!Array.isArray(section.items) || section.items.length === 0){
    fail(`${prefix}: items must be a non-empty array`);
  } else {
    section.items.forEach((item, i) => {
      const itemPrefix = `${prefix}.items[${i}]`;
      if (!item || typeof item !== 'object' || Array.isArray(item)){
        fail(`${itemPrefix}: must be an object with hint and explanation`);
        return;
      }
      if (typeof item.hint !== 'string' || !item.hint.trim()){
        fail(`${itemPrefix}: hint must be a non-empty string`);
      }
      if (item.explanation != null && typeof item.explanation !== 'string'){
        fail(`${itemPrefix}: explanation must be a string`);
      }
    });
  }
});

if (process.exitCode){
  console.error('\nTips validation failed.');
  process.exit(1);
}

console.log(`OK: ${data.sections.length} tip section(s) validated.`);
