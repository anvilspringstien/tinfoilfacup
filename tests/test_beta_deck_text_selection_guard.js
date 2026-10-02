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
assert(/button\{font:inherit;touch-action:manipulation\}/.test(html),
  'Rapid-tap controls must suppress accidental double-tap zoom');
assert(/\.cardstage\{[^}]*touch-action:manipulation/.test(html),
  'Main Challenge mat must permit deliberate pinch zoom');
assert(/\.trophy-viewer\{[^}]*touch-action:manipulation/.test(html) &&
       /\.trophy-viewer-mat\{[^}]*touch-action:manipulation/.test(html),
  'Trophy viewer must permit pinch zoom without restoring double-tap zoom');
assert(/\.trophy-viewer-mat\{[^}]*width:min\(610px,96vw,calc\(100dvh - 110px\)\)/.test(html),
  'Mobile Trophy mat must use the same 96vw legibility target as the main Deck');

console.log('BETA DECK TEXT-SELECTION GUARD: PASS');
