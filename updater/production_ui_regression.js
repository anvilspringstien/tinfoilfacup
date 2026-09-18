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
const locationStub={href:'https://anvilspringstien.github.io/tinfoilfacup/clubfinder.html'};
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
    if(s==='https://counter.test/increment'){
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
  if(!origin)throw new Error('Production UI regression: Amersham origin missing');

  // Exercise the real Find My Club browser path: a successful user-initiated
  // search must request exactly one number and display it in the live badge.
  const freshGround=findGround(origin)||{};
  lookup=async()=>({lat:Number(freshGround.lat),lon:Number(freshGround.lon),postcode:'HP7 0EJ'});
  geocodeClubPostcodes=async()=>{};
  document.getElementById('postcode').value='HP7 0EJ';
  await go(true);
  if(!TIN_FOIL_SEARCH_NUMBER_PROMISE)throw new Error('Production UI regression: fresh search did not start counter request');
  await TIN_FOIL_SEARCH_NUMBER_PROMISE;
  if(tinFoilCurrentSearchNumber()!==9842)throw new Error('Production UI regression: fresh search did not adopt issued counter number');
  if(getCounterIncrementCalls()!==1)throw new Error('Production UI regression: fresh search counter called '+getCounterIncrementCalls()+' times');
  if(!String(document.getElementById('liveDataBadge').textContent||'').includes('#09842'))throw new Error('Production UI regression: issued counter number not displayed in live badge');
  tinFoilClearCurrentSearchIdentity();

  // Real existing-Campaign path: the Campaign already exists without an identity,
  // then a fresh Find My Club search receives a number. That issued number must
  // attach to the existing Campaign automatically and reveal its Pigeon Call Sign.
  localStorage.setItem(JOURNEY_STORAGE_KEY,JSON.stringify({
    originName:origin.name,
    postcode:'HP7 0EJ',
    ended:false,
    selectedAt:'2026-09-18T11:55:00.000Z'
  }));
  TIN_FOIL_COUNTER_ENDPOINT_PROMISE=Promise.resolve('https://counter.test/increment');
  document.getElementById('postcode').value='HP7 0EJ';
  await go(true);
  if(!TIN_FOIL_SEARCH_NUMBER_PROMISE)throw new Error('Production UI regression: existing Campaign search did not start counter request');
  await TIN_FOIL_SEARCH_NUMBER_PROMISE;
  const autoBackfilled=loadSavedJourney();
  if(Number(autoBackfilled.searchNumber)!==9842)throw new Error('Production UI regression: issued search number did not attach to existing Campaign');
  if(autoBackfilled.callSign!=='Tango Foxtrot 2 Alpha Charlie 09842')throw new Error('Production UI regression: existing Campaign Pigeon Call Sign was not backfilled');
  if(!String(document.getElementById('results').innerHTML||'').includes('Pigeon Call Sign: Tango Foxtrot 2 Alpha Charlie 09842'))throw new Error('Production UI regression: existing Campaign did not reveal backfilled Pigeon Call Sign');
  tinFoilClearCurrentSearchIdentity();

  // Recover a Campaign that was chosen while the counter was unavailable.
  localStorage.setItem(JOURNEY_STORAGE_KEY,JSON.stringify({
    originName:origin.name,
    postcode:'HP7 0EJ',
    ended:false,
    selectedAt:'2026-09-18T12:00:00.000Z'
  }));
  TIN_FOIL_SEARCH_SEQUENCE=41;
  tinFoilBackfillExistingCampaignIdentity(9843,41);
  const repairedIdentity=loadSavedJourney();
  if(Number(repairedIdentity.searchNumber)!==9843)throw new Error('Production UI regression: identity-less Campaign was not repaired');
  if(repairedIdentity.callSign!=='Tango Foxtrot 2 Alpha Charlie 09843')throw new Error('Production UI regression: repaired Campaign Call Sign mismatch: '+repairedIdentity.callSign);

  tinFoilSetCurrentSearchNumber(9843);
  saveJourney(origin,'HP7 0EJ');
  const savedIdentity=loadSavedJourney();
  if(Number(savedIdentity.searchNumber)!==9843)throw new Error('Production UI regression: Campaign search number was not persisted');
  if(savedIdentity.callSign!=='Tango Foxtrot 2 Alpha Charlie 09843')throw new Error('Production UI regression: Campaign Call Sign mismatch: '+savedIdentity.callSign);
  const identityBackup=JSON.parse(localStorage.getItem(TIN_FOIL_CAMPAIGN_IDENTITY_BACKUP_KEY)||'null');
  if(!identityBackup||Number(identityBackup.searchNumber)!==9843)throw new Error('Production UI regression: Campaign identity backup missing');

  // Primary Campaign storage may lose optional identity fields during a migration/rebuild.
  // Recover the original identity from the dedicated backup without issuing a new number.
  localStorage.setItem(JOURNEY_STORAGE_KEY,JSON.stringify({
    originName:origin.name,
    postcode:'HP7 0EJ',
    ended:false,
    selectedAt:savedIdentity.selectedAt
  }));
  const recoveredFromBackup=loadSavedJourney();
  if(Number(recoveredFromBackup.searchNumber)!==9843)throw new Error('Production UI regression: Campaign identity backup recovery failed');
  if(recoveredFromBackup.callSign!=='Tango Foxtrot 2 Alpha Charlie 09843')throw new Error('Production UI regression: backup Call Sign recovery mismatch');

  // Challenges carries a second canonical snapshot. It can also repair the same Campaign.
  localStorage.removeItem(TIN_FOIL_CAMPAIGN_IDENTITY_BACKUP_KEY);
  localStorage.setItem(TIN_FOIL_CHALLENGE_BRIDGE_IDENTITY_KEY,JSON.stringify({
    source:'Clubfinder v7.6',
    originName:origin.name,
    postcode:'HP7 0EJ',
    selectedAt:savedIdentity.selectedAt,
    searchNumber:9843,
    callSign:'Tango Foxtrot 2 Alpha Charlie 09843',
    updatedAt:'2026-09-18T13:00:00.000Z'
  }));
  localStorage.setItem(JOURNEY_STORAGE_KEY,JSON.stringify({
    originName:origin.name,
    postcode:'HP7 0EJ',
    ended:false,
    selectedAt:savedIdentity.selectedAt
  }));
  const recoveredFromBridge=loadSavedJourney();
  if(Number(recoveredFromBridge.searchNumber)!==9843)throw new Error('Production UI regression: Challenges bridge identity recovery failed');
  if(recoveredFromBridge.callSign!=='Tango Foxtrot 2 Alpha Charlie 09843')throw new Error('Production UI regression: Challenges bridge Call Sign recovery mismatch');
  const g=findGround(origin)||{};
  lookup=async()=>({lat:Number(g.lat),lon:Number(g.lon),postcode:'HP7 0EJ'});
  geocodeClubPostcodes=async()=>{};

  // Chrome and other browsers may restore the previous postcode field on a plain
  // refresh while the rendered results are empty. The saved Campaign must still
  // redraw without issuing another counter number.
  document.getElementById('postcode').value='HP7 0EJ';
  document.getElementById('results').innerHTML='';
  TIN_FOIL_CURRENT_SEARCH_NUMBER=null;
  const refreshSequence=TIN_FOIL_SEARCH_SEQUENCE;
  await tinFoilRestoreSavedCampaignOnLoad();
  if(TIN_FOIL_SEARCH_SEQUENCE!==refreshSequence)throw new Error('Production UI regression: refresh redraw incremented search sequence');
  if(tinFoilCurrentSearchNumber()!==null)throw new Error('Production UI regression: refresh redraw minted a counter number');
  if(document.getElementById('postcode').value!=='HP7 0EJ')throw new Error('Production UI regression: refresh redraw did not restore Campaign postcode');

  const rendered=String(document.getElementById('results').innerHTML||'');
  for(const required of [
    'My Tin Foil FA Cup Campaign',
    'View Original Campaigns',
    '>Challenges<',
    'End My Campaign',
    'class="round challenges-launch"',
    'Pigeon Call Sign: Tango Foxtrot 2 Alpha Charlie 09843'
  ]){
    if(!rendered.includes(required))throw new Error('Production UI regression: rendered Campaign toolbar missing '+required);
  }
  for(const retired of ['My Tin Foil FA Cup Journey','View Original Journeys','End My Journey']){
    if(rendered.includes(retired))throw new Error('Production UI regression: retired Journey toolbar text remains: '+retired);
  }
  if(!/This Campaign starts with:/i.test(rendered))throw new Error('Production UI regression: Campaign history origin wording missing');

  await journeyCertificate(origin);
  const cert=getCertificateHtml();
  if(!cert)throw new Error('Production UI regression: Stats certificate did not render');
  for(const required of [
    'YOUR TIN FOIL FA CUP CAMPAIGN',
    'THE CAMPAIGN SO FAR',
    'Pigeon Miles Flown',
    'Pigeon Miles Flown:',
    'grid-template-columns:repeat(6,minmax(0,1fr))',
    '.g:last-child{grid-column:auto}'
  ]){
    if(!cert.includes(required))throw new Error('Production UI regression: Stats certificate missing '+required);
  }
  if(cert.includes('PIGEON CALL SIGN:'))throw new Error('Production UI regression: retired Stats-header Pigeon Call Sign returned');
  if(cert.includes('>🐦</div>'))throw new Error('Production UI regression: generic pigeon emoji remains in Stats At a Glance');
  const pigeonLabel=(cert.match(/Pigeon<br><span style="white-space:nowrap">Miles Flown<\\/span>/g)||[]).length;
  if(pigeonLabel!==1)throw new Error('Production UI regression: expected one two-line Pigeon Miles Flown At-a-Glance card, got '+pigeonLabel);
  if(cert.includes('<div class="g-label">Pigeon<br>Miles<br>Flown</div>'))throw new Error('Production UI regression: old three-line Pigeon Miles Flown label remains');
  if(cert.includes('<div class="g-label">Pigeon<br>Miles</div>'))throw new Error('Production UI regression: old Pigeon Miles label remains');

  location.href='https://anvilspringstien.github.io/tinfoilfacup/clubfinder.html';
  await openChallenges(origin);
  if(!String(location.href).endsWith('beta/challenges-beta.html'))throw new Error('Production UI regression: Challenges did not launch Candidate 13 beta path: '+location.href);
  const raw=localStorage.getItem('tffc.clubfinderCampaign.v1');
  if(!raw)throw new Error('Production UI regression: Challenges bridge truth was not persisted');
  const truth=JSON.parse(raw);
  if(!same(truth.currentCustodian,'Windsor & Eton'))throw new Error('Production UI regression: Challenges bridge custodian mismatch: '+truth.currentCustodian);
  if(Number(truth.searchNumber)!==9843||truth.callSign!=='Tango Foxtrot 2 Alpha Charlie 09843'){
    throw new Error('Production UI regression: Challenges bridge lost Campaign identity: '+JSON.stringify({searchNumber:truth.searchNumber,callSign:truth.callSign}));
  }
  if(!truth.statsSnapshot||Number(truth.statsSnapshot.searchNumber)!==9843||truth.statsSnapshot.callSign!=='Tango Foxtrot 2 Alpha Charlie 09843'){
    throw new Error('Production UI regression: Stats snapshot lost Campaign identity');
  }
  if(!truth.statsSnapshot||!Number.isFinite(Number(truth.statsSnapshot.pigeonMiles))||Number(truth.statsSnapshot.pigeonMiles)<=0){
    throw new Error('Production UI regression: Challenges bridge Pigeon Miles unresolved');
  }
  const petts=(truth.statsSnapshot.history||[]).find(x=>/Petts Wood/i.test(String(x.fixture||''))&&/Windsor/i.test(String(x.fixture||'')));
  if(!petts||String(petts.postcode||'').replaceAll(' ','').toUpperCase()!=='BR28HQ'){
    throw new Error('Production UI regression: Challenges bridge lost canonical Petts Wood historical venue: '+JSON.stringify(petts));
  }

  console.log('PROTECTED PRODUCTION UI REGRESSION: PASS');
  console.log('Campaign terminology: PASS');
  console.log('Yellow Challenges launcher + Candidate 13 bridge: PASS');
  if(cert.includes('Pigeon Miles Travelled:')||cert.includes('Pigeon Miles Traveled:'))throw new Error('Production UI regression: retired Pigeon Miles travel wording remains');
  console.log('Pigeon Miles wording is universally Flown: PASS');
  console.log('Pigeon Miles approved roundel + six-column no-wrap layout: PASS');
  console.log('HP7 bridge custodian: Windsor & Eton — PASS');
  console.log('HP7 bridge Petts Wood venue: BR2 8HQ — PASS');
})().catch(e=>{console.error(e.stack||e);process.exitCode=1});
`;

try{
  vm.runInContext(scripts+'\n'+assertions,sandbox,{filename:'clubfinder.html'});
}catch(e){
  console.error(e.stack||e);
  process.exit(1);
}
