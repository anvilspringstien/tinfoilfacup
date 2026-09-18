#!/usr/bin/env node
const fs=require('fs');
const vm=require('vm');
const path=require('path');

const ROOT=path.resolve(__dirname,'..');
const html=fs.readFileSync(path.join(ROOT,'beta','clubfinder-beta.html'),'utf8');
const competition=JSON.parse(fs.readFileSync(path.join(ROOT,'competition.json'),'utf8'));
const scripts=[...html.matchAll(/<script[^>]*>([\s\S]*?)<\/script>/gi)].map(m=>m[1]).join('\n');
if(!scripts.trim())throw new Error('No inline Clubfinder JavaScript found');

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
  console,process,document:documentStub,MutationObserver:undefined,
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
  if(!refreshed.includes('Amersham Town'))throw new Error('BETA identity regression: refresh returned a blank Clubfinder');

  console.log('BETA COUNTER -> PIGEON -> REFRESH PERSISTENCE: PASS');
})().catch(e=>{console.error(e.stack||e);process.exitCode=1});
`;

try{
  vm.runInContext(scripts+'\\n'+assertions,sandbox,{filename:'beta/clubfinder-beta.html'});
}catch(e){
  console.error(e.stack||e);
  process.exit(1);
}
