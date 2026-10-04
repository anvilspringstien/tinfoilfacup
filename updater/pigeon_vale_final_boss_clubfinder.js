#!/usr/bin/env node
const fs=require('fs'),vm=require('vm'),path=require('path');
const ROOT=path.resolve(__dirname,'..'), candidate=JSON.parse(fs.readFileSync(path.join(__dirname,'pigeon-vale-catastrophe-candidate.json'),'utf8'));
const html=fs.readFileSync(path.join(ROOT,'clubfinder.html'),'utf8');
const scripts=[...html.matchAll(/<script[^>]*>([\s\S]*?)<\/script>/gi)].map(m=>m[1]).join('\n');
function stub(){return {value:'',textContent:'',innerHTML:'',style:{},disabled:false,children:[],parentElement:null,addEventListener(){},focus(){},setAttribute(){},removeAttribute(){},appendChild(){},remove(){},querySelectorAll(){return []},classList:{add(){},remove(){}}}}
const elements=new Proxy({}, {get:(o,k)=>o[k]||(o[k]=stub())}), documentStub={readyState:'complete',getElementById(id){return elements[id]},querySelector(){return stub()},querySelectorAll(){return []},createElement(){return stub()},addEventListener(){},body:stub()};
function pcFromUrl(url){const m=decodeURIComponent(String(url)).match(/\/postcodes\/([^?/#]+)/i);return m?m[1].replace(/\s+/g,'').toUpperCase():''}
function syntheticPostcodeCoords(pc){const compact=String(pc||'').replace(/\s+/g,'').toUpperCase();if(!/^[A-Z]{1,2}\d[A-Z\d]?\d[A-Z]{2}$/.test(compact))return null;let h=2166136261;for(const ch of compact){h^=ch.charCodeAt(0);h=Math.imul(h,16777619)>>>0;}return {latitude:49.8+(h%9000)/10000,longitude:-7.5+((h>>>12)%9000)/1000}}
const sandbox={console,process,document:documentStub,MutationObserver:undefined,syntheticPostcodeCoords,localStorage:{getItem(){return null},setItem(){},removeItem(){}},navigator:{},location:{href:'https://example.test/clubfinder.html'},URL,URLSearchParams,TextEncoder,TextDecoder,setTimeout,clearTimeout,open:()=>null,fetch:async(url)=>{if(/postcodes\//i.test(String(url))){const hit=syntheticPostcodeCoords(pcFromUrl(url));return {ok:!!hit,json:async()=>({status:hit?200:404,result:hit})}};return {ok:true,json:async()=>candidate,text:async()=>JSON.stringify(candidate)}}};
sandbox.window=sandbox;sandbox.globalThis=sandbox;vm.createContext(sandbox);
const assertions=`
(async()=>{
 LIVE_COMPETITION_DATA=${JSON.stringify(candidate)};
 const origin={name:'Pigeon Vale',entry_round:'Fourth Round Qualifying',fixture:{}},j=buildJourney(origin);
 if(!sameClubIdentity(j.carrier.name,'Deterministic United'))throw new Error('custody did not derive from candidate');
 if((j.breadcrumbs||[]).some(x=>String(x.result.status).toUpperCase()==='VOID'))throw new Error('VOID gained competitive authority');
 const travel=tinFoilPlayedTravelHistory(origin);
 if(travel.length!==2||!travel.some(x=>String(x.result.status).toUpperCase()==='VOID'))throw new Error('played VOID trip not preserved');
 const miles=await tinFoilPigeonMilesForStats(travel,'WW1 1WW',completedResultVenue);
 if(miles.miles===null||miles.unresolved!==0)throw new Error('Catastrophe mileage unresolved');
 const next=Object.values(LIVE_COMPETITION_DATA.fixtures||{}).find(f=>sameClubIdentity(f.home,j.carrier.name)||sameClubIdentity(f.away,j.carrier.name));
 if(!next||next.venue.postcode!=='XX1 1XX')throw new Error('unfamiliar next fixture not reachable from derived custodian');
 console.log('FINAL BOSS STAGE 2 — REAL CLUBFINDER CUSTODY + TRAVEL + MILEAGE + NEXT FIXTURE: PASS');
})().catch(e=>{console.error('FINAL BOSS:',e.message);process.exitCode=1});
`;
vm.runInContext(scripts+'\n'+assertions,sandbox,{filename:'pigeon-vale-final-boss.html'});
