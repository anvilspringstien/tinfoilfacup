#!/usr/bin/env node
// Read-only cross-version behavioural audit on identical canonical competition data.
// Source-only comparison is not sufficient: execute actual completedResultVenue,
// buildJourney, nextRoundInfo and currentDisplayFixture from both HTML builds.
'use strict';
const fs=require('node:fs');
const vm=require('node:vm');
const assert=require('node:assert/strict');
const competition=JSON.parse(fs.readFileSync('competition.json','utf8'));
const sources={
  production:fs.readFileSync('clubfinder.html','utf8'),
  beta:fs.readFileSync('beta/clubfinder-beta.html','utf8')
};
const norm=s=>String(s||'').toLowerCase().replace(/&/g,' and ').replace(/\b(fc|afc|cfc)\b/g,' ').replace(/[^a-z0-9]+/g,' ').trim();
const pc=s=>String(s||'').toUpperCase().replace(/[^A-Z0-9]/g,'');
const usable=s=>!!s&&!/TBC/i.test(String(s));
function harness(label,html){
  const scripts=[...html.matchAll(/<script[^>]*>([\s\S]*?)<\/script>/gi)].map(m=>m[1]).join('\n');
  assert(scripts.length>15000,label+' has no inline scripts');
  const node=()=>({value:'',textContent:'',innerHTML:'',hidden:false,style:{},dataset:{},children:[],
    addEventListener(){},removeEventListener(){},focus(){},setAttribute(){},removeAttribute(){},
    appendChild(){},remove(){},insertAdjacentElement(){},querySelectorAll(){return []},
    classList:{add(){},remove(){}}});
  const elements=new Proxy({}, {get:(o,k)=>o[k]||(o[k]=node())});
  const document={
    readyState:'complete',activeElement:null,getElementById:id=>elements[id],
    querySelector:()=>node(),querySelectorAll:()=>[],createElement:()=>node(),
    addEventListener(){},removeEventListener(){},body:node()
  };
  const local={},session={};
  const store=o=>({getItem:k=>o[k]??null,setItem:(k,v)=>{o[k]=String(v)},removeItem:k=>delete o[k]});
  const ctx={console,process,document,navigator:{},
    localStorage:store(local),sessionStorage:store(session),MutationObserver:undefined,
    location:{href:label==='beta'?'https://example.test/beta/clubfinder-beta.html':'https://example.test/clubfinder.html',
      replace(v){this.href=v}},
    URL,URLSearchParams,TextEncoder,TextDecoder,setTimeout,clearTimeout,
    open:()=>({document:{open(){},write(){},close(){},body:{innerHTML:''},documentElement:{innerHTML:''}},focus(){},print(){},close(){}}),
    fetch:async url=>{
      const s=String(url);
      if(s.includes('competition.json'))return {ok:true,status:200,json:async()=>JSON.parse(JSON.stringify(competition)),
        text:async()=>JSON.stringify(competition)};
      if(s.includes('counter-config.json'))return {ok:true,status:200,json:async()=>({increment_url:'https://counter.invalid/increment'})};
      throw new Error('Unexpected '+label+' fetch during reconciliation: '+s);
    }
  };
  ctx.window=ctx;ctx.globalThis=ctx;
  vm.createContext(ctx);
  vm.runInContext(scripts,ctx,{filename:label+'.html',timeout:25000});
  return {
    ctx,
    async refresh(){
      await vm.runInContext("typeof refreshCompetitionData==='function'?refreshCompetitionData(false):Promise.resolve()",ctx);
    },
    probe(expression,vars={}){
      Object.assign(ctx,vars);
      return vm.runInContext(expression,ctx,{timeout:25000});
    }
  };
}
const models={};
function uniqueRows(){
  const rows=[],seen=new Set();
  for(const group of Object.values(competition.result_history||{})){
    if(!Array.isArray(group))continue;
    for(const r of group){
      if(!r||typeof r!=='object')continue;
      const k=[r.round,r.date,r.home,r.away,r.home_score,r.away_score,r.venue&&r.venue.postcode].join('|');
      if(seen.has(k))continue;
      seen.add(k);rows.push(r);
    }
  }
  return rows;
}
async function main(){
  for(const [label,html] of Object.entries(sources)){
    models[label]=harness(label,html);
    await models[label].refresh();
  }
  const prod=models.production,beta=models.beta;
  const rows=uniqueRows(),explicit=rows.filter(r=>r.venue&&(usable(r.venue.postcode)||usable(r.venue.ground)));
  const mismatches=[],canonicalFailures=[],renames=[];
  for(const r of explicit){
    const a=prod.probe('completedResultVenue(__row)',{__row:r});
    const b=beta.probe('completedResultVenue(__row)',{__row:r});
    const identity={round:r.round,date:r.date,home:r.home,away:r.away};
    const want=r.venue||{};
    for(const [label,v] of [['production',a],['beta',b]]){
      if(usable(want.postcode)&&pc(v.postcode)!==pc(want.postcode))canonicalFailures.push({...identity,side:label,reason:'canonical postcode lost',canonical:want,resolved:v});
      if(usable(want.ground)&&norm(v.ground)!==norm(want.ground))renames.push({...identity,side:label,canonicalGround:want.ground,resolvedGround:v.ground,postcode:v.postcode});
    }
    if(pc(a.postcode)!==pc(b.postcode)||norm(a.ground)!==norm(b.ground))
      mismatches.push({...identity,canonical:want,production:a,beta:b,postcodeDifferent:pc(a.postcode)!==pc(b.postcode)});
  }
  assert(explicit.length>0,'Audit failed: canonical result_history lacks explicit historical venues');
  console.log('VENUE_AUDIT '+JSON.stringify({
    distinctHistoricRows:rows.length,explicitCanonicalVenues:explicit.length,
    differences:mismatches.length,postcodeDifferences:mismatches.filter(x=>x.postcodeDifferent).length,
    lostCanonicalPostcode:canonicalFailures.length,canonicalGroundRenames:renames.length,
    firstDifferences:mismatches.slice(0,12),firstFailures:canonicalFailures.slice(0,8),
    firstRenames:renames.slice(0,8)
  }));
  const petts=rows.find(r=>/First Round Qualifying$/i.test(r.round||'')&&norm(r.home)===norm('Petts Wood & Holmesdale')&&norm(r.away)===norm('Windsor & Eton'));
  assert(petts,'Known Petts Wood v Windsor & Eton historical result missing');
  const historical={};
  for(const [name,m] of Object.entries(models)){
    const v=m.probe('completedResultVenue(__row)',{__row:petts});
    historical[name]={ground:v.ground,postcode:v.postcode};
    assert.equal(pc(v.postcode),'BR28HQ',name+' lost Petts Wood historical venue postcode');
  }
  console.log('PETTS_WOOD '+JSON.stringify(historical));
  const selected=['Newton Aycliffe','Heaton Stannington','Amersham Town','Weston Super Mare',
    'Wimborne Town','Hampton & Richmond Borough','Epsom & Ewell','Corinthian Casuals',
    'Exmouth Town','Thame United','Chesham United','Crowborough Athletic'];
  const journeyComparisons=[],fixtureDifferences=[],missing=[];
  function journey(m,name){
    return m.probe(
      '(function(){const o=ELIGIBLE.find(c=>sameClubIdentity(c.name,__name));if(!o)return null;'+
      'const j=buildJourney(o);const c=j.carrier||o;const n=nextRoundInfo(c);'+
      'const f=currentDisplayFixture(o);return {origin:o.name,custodian:c.name,'+
      'history:(j.breadcrumbs||[]).map(x=>({round:x.round,home:(x.result||{}).home,away:(x.result||{}).away,'+
      'winner:(x.result||{}).winner,date:(x.result||{}).date})),next:n?{name:n.name,'+
      'fixture:n.knownFixture?{round:n.knownFixture.round,home:n.knownFixture.home,'+
      'away:n.knownFixture.away,date:n.knownFixture.date,kickoff:n.knownFixture.kickoff,'+
      'venue:n.knownFixture.venue}:null}:null,'+
      'display:f?{round:f.round,tie:f.tie,kickoff:f.kickoff,venue:f.venue,completed:f.completed}:null};})()',
      {__name:name}
    );
  }
  for(const name of selected){
    const p=journey(prod,name),b=journey(beta,name);
    if(!p||!b){missing.push({requested:name,production:!!p,beta:!!b});continue}
    const custody=norm(p.custodian)===norm(b.custodian);
    const pNext=p.next&&p.next.fixture,bNext=b.next&&b.next.fixture;
    const nextEqual=JSON.stringify(pNext&&[norm(pNext.home),norm(pNext.away),pNext.date,pc(pNext.venue&&pNext.venue.postcode)])===
      JSON.stringify(bNext&&[norm(bNext.home),norm(bNext.away),bNext.date,pc(bNext.venue&&bNext.venue.postcode)]);
    const historyEqual=JSON.stringify(p.history)===JSON.stringify(b.history);
    journeyComparisons.push({origin:p.origin,productionCustodian:p.custodian,betaCustodian:b.custodian,
      custodySame:custody,historySame:historyEqual,nextSame:nextEqual,
      productionNext:pNext&&{home:pNext.home,away:pNext.away,postcode:pNext.venue&&pNext.venue.postcode},
      betaNext:bNext&&{home:bNext.home,away:bNext.away,postcode:bNext.venue&&bNext.venue.postcode}});
    if(!custody||!historyEqual||!nextEqual){
      fixtureDifferences.push({requested:name,production:p,beta:b});
    }
  }
  console.log('FIXTURE_AUDIT '+JSON.stringify({examined:journeyComparisons.length,missing,
    sameCustodians:journeyComparisons.filter(x=>x.custodySame).length,
    sameHistories:journeyComparisons.filter(x=>x.historySame).length,
    sameNextFixtures:journeyComparisons.filter(x=>x.nextSame).length,
    comparisons:journeyComparisons,differences:fixtureDifferences.slice(0,9)}));
  // Independently test the real published Thame draw from both custodians.
  const thameDraw=Object.values(competition.fixtures||{}).find(f=>f&&
    f.round==='Third Round Qualifying'&&/Thame Utd or Exmouth Town/i.test(f.home||'')&&
    /Eastbourne Borough/i.test(f.away||''));
  assert(thameDraw,'Published Thame Utd or Exmouth Town draw is missing');
  const thameDiagnostic={canonicalDraw:{home:thameDraw.home,away:thameDraw.away,round:thameDraw.round,date:thameDraw.date}};
  for(const [label,m] of Object.entries(models)){
    thameDiagnostic[label]=m.probe(
      '(function(){const o=ELIGIBLE.find(c=>sameClubIdentity(c.name,__name));'+
      'const c=buildJourney(o).carrier||o;const next=nextRoundInfo(c);'+
      'const live=liveLookup(\'fixtures\',c.name);'+
      'const explicit=resolveLiveFixtureForCarrier(__draw,c,true);'+
      'return {custodian:c.name,nextName:next&&next.name,nextDate:next&&next.date,'+
      'nextKnown:next&&next.knownFixture,liveLookup:live,'+
      'directResolved:{home:explicit&&explicit.home,away:explicit&&explicit.away,'+
      'conditional:explicit&&explicit.conditional,venue:explicit&&explicit.venue}};})()',
      {__name:'Thame United',__draw:thameDraw}
    );
  }
  console.log('THAME_NEXT_FIXTURE_DIAG '+JSON.stringify(thameDiagnostic));
  // Record discrepancies without failing the audit. Fail only on observed data-integrity
  // regressions; audit alone is not permission to change production or publish.
  assert.equal(canonicalFailures.length,0,'At least one version lost a canonical venue postcode');
  console.log('CROSS_VERSION_BEHAVIOURAL_AUDIT: PASS (read only; differences are reported)');
}
main().catch(e=>{console.error('CROSS_VERSION_BEHAVIOURAL_AUDIT FAILED',e.stack||e);process.exitCode=1});
