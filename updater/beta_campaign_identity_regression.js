#!/usr/bin/env node
const fs=require('fs');
const vm=require('vm');
const path=require('path');

const ROOT=path.resolve(__dirname,'..');
const html=fs.readFileSync(path.join(ROOT,'beta','clubfinder-beta.html'),'utf8');
const competition=JSON.parse(fs.readFileSync(path.join(ROOT,'competition.json'),'utf8'));
const scripts=[...html.matchAll(/<script[^>]*>([\s\S]*?)<\/script>/gi)].map(m=>m[1]).join('\n');
if(!scripts.trim())throw new Error('No inline Clubfinder JavaScript found');
if(!html.includes('maxlength="20"'))throw new Error('BETA identity regression: pigeon-name 20-character cap drifted');
if(!html.includes('class="campaign-call-sign"')||!html.includes('class="campaign-pigeon-name"'))throw new Error('BETA mobile regression: identity must have separate Call Sign and Pigeon Name rows');
if(!html.includes('.campaign-pigeon-name{display:flex;align-items:baseline;flex-wrap:wrap;'))throw new Error('BETA mobile regression: phone name row must wrap instead of clipping');
if(!html.includes('.campaign-pigeon-name .pigeon-name-input{display:block;flex:1 1 205px;'))throw new Error('BETA mobile regression: phone name input must use available width');
if(!html.includes('.campaign-identity-band{margin:0 0 4px;padding:13px 16px 14px;border-bottom:1px solid #d40000;text-align:left;white-space:nowrap}'))throw new Error('BETA identity regression: Stats identity top-gap/nowrap contract drifted');
if(!html.includes('.campaign-identity-label{display:inline;font-stretch:condensed;font-family:Arial Narrow,Arial,Helvetica,sans-serif;font-size:9pt'))throw new Error('BETA identity regression: Stats identity label sizing drifted');
if(!html.includes('.campaign-identity-value{display:inline;font-stretch:condensed;font-family:Arial Narrow,Arial,Helvetica,sans-serif;font-size:10pt'))throw new Error('BETA identity regression: Stats identity value sizing drifted');
if(!html.includes("'petts wood & holmesdale|windsor & eton':{ground:'The New Inn Stadium',postcode:'BR2 8HQ'"))throw new Error('BETA parity regression: Petts Wood historical venue override missing');
if(!html.includes('Pigeon Miles Flown:'))throw new Error('BETA parity regression: canonical Pigeon Miles Flown wording missing');
if(html.includes('Pigeon Miles Travelled:')||html.includes('Pigeon Miles Traveled:'))throw new Error('BETA parity regression: retired Pigeon Miles travel wording returned');
if(!html.includes('Pigeon<br><span style="white-space:nowrap">Miles Flown</span>'))throw new Error('BETA parity regression: At-a-Glance Pigeon Miles Flown label drifted');

function nodeStub(){
  return {
    value:'',textContent:'',innerHTML:'',hidden:false,dataset:{},style:{},disabled:false,
    children:[],parentElement:null,
    addEventListener(){},focus(){},setAttribute(){},removeAttribute(){},appendChild(){},remove(){},insertAdjacentElement(){},
    querySelectorAll(){return []},classList:{add(){},remove(){}}
  };
}
const elements=new Proxy({}, {get:(o,k)=>o[k]||(o[k]=nodeStub())});
const documentStub={
  readyState:'complete',
  activeElement:null,
  getElementById(id){return elements[id]},
  querySelector(){return nodeStub()},
  querySelectorAll(){return []},
  createElement(){return nodeStub()},
  addEventListener(){},
  removeEventListener(){},
  body:nodeStub()
};
const localStore={};
let counterIncrementCalls=0;
let certificateHtml='';
function popupStub(){
  const doc={
    open(){certificateHtml='';},
    write(s){certificateHtml+=String(s)},
    writeln(s){certificateHtml+=String(s)+'\n'},
    close(){},
    body:{innerHTML:''},
    documentElement:{innerHTML:''}
  };
  return {document:doc,closed:false,focus(){},print(){},close(){this.closed=true}};
}
const coords={
  'HP70EJ':{latitude:51.676,longitude:-0.607},
  'OX296SL':{latitude:51.807,longitude:-1.407},
  'SL43DR':{latitude:51.482,longitude:-0.612},
  'BR28HQ':{latitude:51.384,longitude:0.022},
  'BN237QH':{latitude:50.796,longitude:0.323}
};
function postcodeFromUrl(url){
  const s=decodeURIComponent(String(url));
  const m=s.match(/\/postcodes\/([^?/#]+)/i);
  return m?String(m[1]).replace(/\s+/g,'').toUpperCase():'';
}
const locationStub={href:'https://anvilspringstien.github.io/tinfoilfacup/beta/clubfinder-beta.html'};
const sandbox={
  console,process,html,document:documentStub,MutationObserver:undefined,
  localStorage:{
    getItem:k=>localStore[k]??null,
    setItem:(k,v)=>{localStore[k]=String(v)},
    removeItem:k=>delete localStore[k]
  },
  navigator:{},location:locationStub,URL,URLSearchParams,TextEncoder,TextDecoder,setTimeout,clearTimeout,
  open:()=>popupStub(),
  getCertificateHtml:()=>certificateHtml,
  getCounterIncrementCalls:()=>counterIncrementCalls,
  fetch:async(url)=>{
    const s=String(url);
    if(s.includes('counter-config.json'))return {ok:true,status:200,json:async()=>({increment_url:'https://counter.test/increment'})};
    if(s==='https://counter.test/increment'||s==='https://tffac-clubfinder-counter.anvilspringstien.workers.dev/increment'){
      counterIncrementCalls++;
      return {ok:true,status:200,json:async()=>({number:9842})};
    }
    if(s.includes('competition.json'))return {ok:true,status:200,json:async()=>JSON.parse(JSON.stringify(competition)),text:async()=>JSON.stringify(competition)};
    if(/postcodes\//i.test(s)){
      const pc=postcodeFromUrl(s),hit=coords[pc];
      return hit?{ok:true,status:200,json:async()=>({status:200,result:hit})}:{ok:false,status:404,json:async()=>({status:404,result:null})};
    }
    throw new Error('Unexpected network request in production UI regression: '+s);
  }
};
sandbox.window=sandbox;
sandbox.globalThis=sandbox;
vm.createContext(sandbox);

const assertions=`
(async()=>{
  if(typeof refreshCompetitionData==='function')await refreshCompetitionData(false);
  const same=(a,b)=>typeof sameClubIdentity==='function'?sameClubIdentity(a,b):String(a||'')===String(b||'');
  const origin=ELIGIBLE.find(c=>same(c.name,'Amersham Town'));
  if(!origin)throw new Error('BETA identity regression: Amersham origin missing');

  // BETA must consume the same canonical historical venue and mileage truth as production.
  const parityJourney=buildJourney(origin),parityCrumbs=parityJourney.breadcrumbs||[];
  const petts=parityCrumbs.find(x=>{const r=x.result||{};return /First Round Qualifying/i.test(r.round||'')&&same(r.home,'Petts Wood & Holmesdale')&&same(r.away,'Windsor & Eton')});
  if(!petts)throw new Error('BETA parity regression: Petts Wood & Holmesdale v Windsor & Eton breadcrumb missing');
  const pettsVenue=completedResultVenue(petts.result);
  if(!/New Inn Stadium/i.test(String(pettsVenue.ground||''))||String(pettsVenue.postcode||'').replace(/\\s+/g,'').toUpperCase()!=='BR28HQ'){
    throw new Error('BETA parity regression: canonical Petts Wood venue wrong: '+JSON.stringify(pettsVenue));
  }
  const pigeon=await tinFoilPigeonMilesForStats(parityCrumbs,'HP7 0EJ',completedResultVenue);
  if(pigeon.miles===null||!Number.isFinite(Number(pigeon.miles))||Number(pigeon.miles)<=0||/Awaiting venue location/i.test(String(pigeon.display||''))){
    throw new Error('BETA parity regression: Amersham Pigeon Miles unresolved/zero: '+JSON.stringify(pigeon));
  }
  const snapshotSource=String(tinFoilChallengeStatsSnapshot);
  if(!snapshotSource.includes('const v=completedResultVenue(r);'))throw new Error('BETA parity regression: Challenge Stats venue resolver bypasses completedResultVenue');
  const challengeSource=String(openChallenges);
  if(!challengeSource.includes('function venueForChallenge(r){return completedResultVenue(r);}'))throw new Error('BETA parity regression: Challenges Pigeon Miles resolver bypasses completedResultVenue');
  const certSource=String(journeyCertificate).replace(/\\s+/g,' ');
  if(!certSource.includes('function venueForResult(r){ const v=completedResultVenue(r);'))throw new Error('BETA parity regression: Stats venue resolver bypasses completedResultVenue');
  if(!certSource.includes('const pigeonStats=await tinFoilPigeonMilesForStats(crumbs,savedJourneyForStats&&savedJourneyForStats.postcode,venueForResult);'))throw new Error('BETA parity regression: Stats does not recalculate canonical Pigeon Miles');
  if(certSource.includes('bridgeMatches')||certSource.includes('cachedMiles'))throw new Error('BETA parity regression: stale Challenges mileage cache can still override Stats');


  const g=findGround(origin)||{};
  lookup=async()=>({lat:Number(g.lat),lon:Number(g.lon),postcode:'HP7 0EJ'});
  geocodeClubPostcodes=async()=>{};

  // Reproduce the live symptom: an existing Campaign has no identity, then the
  // user performs a real Find My Club search for that Campaign postcode.
  localStorage.setItem(JOURNEY_STORAGE_KEY,JSON.stringify({
    originName:origin.name,
    postcode:'HP7 0EJ',
    ended:false,
    selectedAt:'2026-09-18T20:00:00.000Z'
  }));
  document.getElementById('postcode').value='HP7 0EJ';
  document.getElementById('results').innerHTML='';
  await go(true);
  if(!TIN_FOIL_SEARCH_NUMBER_PROMISE)throw new Error('BETA identity regression: Find My Club did not start counter request');
  await TIN_FOIL_SEARCH_NUMBER_PROMISE;
  if(getCounterIncrementCalls()!==1)throw new Error('BETA identity regression: expected one counter call, got '+getCounterIncrementCalls());
  if(tinFoilCurrentSearchNumber()!==9842)throw new Error('BETA identity regression: issued counter number was not adopted');
  if(!String(document.getElementById('liveDataBadge').textContent||'').includes('#09842'))throw new Error('BETA identity regression: counter missing from live badge');

  const repaired=loadSavedJourney();
  if(Number(repaired.searchNumber)!==9842)throw new Error('BETA identity regression: existing Campaign was not backfilled with search number');
  if(repaired.callSign!=='Tango Foxtrot 2 Alpha Charlie 09842')throw new Error('BETA identity regression: Pigeon Call Sign was not backfilled');

  // Redraw after the asynchronous number arrives. The saved Campaign must show
  // the Pigeon Call Sign before we test browser refresh.
  await go(false);
  const rendered=String(document.getElementById('results').innerHTML||'');
  if(!rendered.includes('Pigeon Call Sign: Tango Foxtrot 2 Alpha Charlie 09842'))throw new Error('BETA identity regression: Pigeon Call Sign did not render');
  if(!rendered.includes('placeholder="Name your pigeon"'))throw new Error('BETA identity regression: inline pigeon-name field did not render');
  if(/Save(?: My)? Pigeon/i.test(rendered))throw new Error('BETA identity regression: pigeon naming unexpectedly requires a Save control');

  // Name the Campaign pigeon using the same autosave path as blur/Enter.
  tinFoilSavePigeonName('  Percy   ');
  const named=loadSavedJourney();
  if(named.pigeonName!=='Percy')throw new Error('BETA identity regression: pigeon name did not autosave');
  const identityBackup=JSON.parse(localStorage.getItem(TIN_FOIL_CAMPAIGN_IDENTITY_BACKUP_KEY)||'null');
  if(!identityBackup||identityBackup.pigeonName!=='Percy')throw new Error('BETA identity regression: pigeon name missing from Campaign identity backup');
  await go(false);
  const namedRendered=String(document.getElementById('results').innerHTML||'');
  if(!namedRendered.includes('Pigeon Name:'))throw new Error('BETA identity regression: Pigeon Name label disappeared after autosave');
  if(!namedRendered.includes('value="Percy"'))throw new Error('BETA identity regression: saved pigeon name did not redraw inline');

  // Long-name iPhone regression: the full 19 characters survive blur, storage,
  // redraw and a browser refresh. CSS must put the input on a usable mobile row.
  tinFoilSavePigeonName('Pigeon McPigeonface');
  const longNamed=loadSavedJourney();
  if(longNamed.pigeonName!=='Pigeon McPigeonface')throw new Error('BETA mobile regression: long pigeon name was truncated in storage');
  const longBackup=JSON.parse(localStorage.getItem(TIN_FOIL_CAMPAIGN_IDENTITY_BACKUP_KEY)||'null');
  if(!longBackup||longBackup.pigeonName!=='Pigeon McPigeonface')throw new Error('BETA mobile regression: long pigeon name missing from identity backup');
  await go(false);
  const longRendered=String(document.getElementById('results').innerHTML||'');
  if(!longRendered.includes('value="Pigeon McPigeonface"'))throw new Error('BETA mobile regression: long pigeon name did not redraw completely');
  if(!longRendered.includes('class="campaign-pigeon-name"'))throw new Error('BETA mobile regression: long pigeon name lacks responsive wrapper');

  // Simulate Safari/iPad refresh: form and results disappear, in-memory current
  // identity disappears, but localStorage persists. Restore must redraw the same
  // Campaign and must not issue a second counter number.
  document.getElementById('postcode').value='';
  document.getElementById('results').innerHTML='';
  TIN_FOIL_CURRENT_SEARCH_NUMBER=null;
  const counterBeforeRefresh=getCounterIncrementCalls();
  const sequenceBeforeRefresh=TIN_FOIL_SEARCH_SEQUENCE;
  await tinFoilRestoreSavedCampaignOnLoad();
  if(getCounterIncrementCalls()!==counterBeforeRefresh)throw new Error('BETA identity regression: refresh issued a new counter number');
  if(TIN_FOIL_SEARCH_SEQUENCE!==sequenceBeforeRefresh)throw new Error('BETA identity regression: refresh changed search sequence');
  if(tinFoilCurrentSearchNumber()!==9842)throw new Error('BETA identity regression: refresh did not restore #09842');
  if(document.getElementById('postcode').value!=='HP7 0EJ')throw new Error('BETA identity regression: refresh did not restore saved postcode');
  const refreshed=String(document.getElementById('results').innerHTML||'');
  if(!refreshed.includes('Pigeon Call Sign: Tango Foxtrot 2 Alpha Charlie 09842'))throw new Error('BETA identity regression: refresh did not redraw Pigeon Call Sign');
  if(!refreshed.includes('value="Pigeon McPigeonface"'))throw new Error('BETA identity regression: refresh did not preserve full pigeon name');
  if(loadSavedJourney().pigeonName!=='Pigeon McPigeonface')throw new Error('BETA identity regression: long pigeon name changed across refresh');
  if(!refreshed.includes('Amersham Town'))throw new Error('BETA identity regression: refresh returned a blank Clubfinder');

  if(!html.includes('pigeonName:tinFoilSavedPigeonName(saved)'))throw new Error('BETA identity regression: Challenges bridge no longer carries pigeon name');

  console.log('BETA HISTORICAL VENUE -> PIGEON MILES -> FLOWN PARITY: PASS');
  console.log('BETA Petts Wood venue: The New Inn Stadium, BR2 8HQ — PASS');
  console.log('BETA Amersham Pigeon Miles:',pigeon.display);
  console.log('BETA COUNTER -> PIGEON NAME -> LONG-NAME REFRESH PERSISTENCE: PASS');
})().catch(e=>{console.error(e.stack||e);process.exitCode=1});
`;

try{
  vm.runInContext(scripts+'\n'+assertions,sandbox,{filename:'beta/clubfinder-beta.html'});
}catch(e){
  console.error(e.stack||e);
  process.exit(1);
}
