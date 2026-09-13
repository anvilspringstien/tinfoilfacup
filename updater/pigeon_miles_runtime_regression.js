#!/usr/bin/env node
const fs=require('fs');
const vm=require('vm');
const path=require('path');
const ROOT=path.resolve(__dirname,'..');
const html=fs.readFileSync(path.join(ROOT,'clubfinder.html'),'utf8');
const scripts=[...html.matchAll(/<script[^>]*>([\s\S]*?)<\/script>/gi)].map(m=>m[1]).join('\n');
function nodeStub(){return {value:'',textContent:'',innerHTML:'',style:{},disabled:false,addEventListener(){},focus(){},setAttribute(){},removeAttribute(){},appendChild(){},remove(){},classList:{add(){},remove(){}}}}
const elements=new Proxy({}, {get:(o,k)=>o[k]||(o[k]=nodeStub())});
const coords={
 'AA1 1AA':{latitude:54.9700,longitude:-1.6100},
 'BB1 1BB':{latitude:54.9000,longitude:-1.5000},
 'CC1 1CC':{latitude:55.0500,longitude:-1.7000},
};
const sandbox={console,process,document:{getElementById:id=>elements[id],querySelector:()=>nodeStub(),querySelectorAll:()=>[],createElement:()=>nodeStub(),body:nodeStub()},localStorage:{getItem(){return null},setItem(){},removeItem(){}},navigator:{},location:{href:'https://example.test/'},URL,URLSearchParams,TextEncoder,TextDecoder,setTimeout,clearTimeout,fetch:async(url)=>{
 const s=decodeURIComponent(String(url));
 const pc=Object.keys(coords).find(k=>s.endsWith(k));
 if(pc)return {ok:true,json:async()=>({status:200,result:coords[pc]})};
 if(s.includes('competition.json'))return {ok:true,json:async()=>({}),text:async()=>'{}'};
 return {ok:false,json:async()=>({status:404,result:null})};
}};
sandbox.window=sandbox;sandbox.globalThis=sandbox;vm.createContext(sandbox);
const assertions=`
(async()=>{
 if(typeof tinFoilPigeonMilesForStats!=='function')throw new Error('Pigeon Miles runtime helper missing');
 if(typeof hav!=='function')throw new Error('Haversine helper missing');
 const crumbs=[
  {result:{postcode:'BB1 1BB',decision:''}},
  {result:{postcode:'CC1 1CC',decision:''}},
  {result:{postcode:'ZZ1 1ZZ',decision:'walkover'}}
 ];
 const resolver=r=>({postcode:r.postcode});
 const got=await tinFoilPigeonMilesForStats(crumbs,'AA1 1AA',resolver);
 const start={lat:54.9700,lon:-1.6100},b={lat:54.9000,lon:-1.5000},c={lat:55.0500,lon:-1.7000};
 const expected=2*hav(start,b)+2*hav(start,c);
 if(Math.abs(got.miles-expected)>1e-9)throw new Error('Pigeon Miles total mismatch: '+got.miles+' vs '+expected);
 if(got.display!==String(Math.round(expected)))throw new Error('Pigeon Miles display rounding mismatch');
 if(got.unresolved!==0)throw new Error('Walkover should not create unresolved venue');
 const bad=await tinFoilPigeonMilesForStats([{result:{postcode:'ZZ1 1ZZ',decision:''}}],'AA1 1AA',resolver);
 if(bad.display!=='Awaiting venue location'||bad.miles!==null)throw new Error('Unresolved venue does not fail closed');
 const none=await tinFoilPigeonMilesForStats([],'AA1 1AA',resolver);
 if(none.display!=='0'||none.miles!==0)throw new Error('Zero-tie Pigeon Miles should be zero');
 console.log('PIGEON MILES RUNTIME REGRESSION: PASS');
 console.log('Two played ties use 2 x start-to-venue Haversine each — PASS');
 console.log('Walkover excluded — PASS');
 console.log('Rounding only at display — PASS');
 console.log('Unresolved venue fails closed — PASS');
})().catch(e=>{console.error(e.stack||e);process.exitCode=1});`;
try{vm.runInContext(scripts+'\n'+assertions,sandbox,{filename:'clubfinder.html'});}catch(e){console.error(e.stack||e);process.exit(1)}
