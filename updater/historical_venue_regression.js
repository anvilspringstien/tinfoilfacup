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
    querySelectorAll(){return []},classList:{add(){},remove(){}}
  };
}
const elements=new Proxy({}, {get:(o,k)=>o[k]||(o[k]=nodeStub())});
const documentStub={
  readyState:'complete',
  getElementById(id){return elements[id]},
  querySelector(){return nodeStub()},
  querySelectorAll(){return []},
  createElement(){return nodeStub()},
  addEventListener(){},
  body:nodeStub()
};
const sandbox={
  console,process,document:documentStub,MutationObserver:undefined,
  localStorage:{getItem(){return null},setItem(){},removeItem(){}},
  navigator:{},location:{href:'https://example.test/clubfinder.html'},
  URL,URLSearchParams,TextEncoder,TextDecoder,setTimeout,clearTimeout,
  fetch:async(url)=>{
    const s=String(url);
    if(s.includes('competition.json')){
      return {ok:true,status:200,json:async()=>JSON.parse(JSON.stringify(competition)),text:async()=>JSON.stringify(competition)};
    }
    throw new Error('Unexpected network request in historical venue regression: '+s);
  }
};
sandbox.window=sandbox;
sandbox.globalThis=sandbox;
vm.createContext(sandbox);

const assertions=`
(async()=>{
  if(typeof refreshCompetitionData==='function')await refreshCompetitionData(false);
  if(typeof completedResultVenue!=='function')throw new Error('Historical venue regression: completedResultVenue helper missing');
  if(typeof buildJourney!=='function')throw new Error('Historical venue regression: buildJourney helper missing');

  const usable=value=>{
    const s=String(value||'').trim();
    return !!s&&!/TBC/i.test(s);
  };
  const groundKey=value=>String(value||'').toLowerCase().replace(/[^a-z0-9]+/g,' ').trim().replace(/\\s+/g,' ');
  const postcodeKey=value=>String(value||'').toUpperCase().replace(/[^A-Z0-9]+/g,'');
  const assertVenue=(result,label)=>{
    const canonical=(result&&result.venue)||{};
    const resolved=completedResultVenue(result||{});
    if(usable(canonical.ground)&&groundKey(resolved&&resolved.ground)!==groundKey(canonical.ground)){
      throw new Error(label+': canonical ground lost. Expected '+canonical.ground+', got '+JSON.stringify(resolved));
    }
    if(usable(canonical.postcode)&&postcodeKey(resolved&&resolved.postcode)!==postcodeKey(canonical.postcode)){
      throw new Error(label+': canonical postcode lost. Expected '+canonical.postcode+', got '+JSON.stringify(resolved));
    }
  };

  const history=(LIVE_COMPETITION_DATA&&LIVE_COMPETITION_DATA.result_history)||{};
  let canonicalRows=0;
  for(const [bucket,rows] of Object.entries(history)){
    if(!Array.isArray(rows))continue;
    rows.forEach((result,index)=>{
      const venue=(result&&result.venue)||{};
      if(!usable(venue.ground)&&!usable(venue.postcode))return;
      canonicalRows++;
      assertVenue(result,'result_history '+bucket+'['+index+']');
    });
  }
  if(!canonicalRows)throw new Error('Historical venue regression: no canonical result venues were available to test');

  let campaignBreadcrumbs=0;
  let campaignsWithCanonicalVenue=0;
  for(const origin of ELIGIBLE){
    const journey=buildJourney(origin);
    let hit=false;
    for(const crumb of (journey.breadcrumbs||[])){
      const result=(crumb||{}).result||{};
      const venue=result.venue||{};
      if(!usable(venue.ground)&&!usable(venue.postcode))continue;
      hit=true;
      campaignBreadcrumbs++;
      assertVenue(result,'Campaign '+String(origin.name||'unknown')+' breadcrumb');
    }
    if(hit)campaignsWithCanonicalVenue++;
  }
  if(!campaignBreadcrumbs)throw new Error('Historical venue regression: no Campaign breadcrumbs exercised canonical historical venues');

  console.log('GENERIC HISTORICAL VENUE REGRESSION: PASS');
  console.log('Canonical result-history venue rows checked:',canonicalRows);
  console.log('Campaign breadcrumbs with canonical venues checked:',campaignBreadcrumbs);
  console.log('Campaign origins exercising canonical venues:',campaignsWithCanonicalVenue);
  console.log('Canonical result.venue precedence over home-ground fallback: PASS');
})().catch(e=>{console.error(e.stack||e);process.exitCode=1});
`;

try{
  vm.runInContext(scripts+'\n'+assertions,sandbox,{filename:'clubfinder.html'});
}catch(e){
  console.error(e.stack||e);
  process.exit(1);
}
