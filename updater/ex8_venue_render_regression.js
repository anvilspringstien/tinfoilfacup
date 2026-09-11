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
const sandbox={console,process,document:documentStub,localStorage:{getItem:k=>localStore[k]??null,setItem:(k,v)=>{localStore[k]=String(v)},removeItem:k=>delete localStore[k]},navigator:{},location:{href:'https://example.test/clubfinder.html'},URL,URLSearchParams,TextEncoder,TextDecoder,setTimeout,clearTimeout,fetch:async(url)=>{const s=String(url);if(s.includes('competition.json'))return {ok:true,json:async()=>competition,text:async()=>JSON.stringify(competition)};throw new Error('Unexpected network request in EX8 venue regression: '+s)}};
sandbox.window=sandbox;sandbox.globalThis=sandbox;vm.createContext(sandbox);
const assertions=`
(async()=>{
  if(typeof refreshCompetitionData==='function') await refreshCompetitionData(false);
  const same=(a,b)=>typeof sameClubIdentity==='function'?sameClubIdentity(a,b):norm(a)===norm(b);
  const sidmouth=ELIGIBLE.find(c=>same(c.name,'Sidmouth Town FC'));
  if(!sidmouth)throw new Error('EX8 venue regression: Sidmouth Town FC not found in ELIGIBLE');
  const journey=buildJourney(sidmouth);
  const custodian=journey.carrier||sidmouth;
  if(!same(custodian.name,'Frome Town'))throw new Error('EX8 venue regression: expected Frome Town custodian, got '+custodian.name);
  const next=nextRoundInfo(custodian);
  if(!next||next.name!=='Second Round Qualifying')throw new Error('EX8 venue regression: expected Second Round Qualifying next round');
  if(!next.knownFixture)throw new Error('EX8 venue regression: expected published Frome Town v Plymouth Parkway fixture');
  const f=next.knownFixture;
  if(!same(f.home,'Frome Town')||!same(f.away,'Plymouth Parkway'))throw new Error('EX8 venue regression: wrong next fixture '+(f.home||'?')+' v '+(f.away||'?'));
  const venue=f.venue||{};
  const postcode=String(venue.postcode||'').toUpperCase().replace(/\\s+/g,' ').trim();
  if(postcode!=='BA11 2EH')throw new Error('EX8 venue regression: Frome Town v Plymouth Parkway rendered fixture postcode expected BA11 2EH, got '+(postcode||'TBC'));
  if(!venue.ground||/TBC/i.test(String(venue.ground)))throw new Error('EX8 venue regression: Frome Town v Plymouth Parkway rendered fixture ground is TBC');
  console.log('EX8 VENUE RENDER REGRESSION: PASS');
  console.log('Sidmouth Town -> Frome Town custody: PASS');
  console.log('Next:',f.home,'v',f.away,'•',venue.ground,'•',postcode);
})().catch(e=>{console.error(e.stack||e);process.exitCode=1});`;
try{vm.runInContext(scripts+'\n'+assertions,sandbox,{filename:'clubfinder.html'});}catch(e){console.error(e.stack||e);process.exit(1)}
