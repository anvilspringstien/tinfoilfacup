#!/usr/bin/env node
const fs=require('fs');
const vm=require('vm');
const path=require('path');
const ROOT=path.resolve(__dirname,'..');
const html=fs.readFileSync(path.join(ROOT,'clubfinder.html'),'utf8');
const competition=JSON.parse(fs.readFileSync(path.join(ROOT,'competition.json'),'utf8'));
const scripts=[...html.matchAll(/<script[^>]*>([\s\S]*?)<\/script>/gi)].map(m=>m[1]).join('\n');
function nodeStub(){return {value:'',textContent:'',innerHTML:'',style:{},disabled:false,addEventListener(){},focus(){},setAttribute(){},removeAttribute(){},appendChild(){},remove(){},querySelectorAll(){return []},classList:{add(){},remove(){}}}}
const elements=new Proxy({}, {get:(o,k)=>o[k]||(o[k]=nodeStub())});
const documentStub={readyState:'complete',getElementById(id){return elements[id]},querySelector(){return nodeStub()},querySelectorAll(){return []},createElement(){return nodeStub()},addEventListener(){},body:nodeStub()};
const localStore={};
const sandbox={console,process,document:documentStub,localStorage:{getItem:k=>localStore[k]??null,setItem:(k,v)=>{localStore[k]=String(v)},removeItem:k=>delete localStore[k]},navigator:{},location:{href:'https://example.test/clubfinder.html'},URL,URLSearchParams,TextEncoder,TextDecoder,setTimeout,clearTimeout,MutationObserver:undefined,fetch:async(url)=>{const s=String(url);if(s.includes('competition.json'))return {ok:true,json:async()=>competition,text:async()=>JSON.stringify(competition)};throw new Error('Unexpected network request: '+s)}};
sandbox.window=sandbox;sandbox.globalThis=sandbox;vm.createContext(sandbox);
const assertions=`
(async()=>{
  if(typeof refreshCompetitionData==='function') await refreshCompetitionData(false);
  const same=(a,b)=>typeof sameClubIdentity==='function'?sameClubIdentity(a,b):String(a||'')===String(b||'');
  if(typeof tinFoilStatsWinnerFromFixture!=='function')throw new Error('DL5 Stats regression: Stats custody guard missing');
  const scoreWinner=tinFoilStatsWinnerFromFixture('Newton Aycliffe (0) v (1) Kendal Town');
  if(scoreWinner!=='Kendal Town')throw new Error('DL5 Stats regression: 0-1 scoreline must render Kendal Town, got '+scoreWinner);
  if(tinFoilStatsWinnerFromFixture('Kendal Town (2) v (2) Heaton Stannington')!=='')throw new Error('DL5 Stats regression: drawn tie must not invent a new custodian');
  if(tinFoilStatsWinnerFromFixture('Heaton Stannington (4) v (2) Kendal Town')!=='Heaton Stannington')throw new Error('DL5 Stats regression: replay winner mismatch');
  const origin=ELIGIBLE.find(c=>same(c.name,'Newton Aycliffe FC'));
  if(!origin)throw new Error('DL5 Stats regression: Newton Aycliffe FC origin missing');
  const j=buildJourney(origin),carrier=j.carrier||origin,history=(j.breadcrumbs||[]).map(x=>x.result||{});
  const first=history.find(r=>same(r.home,'Newton Aycliffe')&&same(r.away,'Kendal Town')&&Number(r.home_score)===0&&Number(r.away_score)===1);
  if(!first)throw new Error('DL5 Stats regression: Newton Aycliffe 0-1 Kendal missing');
  if(typeof canonicalResultWinner!=='function'||!same(canonicalResultWinner(first),'Kendal Town'))throw new Error('DL5 Stats regression: canonical first custody transfer is not Kendal Town');
  if(!same(carrier.name,'Heaton Stannington'))throw new Error('DL5 Stats regression: expected current custodian Heaton Stannington, got '+carrier.name);
  const next=nextRoundInfo(carrier);
  if(!next||!next.knownFixture||!same(next.knownFixture.home,'Heaton Stannington')||!same(next.knownFixture.away,'Trafford'))throw new Error('DL5 Stats regression: expected Heaton Stannington v Trafford next');
  console.log('CLUBFINDER STATS REGRESSION: PASS');
  console.log('Canonical postcode: DL5 4RQ');
  console.log('Custody: Newton Aycliffe FC -> Kendal Town -> Heaton Stannington');
  console.log('Extra Preliminary winner display: Kendal Town — PASS');
  console.log('Draw custody remains unresolved until replay — PASS');
  console.log('Replay transfer to Heaton Stannington — PASS');
  console.log('Next: Heaton Stannington v Trafford — PASS');
})().catch(e=>{console.error(e.stack||e);process.exitCode=1});`;
try{vm.runInContext(scripts+'\n'+assertions,sandbox,{filename:'clubfinder.html'});}catch(e){console.error(e.stack||e);process.exit(1)}
