#!/usr/bin/env node
const fs=require('fs');
const vm=require('vm');
const path=require('path');
const ROOT=path.resolve(__dirname,'..');
const html=fs.readFileSync(path.join(ROOT,'clubfinder.html'),'utf8');
const competition=JSON.parse(fs.readFileSync(path.join(ROOT,'competition.json'),'utf8'));
const scripts=[...html.matchAll(/<script[^>]*>([\s\S]*?)<\/script>/gi)].map(m=>m[1]).join('\n');
function nodeStub(){return {value:'',textContent:'',innerHTML:'',style:{},disabled:false,children:[],parentElement:null,addEventListener(){},focus(){},setAttribute(){},removeAttribute(){},appendChild(){},remove(){},querySelectorAll(){return []},classList:{add(){},remove(){}}}}
const elements=new Proxy({}, {get:(o,k)=>o[k]||(o[k]=nodeStub())});
const documentStub={readyState:'complete',getElementById(id){return elements[id]},querySelector(){return nodeStub()},querySelectorAll(){return []},createElement(){return nodeStub()},addEventListener(){},body:nodeStub()};
const localStore={};
const sandbox={console,process,document:documentStub,localStorage:{getItem:k=>localStore[k]??null,setItem:(k,v)=>{localStore[k]=String(v)},removeItem:k=>delete localStore[k]},navigator:{},location:{href:'https://example.test/clubfinder.html'},URL,URLSearchParams,TextEncoder,TextDecoder,setTimeout,clearTimeout,MutationObserver:undefined,fetch:async(url)=>{const s=String(url);if(s.includes('competition.json'))return {ok:true,json:async()=>competition,text:async()=>JSON.stringify(competition)};throw new Error('Unexpected network request: '+s)}};
sandbox.window=sandbox;sandbox.globalThis=sandbox;vm.createContext(sandbox);
const assertions=`
(async()=>{
  if(typeof refreshCompetitionData==='function') await refreshCompetitionData(false);
  const same=(a,b)=>typeof sameClubIdentity==='function'?sameClubIdentity(a,b):String(a||'')===String(b||'');
  if(typeof tinFoilStatsRepairRenderedRow!=='function')throw new Error('DL5 Stats regression: rendered-row repair missing');

  function leaf(text){return {textContent:text,children:[],parentElement:null,querySelectorAll(){return []}}}
  function row(parts){
    const r={children:parts,parentElement:null,textContent:parts.map(x=>x.textContent).join(' '),querySelectorAll(){return parts}};
    parts.forEach(x=>x.parentElement=r);
    return r;
  }
  const extra=row([
    leaf('Extra Preliminary Round'),leaf('Newton Aycliffe (0) v (1) Kendal Town'),leaf('8 Aug 2026'),leaf('Moore Lane Park DL5 5AG'),leaf('Newton Aycliffe FC')
  ]);
  if(!tinFoilStatsRepairRenderedRow(extra))throw new Error('DL5 Stats regression: actual rendered row was not repaired');
  if(extra.children[4].textContent!=='Kendal Town')throw new Error('DL5 Stats regression: visible Extra Preliminary winner must be Kendal Town, got '+extra.children[4].textContent);

  const draw=row([
    leaf('Preliminary Round'),leaf('Kendal Town (2) v (2) Heaton Stannington'),leaf('22 Aug 2026'),leaf('The Westmorland Flooring Stadium LA9 7BL'),leaf('')
  ]);
  if(tinFoilStatsRepairRenderedRow(draw))throw new Error('DL5 Stats regression: drawn visible row must remain unresolved');

  const replay=row([
    leaf('Preliminary Round Replay'),leaf('Heaton Stannington (4) v (2) Kendal Town'),leaf('25 Aug 2026'),leaf('The Willow Park NE7 7HP'),leaf('Heaton Stannington')
  ]);
  tinFoilStatsRepairRenderedRow(replay);
  if(replay.children[4].textContent!=='Heaton Stannington')throw new Error('DL5 Stats regression: replay visible winner mismatch');

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
  console.log('VISIBLE rendered Extra Preliminary row: Kendal Town — PASS');
  console.log('Draw visible row remains unresolved — PASS');
  console.log('Replay visible row: Heaton Stannington — PASS');
  console.log('Custody: Newton Aycliffe FC -> Kendal Town -> Heaton Stannington');
  console.log('Next: Heaton Stannington v Trafford — PASS');
})().catch(e=>{console.error(e.stack||e);process.exitCode=1});`;
try{vm.runInContext(scripts+'\n'+assertions,sandbox,{filename:'clubfinder.html'});}catch(e){console.error(e.stack||e);process.exit(1)}
