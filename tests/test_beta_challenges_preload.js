#!/usr/bin/env node
'use strict';

const assert=require('node:assert/strict');
const fs=require('node:fs');

const html=fs.readFileSync('beta/clubfinder-beta.html','utf8');

const helperStart=html.indexOf('function tinFoilShowChallengesPrep(){');
const openStart=html.indexOf('async function openChallenges(origin){');
const nav=html.indexOf("window.location.href='challenges-beta.html';",openStart);

assert(helperStart>=0&&helperStart<openStart,'Challenges preparation helper must exist before openChallenges');
assert(openStart>=0,'openChallenges missing');
assert(nav>openStart,'Challenges navigation changed or disappeared');

const openHead=html.slice(openStart,Math.min(nav,openStart+1200));
assert(openHead.includes('await tinFoilPaintChallengesPrep();'),
  'Challenges preparation card must be painted before bridge/Pigeon Miles work');
assert(openHead.indexOf('await tinFoilPaintChallengesPrep();')<openHead.indexOf('const journey=buildJourney(origin)'),
  'Challenges preparation card must paint before journey construction');

const helper=html.slice(helperStart,openStart);
for(const token of [
  "id='tffc-challenges-prep'",
  'Preparing Your Challenges…',
  'Checking your Campaign and loading the Challenge Deck',
  "class=\"prep-rollers\"",
  "aria-live','polite'",
  "prefers-reduced-motion",
  "requestAnimationFrame",
  "@keyframes tffcChallengeRoll",
  "translate3d",
  "window.addEventListener('pagehide',tinFoilRemoveChallengesPrep)",
  "window.addEventListener('pageshow',tinFoilRemoveChallengesPrep)"
]) assert(helper.includes(token),'Challenges preparation contract missing: '+token);

assert(html.includes("window.location.href='challenges-beta.html';"),
  'Challenges must still use the existing same-tab route');
assert(html.includes("sessionStorage.setItem('tffc.challengeOrigin','clubfinder-beta')"),
  'Challenges origin marker changed');
assert(html.includes('tinFoilSaveClubfinderReturnSnapshot();'),
  'Clubfinder return snapshot changed');

console.log('BETA CHALLENGES PRELOAD CARD: PASS');
assert(!helper.includes('setInterval('),'Challenges rollers must not depend on the busy JS main thread');
assert(helper.includes("function tinFoilRemoveChallengesPrep(){"),'History cleanup helper missing');

console.log('BETA CHALLENGES PRELOAD CARD: PASS');
console.log('immediate prep paint | compositor rollers | bfcache cleanup | same route/return semantics');
