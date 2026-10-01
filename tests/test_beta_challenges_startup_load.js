#!/usr/bin/env node
'use strict';

const assert=require('node:assert/strict');
const fs=require('node:fs');

const html=fs.readFileSync('beta/challenges-beta.html','utf8');

assert(html.includes('function warmChallengeArt(){\n  preloadMatAt(0,"high");\n}'),
  'Challenges startup must warm only the opening mat before it is visible');
assert(html.includes('function warmOpeningNeighbours(){\n  preloadMatAt(1,"high");\n  preloadMatAt(2,"low");\n}'),
  'Challenges must retain neighbour warmup after the opening mat');
assert(html.includes('if(side==="front" && c.id==="00" && !INITIAL_FRONT_READY)'),
  'Opening neighbour warmup must wait for the visible mat 00 front');
assert(html.includes('requestAnimationFrame(()=>warmOpeningNeighbours());'),
  'Opening neighbour warmup must be deferred until after mat 00 front reveal');
assert(html.includes('if(index!==0 || INITIAL_FRONT_READY)'),
  'Initial render must not preload neighbours before mat 00 is visible');

assert(html.includes('let CABINET_IMAGE_OBSERVER=null;'),
  'Trophy Cabinet must use explicit image deferral');
assert(html.includes('const CABINET_THUMB=id=>`assets/challenge-thumbs/mat-${id}-front.webp`;'),
  'Trophy Cabinet must have a dedicated thumbnail asset route');
assert(html.includes('img.dataset.src=CABINET_THUMB(c.id);'),
  'Trophy Cabinet thumbnails must remain in data-src until near the viewport');
assert(html.includes('img.dataset.fallback=ART[c.id]?.front || CANONICAL_CUP || "";'),
  'Trophy Cabinet thumbnail failure must retain the full front artwork fallback');
assert(html.includes('function loadCabinetImage(img){'),
  'Trophy Cabinet deferred loader helper is missing');
assert(html.includes('new IntersectionObserver(entries=>'),
  'Trophy Cabinet artwork must load through IntersectionObserver when supported');
assert(!html.includes('img.loading="lazy"; img.decoding="async"; img.src=ART[c.id]?.front'),
  'Trophy Cabinet must not rely on browser lazy-loading for startup artwork');

console.log('BETA CHALLENGES STARTUP LOAD: PASS');
