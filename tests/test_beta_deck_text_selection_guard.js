#!/usr/bin/env node
'use strict';

const assert=require('node:assert/strict');
const fs=require('node:fs');
const html=fs.readFileSync('beta/challenges-beta.html','utf8');

assert(html.includes('flipcard.addEventListener("mousedown",e=>{'),
  'Deck flip card must suppress native mouse-down selection');
assert(html.includes('if(e.button===0)e.preventDefault();'),
  'Primary mouse button must prevent default selection behaviour');
assert(html.includes('flipcard.onclick=()=>{ if(suppressFlip){suppressFlip=false;return;} flipMat(); };'),
  'Deck click-to-flip behaviour must remain intact');
assert(html.includes('flipcard.addEventListener("keydown",e=>{'),
  'Keyboard flip interaction must remain intact');

console.log('BETA DECK TEXT-SELECTION GUARD: PASS');
