#!/usr/bin/env node
const fs=require('fs');
const vm=require('vm');
const path=require('path');
const ROOT=path.resolve(__dirname,'..');
const html=fs.readFileSync(path.join(ROOT,'clubfinder.html'),'utf8');
const competition=JSON.parse(fs.readFileSync(path.join(ROOT,'competition.json'),'utf8'));
const scripts=[...html.matchAll(/<script[^>]*>([\s\S]*?)<\/script>/gi)].map(m=>m[1]).join('\n');
function nodeStub(){return {value:'',textContent:'',innerHTML:'',style:{},disabled:false,children:[],parentElement:null,addEventListener(){},focus(){},setAttribute(){},removeAttribute(){},appendChild(){},remove(){},querySelectorAll(){return []},classList:{add(){},remove(){}}}}
const elements=new Proxy({}, {get:(o,k)=>o[k]||(o[k]=nodeStub())});
const documentStub={readyState:'complete',getElementById(id){return elements[id]},querySelector(){return nodeStub()},querySelectorAll(){return []},createElement(){return nodeStub()},addEventListener(){},body:nodeStub()};
const localStore={};
let certificateHtml='';
function popupStub(){
  const doc={
    open(){},
    write(s){certificateHtml+=String(s)},
    writeln(s){certificateHtml+=String(s)+'\n'},
    close(){},
    body:{innerHTML:''},
    documentElement:{innerHTML:''}
  };
  return {document:doc,focus(){},print(){},close(){}};
}
const sandbox={console,process,document:documentStub,localStorage:{getItem:k=>localStore[k]??null,setItem:(k,v)=>{localStore[k]=String(v)},removeItem:k=>delete localStore[k]},navigator:{},location:{href:'https://example.test/clubfinder.html'},URL,URLSearchParams,TextEncoder,TextDecoder,setTimeout,clearTimeout,MutationObserver:undefined,open:()=>popupStub(),fetch:async(url)=>{const s=String(url);if(s.includes('competition.json'))return {ok:true,json:async()=>competition,text:async()=>JSON.stringify(competition)};throw new Error('Unexpected network request: '+s)}};
sandbox.window=sandbox;sandbox.globalThis=sandbox;vm.createContext(sandbox);
const assertions=`
(async()=>{
  if(typeof refreshCompetitionData==='function') await refreshCompetitionData(false);
  const same=(a,b)=>typeof sameClubIdentity==='function'?sameClubIdentity(a,b):String(a||'')===String(b||'');
  if(typeof tinFoilCertificateWinner!=='function')throw new Error('DL5 Stats regression: certificate winner helper missing');
  if(!String(${JSON.stringify(html)}).includes("certEsc(tinFoilCertificateWinner(r))"))throw new Error('DL5 Stats regression: certificate renderer is not using canonical winner helper');
  if(String(${JSON.stringify(html)}).includes("certEsc(r.winner||'')"))throw new Error('DL5 Stats regression: stale r.winner certificate renderer still present');

  const origin=ELIGIBLE.find(c=>same(c.name,'Newton Aycliffe FC'));
  if(!origin)throw new Error('DL5 Stats regression: Newton Aycliffe FC origin missing');
  const j=buildJourney(origin),carrier=j.carrier||origin,history=(j.breadcrumbs||[]).map(x=>x.result||{});
  const first=history.find(r=>same(r.home,'Newton Aycliffe')&&same(r.away,'Kendal Town')&&Number(r.home_score)===0&&Number(r.away_score)===1);
  if(!first)throw new Error('DL5 Stats regression: Newton Aycliffe 0-1 Kendal missing');
  if(!same(tinFoilCertificateWinner(first),'Kendal Town'))throw new Error('DL5 Stats regression: certificate helper must return Kendal Town');
  if(typeof canonicalResultWinner!=='function'||!same(canonicalResultWinner(first),'Kendal Town'))throw new Error('DL5 Stats regression: canonical first custody transfer is not Kendal Town');

  const draw=history.find(r=>same(r.home,'Kendal Town')&&same(r.away,'Heaton Stannington')&&Number(r.home_score)===2&&Number(r.away_score)===2);
  if(!draw)throw new Error('DL5 Stats regression: Kendal 2-2 Heaton draw missing');
  if(tinFoilCertificateWinner(draw)!=='')throw new Error('DL5 Stats regression: drawn certificate row must remain unresolved');

  const replay=history.find(r=>same(r.home,'Heaton Stannington')&&same(r.away,'Kendal Town')&&Number(r.home_score)===4&&Number(r.away_score)===2);
  if(!replay||!same(tinFoilCertificateWinner(replay),'Heaton Stannington'))throw new Error('DL5 Stats regression: replay certificate winner mismatch');

  if(!same(carrier.name,'Heaton Stannington'))throw new Error('DL5 Stats regression: expected current custodian Heaton Stannington, got '+carrier.name);
  const next=nextRoundInfo(carrier);
  if(!next||!next.knownFixture||!same(next.knownFixture.home,'Heaton Stannington')||!same(next.knownFixture.away,'Trafford'))throw new Error('DL5 Stats regression: expected Heaton Stannington v Trafford next');

  if(typeof journeyCertificate!=='function')throw new Error('DL5 Stats regression: journeyCertificate renderer missing');
  certificateHtml='';
  const returned=journeyCertificate(origin);
  if(typeof returned==='string'&&returned.includes('THE JOURNEY SO FAR'))certificateHtml=returned;
  if(!certificateHtml){
    const p=window.open();
    if(p&&p.document){
      certificateHtml=p.document.documentElement&&p.document.documentElement.innerHTML||p.document.body&&p.document.body.innerHTML||'';
    }
  }
  if(certificateHtml){
    const fixture='Newton Aycliffe (0) v (1) Kendal Town';
    const idx=certificateHtml.indexOf(fixture);
    if(idx<0)throw new Error('DL5 Stats regression: actual certificate missing Extra Preliminary fixture');
    const chunk=certificateHtml.slice(idx,idx+1400);
    if(!/jr-winner[^>]*>\s*Kendal Town\s*</i.test(chunk))throw new Error('DL5 Stats regression: actual certificate Extra Preliminary row does not render Kendal Town');
    if(/jr-winner[^>]*>\s*Newton Aycliffe FC\s*</i.test(chunk))throw new Error('DL5 Stats regression: actual certificate still renders Newton Aycliffe FC as winner');
  }

  console.log('CLUBFINDER STATS CERTIFICATE REGRESSION: PASS');
  console.log('Canonical postcode: DL5 4RQ');
  console.log('Certificate source uses decisive-score winner helper — PASS');
  console.log('Extra Preliminary: Newton Aycliffe 0-1 Kendal Town -> Kendal Town — PASS');
  console.log('Draw remains unresolved — PASS');
  console.log('Replay -> Heaton Stannington — PASS');
  console.log('Custody: Newton Aycliffe FC -> Kendal Town -> Heaton Stannington');
  console.log('Next: Heaton Stannington v Trafford — PASS');
})().catch(e=>{console.error(e.stack||e);process.exitCode=1});`;
try{vm.runInContext(scripts+'\n'+assertions,sandbox,{filename:'clubfinder.html'});}catch(e){console.error(e.stack||e);process.exit(1)}
