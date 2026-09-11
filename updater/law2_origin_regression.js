#!/usr/bin/env node
const fs=require('fs');
const vm=require('vm');
const path=require('path');
const ROOT=path.resolve(__dirname,'..');
const html=fs.readFileSync(path.join(ROOT,'clubfinder.html'),'utf8');
const competition=JSON.parse(fs.readFileSync(path.join(ROOT,'competition.json'),'utf8'));
const scripts=[...html.matchAll(/<script[^>]*>([\s\S]*?)<\/script>/gi)].map(m=>m[1]).join('\n');
if(!scripts.trim())throw new Error('No inline Clubfinder JavaScript found');
function nodeStub(){return {value:'',textContent:'',innerHTML:'',style:{},disabled:false,hidden:false,dataset:{},addEventListener(){},focus(){},setAttribute(){},removeAttribute(){},appendChild(){},remove(){},insertAdjacentElement(){},classList:{add(){},remove(){}}}}
const elements=new Proxy({}, {get:(o,k)=>o[k]||(o[k]=nodeStub())});
const documentStub={readyState:'complete',getElementById(id){return elements[id]},querySelector(){return nodeStub()},querySelectorAll(){return []},createElement(){return nodeStub()},addEventListener(){},body:nodeStub()};
const sandbox={console,process,document:documentStub,MutationObserver:undefined,localStorage:{getItem(){return null},setItem(){},removeItem(){}},navigator:{},location:{href:'https://example.test/clubfinder.html'},URL,URLSearchParams,TextEncoder,TextDecoder,setTimeout,clearTimeout,fetch:async(url)=>{if(String(url).includes('competition.json'))return {ok:true,json:async()=>competition,text:async()=>JSON.stringify(competition)};throw new Error('Unexpected network request: '+url)}};
sandbox.window=sandbox;sandbox.globalThis=sandbox;vm.createContext(sandbox);
const assertions=`
(async()=>{
  if(ELIGIBLE.length!==651)throw new Error('Expected 651 Law 2 origins, got '+ELIGIBLE.length);
  const expected={'Extra Preliminary Round':438,'Preliminary Round':53,'First Round Qualifying':88,'Second Round Qualifying':48,'Fourth Round Qualifying':24};
  const counts={}; for(const c of ELIGIBLE)counts[c.entry_round]=(counts[c.entry_round]||0)+1;
  if(JSON.stringify(counts)!==JSON.stringify(expected))throw new Error('Entry-round counts drift: '+JSON.stringify(counts));
  if(ELIGIBLE.some(c=>/Round Proper/.test(c.entry_round||'')))throw new Error('Proper-round entrant present in Law 2 origins');
  if(ELIGIBLE.some(c=>c.entry_round==='Third Round Qualifying'))throw new Error('Unexpected Third Qualifying entrant cohort present');
  const keys=new Set(ELIGIBLE.map(c=>norm(c.name)));
  if(keys.size!==651)throw new Error('Duplicate Law 2 origin identities');
  if(!Array.isArray(LAW2_ORIGIN_LOCATIONS)||!LAW2_ORIGIN_LOCATIONS.length)throw new Error('Supplemental Law 2 locations missing');

  const leather=ELIGIBLE.find(c=>norm(c.name)===norm('Leatherhead FC'));
  if(!leather)throw new Error('Leatherhead FC is not selectable');
  if(leather.entry_round!=='First Round Qualifying')throw new Error('Leatherhead entry round wrong: '+leather.entry_round);
  const lg=findGround(leather);
  if(!lg)throw new Error('Leatherhead location missing');
  if(lg.postcode!=='KT22 9AS')throw new Error('Leatherhead postcode wrong: '+lg.postcode);
  if(!/Fetcham Grove/i.test(lg.ground||''))throw new Error('Leatherhead ground wrong: '+lg.ground);
  if(!Number.isFinite(Number(lg.lat))||!Number.isFinite(Number(lg.lon)))throw new Error('Leatherhead coordinates missing');
  if((lg.verification||'').toLowerCase()==='verified')throw new Error('Supporting Leatherhead evidence was silently promoted to verified');

  const rows=[];
  for(const c of ELIGIBLE){const g=findGround(c);if(!g)throw new Error('No origin location for '+c.name);const ok=Number.isFinite(Number(g.lat))&&Number.isFinite(Number(g.lon));if(!ok)throw new Error('No origin coordinates for '+c.name);rows.push({...c,...g,distance:hav({lat:Number(lg.lat),lon:Number(lg.lon)},{lat:Number(g.lat),lon:Number(g.lon)})})}
  rows.sort((a,b)=>a.distance-b.distance);
  const top=rows.slice(0,3);
  if(top.length!==3)throw new Error('Nearest journey count is not 3');
  if(norm(top[0].name)!==norm('Leatherhead FC'))throw new Error('KT22 9AS canary does not rank Leatherhead first; got '+top[0].name);

  const journey=buildJourney(leather);
  const history=previousRoundsHtml(journey);
  const entryCopy='Leatherhead FC enters the competition at First Round Qualifying.';
  if(!history.includes(entryCopy))throw new Error('Later-entry explanation missing: '+history);
  const early=(journey.breadcrumbs||[]).filter(x=>['Extra Preliminary Round','Preliminary Round'].includes((x.result||{}).round||x.round));
  if(early.length)throw new Error('Leatherhead journey fabricated pre-entry rounds');

  if(!html.includes('const top=rows.slice(0,3);'))throw new Error('Nearest-three source guard missing');
  console.log('LAW 2 ORIGIN REGRESSION: PASS');
  console.log('Selectable origins: 651');
  console.log('Entry cohorts:',JSON.stringify(counts));
  console.log('KT22 9AS -> Leatherhead FC:',lg.ground,'•',lg.postcode);
  console.log('Leatherhead entry explanation: PASS');
  console.log('Nearest journeys returned: 3');
  console.log('Proper-round-only origins excluded: PASS');
})().catch(e=>{console.error(e.stack||e);process.exitCode=1});`;
try{vm.runInContext(scripts+'\n'+assertions,sandbox,{filename:'clubfinder.html'});}catch(e){console.error(e.stack||e);process.exit(1)}
