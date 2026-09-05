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
const fetchCalls=[];
const sandbox={console,process,document:documentStub,MutationObserver:undefined,localStorage:{getItem(){return null},setItem(){},removeItem(){}},navigator:{},location:{href:'https://example.test/clubfinder.html'},URL,URLSearchParams,TextEncoder,TextDecoder,setTimeout,clearTimeout,fetchCalls,fetch:async(url,opts={})=>{fetchCalls.push({url:String(url),opts});if(String(url).includes('competition.json'))return {ok:true,json:async()=>competition,text:async()=>JSON.stringify(competition)};throw new Error('Unexpected network request: '+url)}};
sandbox.window=sandbox;sandbox.globalThis=sandbox;vm.createContext(sandbox);
const assertions=`
(async()=>{
  if(typeof refreshCompetitionData!=='function')throw new Error('refreshCompetitionData missing');
  await refreshCompetitionData(false);
  const liveFetch=fetchCalls.find(x=>x.url.includes('competition.json'));
  if(!liveFetch)throw new Error('No live competition fetch observed');
  if(!/[?&]t=\\d+/.test(liveFetch.url))throw new Error('Live competition fetch is not cache-busted: '+liveFetch.url);
  if(!liveFetch.opts||liveFetch.opts.cache!=='no-store')throw new Error('Live competition fetch does not use no-store');

  const same=(a,b)=>typeof sameClubIdentity==='function'?sameClubIdentity(a,b):norm(a)===norm(b);
  let checked=0,totalBreadcrumbs=0;
  for(const origin of ELIGIBLE){
    const j=buildJourney(origin);
    let custodian=origin.name;
    for(const item of (j.breadcrumbs||[])){
      const r=item.result||{};
      const participates=same(r.home,custodian)||same(r.away,custodian);
      if(!participates)throw new Error('Previous Rounds contamination for '+origin.name+': '+custodian+' did not participate in '+r.home+' v '+r.away+' ('+(r.round||'unknown round')+')');
      totalBreadcrumbs++;
      const winner=canonicalResultWinner(r);
      if(winner&&!resultNeedsReplay(r))custodian=winner;
    }
    if(!same((j.carrier||origin).name,custodian))throw new Error('Journey carrier mismatch for '+origin.name+': breadcrumbs end at '+custodian+' but buildJourney returned '+(j.carrier||origin).name);
    checked++;
  }
  console.log('JOURNEY INTEGRITY REGRESSION: PASS');
  console.log('Selectable origins checked:',checked);
  console.log('Custody-chain breadcrumbs checked:',totalBreadcrumbs);
  console.log('Live competition cache-busting: PASS');
})().catch(e=>{console.error(e.stack||e);process.exitCode=1});`;
try{vm.runInContext(scripts+'\n'+assertions,sandbox,{filename:'clubfinder.html'});}catch(e){console.error(e.stack||e);process.exit(1)}
