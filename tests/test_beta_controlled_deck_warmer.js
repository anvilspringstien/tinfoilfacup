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

function bySrc(src){return images.filter(x=>x.src===src);}
function fire(src){
  for(const img of bySrc(src)) if(img.onload) img.onload();
}
async function flush(){
  for(let i=0;i<8;i++) await Promise.resolve();
}

(async()=>{
  assert.equal(typeof idleCallback,'function','Opening front warmup must remain idle-scheduled');

  // Cold start: only the visible mat 00 front gets an immediate request.
  idleCallback();
  assert.equal(images.length,1,'Cold warmup must request only the visible mat 00 front immediately');
  assert.equal(images[0].src,'mat-00-front.webp','Wrong opening asset');
  assert.equal(images[0].fetchPriority,'high','Visible mat 00 front must be high priority');
  assert.equal(timers.length,1,'Future-front sweep must be scheduled separately');
  assert.equal(timers[0].delay,100,'Future-front sweep should begin gently after mat 00 starts');

  // One quiet future front at a time.
  timers.shift().fn();
  assert.equal(bySrc('mat-01-front.webp').length,1,'First background asset must be mat 01 front');
  assert.equal(bySrc('mat-01-back.webp').length,0,'Future reverse must not compete with browse fronts');
  const front1=bySrc('mat-01-front.webp')[0];
  assert.equal(front1.fetchPriority,'low','Background future front must start low priority');
  assert.equal(bySrc('mat-02-front.webp').length,0,'Only one cold future front may be in flight');

  // Foreground navigation promotes the same request instead of duplicating it.
  vm.runInContext('preloadFaceAt(1,"front","high")',ctx);
  assert.equal(bySrc('mat-01-front.webp').length,1,'Foreground promotion must not duplicate mat 01 front');
  assert.equal(front1.fetchPriority,'high','Foreground navigation must promote an in-flight future front');

  fire('mat-01-front.webp');
  await flush();
  assert.equal(vm.runInContext('ART_PRELOAD_CACHE.get("mat-01-front.webp").img',ctx),null,
    'Settled preloader Image must be released so hidden decoded mats cannot accumulate');
  assert.equal(timers.length,1,'Next future front should schedule only after mat 01 settles');
  assert.equal(timers[0].delay,120,'Steady-state front sweep cadence changed unexpectedly');
  assert.equal(bySrc('mat-02-front.webp').length,0,'Mat 02 front must wait for the next sweep turn');

  timers.shift().fn();
  assert.equal(bySrc('mat-02-front.webp').length,1,'Second sweep turn must fetch mat 02 front');
  assert.equal(bySrc('mat-02-back.webp').length,0,'Back sweep must not start while fronts remain');

  // Finish the front sweep.
  for(let i=2;i<=5;i++){
    const src=`mat-${String(i).padStart(2,'0')}-front.webp`;
    if(bySrc(src).length===0){
      assert.equal(timers.length,1,'Expected one timer before '+src);
      timers.shift().fn();
      assert.equal(bySrc(src).length,1,'Missing '+src);
    }
    fire(src);
    await flush();
  }

  // One transition turn changes phase; only then may reverse artwork begin.
  assert.equal(timers.length,1,'Front sweep completion must schedule a phase transition');
  timers.shift().fn();
  assert.equal(bySrc('mat-00-back.webp').length,0,'Phase transition must not burst a reverse immediately');
  assert.equal(timers.length,1,'Back sweep must be separately scheduled');
  assert.equal(timers[0].delay,180,'Back sweep should start with a larger pause');

  timers.shift().fn();
  assert.equal(bySrc('mat-00-back.webp').length,1,'Back sweep must begin at mat 00 only after all fronts');
  assert.equal(bySrc('mat-01-back.webp').length,0,'Only one cold reverse may be in flight');
  assert.equal(bySrc('mat-00-back.webp')[0].fetchPriority,'low','Background reverse must stay low priority');

  console.log('BETA CONTROLLED DECK WARMER: PASS');
  console.log('visible front first | sequential future fronts | foreground promotion | backs only after fronts');
})().catch(err=>{console.error(err);process.exit(1);});
