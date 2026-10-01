#!/usr/bin/env node
'use strict';

const assert=require('node:assert/strict');
const fs=require('node:fs');

const html=fs.readFileSync('beta/challenges-beta.html','utf8');

assert(html.includes('.face img{width:100%;height:100%;object-fit:cover;display:block;pointer-events:none;user-select:none;-webkit-user-select:none;-webkit-user-drag:none}'),
  'Deck artwork must remain non-interactive so Chromium cannot press/drag/select the transformed image layer');
assert(html.includes('.flipcard,.face{-webkit-tap-highlight-color:transparent;user-select:none;-webkit-user-select:none}'),
  'Deck card/face native press highlighting and selection must remain disabled');
assert(html.includes('flipcard.onclick=()=>'),
  'Deck card itself must continue to own flip interaction');

console.log('BETA DECK IMAGE HIT-TEST GUARD: PASS');
