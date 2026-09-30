#!/usr/bin/env node
'use strict';

const assert=require('node:assert/strict');
const fs=require('node:fs');

const live=fs.readFileSync('beta/clubfinder-beta.html','utf8');
const shell=fs.readFileSync('beta/clubfinder-shell-prototype.html','utf8');
const engine=fs.readFileSync('beta/clubfinder-shell-prototype-engine.js','utf8');

const scripts=[...live.matchAll(/<script[^>]*>([\s\S]*?)<\/script>/gi)];
assert(scripts.length>=3,'Expected current BETA scripts');
const inlineEngine=scripts.map(m=>m[1]).sort((a,b)=>b.length-a.length)[0];

assert.equal(engine,inlineEngine,'Prototype engine is not an exact extraction of current BETA inline engine');
assert(engine.length>500000,'Prototype engine unexpectedly small');
assert(shell.length<20000,'Shell-first prototype exceeded 20 KB source budget');
assert(shell.includes('id="postcode"'),'Postcode input missing from shell');
assert(shell.includes('id="findBtn"'),'Find My Club button missing from shell');
assert(shell.includes("clubfinder-shell-prototype-engine.js"),'External engine loader missing');
assert(shell.includes("requestAnimationFrame(()=>requestAnimationFrame(loadEngine))"),
  'Prototype no longer guarantees a paint opportunity before background engine load');
assert(shell.includes("warmCompetitionWhenReady"),'Typing no longer warms competition data');
assert(shell.includes("pendingFind"),'Early Find click queue missing');
assert(!shell.includes('const ELIGIBLE='),'Eligible table still blocks shell paint');
assert(!shell.includes('const GROUNDS='),'Ground table still blocks shell paint');
assert(!shell.includes('LAW2_ORIGIN_LOCATIONS=['),'Law 2 table still blocks shell paint');
assert(!shell.includes('function go('),'Heavy Clubfinder engine still embedded in shell');

for(const needle of [
  'Gloucester City AFC',
  'The KMM Energy Stadium',
  'tinFoilBetaVerifiedMulbartonReplay',
  'tinFoilBetaResultVoided',
  'BETA diagnostic competition data loaded'
]){
  assert(engine.includes(needle),'Accepted BETA engine anchor missing: '+needle);
}

const liveBytes=Buffer.byteLength(live);
const shellBytes=Buffer.byteLength(shell);
const engineBytes=Buffer.byteLength(engine);
const reduction=100*(1-shellBytes/liveBytes);

console.log('BETA SHELL-FIRST PROTOTYPE: PASS');
console.log(JSON.stringify({
  liveHtmlBytes:liveBytes,
  shellHtmlBytes:shellBytes,
  externalEngineBytes:engineBytes,
  initialHtmlReductionPercent:Number(reduction.toFixed(1)),
  engineExactMatch:true
}));
