#!/usr/bin/env node
'use strict';
// Execute the ACTUAL BETA code with the real canonical fixture index.
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const html=fs.readFileSync('beta/clubfinder-beta.html','utf8');
const competition=JSON.parse(fs.readFileSync('competition.json','utf8'));
const node=()=>({value:'',textContent:'',innerHTML:'',hidden:false,style:{},dataset:{},children:[],
  addEventListener(){},removeEventListener(){},focus(){},setAttribute(){},removeAttribute(){},
  appendChild(){},remove(){},insertAdjacentElement(){},querySelectorAll(){return []},
  classList:{add(){},remove(){}}});
const els=new Proxy({},{get:(o,k)=>o[k]||(o[k]=node())});
const doc={readyState:'complete',activeElement:null,getElementById:id=>els[id],
  querySelector:()=>node(),querySelectorAll:()=>[],createElement:()=>node(),
  addEventListener(){},removeEventListener(){},body:node()};
const local={},session={},store=o=>({getItem:k=>o[k]??null,
  setItem:(k,v)=>{o[k]=String(v)},removeItem:k=>delete o[k]});
const ctx={console,process,document:doc,navigator:{},localStorage:store(local),
  sessionStorage:store(session),MutationObserver:undefined,URL,URLSearchParams,
  TextEncoder,TextDecoder,setTimeout,clearTimeout,
  location:{href:'https://example.test/beta/clubfinder-beta.html',
    replace(v){this.href=v}},
  open:()=>({document:{open(){},write(){},close(){},body:{innerHTML:''},
    documentElement:{innerHTML:''}},focus(){},print(){},close(){}}),
  fetch:async url=>{
    const s=String(url);
    if(s.includes('competition.json'))return {ok:true,status:200,
      json:async()=>JSON.parse(JSON.stringify(competition)),
      text:async()=>JSON.stringify(competition)};
    if(s.includes('counter-config.json'))return {ok:true,status:200,
      json:async()=>({increment_url:'https://counter.invalid/increment'})};
    throw Error('Unexpected BETA Exmouth regression network call: '+s);
  }};
ctx.window=ctx;ctx.globalThis=ctx;vm.createContext(ctx);
const scripts=[...html.matchAll(/<script[^>]*>([\s\S]*?)<\/script>/gi)]
  .map(m=>m[1]).join('\n');
assert(scripts.length>15000,'BETA scripts missing');
vm.runInContext(scripts,ctx,{filename:'beta/clubfinder-beta.html',timeout:25000});
const run=(s,vars={})=>{Object.assign(ctx,vars);return vm.runInContext(s,ctx,{timeout:25000});};
const norm=s=>String(s||'').toLowerCase().replace(/&/g,' and ')
  .replace(/\b(fc|afc|cfc)\b/g,' ').replace(/[^a-z0-9]+/g,' ').trim();
(async()=>{
  await run('refreshCompetitionData(false)');
  const indexed=competition.fixtures['Exmouth Town']||competition.fixtures['Exmouth Town FC'];
  assert(indexed&&indexed.home==='Thame Utd or Exmouth Town',
    'Real canonical Exmouth source index absent: regression would be meaningless');
  const origin=name=>run('ELIGIBLE.find(c=>sameClubIdentity(c.name,__n))',{__n:name});
  const exmouth=origin('Exmouth Town');
  const thame=origin('Thame United');
  const eastbourne=origin('Eastbourne Borough');
  assert(exmouth&&thame&&eastbourne,'Required eligible origins missing');
  const next=o=>run('nextRoundInfo(__o)',{__o:o});
  const losing=next(exmouth),winning=next(thame),opposing=next(eastbourne);
  assert(!losing.knownFixture,'Direct Exmouth index falsely promotes eliminated club');
  assert(winning.knownFixture,'Verified Thame fixture disappeared');
  assert.equal(norm(winning.knownFixture.home),norm('Thame United'));
  assert.equal(norm(winning.knownFixture.away),norm('Eastbourne Borough'));
  assert.equal(winning.knownFixture.date,'2026-10-03');
  assert.equal(winning.knownFixture.conditional,false);
  assert(opposing.knownFixture,'Legitimate Eastbourne opposing fixture disappeared');
  assert.equal(norm(opposing.knownFixture.home),norm('Thame United'));
  const lastReplay=r=>r&&r.round==='Second Round Qualifying Replay'&&
    r.home==='Exmouth Town'&&r.away==='Thame United'&&
    r.date==='2026-09-23'&&r.home_score===1&&r.away_score===3;
  assert(Object.values(competition.results||{}).some(lastReplay),
    'Final replay result not in canonical competition');
  const pending=JSON.parse(JSON.stringify(competition));
  pending.results=Object.fromEntries(Object.entries(pending.results||{})
    .filter(([,r])=>!lastReplay(r)));
  pending.result_history=Object.fromEntries(Object.entries(pending.result_history||{})
    .map(([k,rows])=>[k,Array.isArray(rows)?rows.filter(r=>!lastReplay(r)):rows]));
  run('LIVE_COMPETITION_DATA=__pending',{__pending:pending});
  const thamePending=next(thame);
  assert(!thamePending.knownFixture,
    'Unverified replay must not promote Thame');
  run('LIVE_COMPETITION_DATA=__canonical',{__canonical:competition});
  console.log('BETA ACTUAL DIRECT EXMOUTH INDEX REGRESSION: PASS');
  console.log('Exmouth: no next fixture; Thame: Thame v Eastbourne 2026-10-03; pending replay fail-closed');
})().catch(e=>{console.error(e.stack||e);process.exitCode=1});
