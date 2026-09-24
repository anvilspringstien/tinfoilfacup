#!/usr/bin/env node
'use strict';
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
const document={readyState:'complete',activeElement:null,getElementById:id=>els[id],
  querySelector:()=>node(),querySelectorAll:()=>[],createElement:()=>node(),
  addEventListener(){},removeEventListener(){},body:node()};
const local={},session={};
const store=o=>({getItem:k=>o[k]??null,setItem:(k,v)=>{o[k]=String(v)},removeItem:k=>delete o[k]});
const ctx={console,process,document,navigator:{},localStorage:store(local),sessionStorage:store(session),
  MutationObserver:undefined,URL,URLSearchParams,TextEncoder,TextDecoder,setTimeout,clearTimeout,
  location:{href:'https://example.test/beta/clubfinder-beta.html',replace(v){this.href=v}},
  open:()=>({document:{open(){},write(){},close(){},body:{innerHTML:''},documentElement:{innerHTML:''}},focus(){},print(){},close(){}}),
  fetch:async url=>{
    const s=String(url);
    if(s.includes('competition.json'))return {ok:true,status:200,json:async()=>JSON.parse(JSON.stringify(competition)),text:async()=>JSON.stringify(competition)};
    if(s.includes('counter-config.json'))return {ok:true,status:200,json:async()=>({increment_url:'https://counter.invalid/increment'})};
    throw Error('Unexpected network call in Petts Wood display regression: '+s);
  }};
ctx.window=ctx;ctx.globalThis=ctx;
vm.createContext(ctx);
const scripts=[...html.matchAll(/<script[^>]*>([\s\S]*?)<\/script>/gi)].map(m=>m[1]).join('\n');
vm.runInContext(scripts,ctx,{filename:'beta/clubfinder-beta.html',timeout:25000});
const run=(s,vars={})=>{Object.assign(ctx,vars);return vm.runInContext(s,ctx,{timeout:25000})};
(async()=>{
  await run("refreshCompetitionData(false)");
  const current=run("ELIGIBLE.find(c=>c.name==='Petts Wood & Holmesdale FC')");
  assert(current,'Current merged club is absent from BETA eligible list');
  assert.equal(run("ELIGIBLE.some(c=>c.name==='Holmesdale FC')"),false,'Retired name still exposed as an eligible club');
  assert.equal(current.postcode,'BR2 8HQ');
  assert.equal(current.ground,'RTL Group Stadium');
  assert.equal(run("sameClubIdentity('Holmesdale FC','Petts Wood & Holmesdale FC')"),true,'Legacy saved name must map to current club');
  const legacy={originName:'Holmesdale FC',postcode:'BR2 8HQ',ended:false,selectedAt:'2026-09-24T15:18:33Z',
    searchNumber:1088,callSign:'Tango Foxtrot 2 Alpha Charlie 01088',pigeonName:''};
  run("localStorage.setItem(JOURNEY_STORAGE_KEY,JSON.stringify(__legacy))",{__legacy:legacy});
  const restored=run("savedOrigin(ELIGIBLE,loadSavedJourney())");
  assert(restored,'Legacy saved campaign no longer resolves');
  assert.equal(restored.name,'Petts Wood & Holmesdale FC');
  const journey=run("buildJourney(__origin)",{__origin:restored});
  assert.equal(journey.origin.name,'Petts Wood & Holmesdale FC');
  assert.equal(journey.carrier.name,'Eastbourne Borough FC');
  const previous=run("previousRoundsHtml(__journey)",{__journey:journey});
  assert(previous.includes('This Campaign starts with: Petts Wood &amp; Holmesdale FC'),
    'Previous Rounds still exposes retired Holmesdale name');
  const savedAfter=run("saveJourney(__origin,'BR2 8HQ')",{__origin:restored});
  assert.equal(savedAfter.originName,'Petts Wood & Holmesdale FC');
  assert.equal(savedAfter.searchNumber,1088,'Existing campaign number was not preserved through rename');
  assert.equal(savedAfter.callSign,'Tango Foxtrot 2 Alpha Charlie 01088');
  const crumbs=journey.breadcrumbs||[];
  const snap=run("tinFoilChallengeStatsSnapshot(__origin,__journey,__crumbs,__saved,0)",
    {__origin:restored,__journey:journey,__crumbs:crumbs,__saved:savedAfter});
  assert.equal(snap.origin,'Petts Wood & Holmesdale FC','Stats snapshot still uses retired name');
  const firstVenue=run("completedResultVenue(__r)",{__r:crumbs[0].result});
  assert.equal(firstVenue.postcode,'BR2 8HQ','Historic location changed during display rename');
  console.log('BETA PETTS WOOD PUBLIC IDENTITY: PASS');
  console.log(JSON.stringify({display:restored.name,postcode:restored.postcode,ground:restored.ground,
    legacyCampaignNumber:savedAfter.searchNumber,currentCustodian:journey.carrier.name,history:crumbs.length}));
})().catch(e=>{console.error(e.stack||e);process.exitCode=1});
