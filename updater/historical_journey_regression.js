#!/usr/bin/env node
const fs=require('fs');
const vm=require('vm');
const path=require('path');
const ROOT=path.resolve(__dirname,'..');
const html=fs.readFileSync(path.join(ROOT,'clubfinder.html'),'utf8');
const competition=JSON.parse(fs.readFileSync(path.join(ROOT,'competition.json'),'utf8'));
const scripts=[...html.matchAll(/<script[^>]*>([\s\S]*?)<\/script>/gi)].map(m=>m[1]).join('\n');
if(!scripts.trim())throw new Error('No inline Clubfinder JavaScript found');
function nodeStub(){return {value:'',textContent:'',innerHTML:'',style:{},disabled:false,addEventListener(){},focus(){},setAttribute(){},removeAttribute(){},appendChild(){},remove(){},insertAdjacentElement(){},classList:{add(){},remove(){}}}}
const elements=new Proxy({}, {get:(o,k)=>o[k]||(o[k]=nodeStub())});
const documentStub={readyState:'complete',getElementById(id){return elements[id]},querySelector(){return nodeStub()},querySelectorAll(){return []},createElement(){return nodeStub()},addEventListener(){},body:nodeStub()};
const sandbox={console,process,document:documentStub,MutationObserver:undefined,localStorage:{getItem(){return null},setItem(){},removeItem(){}},navigator:{},location:{href:'https://example.test/clubfinder.html'},URL,URLSearchParams,TextEncoder,TextDecoder,setTimeout,clearTimeout,fetch:async(url)=>{if(String(url).includes('competition.json'))return {ok:true,json:async()=>JSON.parse(JSON.stringify(competition)),text:async()=>JSON.stringify(competition)};throw new Error('Unexpected network request: '+url)}};
sandbox.window=sandbox;sandbox.globalThis=sandbox;vm.createContext(sandbox);
const assertions=`
(async()=>{
  await refreshCompetitionData(false);
  const same=(a,b)=>typeof sameClubIdentity==='function'?sameClubIdentity(a,b):norm(a)===norm(b);
  const isOriginal=r=>r&&r.round==='Extra Preliminary Round'&&same(r.home,'North Leigh')&&same(r.away,'Amersham Town')&&Number(r.home_score)===2&&Number(r.away_score)===2;
  const history=(LIVE_COMPETITION_DATA&&LIVE_COMPETITION_DATA.result_history)||{};
  let removed=0,survivors=0;
  for(const [key,arr] of Object.entries(history)){
    if(!Array.isArray(arr))continue;
    if(same(key,'Amersham Town')){
      const before=arr.length;
      history[key]=arr.filter(r=>!isOriginal(r));
      removed+=before-history[key].length;
    }else{
      survivors+=arr.filter(isOriginal).length;
    }
  }
  if(!removed)throw new Error('Fragmented-alias regression could not remove Amersham exact-name original tie');
  if(!survivors)throw new Error('Fragmented-alias regression has no opponent/alternate history copy to recover');

  const amersham=ELIGIBLE.find(c=>same(c.name,'Amersham Town'));
  if(!amersham)throw new Error('Amersham Town origin missing');
  const journey=buildJourney(amersham),crumbs=journey.breadcrumbs||[];
  const first=crumbs.find(x=>isOriginal(x.result||{}));
  if(!first)throw new Error('Amersham original Extra Preliminary tie missing from Campaign history after exact-name alias fragmentation');
  const replay=crumbs.find(x=>{const r=x.result||{};return r.round==='Extra Preliminary Round Replay'&&same(r.home,'Amersham Town')&&same(r.away,'North Leigh')});
  if(!replay)throw new Error('Amersham Extra Preliminary replay missing from Campaign history');
  if(Number(replay.result.home_score)!==1||Number(replay.result.away_score)!==2)throw new Error('Amersham replay is not Amersham Town 1-2 North Leigh');
  if(resultSortValue(first.result)>=resultSortValue(replay.result))throw new Error('Amersham original draw does not precede replay');
  const prelim=crumbs.find(x=>{const r=x.result||{};return r.round==='Preliminary Round'&&same(r.home,'Windsor & Eton')&&same(r.away,'North Leigh')});
  if(!prelim||Number(prelim.result.home_score)!==5||Number(prelim.result.away_score)!==0)throw new Error('Amersham custody chain lost Windsor & Eton 5-0 North Leigh');
  const petts=crumbs.find(x=>{const r=x.result||{};return same(r.home,'Petts Wood & Holmesdale')&&same(r.away,'Windsor & Eton')&&r.round==='First Round Qualifying'});
  if(!petts)throw new Error('Petts Wood & Holmesdale v Windsor & Eton history row missing');
  if(Number(petts.result.home_score)!==1||Number(petts.result.away_score)!==5)throw new Error('Petts Wood result is not 1-5 Windsor & Eton');
  const venue=completedResultVenue(petts.result);
  if(String(venue.postcode||'').replace(/\\s+/g,'').toUpperCase()!=='BR28HQ')throw new Error('Petts Wood historical venue postcode wrong: '+JSON.stringify(venue));
  if(!/New Inn Stadium/i.test(String(venue.ground||'')))throw new Error('Petts Wood historical venue ground wrong: '+JSON.stringify(venue));
  console.log('HISTORICAL JOURNEY REGRESSION: PASS');
  console.log('Fragmented Amersham alias recovered from canonical opponent/alternate bucket: PASS');
  console.log('Amersham 2-2 -> 1-2 -> Windsor & Eton 5-0 -> Petts Wood 1-5 chronology: PASS');
  console.log('Petts Wood & Holmesdale v Windsor & Eton historical venue: PASS');
  console.log('Amersham breadcrumb count:',crumbs.length);
})().catch(e=>{console.error(e.stack||e);process.exitCode=1});`;
try{vm.runInContext(scripts+'\n'+assertions,sandbox,{filename:'clubfinder.html'});}catch(e){console.error(e.stack||e);process.exit(1)}
