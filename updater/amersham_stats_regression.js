#!/usr/bin/env node
const fs=require('fs');
const vm=require('vm');
const path=require('path');
const childProcess=require('child_process');
const ROOT=path.resolve(__dirname,'..');
const html=fs.readFileSync(path.join(ROOT,'clubfinder.html'),'utf8');
const competition=JSON.parse(fs.readFileSync(path.join(ROOT,'competition.json'),'utf8'));

// Campaign UI gate v3: structural Pigeon card + main-document Challenges styling.
// This regression is already run by both publishers and again immediately
// before a production push. Reuse that protected choke-point to ensure the
// Campaign UI cannot disappear while chronology/Stats remain green.
childProcess.execFileSync(process.execPath,[path.join(ROOT,'updater','clubfinder_campaign_ui_regression.js')],{cwd:ROOT,stdio:'inherit'});

const scripts=[...html.matchAll(/<script[^>]*>([\s\S]*?)<\/script>/gi)].map(m=>m[1]).join('\n');
if(!scripts.trim())throw new Error('No inline Clubfinder JavaScript found');

function nodeStub(){return {value:'',textContent:'',innerHTML:'',style:{},disabled:false,children:[],parentElement:null,addEventListener(){},focus(){},setAttribute(){},removeAttribute(){},appendChild(){},remove(){},querySelectorAll(){return []},classList:{add(){},remove(){}}}}
const elements=new Proxy({}, {get:(o,k)=>o[k]||(o[k]=nodeStub())});
const documentStub={readyState:'complete',getElementById(id){return elements[id]},querySelector(){return nodeStub()},querySelectorAll(){return []},createElement(){return nodeStub()},addEventListener(){},body:nodeStub()};
const coords={
  'HP70EJ':{latitude:51.676,longitude:-0.607},
  'OX296SL':{latitude:51.807,longitude:-1.407},
  'SL43DR':{latitude:51.482,longitude:-0.612},
  'BR28HQ':{latitude:51.384,longitude:0.022}
};
function postcodeFromUrl(url){
  const s=decodeURIComponent(String(url));
  const m=s.match(/\/postcodes\/([^?/#]+)/i);
  return m?String(m[1]).replace(/\s+/g,'').toUpperCase():'';
}
const sandbox={
  console,process,document:documentStub,MutationObserver:undefined,
  localStorage:{getItem(){return null},setItem(){},removeItem(){}},
  navigator:{},location:{href:'https://example.test/clubfinder.html'},URL,URLSearchParams,TextEncoder,TextDecoder,setTimeout,clearTimeout,
  open:()=>({document:{open(){},write(){},writeln(){},close(){},body:{innerHTML:''},documentElement:{innerHTML:''}},focus(){},print(){},close(){}}),
  fetch:async(url)=>{
    const s=String(url);
    if(s.includes('competition.json'))return {ok:true,json:async()=>JSON.parse(JSON.stringify(competition)),text:async()=>JSON.stringify(competition)};
    if(/postcodes\//i.test(s)){
      const pc=postcodeFromUrl(s),hit=coords[pc];
      return hit?{ok:true,json:async()=>({status:200,result:hit})}:{ok:false,json:async()=>({status:404,result:null})};
    }
    throw new Error('Unexpected network request: '+s);
  }
};
sandbox.window=sandbox;sandbox.globalThis=sandbox;vm.createContext(sandbox);

const assertions=`
(async()=>{
  if(typeof refreshCompetitionData==='function')await refreshCompetitionData(false);
  const same=(a,b)=>typeof sameClubIdentity==='function'?sameClubIdentity(a,b):String(a||'')===String(b||'');
  const origin=ELIGIBLE.find(c=>same(c.name,'Amersham Town'));
  if(!origin)throw new Error('HP7 Stats regression: Amersham Town origin missing');
  const journey=buildJourney(origin),crumbs=journey.breadcrumbs||[];
  const petts=crumbs.find(x=>{const r=x.result||{};return r.round==='First Round Qualifying'&&same(r.home,'Petts Wood & Holmesdale')&&same(r.away,'Windsor & Eton')});
  if(!petts)throw new Error('HP7 Stats regression: Petts Wood & Holmesdale v Windsor & Eton row missing');
  const pv=completedResultVenue(petts.result);
  if(!/New Inn Stadium/i.test(String(pv.ground||''))||String(pv.postcode||'').replace(/\\s+/g,'').toUpperCase()!=='BR28HQ'){
    throw new Error('HP7 Stats regression: canonical Petts Wood historical venue wrong: '+JSON.stringify(pv));
  }
  if(typeof tinFoilPigeonMilesForStats!=='function')throw new Error('HP7 Stats regression: Pigeon Miles helper missing');
  const pigeon=await tinFoilPigeonMilesForStats(crumbs,'HP7 0EJ',completedResultVenue);
  if(pigeon.miles===null||/Awaiting venue location/i.test(String(pigeon.display||''))){
    throw new Error('HP7 Stats regression: Pigeon Miles still unresolved: '+JSON.stringify(pigeon));
  }
  if(!Number.isFinite(Number(pigeon.miles))||Number(pigeon.miles)<=0)throw new Error('HP7 Stats regression: Pigeon Miles must be a positive number');

  if(typeof journeyCertificate!=='function')throw new Error('HP7 Stats regression: journeyCertificate missing');
  const certSource=String(journeyCertificate).replace(/\\s+/g,' ');
  if(!certSource.includes('function venueForResult(r){ const v=completedResultVenue(r);')){
    throw new Error('HP7 Stats regression: loaded Stats venueForResult does not delegate to completedResultVenue');
  }
  if(!certSource.includes('await tinFoilPigeonMilesForStats(crumbs,savedJourneyForStats&&savedJourneyForStats.postcode,venueForResult)')){
    throw new Error('HP7 Stats regression: loaded Stats certificate is not using canonical venueForResult for Pigeon Miles');
  }
  console.log('HP7 STATS REGRESSION: PASS');
  console.log('Campaign: Amersham Town -> North Leigh -> Windsor & Eton');
  console.log('Petts Wood historical venue: The New Inn Stadium, BR2 8HQ — PASS');
  console.log('Stats venue resolver delegates to completedResultVenue — PASS');
  console.log('Pigeon Miles resolved:',pigeon.display);
})().catch(e=>{console.error(e.stack||e);process.exitCode=1});`;

try{vm.runInContext(scripts+'\n'+assertions,sandbox,{filename:'clubfinder.html'});}catch(e){console.error(e.stack||e);process.exit(1)}
