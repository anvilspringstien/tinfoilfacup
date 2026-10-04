#!/usr/bin/env node
const fs=require('fs');
const vm=require('vm');
const path=require('path');

const ROOT=path.resolve(__dirname,'..');
const html=fs.readFileSync(path.join(ROOT,'clubfinder.html'),'utf8');
const competition=JSON.parse(fs.readFileSync(path.join(ROOT,'competition.json'),'utf8'));
const scripts=[...html.matchAll(/<script[^>]*>([\s\S]*?)<\/script>/gi)].map(m=>m[1]).join('\n');
if(!scripts.trim())throw new Error('No inline Clubfinder JavaScript found');

function nodeStub(){return {value:'',textContent:'',innerHTML:'',style:{},disabled:false,children:[],parentElement:null,addEventListener(){},focus(){},setAttribute(){},removeAttribute(){},appendChild(){},remove(){},querySelectorAll(){return []},classList:{add(){},remove(){}}}}
const elements=new Proxy({}, {get:(o,k)=>o[k]||(o[k]=nodeStub())});
const documentStub={readyState:'complete',getElementById(id){return elements[id]},querySelector(){return nodeStub()},querySelectorAll(){return []},createElement(){return nodeStub()},addEventListener(){},body:nodeStub()};

function postcodeFromUrl(url){
  const s=decodeURIComponent(String(url));
  const m=s.match(/\/postcodes\/([^?/#]+)/i);
  return m?String(m[1]).replace(/\s+/g,'').toUpperCase():'';
}
function syntheticPostcodeCoords(pc){
  // Exercise the production postcode-geocoding contract without teaching the
  // regression any particular future postcode.
  const compact=String(pc||'').replace(/\s+/g,'').toUpperCase();
  if(!/^[A-Z]{1,2}\d[A-Z\d]?\d[A-Z]{2}$/.test(compact))return null;
  let hash=2166136261;
  for(const ch of compact){hash^=ch.charCodeAt(0);hash=Math.imul(hash,16777619)>>>0;}
  return {latitude:49.8+(hash%9000)/10000,longitude:-7.5+((hash>>>12)%9000)/1000};
}
const sandbox={
  console,process,document:documentStub,MutationObserver:undefined,
  syntheticPostcodeCoords,
  localStorage:{getItem(){return null},setItem(){},removeItem(){}},
  navigator:{},location:{href:'https://example.test/clubfinder.html'},
  URL,URLSearchParams,TextEncoder,TextDecoder,setTimeout,clearTimeout,
  open:()=>({document:{open(){},write(){},writeln(){},close(){},body:{innerHTML:''},documentElement:{innerHTML:''}},focus(){},print(){},close(){}}),
  fetch:async(url)=>{
    const s=String(url);
    if(s.includes('competition.json'))return {ok:true,json:async()=>JSON.parse(JSON.stringify(competition)),text:async()=>JSON.stringify(competition)};
    if(/postcodes\//i.test(s)){
      const hit=syntheticPostcodeCoords(postcodeFromUrl(s));
      return hit?{ok:true,json:async()=>({status:200,result:hit})}:{ok:false,json:async()=>({status:404,result:null})};
    }
    throw new Error('Unexpected network request: '+s);
  }
};
sandbox.window=sandbox;sandbox.globalThis=sandbox;vm.createContext(sandbox);

const assertions=`
(async()=>{
  if(typeof completedResultVenue!=='function')throw new Error('completedResultVenue missing');
  if(typeof tinFoilPigeonMilesForStats!=='function')throw new Error('tinFoilPigeonMilesForStats missing');
  if(typeof hav!=='function')throw new Error('production hav helper missing');

  const result={
    round:'Fourth Round Qualifying',
    date:'2099-10-10',
    home:'Pigeon Vale',
    away:'Anvil Rovers',
    home_score:3,
    away_score:1,
    winner:'Pigeon Vale',
    status:'FT',
    decision:'',
    venue:{ground:'The Great Deterministic Boundary',postcode:'ZZ1 1ZZ',verification:'verified'}
  };
  const crumbs=[{result}];
  const venue=completedResultVenue(result);
  if(String(venue.ground)!=='The Great Deterministic Boundary'||String(venue.postcode).replace(/\\s+/g,'').toUpperCase()!=='ZZ11ZZ'){
    throw new Error('unfamiliar canonical result.venue was not preserved: '+JSON.stringify(venue));
  }

  const startPostcode='YY1 1YY';
  const stats=await tinFoilPigeonMilesForStats(crumbs,startPostcode,completedResultVenue);
  if(stats.miles===null||stats.unresolved!==0)throw new Error('unfamiliar postcode mileage did not resolve: '+JSON.stringify(stats));

  const startRaw=syntheticPostcodeCoords(startPostcode);
  const venueRaw=syntheticPostcodeCoords(result.venue.postcode);
  const expected=2*hav({lat:startRaw.latitude,lon:startRaw.longitude},{lat:venueRaw.latitude,lon:venueRaw.longitude});
  if(Math.abs(Number(stats.miles)-expected)>1e-9)throw new Error('Pigeon Miles formula mismatch: expected '+expected+', got '+stats.miles);
  if(stats.display!==String(Math.round(expected)))throw new Error('Pigeon Miles display mismatch: '+JSON.stringify(stats));

  console.log('FUTURE ROUND STATS + PIGEON MILES TRUTH: PASS');
  console.log('Unknown ground/postcode consumed from canonical result.venue: PASS');
  console.log('Generic postcode geocoding contract: PASS');
  console.log('Production round-trip formula 2 x hav(start, venue): PASS');
  console.log('Pigeon Miles:',stats.display);
})().catch(e=>{console.error('FUTURE ROUND STATS TRUTH ERROR:',e&&e.message?e.message:String(e));process.exitCode=1});
`;

try{vm.runInContext(scripts+'\n'+assertions,sandbox,{filename:'clubfinder-future-round-stats.html'});}catch(e){console.error(e.stack||e);process.exit(1)}
