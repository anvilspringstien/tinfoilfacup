#!/usr/bin/env node
const fs=require('fs');
const vm=require('vm');
const path=require('path');

const ROOT=path.resolve(__dirname,'..');
const html=fs.readFileSync(path.join(ROOT,'clubfinder.html'),'utf8');
const competition=JSON.parse(fs.readFileSync(path.join(ROOT,'competition.json'),'utf8'));
const scripts=[...html.matchAll(/<script[^>]*>([\s\S]*?)<\/script>/gi)].map(m=>m[1]).join('\n');
if(!scripts.trim()) throw new Error('No inline Clubfinder JavaScript found');

function nodeStub(){
  return {
    value:'',textContent:'',innerHTML:'',style:{},disabled:false,
    addEventListener(){},focus(){},setAttribute(){},removeAttribute(){},
    appendChild(){},remove(){},classList:{add(){},remove(){}},
  };
}
const elements=new Proxy({}, {get:(o,k)=>o[k]||(o[k]=nodeStub())});
const documentStub={
  getElementById(id){return elements[id]},
  querySelector(){return nodeStub()},
  querySelectorAll(){return []},
  createElement(){return nodeStub()},
  body:nodeStub(),
};
const localStore={};
const sandbox={
  console,process,
  document:documentStub,
  localStorage:{getItem:k=>localStore[k]??null,setItem:(k,v)=>{localStore[k]=String(v)},removeItem:k=>delete localStore[k]},
  navigator:{},location:{href:'https://example.test/clubfinder.html'},
  URL,URLSearchParams,TextEncoder,TextDecoder,setTimeout,clearTimeout,
  fetch:async (url)=>{
    const s=String(url);
    if(s.includes('competition.json')) return {ok:true,json:async()=>competition,text:async()=>JSON.stringify(competition)};
    throw new Error('Unexpected network request in render regression: '+s);
  }
};
sandbox.window=sandbox;
sandbox.globalThis=sandbox;
vm.createContext(sandbox);

const assertions=`
(async()=>{
  if(typeof refreshCompetitionData==='function') await refreshCompetitionData(false);
  const same=(a,b)=>typeof sameClubIdentity==='function'?sameClubIdentity(a,b):norm(a)===norm(b);
  const origin=ELIGIBLE.find(c=>same(c.name,'Newton Aycliffe FC'));
  if(!origin) throw new Error('DL5 regression: Newton Aycliffe FC not found in ELIGIBLE');
  const j=buildJourney(origin);
  const carrier=j.carrier||origin;
  const history=(j.breadcrumbs||[]).map(x=>x.result||{});
  const hasNewtonLoss=history.some(r=>same(r.home,'Newton Aycliffe')&&same(r.away,'Kendal Town')&&Number(r.home_score)===0&&Number(r.away_score)===1);
  const hasHeatonReplay=history.some(r=>same(r.home,'Heaton Stannington')&&same(r.away,'Kendal Town')&&Number(r.home_score)===4&&Number(r.away_score)===2);
  if(!hasNewtonLoss) throw new Error('DL5 render regression: Newton Aycliffe 0-1 Kendal missing from journey history');
  if(!hasHeatonReplay) throw new Error('DL5 render regression: Heaton Stannington 4-2 Kendal replay missing from journey history');
  if(!same(carrier.name,'Heaton Stannington')) throw new Error('DL5 render regression: expected current custodian Heaton Stannington, got '+carrier.name);
  const state=competitionState(carrier);
  if(state.type!=='won' && state.type!=='pending') throw new Error('DL5 render regression: unexpected Heaton state '+state.type);
  const emley=groundByClubName('Emley AFC');
  if(!emley || !emley.postcode || /TBC/i.test(emley.postcode)) throw new Error('DL5 render regression: Emley AFC ground/postcode did not resolve');
  const bishop=ELIGIBLE.find(c=>same(c.name,'Bishop Auckland FC'));
  const next=nextRoundInfo(bishop);
  if(!next||!next.knownFixture) throw new Error('DL5 render regression: Bishop Auckland next fixture missing');
  const v=next.knownFixture.venue||{};
  if(!v.postcode || /TBC/i.test(v.postcode)) throw new Error('DL5 render regression: Emley v Bishop Auckland venue/postcode still TBC');
  console.log('CLUBFINDER RENDER REGRESSION: PASS');
  console.log('DL5 custody:',origin.name,'-> Kendal Town ->',carrier.name);
  console.log('Heaton replay present: PASS');
  console.log('Emley venue:',v.ground,'•',v.postcode);
})().catch(e=>{console.error(e.stack||e);process.exitCode=1});
`;

try{
  vm.runInContext(scripts+'\n'+assertions,sandbox,{filename:'clubfinder.html'});
}catch(e){
  console.error(e.stack||e);
  process.exit(1);
}
