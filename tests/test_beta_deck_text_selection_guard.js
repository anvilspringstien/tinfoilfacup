#!/usr/bin/env node
'use strict';

const assert=require('node:assert/strict');
const fs=require('node:fs');
const html=fs.readFileSync('beta/challenges-beta.html','utf8');

assert(/\.deck\{[^}]*user-select:none;[^}]*-webkit-user-select:none/.test(html),
  'Entire Deck UI must be non-selectable');
assert(!html.includes('flipcard.addEventListener("mousedown",e=>{'),
  'Ineffective mouse-down selection workaround must be removed');
assert(html.includes('flipcard.onclick=()=>{ if(suppressFlip){suppressFlip=false;return;} flipMat(); };'),
  'Deck click-to-flip behaviour must remain intact');
assert(html.includes('flipcard.addEventListener("keydown",e=>{'),
  'Keyboard flip interaction must remain intact');

console.log('BETA DECK TEXT-SELECTION GUARD: PASS');
