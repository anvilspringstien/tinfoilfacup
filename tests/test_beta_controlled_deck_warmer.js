#!/usr/bin/env node
'use strict';

const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');

const html=fs.readFileSync('beta/challenges-beta.html','utf8');
const start=html.indexOf('const ART_PRELOAD_CACHE=new Map();');
const end=html.indexOf("window.name='TFFC_CHALLENGES';",start);
assert(start>=0&&end>start,'Deck warmup subsystem missing');
const code=html.slice(start,end);

const images=[];
const timers=[];
let idleCallback=null;

class FakeImage{
  constructor(){this.fetchPriority='auto';this.decoding='';this.onload=null;this.onerror=null;this._src='';images.push(this);}
  set src(v){this._src=v;}
  get src(){return this._src;}
  decode(){return Promise.resolve();}
}

const ctx={
  console,
  Image:FakeImage,
  Promise,
  Map,
  setTimeout(fn,delay){timers.push({fn,delay});return timers.length;},
  requestIdleCallback(fn){idleCallback=fn;return 1;}
};
ctx.window=ctx;
vm.createContext(ctx);

const challenges=Array.from({length:6},(_,i)=>({id:String(i).padStart(2,'0')}));
const art=Object.fromEntries(challenges.map(c=>[c.id,{
  front:`mat-${c.id}-front.webp`,
  back:`mat-${c.id}-back.webp`
}]));
vm.runInContext('const CHALLENGES='+JSON.stringify(challenges)+'; const ART='+JSON.stringify(art)+';',ctx);
vm.runInContext(code,ctx,{filename:'deck-warmer-subsystem.js'});

assert.equal(typeof idleCallback,'function','Opening mat warmup must remain idle-scheduled');
idleCallback();
assert.equal(images.length,2,'Opening warmup must request only mat 00 front/back');
assert(images.every(img=>img.fetchPriority==='high'),'Opening mat must be high priority');

function fireFor(prefix){
  for(const img of images.filter(x=>x.src.startsWith(prefix)&&x.onload)) img.onload();
}
async function flush(){
  for(let i=0;i<8;i++) await Promise.resolve();
}

(async()=>{
  // Opening-neighbour stage must not start the background march until 00-02 settle.
  vm.runInContext('warmOpeningNeighbours()',ctx);
  assert.equal(images.length,6,'Opening neighbourhood must total mats 00-02 only');
  assert.equal(images.filter(x=>x.src.startsWith('mat-01')).length,2,'Mat 01 missing');
  assert.equal(images.filter(x=>x.src.startsWith('mat-02')).length,2,'Mat 02 missing');
  assert.equal(images.find(x=>x.src==='mat-01-front.webp').fetchPriority,'high','Mat 01 must be high priority');
  assert.equal(images.find(x=>x.src==='mat-02-front.webp').fetchPriority,'low','Mat 02 must stay low priority');

  fireFor('mat-00');
  fireFor('mat-01');
  fireFor('mat-02');
  await flush();

  assert.equal(timers.length,1,'Exactly one background timer should be queued after 00-02 settle');
  assert.equal(timers[0].delay,250,'First background march should pause after opening neighbourhood');
  assert.equal(images.filter(x=>x.src.startsWith('mat-03')).length,0,'Mat 03 must not start before scheduled background turn');

  // One cold mat at a time.
  timers.shift().fn();
  assert.equal(images.filter(x=>x.src.startsWith('mat-03')).length,2,'First background turn must fetch mat 03 only');
  assert.equal(images.filter(x=>x.src.startsWith('mat-04')).length,0,'Mat 04 must wait until mat 03 settles');
  const mat3=images.filter(x=>x.src.startsWith('mat-03'));
  assert(mat3.every(x=>x.fetchPriority==='low'),'Background mat must start low priority');

  // Foreground navigation reuses and promotes the in-flight requests.
  vm.runInContext('preloadMatAt(3,"high")',ctx);
  assert.equal(images.filter(x=>x.src.startsWith('mat-03')).length,2,'Foreground promotion must not duplicate mat 03 requests');
  assert(mat3.every(x=>x.fetchPriority==='high'),'Foreground navigation must promote in-flight mat 03 requests');

  fireFor('mat-03');
  await flush();
  assert.equal(timers.length,1,'Next background turn should be queued only after mat 03 settles');
  assert.equal(images.filter(x=>x.src.startsWith('mat-04')).length,0,'Mat 04 must still be untouched before the timer fires');

  timers.shift().fn();
  assert.equal(images.filter(x=>x.src.startsWith('mat-04')).length,2,'Second background turn must move to mat 04');
  assert.equal(images.filter(x=>x.src.startsWith('mat-05')).length,0,'Only one background mat may be in flight');

  console.log('BETA CONTROLLED DECK WARMER: PASS');
  console.log('00-02 first | one cold mat at a time | foreground promotion | no duplicate requests');
})().catch(err=>{console.error(err);process.exit(1);});
