#!/usr/bin/env node
'use strict';

const assert=require('node:assert/strict');
const fs=require('node:fs');

const html=fs.readFileSync('beta/challenges-beta.html','utf8');

assert(html.includes('function warmChallengeArt(){\n  preloadFaceAt(0,"front","high");\n  scheduleDeckWarm(100);\n}'),
  'Challenges startup must give the visible mat 00 front first claim, then start a gentle future-front sweep');
assert(html.includes('function warmOpeningNeighbours(){'),
  'Challenges must retain neighbour strengthening after mat 00 paints');
assert(html.includes('preloadFaceAt(0,"back","high");\n  preloadFaceAt(1,"front","high");\n  preloadFaceAt(2,"front","high");\n  preloadFaceAt(3,"front","low");'),
  'Opening browse path must strengthen nearby fronts without bursting unseen reverses');
assert(html.includes('if(side==="front" && c.id==="00" && !INITIAL_FRONT_READY)'),
  'Opening neighbour warmup must wait for the visible mat 00 front');
assert(html.includes('requestAnimationFrame(()=>warmOpeningNeighbours());'),
  'Opening neighbour warmup must be deferred until after mat 00 front reveal');
assert(html.includes('preloadFaceAt(index,"front","high");'),
  'Current visible front must remain high priority');
assert(html.includes('preloadFaceAt(index,"back",(index===0 && !INITIAL_FRONT_READY)?"low":"high");'),
  'Initial hidden mat 00 reverse must not compete equally with the visible front');
assert(html.includes('preloadFaceAt(index+1,"front","high");'),
  'Foreground neighbour warmup must favour next-card fronts');

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
