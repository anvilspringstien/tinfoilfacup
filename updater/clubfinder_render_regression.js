#!/usr/bin/env node
const fs=require('fs');
const vm=require('vm');
const path=require('path');
const ROOT=path.resolve(__dirname,'..');
const html=fs.readFileSync(path.join(ROOT,'clubfinder.html'),'utf8');
const competition=JSON.parse(fs.readFileSync(path.join(ROOT,'competition.json'),'utf8'));
const scripts=[...html.matchAll(/<script[^>]*>([\s\S]*?)<\/script>/gi)].map(m=>m[1]).join('\n');
if(!scripts.trim()) throw new Error('No inline Clubfinder JavaScript found');
function nodeStub(){return {value:'',textContent:'',innerHTML:'',style:{},disabled:false,addEventListener(){},focus(){},setAttribute(){},removeAttribute(){},appendChild(){},remove(){},classList:{add(){},remove(){}}}}
const elements=new Proxy({}, {get:(o,k)=>o[k]||(o[k]=nodeStub())});
const documentStub={getElementById(id){return elements[id]},querySelector(){return nodeStub()},querySelectorAll(){return []},createElement(){return nodeStub()},body:nodeStub()};
const localStore={};
const sandbox={console,process,document:documentStub,localStorage:{getItem:k=>localStore[k]??null,setItem:(k,v)=>{localStore[k]=String(v)},removeItem:k=>delete localStore[k]},navigator:{},location:{href:'https://example.test/clubfinder.html'},URL,URLSearchParams,TextEncoder,TextDecoder,setTimeout,clearTimeout,fetch:async(url)=>{const s=String(url);if(s.includes('competition.json'))return {ok:true,json:async()=>competition,text:async()=>JSON.stringify(competition)};throw new Error('Unexpected network request in render regression: '+s)}};
sandbox.window=sandbox;sandbox.globalThis=sandbox;vm.createContext(sandbox);
const assertions=`
(async()=>{
  if(typeof refreshCompetitionData==='function') await refreshCompetitionData(false);
  const same=(a,b)=>typeof sameClubIdentity==='function'?sameClubIdentity(a,b):norm(a)===norm(b);
  const assertSecondQFixture=(next,club,label)=>{
    if(!next||next.name!=='Second Round Qualifying')throw new Error(label+': expected Second Round Qualifying next-round metadata');
    if(!next.knownFixture)throw new Error(label+': Second Round Qualifying draw is published but Clubfinder has no known fixture');
    const f=next.knownFixture||{};
    if(!/Second Round Qualifying/i.test(f.round||''))throw new Error(label+': known fixture has wrong round '+(f.round||'UNKNOWN'));
    if(!same(f.home,club.name)&&!same(f.away,club.name))throw new Error(label+': known fixture does not contain current custodian '+club.name+' ('+(f.home||'?')+' v '+(f.away||'?')+')');
    return f;
  };

  const origin=ELIGIBLE.find(c=>same(c.name,'Newton Aycliffe FC'));
  if(!origin) throw new Error('DL5 regression: Newton Aycliffe FC not found in ELIGIBLE');
  const j=buildJourney(origin);const carrier=j.carrier||origin;const history=(j.breadcrumbs||[]).map(x=>x.result||{});
  const hasNewtonLoss=history.some(r=>same(r.home,'Newton Aycliffe')&&same(r.away,'Kendal Town')&&Number(r.home_score)===0&&Number(r.away_score)===1);
  const hasHeatonReplay=history.some(r=>same(r.home,'Heaton Stannington')&&same(r.away,'Kendal Town')&&Number(r.home_score)===4&&Number(r.away_score)===2);
  const kendalHeatonDraws=history.filter(r=>same(r.home,'Kendal Town')&&same(r.away,'Heaton Stannington')&&Number(r.home_score)===2&&Number(r.away_score)===2&&/Preliminary Round/i.test(r.round||''));
  if(!hasNewtonLoss) throw new Error('DL5 render regression: Newton Aycliffe 0-1 Kendal missing from journey history');
  if(!hasHeatonReplay) throw new Error('DL5 render regression: Heaton Stannington 4-2 Kendal replay missing from journey history');
  if(kendalHeatonDraws.length!==1) throw new Error('DL5 render regression: expected one Kendal 2-2 Heaton draw, got '+kendalHeatonDraws.length);
  if(!same(carrier.name,'Heaton Stannington')) throw new Error('DL5 render regression: expected current custodian Heaton Stannington, got '+carrier.name);
  const state=competitionState(carrier);
  if(state.type!=='won')throw new Error('DL5 render regression: Heaton should be a confirmed First Qualifying winner, got '+state.type);
  if(!state.result||!same(state.result.home,'Heaton Stannington')||!same(state.result.away,'Knaresborough Town')||Number(state.result.home_score)!==1||Number(state.result.away_score)!==0)throw new Error('DL5 render regression: Heaton 1-0 Knaresborough result not driving winner state');
  const heatonNext=nextRoundInfo(carrier);
  const heatonSecondQ=assertSecondQFixture(heatonNext,carrier,'DL5 render regression');
  if(same(heatonSecondQ.home,'Knaresborough Town')||same(heatonSecondQ.away,'Knaresborough Town'))throw new Error('DL5 render regression: played Heaton-Knaresborough First Qualifying tie leaked into Second Round Qualifying fixture');

  const bishop=ELIGIBLE.find(c=>same(c.name,'Bishop Auckland FC'));
  if(!bishop)throw new Error('DL5 regression: Bishop Auckland FC not found in ELIGIBLE');
  const bishopHistory=historicalResultsForClub(bishop).map(x=>x.result||{});
  const bishopDraw=bishopHistory.find(r=>same(r.home,'Emley AFC')&&same(r.away,'Bishop Auckland')&&Number(r.home_score)===1&&Number(r.away_score)===1&&/First Round Qualifying/i.test(r.round||''));
  if(!bishopDraw)throw new Error('DL5 render regression: Emley 1-1 Bishop Auckland First Qualifying draw missing');
  if(!resultNeedsReplay(bishopDraw))throw new Error('DL5 render regression: Emley-Bishop Auckland draw must remain unresolved pending replay');
  const bishopState=competitionState(bishop);
  if(bishopState.type==='won'||bishopState.type==='eliminated')throw new Error('DL5 render regression: unresolved Emley-Bishop Auckland draw incorrectly resolved as '+bishopState.type);
  const bishopNext=nextRoundInfo(bishop);
  if(bishopNext&&bishopNext.knownFixture){
    const bf=bishopNext.knownFixture||{};
    if(!/Second Round Qualifying/i.test(bf.round||''))throw new Error('DL5 render regression: Bishop conditional next fixture has wrong round');
    if(!bf.conditional)throw new Error('DL5 render regression: unresolved Bishop replay mapped to an unconditional Second Qualifying fixture');
  }
  const bishopFixture=liveLookup('fixtures',bishop.name)||{};
  const bv=bishopFixture.venue||{};
  if(!bv.postcode||/TBC/i.test(bv.postcode))throw new Error('DL5 render regression: Bishop Auckland current mapped fixture venue/postcode still TBC');
  if(!bv.ground||/TBC/i.test(bv.ground))throw new Error('DL5 render regression: Bishop Auckland current mapped fixture ground still TBC');

  const sporting=ELIGIBLE.find(c=>same(c.name,'Sporting Bengal United FC'));
  if(!sporting) throw new Error('W1D regression: Sporting Bengal United FC not found');
  const wj=buildJourney(sporting);const wcarrier=wj.carrier||sporting;const whistory=(wj.breadcrumbs||[]).map(x=>x.result||{});
  const frenfordReplay=whistory.find(r=>same(r.home,'Frenford')&&same(r.away,'Haringey Borough')&&/Replay/i.test(r.round||''));
  if(!frenfordReplay)throw new Error('W1D regression: Frenford v Haringey Borough replay missing from journey history');
  if(frenfordReplay.kickoff!=='19:45')throw new Error('W1D regression: Frenford replay kick-off expected 19:45, got '+frenfordReplay.kickoff);
  const frenfordLoss=whistory.find(r=>same(r.home,'Frenford')&&same(r.away,'Enfield Town')&&Number(r.home_score)===0&&Number(r.away_score)===4);
  if(!frenfordLoss)throw new Error('W1D regression: Frenford 0-4 Enfield Town missing from journey history');
  if(!same(wcarrier.name,'Enfield Town'))throw new Error('W1D regression: expected live custodian Enfield Town after Frenford loss, got '+wcarrier.name);
  const enfieldState=competitionState(wcarrier);if(enfieldState.type!=='won')throw new Error('W1D regression: Enfield should be confirmed First Qualifying winner');
  const enfieldNext=nextRoundInfo(wcarrier);
  const enfieldSecondQ=assertSecondQFixture(enfieldNext,wcarrier,'W1D regression');
  if(same(enfieldSecondQ.home,'Frenford')||same(enfieldSecondQ.away,'Frenford'))throw new Error('W1D regression: played Frenford-Enfield First Qualifying tie leaked into Enfield next-round fixture');

  console.log('CLUBFINDER RENDER REGRESSION: PASS');
  console.log('DL5 custody:',origin.name,'-> Kendal Town ->',carrier.name);
  console.log('Heaton First Qualifying result: 1-0 Knaresborough — PASS');
  console.log('Heaton Second Qualifying fixture:',heatonSecondQ.home,'v',heatonSecondQ.away);
  console.log('Kendal-Heaton draw count:',kendalHeatonDraws.length);
  console.log('Heaton replay present: PASS');
  console.log('Emley-Bishop Auckland replay-pending state: PASS');
  console.log('Bishop IF THROUGH fixture:',bishopNext&&bishopNext.knownFixture?(bishopNext.knownFixture.home+' v '+bishopNext.knownFixture.away):'not yet mapped');
  console.log('Emley-Bishop Auckland mapped venue:',bv.ground,'•',bv.postcode);
  console.log('W1D custody: Sporting Bengal United -> Frenford ->',wcarrier.name);
  console.log('Enfield Second Qualifying fixture:',enfieldSecondQ.home,'v',enfieldSecondQ.away);
  console.log('W1D Frenford replay kick-off:',frenfordReplay.kickoff);
})().catch(e=>{console.error(e.stack||e);process.exitCode=1});`;
try{vm.runInContext(scripts+'\n'+assertions,sandbox,{filename:'clubfinder.html'});}catch(e){console.error(e.stack||e);process.exit(1)}
