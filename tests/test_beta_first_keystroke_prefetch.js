#!/usr/bin/env node
'use strict';

const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');

const html=fs.readFileSync('beta/clubfinder-beta.html','utf8');

const readyStart=html.indexOf('let tinFoilCompetitionReady=null;');
const readyEnd=html.indexOf('const tinFoilSavedCampaignAtStartup=',readyStart);
assert(readyStart>=0&&readyEnd>readyStart,'Competition readiness promise boundary missing');
const readySource=html.slice(readyStart,readyEnd);

const inputStart=html.indexOf("document.getElementById('postcode').addEventListener('input'");
const inputEnd=html.indexOf("document.getElementById('findBtn')",inputStart);
assert(inputStart>=0&&inputEnd>inputStart,'Postcode input handler boundary missing');
const inputSource=html.slice(inputStart,inputEnd);

assert(inputSource.includes("if(this.value.trim())tinFoilEnsureCompetitionReady().catch(()=>{});"),
  'First-keystroke competition warm-up missing');
assert(html.includes("const tinFoilNeedsCompetitionAtStartup=!!(tinFoilStatsRouteRequested||(tinFoilSavedCampaignAtStartup&&tinFoilSavedCampaignAtStartup.postcode));"),
  'Fresh-load deferral contract changed');

let fetches=0,inputHandler=null;
const postcode={
  value:'',
  addEventListener(type,fn){if(type==='input')inputHandler=fn;}
};
const ctx={
  console,
  refreshCompetitionData:()=>{fetches++;return Promise.resolve(true);},
  document:{getElementById:id=>{assert.equal(id,'postcode');return postcode;}}
};
vm.createContext(ctx);
vm.runInContext(readySource,ctx);
vm.runInContext(inputSource,ctx);

assert.equal(fetches,0,'Fresh Clubfinder setup must not fetch competition data');
assert.equal(typeof inputHandler,'function','Postcode input handler was not registered');

postcode.value='';
inputHandler.call(postcode);
assert.equal(fetches,0,'Empty input must not fetch competition data');

postcode.value='g';
inputHandler.call(postcode);
assert.equal(postcode.value,'G','Postcode uppercase behaviour changed');
assert.equal(fetches,1,'First non-empty postcode input must start competition fetch');

postcode.value='gl';
inputHandler.call(postcode);
assert.equal(postcode.value,'GL');
assert.equal(fetches,1,'Further typing must reuse the same competition readiness promise');

const findPromise=vm.runInContext('tinFoilEnsureCompetitionReady()',ctx);
assert.equal(fetches,1,'Find path must reuse the first-keystroke competition promise');
await findPromise;

console.log('BETA FIRST-KEYSTROKE COMPETITION PREFETCH: PASS');
console.log('fresh load: deferred | first input: starts once | further input/Find: reuses promise');
