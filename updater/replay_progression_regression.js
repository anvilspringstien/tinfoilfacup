#!/usr/bin/env node
const fs=require('fs');
const path=require('path');
const ROOT=path.resolve(__dirname,'..');
const html=fs.readFileSync(path.join(ROOT,'clubfinder.html'),'utf8');
const competition=JSON.parse(fs.readFileSync(path.join(ROOT,'competition.json'),'utf8'));

function fail(msg){throw new Error(msg)}
function canon(s){return String(s||'').toLowerCase().replace(/\b(association football club|football club)\b/g,' ').replace(/\b(fc|afc|cfc)\b/g,' ').replace(/[^a-z0-9]+/g,' ').trim().replace(/\s+/g,' ')}
function same(a,b){return canon(a)===canon(b)}

if(!html.includes("const progressionRound=String(current||'').replace(/\\s+Replay$/i,'');"))fail('Replay progression normalisation is missing from Clubfinder');
if(!html.includes("if(progressionRound==='First Round Qualifying')nextName='Second Round Qualifying';"))fail('First Qualifying -> Second Qualifying progression map is missing');
if(!html.includes('const compatible=a.filter(x=>{'))fail('Conditional draw abbreviation resolver is missing');

const results=competition.results||{};
const next=competition.fixtures||{};
const replayCases=[
  {winner:'Exmouth Town', opponent:'Banbury United', fixtureKeys:['Exmouth Town']},
  {winner:'Emley AFC', opponent:'Bishop Auckland', fixtureKeys:['Emley AFC','Emley']},
  {winner:'Crowborough Athletic', opponent:'AFC Whyteleafe', fixtureKeys:['Crowborough Athletic','Crowborough']}
];

for(const c of replayCases){
  const candidates=Object.entries(results).filter(([k,r])=>same(k,c.winner)||same(r&&r.winner,c.winner));
  const replay=candidates.map(([,r])=>r).find(r=>/First Round Qualifying Replay$/i.test(String(r&&r.round||''))&&same(r.winner,c.winner));
  if(!replay)fail(c.winner+': decisive First Round Qualifying Replay result missing');
  if(![replay.home,replay.away].some(x=>same(x,c.opponent)))fail(c.winner+': replay opponent mismatch');
  const fixture=c.fixtureKeys.map(k=>next[k]).find(Boolean);
  if(!fixture)fail(c.winner+': published next fixture missing');
  if(fixture.round!=='Second Round Qualifying')fail(c.winner+': next fixture is not Second Round Qualifying');
  const sides=String(fixture.home||'')+' | '+String(fixture.away||'');
  const winnerRoot=canon(c.winner).split(' ')[0];
  if(!canon(sides).includes(winnerRoot))fail(c.winner+': next fixture does not contain winner identity');
}

const frome=next['Frome Town'];
if(!frome||frome.round!=='Second Round Qualifying')fail('Non-replay control: Frome Town next fixture missing or wrong round');

console.log('REPLAY PROGRESSION REGRESSION: PASS');
console.log('First Qualifying replay -> Second Qualifying: PASS');
console.log('Exmouth, Emley and Crowborough published draw links: PASS');
console.log('Abbreviated conditional winner resolver: PRESENT');
console.log('Non-replay control Frome Town: PASS');
