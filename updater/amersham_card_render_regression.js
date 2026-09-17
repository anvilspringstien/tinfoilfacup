#!/usr/bin/env node
const fs=require('fs');
const vm=require('vm');
const path=require('path');
const ROOT=path.resolve(__dirname,'..');
const html=fs.readFileSync(path.join(ROOT,'clubfinder.html'),'utf8');
const competition=JSON.parse(fs.readFileSync(path.join(ROOT,'competition.json'),'utf8'));
const scripts=[...html.matchAll(/<script[^>]*>([\s\S]*?)<\/script>/gi)].map(m=>m[1]).join('\n');
if(!scripts.trim())throw new Error('No inline Clubfinder JavaScript found');

function nodeStub(){
  return {
    value:'',textContent:'',innerHTML:'',hidden:false,dataset:{},style:{},disabled:false,
    addEventListener(){},focus(){},setAttribute(){},removeAttribute(){},appendChild(){},remove(){},insertAdjacentElement(){},
    classList:{add(){},remove(){}}
  };
}
const elements=new Proxy({}, {get:(o,k)=>o[k]||(o[k]=nodeStub())});
const documentStub={
  readyState:'complete',
  getElementById(id){return elements[id]},
  querySelector(){return nodeStub()},querySelectorAll(){return []},createElement(){return nodeStub()},
  addEventListener(){},body:nodeStub()
};
const localStore={};
const sandbox={
  console,process,document:documentStub,MutationObserver:undefined,
  localStorage:{getItem:k=>localStore[k]??null,setItem:(k,v)=>{localStore[k]=String(v)},removeItem:k=>delete localStore[k]},
  navigator:{},location:{href:'https://example.test/clubfinder.html'},URL,URLSearchParams,TextEncoder,TextDecoder,
  setTimeout,clearTimeout,
  fetch:async(url)=>{
    const s=String(url);
    if(s.includes('competition.json'))return {ok:true,status:200,json:async()=>JSON.parse(JSON.stringify(competition)),text:async()=>JSON.stringify(competition)};
    throw new Error('Unexpected network request in Amersham card regression: '+s);
  }
};
sandbox.window=sandbox;sandbox.globalThis=sandbox;vm.createContext(sandbox);

const assertions=`
(async()=>{
  const same=(a,b)=>typeof sameClubIdentity==='function'?sameClubIdentity(a,b):norm(a)===norm(b);
  const amersham=ELIGIBLE.find(c=>same(c.name,'Amersham Town FC')||same(c.name,'Amersham Town'));
  if(!amersham)throw new Error('HP7 regression: Amersham Town origin missing');
  const ground=findGround(amersham)||{};
  if(!Number.isFinite(Number(ground.lat))||!Number.isFinite(Number(ground.lon)))throw new Error('HP7 regression: Amersham verified coordinates missing');

  lookup=async()=>({lat:Number(ground.lat),lon:Number(ground.lon),postcode:'HP7 0EJ'});
  geocodeClubPostcodes=async()=>{};
  document.getElementById('postcode').value='HP7 0EJ';
  await go();

  const rendered=String(document.getElementById('results').innerHTML||'');
  if(!rendered)throw new Error('HP7 regression: go() produced no rendered Campaign cards');
  if(/Replay details TBC/i.test(rendered))throw new Error('HP7 regression: resolved Amersham ancestry fell back to Replay details TBC');
  if(/↻\\s*Replay required/i.test(rendered))throw new Error('HP7 regression: resolved Amersham ancestry rendered as an unresolved replay');
  if(!/current custodian of your Tin Foil FA Cup/i.test(rendered))throw new Error('HP7 regression: resolved Amersham card did not render a current custodian');
  if(!/Windsor\\s*&(?:amp;)?\\s*Eton/i.test(rendered)){
    console.error('HP7 RENDERED OUTPUT BEGIN');
    console.error(rendered);
    console.error('HP7 RENDERED OUTPUT END');
    const debugJourney=tinFoilJourneyForRender(amersham);
    console.error('HP7 render-boundary carrier:',(debugJourney.carrier||amersham).name);
    console.error('HP7 render-boundary crumbs:',(debugJourney.breadcrumbs||[]).map(x=>{const r=x.result||{};return [r.round,r.home,r.home_score,r.away_score,r.away,r.winner,r.decision].join(' | ')}).join('\\n'));
    throw new Error('HP7 regression: expected Windsor & Eton to be visible as resolved custodian/history');
  }
  if(!/The New Inn Stadium/i.test(rendered)||!/BR2\\s*8HQ/i.test(rendered)){
    console.error('HP7 HISTORICAL VENUE RENDER BEGIN');
    console.error(rendered);
    console.error('HP7 HISTORICAL VENUE RENDER END');
    throw new Error('HP7 regression: rendered Petts Wood & Holmesdale v Windsor & Eton historical venue must be The New Inn Stadium, BR2 8HQ');
  }

  const journey=tinFoilJourneyForRender(amersham);
  if(!same((journey.carrier||amersham).name,'Windsor & Eton'))throw new Error('HP7 regression: render-boundary custodian expected Windsor & Eton, got '+((journey.carrier||amersham).name));
  const crumbs=(journey.breadcrumbs||[]).map(x=>x.result||{});
  const replay=crumbs.find(r=>/Extra Preliminary Round Replay/i.test(r.round||'')&&same(r.home,'Amersham Town')&&same(r.away,'North Leigh'));
  if(!replay||Number(replay.home_score)!==1||Number(replay.away_score)!==2)throw new Error('HP7 regression: decisive Amersham 1-2 North Leigh replay missing');

  console.log('AMERSHAM CARD RENDER REGRESSION: PASS');
  console.log('HP7 0EJ go() render: PASS');
  console.log('Resolved custodian: Windsor & Eton');
  console.log('Replay details TBC absent: PASS');
  console.log('Petts Wood historical venue rendered: The New Inn Stadium, BR2 8HQ — PASS');
})().catch(e=>{console.error(e.stack||e);process.exitCode=1});`;

try{vm.runInContext(scripts+'\n'+assertions,sandbox,{filename:'clubfinder.html'});}catch(e){console.error(e.stack||e);process.exit(1)}
