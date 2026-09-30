#!/usr/bin/env node
'use strict';

const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');

const live=fs.readFileSync('beta/clubfinder-beta.html','utf8');
const normal=fs.readFileSync('beta/clubfinder-load-diagnostic-normal.html','utf8');
const shellBase=fs.readFileSync('beta/clubfinder-shell-prototype.html','utf8');
const shell=fs.readFileSync('beta/clubfinder-load-diagnostic-shell.html','utf8');
const externalEngine=fs.readFileSync('beta/clubfinder-shell-prototype-engine.js','utf8');

function scripts(html){
  return [...html.matchAll(/<script[^>]*>([\s\S]*?)<\/script>/gi)].map(m=>m[1]);
}
function largest(list){return list.slice().sort((a,b)=>b.length-a.length)[0]||'';}

const liveEngine=largest(scripts(live));
const normalEngine=largest(scripts(normal));
assert.equal(normalEngine,liveEngine,'Normal diagnostic changed the accepted inline Clubfinder engine');
assert.equal(externalEngine,liveEngine,'Shell prototype engine is no longer the accepted BETA engine');

for(const [name,html] of [['normal',normal],['shell',shell]]){
  const blocks=scripts(html);
  assert(blocks.length>=3,name+' diagnostic scripts missing');
  for(let i=0;i<blocks.length;i++)assert.doesNotThrow(()=>new vm.Script(blocks[i]),name+' script '+i+' has a syntax error');
  assert(html.includes('TFFC LOAD DIAGNOSTICS'),name+' diagnostic instrumentation missing');
  assert(html.includes('Copy results'),name+' copy-results control missing');
  assert(html.includes('firstContentfulPaint'),name+' FCP timing missing');
  assert(html.includes('competitionReady'),name+' competition-ready timing missing');
  assert(html.includes('campaignsRendered'),name+' rendered-campaign timing missing');
}

assert(normal.includes('__tffcDiagMark("engineReady")'),'Normal inline engine-ready marker missing');
assert(shell.includes('__diagSlow'),'Shell controlled slow-engine mode missing');
assert(shell.includes("get('cold')==='1'"),'Shell cold-engine cache-bust mode missing');
assert(shell.includes('engineDelayStart'),'Shell engine-delay timing marker missing');
assert(shell.includes('clubfinder-shell-prototype-engine.js'),'Shell no longer loads accepted external engine');
assert(!shell.includes('const ELIGIBLE=['),'Heavy club index leaked back into diagnostic shell');

const liveBytes=Buffer.byteLength(live);
const normalBytes=Buffer.byteLength(normal);
const shellBytes=Buffer.byteLength(shell);
assert(normalBytes-liveBytes<15000,'Normal instrumentation grew unexpectedly large');
assert(shellBytes<30000,'Shell diagnostic exceeded 30 KB HTML budget');

console.log('BETA LOAD DIAGNOSTICS: PASS');
console.log(JSON.stringify({
  liveBytes,normalDiagnosticBytes:normalBytes,shellDiagnosticBytes:shellBytes,
  acceptedEngineBytes:Buffer.byteLength(liveEngine),normalEngineExact:true,shellEngineExact:true,
  slowMode:true,coldMode:true
}));
