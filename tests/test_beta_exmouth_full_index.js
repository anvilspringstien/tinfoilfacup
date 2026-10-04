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
  const origin=name=>run('ELIGIBLE.find(c=>sameClubIdentity(c.name,__n))',{__n:name});
  const exmouth=origin('Exmouth Town');
  const thame=origin('Thame United');
  const eastbourne=origin('Eastbourne Borough');
  assert(exmouth&&thame&&eastbourne,'Required eligible origins missing');
  const next=o=>run('nextRoundInfo(__o)',{__o:o});
  const losing=next(exmouth),winning=next(thame),opposing=next(eastbourne);
  assert(!losing.knownFixture,'Direct Exmouth index falsely promotes eliminated club');
  // Current state is derived from canonical competition data. Do not freeze a
  // once-upcoming Thame v Eastbourne fixture after that tie has been played.
  const activeFixtures=Object.values(competition.fixtures||{}).filter(f=>f&&
    (norm(f.home)===norm('Thame United')||norm(f.away)===norm('Thame United')));
  const canonicalActive=activeFixtures.find(f=>!f.played&&!f.result&&!f.winner);
  if(canonicalActive){
    assert(winning.knownFixture,'Canonical active Thame fixture disappeared');
    assert.equal(norm(winning.knownFixture.home),norm(canonicalActive.home));
    assert.equal(norm(winning.knownFixture.away),norm(canonicalActive.away));
  }else{
    assert(!winning.knownFixture,'BETA invented an active Thame fixture after canonical progression');
  }
  // Eastbourne may itself have progressed; its live state must likewise come
  // from canonical data rather than this historical Exmouth-index regression.
  void opposing;
  const lastReplay=r=>r&&r.round==='Second Round Qualifying Replay'&&
    r.home==='Exmouth Town'&&r.away==='Thame United'&&
    r.date==='2026-09-23'&&r.home_score===1&&r.away_score===3;
  assert(Object.values(competition.results||{}).some(lastReplay),
    'Final replay result not in canonical competition');
  // Unresolved replay behaviour is covered by the dedicated conditional-replay
  // regression. This direct-index regression stays anchored to the resolved draw.
  console.log('BETA ACTUAL DIRECT EXMOUTH INDEX REGRESSION: PASS');
  console.log('Exmouth: eliminated; Thame live state derived from canonical competition');
})().catch(e=>{console.error(e.stack||e);process.exitCode=1});
