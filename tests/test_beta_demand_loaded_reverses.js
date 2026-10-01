#!/usr/bin/env node
'use strict';

const assert=require('node:assert/strict');
const fs=require('node:fs');

const html=fs.readFileSync('beta/challenges-beta.html','utf8');

assert(html.includes('function scheduleCurrentBackWarm(i,id){'),
  'Reverse linger scheduler missing');
assert(html.includes('},2500);'),
  'Reverse linger scheduler must wait 2.5 seconds');
assert(html.includes('buildFace(front,c,"front","high");'),
  'Visible Deck front must load immediately');
assert(html.includes('// The hidden reverse is demand-loaded:'),
  'Demand-loaded reverse marker missing');
assert(!html.includes('buildFace(front,c,"front"); buildFace(back,c,"back");'),
  'Navigation must not build both Deck faces eagerly');
assert(!html.includes('preloadFaceAt(index,"back",(index===0 && !INITIAL_FRONT_READY)?"low":"high");'),
  'Navigation must not request current reverse eagerly');
assert(html.includes('buildFace(back,c,"back","high").then(ok=>{'),
  'Explicit flip must demand-load reverse at high priority');
assert(html.includes('if(!ok || index!==expectedIndex || CHALLENGES[index]?.id!==expectedId)return;'),
  'Flip must not complete on stale reverse loads');
assert(html.includes('setDeckFlip(true);'),
  'Flip must wait until reverse load succeeds');
assert(html.includes('entry.img=null;'),
  'Completed preload image objects must be released');

console.log('BETA DEMAND-LOADED DECK REVERSES: PASS');
