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
const sandbox={console,process,document:documentStub,localStorage:{getItem:k=>localStore[k]??null,setItem:(k,v)=>{localStore[k]=String(v)},removeItem:k=>delete localStore[k]},navigator:{},location:{href:'https://example.test/clubfinder.html'},URL,URLSearchParams,TextEncoder,TextDecoder,setTimeout,clearTimeout,fetch:async(url)=>{const s=String(url);if(s.includes('competition.json'))return {ok:true,json:async()=>competition,text:async()=>JSON.stringify(competition)};throw new Error('Unexpected network request in KT21 venue regression: '+s)}};
sandbox.window=sandbox;sandbox.globalThis=sandbox;vm.createContext(sandbox);
const assertions=`
(async()=>{
  if(typeof refreshCompetitionData==='function') await refreshCompetitionData(false);
  const same=(a,b)=>typeof sameClubIdentity==='function'?sameClubIdentity(a,b):norm(a)===norm(b);
  function verify(originName,custodianName,home,away,postcode){
    const origin=ELIGIBLE.find(c=>same(c.name,originName));
    if(!origin)throw new Error('KT21 venue regression: '+originName+' not found in ELIGIBLE');
    const journey=buildJourney(origin);
    const custodian=journey.carrier||origin;
    if(!same(custodian.name,custodianName))throw new Error('KT21 venue regression: expected '+custodianName+' custodian from '+originName+', got '+custodian.name);
    const next=nextRoundInfo(custodian);
    if(!next||next.name!=='Second Round Qualifying')throw new Error('KT21 venue regression: expected Second Round Qualifying for '+custodianName);
    if(!next.knownFixture)throw new Error('KT21 venue regression: expected published next fixture for '+custodianName);
    const f=next.knownFixture;
    if(!same(f.home,home)||!same(f.away,away))throw new Error('KT21 venue regression: wrong next fixture '+(f.home||'?')+' v '+(f.away||'?'));
    const venue=f.venue||{};
    const pc=String(venue.postcode||'').toUpperCase().replace(/\\s+/g,' ').trim();
    if(pc!==postcode)throw new Error('KT21 venue regression: '+home+' v '+away+' expected '+postcode+', got '+(pc||'TBC'));
    if(!venue.ground||/TBC/i.test(String(venue.ground)))throw new Error('KT21 venue regression: '+home+' v '+away+' ground is TBC');
    if(typeof stateHtml!=='function')throw new Error('KT21 venue regression: stateHtml renderer unavailable');
    const rendered=String(stateHtml(custodian)||'');
    if(!rendered.includes(postcode))throw new Error('KT21 venue regression: rendered Next block drops '+postcode);
    if(/Venue TBC|Postcode TBC/i.test(rendered))throw new Error('KT21 venue regression: rendered Next block still contains venue/postcode TBC for '+custodianName);
    console.log(originName+' -> '+custodianName+': PASS');
    console.log('Next:',f.home,'v',f.away,'•',venue.ground,'•',pc);
  }
  verify('Epsom & Ewell FC','Crowborough Athletic FC','Hampton & Richmond Borough','Crowborough Athletic','TW12 2BX');
  verify('Corinthian Casuals FC','Welling United','Dulwich Hamlet','Welling United','SE22 8BD');
  console.log('KT21 VENUE RENDER REGRESSION: PASS');
})().catch(e=>{console.error(e.stack||e);process.exitCode=1});`;
try{vm.runInContext(scripts+'\n'+assertions,sandbox,{filename:'clubfinder.html'});}catch(e){console.error(e.stack||e);process.exit(1)}
