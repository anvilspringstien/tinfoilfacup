#!/usr/bin/env node
'use strict';
// Regress the actual BETA decision functions, not a copied implementation.
// Legacy results may have a completed, oriented "pens 5-6" decision but
// lack the separate winner field. Do not invent a winner for ambiguous rows.
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const html=fs.readFileSync('beta/clubfinder-beta.html','utf8');
function between(start,end){
  const a=html.indexOf(start),b=html.indexOf(end,a);
  assert(a>=0&&b>a,'Missing Clubfinder function boundary: '+start);
  return html.slice(a,b);
}
const ctx={};vm.createContext(ctx);
vm.runInContext(
  between('function canonicalResultWinner(','function sameSemanticResult(')+
  between('function resultNeedsReplay(','function replayVenue('),ctx);
const base={round:'Extra Preliminary Round Replay',
  home:'Nantwich Town',away:'Sporting Khalsa',
  home_score:1,away_score:1,status:'FT'};
const verdict=(r)=>[ctx.canonicalResultWinner(r),ctx.resultNeedsReplay(r)];
assert.deepEqual(verdict({...base,decision:'pens 5-6'}),['Sporting Khalsa',false],
  'Completed Nantwich replay must transfer custody to Sporting Khalsa');
assert.deepEqual(verdict({...base,decision:'pens 6-5'}),['Nantwich Town',false],
  'Shootout orientation must work in both directions');
assert.deepEqual(verdict({...base,decision:'penalties',winner:'Sporting Khalsa'}),
  ['Sporting Khalsa',false],'Modern explicit penalty winner regressed');
assert.deepEqual(verdict({...base,decision:'draw-replay',winner:''}),
  ['',true],'First tied fixture must still require its replay');
assert.deepEqual(verdict({...base,decision:'pens 5-5'}),
  ['',true],'Tied shootout must not invent a winner');
assert.deepEqual(verdict({...base,decision:'pens unknown'}),
  ['',true],'Unknown shootout must not invent a winner');
assert.deepEqual(verdict({...base,decision:'pens 5-6',status:'VOID'}),
  ['',true],'Voided fixture cannot establish custody');
assert.deepEqual(verdict({...base,home_score:2,away_score:1,decision:''}),
  ['Nantwich Town',false],'Ordinary regulation winner regressed');
assert.deepEqual(verdict({...base,decision:'',winner:''}),
  ['',true],'Unresolved level score must remain pending');
console.log('BETA LEGACY PENALTY PROGRESSION REGRESSION: PASS');
