#!/usr/bin/env node
// Guard the ACTUAL BETA campaign, not a synthetic alias-only helper.
'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const html=fs.readFileSync('beta/clubfinder-beta.html','utf8');
const competition=JSON.parse(fs.readFileSync('competition.json','utf8'));
const four=[
  ['2026-08-08','Extra Preliminary Round','Petts Wood & Holmesdale','Tooting & Mitcham United',2,2],
  ['2026-08-11','Extra Preliminary Round Replay','Tooting & Mitcham United','Petts Wood & Holmesdale',2,3],
  ['2026-08-22','Preliminary Round','Raynes Park Vale','Petts Wood & Holmesdale',1,5],
  ['2026-09-05','First Round Qualifying','Petts Wood & Holmesdale','Windsor & Eton',1,5]
];
const norm=s=>String(s||'').toLowerCase().replace(/&/g,' and ').replace(/\b(fc|afc|cfc)\b/g,' ').replace(/[^a-z0-9]+/g,' ').trim();
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
    if(s.includes('competition.json'))return {ok:true,status:200,
      json:async()=>JSON.parse(JSON.stringify(competition)),text:async()=>JSON.stringify(competition)};
    if(s.includes('counter-config.json'))return {ok:true,status:200,json:async()=>({increment_url:'https://counter.invalid/increment'})};
    throw Error('Unexpected network call in Holmesdale regression: '+s);
  }};
ctx.window=ctx;ctx.globalThis=ctx;
vm.createContext(ctx);
const scripts=[...html.matchAll(/<script[^>]*>([\s\S]*?)<\/script>/gi)].map(m=>m[1]).join('\n');
assert(scripts.length>15000,'BETA scripts missing');
vm.runInContext(scripts,ctx,{filename:'beta/clubfinder-beta.html',timeout:25000});
const run=(s,vars={})=>{Object.assign(ctx,vars);return vm.runInContext(s,ctx,{timeout:25000})};
async function main(){
  await run("refreshCompetitionData(false)");
  assert.equal(run("typeof tinFoilBetaHolmesdale2026Ready"),'function');
  assert.equal(run("tinFoilBetaHolmesdale2026Ready()"),true,'Historical merger evidence missing');
  assert.equal(run("sameClubIdentity('Holmesdale FC','Petts Wood & Holmesdale')"),true);
  assert.equal(run("sameClubIdentity('Holmesdale United','Petts Wood & Holmesdale')"),false,
    'Merger must not become fuzzy global name matching');
  const info=run("(function(){const o=ELIGIBLE.find(c=>c.name==='Holmesdale FC');if(!o)throw Error('Holmesdale origin absent');return {name:o.name,ground:o.ground,postcode:o.postcode,entry:o.entry_round}})()");
  assert.equal(info.name,'Holmesdale FC','Original postcode-based origin identity changed');
  assert.equal(info.entry,'Extra Preliminary Round');
  const direct=run("liveLookup('result_history','Holmesdale FC')");
  assert(Array.isArray(direct)&&direct.length>=4,'Original name cannot retrieve merged historical results');
  const origin=run("ELIGIBLE.find(c=>c.name==='Holmesdale FC')");
  // Regress the visible completed fixture as well as the underlying journey.
  // A restored Holmesdale campaign must not keep saying 'result not embedded'.
  const displayed=run("currentDisplayFixture(__origin)",{__origin:origin});
  assert.equal(displayed.completed,true,'The visible Holmesdale fixture is still pending');
  assert.equal(displayed.round,'First Round Qualifying');
  assert(/petts wood/i.test(displayed.tie)&&/windsor/i.test(displayed.tie),
    'Displayed result does not identify the merged club and Windsor & Eton');
  assert.equal(String(displayed.venue.postcode).toUpperCase().replace(/\s+/g,''),'BR28HQ');
  const journey=run("buildJourney(__origin)",{__origin:origin});
  const crumbs=journey.breadcrumbs||[];
  const selected=[];
  for(const [date,round,home,away,hs,as] of four){
    const hits=crumbs.filter(x=>{const r=x.result||{};return r.date===date&&r.round===round&&
      norm(r.home)===norm(home)&&norm(r.away)===norm(away)&&
      Number(r.home_score)===hs&&Number(r.away_score)===as;});
    assert.equal(hits.length,1,'Missing or duplicate historical match '+date+': '+JSON.stringify(crumbs.map(x=>x.result)));
    selected.push(hits[0]);
  }
  const keys=selected.map(x=>x.result.date);
  assert.deepEqual(keys,four.map(x=>x[0]),'Holmesdale campaign chronology altered');
  assert.equal(norm(selected[3].result.winner),norm('Windsor & Eton'));
  // Don't impose an obsolete *current* custodian: Windsor may have played again.
  assert(crumbs.length>=4,'Campaign stopped before verified four-match history');
  const venues=selected.map(x=>run("completedResultVenue(__r)",{__r:x.result}));
  console.log('HOLMESDALE_VENUES '+JSON.stringify(venues));
  assert.equal(String(venues[0].postcode).toUpperCase().replace(/\s+/g,''),'BR28HQ',
    'Extra Preliminary tie lost its independently surveyed location');
  assert.equal(String(venues[3].postcode).toUpperCase().replace(/\s+/g,''),'BR28HQ');
  assert.equal(venues[3].ground,'The New Inn Stadium',
    'The historic 5 September fixture must retain its sourced ground name');
  const unresolved=venues.map((v,i)=>/TBC/i.test(v.postcode||'')?four[i][0]:null).filter(Boolean);
  assert.deepEqual(unresolved,[],'Pigeon Miles cannot include all four matches until actual venues are sourced');
  // Use deterministic postcode coordinates solely to test round-trip arithmetic.
  // This deliberately does not claim a real-world mileage measurement.
  const postcodes=[...new Set(['BR2 8HQ',...venues.map(v=>v.postcode)])];
  const coords=Object.fromEntries(postcodes.map((pc,i)=>[pc.toUpperCase().replace(/\s+/g,''),
    {lat:51.384+i*0.041,lon:0.022+i*0.027}]));
  run("tinFoilPigeonCoords=async pc=>__coords[String(pc||'').toUpperCase().replace(/\\s+/g,'')]||null",
    {__coords:coords});
  const miles=await run("tinFoilPigeonMilesForStats(__selected,'BR2 8HQ',completedResultVenue)",
    {__selected:selected});
  assert.equal(miles.unresolved,0,'Four-match Pigeon Miles still has unresolved venue');
  assert(Number.isFinite(miles.miles)&&miles.miles>=0);
  const expected=venues.reduce((sum,v)=>sum+2*run("hav(__start,__end)",{
    __start:coords.BR28HQ,__end:coords[v.postcode.toUpperCase().replace(/\s+/g,'')]}),0);
  assert(Math.abs(miles.miles-expected)<1e-7,'Pigeon Miles lost its 2× straight-line definition');
  assert.equal(miles.display,String(Math.round(expected)));
  assert.equal(run("tinFoilCertificateWinner(__r)",{__r:selected[0].result}),'',
    'Unsettled draw must not invent a winner');
  assert.equal(norm(run("tinFoilCertificateWinner(__r)",{__r:selected[3].result})),
    norm('Windsor & Eton'));
  // No fabricated merger: remove its 8 August historical evidence and fail closed.
  const noProof=JSON.parse(JSON.stringify(competition));
  noProof.result_history['Petts Wood & Holmesdale']=
    (noProof.result_history['Petts Wood & Holmesdale']||[]).filter(x=>x.date!=='2026-08-08');
  run("LIVE_COMPETITION_DATA=__noProof",{__noProof:noProof});
  assert.equal(run("tinFoilBetaHolmesdale2026Ready()"),false);
  assert.equal(run("sameClubIdentity('Holmesdale FC','Petts Wood & Holmesdale')"),false);
  run("LIVE_COMPETITION_DATA=__canonical",{__canonical:competition});
  console.log('HOLMESDALE_CAMPAIGN '+JSON.stringify({origin:info,firstFour:selected.map(x=>({
    date:x.result.date,home:x.result.home,away:x.result.away,winner:x.result.winner})),
    postFourCustodian:'Windsor & Eton',latestCustodian:journey.carrier.name,
    historicalVenue:venues[3],roundTripMileageArithmetic:'PASS'}));
  console.log('BETA Holmesdale season-scoped identity, history, venues, Stats and Pigeon Miles: PASS');
}
main().catch(e=>{console.error('BETA HOLMESDALE CAMPAIGN REGRESSION FAILED',e.stack||e);process.exitCode=1});
