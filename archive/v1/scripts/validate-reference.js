#!/usr/bin/env node
'use strict';

const fs = require('fs');
const path = require('path');

const DATA_DIR = path.join(__dirname, '..', 'data');

function fail(message){
  console.error(`ERROR: ${message}`);
  process.exitCode = 1;
}

function readJson(filePath){
  try {
    return JSON.parse(fs.readFileSync(filePath, 'utf8'));
  } catch (e){
    fail(`${filePath}: ${e.message}`);
    return null;
  }
}

function validateGrains(data, label){
  if (!data?.intro_lead || !data?.intro) fail(`${label}: missing intro`);
  if (!Array.isArray(data?.rows) || data.rows.length === 0){
    fail(`${label}: rows must be a non-empty array`);
    return;
  }
  data.rows.forEach((row, i) => {
    for (const field of ['name', 'wash', 'ratio', 'time', 'note']){
      if (row[field] == null || row[field] === ''){
        fail(`${label}.rows[${i}]: missing "${field}"`);
      }
    }
  });
}

function validateMeat(data, label){
  if (!data?.intro_lead || !data?.intro) fail(`${label}: missing intro`);
  if (!Array.isArray(data?.methods) || data.methods.length === 0){
    fail(`${label}: methods must be a non-empty array`);
    return;
  }
  data.methods.forEach((method, mi) => {
    const mp = `${label}.methods[${mi}]`;
    for (const field of ['name', 'sub', 'cards']){
      if (method[field] == null) fail(`${mp}: missing "${field}"`);
    }
    if (!Array.isArray(method.cards) || method.cards.length === 0){
      fail(`${mp}: cards must be a non-empty array`);
      return;
    }
    method.cards.forEach((card, ci) => {
      const cp = `${mp}.cards[${ci}]`;
      for (const field of ['title', 'readout_label', 'readout_value', 'text', 'pitfall']){
        if (card[field] == null || card[field] === ''){
          fail(`${cp}: missing "${field}"`);
        }
      }
    });
  });
}

const grains = readJson(path.join(DATA_DIR, 'grains.json'));
if (grains) validateGrains(grains, 'grains.json');

for (const file of ['meat-beef.json', 'meat-pork.json', 'meat-poultry.json']){
  const meat = readJson(path.join(DATA_DIR, file));
  if (meat) validateMeat(meat, file);
}

if (process.exitCode){
  console.error('\nReference validation failed.');
  process.exit(1);
}

console.log('OK: grains + meat reference JSON validated.');
