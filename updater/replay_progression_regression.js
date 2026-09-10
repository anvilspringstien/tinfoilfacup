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
const sandbox={console,process,document:documentStub,MutationObserver:undefined,localStorage:{getItem(){return null},setItem(){},removeItem(){}},navigator:{},location:{href:'https://example.test/clubfinder.html'},URL,URLSearchParams,TextEncoder,TextDecoder,setTimeout,clearTimeout,fetch:async(url)=>{if(String(url).includes('competition.json'))return {ok:true,json:async()=>competition,text:async()=>JSON.stringify(competition)};throw new Error('Unexpected network request: '+url)}};
sandbox.window=sandbox;sandbox.globalThis=sandbox;vm.createContext(sandbox);
const assertions=`
(async()=>{
  if(typeof refreshCompetitionData==='function')await refreshCompetitionData(false);
  const same=(a,b)=>typeof sameClubIdentity==='function'?sameClubIdentity(a,b):norm(a)===norm(b);
  const clubFor=name=>ELIGIBLE.find(c=>same(c.name,name))||(typeof candidateClubByName==='function'?candidateClubByName(name):null)||{name,entry_round:'',fixture:{}};
  const assertSecondQ=(name,label)=>{
    const club=clubFor(name);
    const r=resultFor(club);
    if(!r||!/First Round Qualifying Replay$/i.test(String(r.round||'')))throw new Error(label+': expected latest result to be First Round Qualifying Replay, got '+((r&&r.round)||'NONE'));
    const next=nextRoundInfo(club);
    if(!next||next.name!=='Second Round Qualifying')throw new Error(label+': replay did not progress to Second Round Qualifying; got '+((next&&next.name)||'NONE'));
    if(!next.knownFixture)throw new Error(label+': published Second Round Qualifying fixture was not resolved');
    const f=next.knownFixture;
    if(!/Second Round Qualifying/i.test(String(f.round||'')))throw new Error(label+': resolved fixture has wrong round '+(f.round||'NONE'));
    if(!same(f.home,club.name)&&!same(f.away,club.name))throw new Error(label+': resolved fixture does not contain '+club.name+' ('+(f.home||'?')+' v '+(f.away||'?')+')');
    return f;
  };

  const exmouth=assertSecondQ('Exmouth Town','Exmouth replay');
  const emley=assertSecondQ('Emley AFC','Emley replay');
  const crowborough=assertSecondQ('Crowborough Athletic','Crowborough replay');

  const frome=clubFor('Frome Town');
  const fromeNext=nextRoundInfo(frome);
  if(!fromeNext||fromeNext.name!=='Second Round Qualifying'||!fromeNext.knownFixture)throw new Error('Non-replay control: Frome Town next-round behaviour regressed');

  console.log('REPLAY PROGRESSION REGRESSION: PASS');
  console.log('Exmouth ->',exmouth.home,'v',exmouth.away);
  console.log('Emley ->',emley.home,'v',emley.away);
  console.log('Crowborough ->',crowborough.home,'v',crowborough.away);
  console.log('Non-replay control Frome Town: PASS');
})().catch(e=>{console.error(e.stack||e);process.exitCode=1});`;
try{vm.runInContext(scripts+'\n'+assertions,sandbox,{filename:'clubfinder.html'});}catch(e){console.error(e.stack||e);process.exit(1)}
