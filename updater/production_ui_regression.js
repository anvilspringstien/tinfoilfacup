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
  fetch:async(url)=>{
    const s=String(url);
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

  saveJourney(origin,'HP7 0EJ');
  const g=findGround(origin)||{};
  lookup=async()=>({lat:Number(g.lat),lon:Number(g.lon),postcode:'HP7 0EJ'});
  geocodeClubPostcodes=async()=>{};
  document.getElementById('postcode').value='HP7 0EJ';
  await go();

  const rendered=String(document.getElementById('results').innerHTML||'');
  for(const required of [
    'My Tin Foil FA Cup Campaign',
    'View Original Campaigns',
    '>Challenges<',
    'End My Campaign',
    'class="round challenges-launch"'
  ]){
    if(!rendered.includes(required))throw new Error('Production UI regression: rendered Campaign toolbar missing '+required);
  }
  for(const retired of ['My Tin Foil FA Cup Journey','View Original Journeys','End My Journey']){
    if(rendered.includes(retired))throw new Error('Production UI regression: retired Journey toolbar text remains: '+retired);
  }
  if(!/This Campaign starts with:/i.test(rendered))throw new Error('Production UI regression: Campaign history origin wording missing');

  certificateHtml='';
  await journeyCertificate(origin);
  if(!certificateHtml)throw new Error('Production UI regression: Stats certificate did not render');
  for(const required of [
    'YOUR TIN FOIL FA CUP CAMPAIGN',
    'THE CAMPAIGN SO FAR',
    'Pigeon Miles Flown',
    'grid-template-columns:repeat(6,minmax(0,1fr))',
    '.g:last-child{grid-column:auto}'
  ]){
    if(!certificateHtml.includes(required))throw new Error('Production UI regression: Stats certificate missing '+required);
  }
  if(certificateHtml.includes('>🐦</div>'))throw new Error('Production UI regression: generic pigeon emoji remains in Stats At a Glance');
  const pigeonLabel=(certificateHtml.match(/Pigeon<br>Miles/g)||[]).length;
  if(pigeonLabel!==1)throw new Error('Production UI regression: expected one Pigeon Miles At-a-Glance card, got '+pigeonLabel);

  location.href='https://anvilspringstien.github.io/tinfoilfacup/clubfinder.html';
  await openChallenges(origin);
  if(!String(location.href).endsWith('/beta/challenges-beta.html'))throw new Error('Production UI regression: Challenges did not launch Candidate 13 beta path: '+location.href);
  const raw=localStorage.getItem('tffc.clubfinderCampaign.v1');
  if(!raw)throw new Error('Production UI regression: Challenges bridge truth was not persisted');
  const truth=JSON.parse(raw);
  if(!same(truth.currentCustodian,'Windsor & Eton'))throw new Error('Production UI regression: Challenges bridge custodian mismatch: '+truth.currentCustodian);
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
