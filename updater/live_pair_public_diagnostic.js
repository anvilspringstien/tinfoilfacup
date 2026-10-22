#!/usr/bin/env node
// Read-only: check exact public GitHub Pages assets against repository test data.
const fs=require('fs'),vm=require('vm');
const base='https://anvilspringstien.github.io/tinfoilfacup/';
async function get(path){
  const url=base+path;
  const response=await fetch(url,{headers:{'Cache-Control':'no-cache'}});
  console.log('PUBLIC ASSET:',url,'HTTP',response.status,'last-modified',response.headers.get('last-modified'));
  if(!response.ok)throw new Error(url+' HTTP '+response.status);
  return response.text();
}
const simple=x=>({date:x?.date,home:x?.home,away:x?.away,round:x?.round,
  home_score:x?.home_score,away_score:x?.away_score,winner:x?.winner,decision:x?.decision});
function report(data,label){
  const results=Object.entries(data.results||{}).filter(([k])=>/^(wimborne town|crowborough athletic|hampton & richmond borough|weston-super-mare)( fc| afc)?$/i.test(k));
  console.log(label+' KEY RESULTS:',JSON.stringify(results.map(([k,v])=>[k,simple(v)])));
  const hist=Object.entries(data.result_history||{}).filter(([k])=>/^(wimborne town|crowborough athletic)( fc| afc)?$/i.test(k));
  console.log(label+' KEY HISTORY:',JSON.stringify(hist.map(([k,v])=>[k,Array.isArray(v)?v.length:typeof v,Array.isArray(v)?simple(v[v.length-1]):null])));
  const fixtures=Object.entries(data.fixtures||{}).filter(([k])=>/wimborne|crowborough|hampton/i.test(k));
  console.log(label+' KEY FIXTURES:',JSON.stringify(fixtures.slice(0,10)));
}
(async()=>{
  const [html,jstr]=await Promise.all([get('clubfinder.html'),get('competition.json')]);
  const data=JSON.parse(jstr),repo=JSON.parse(fs.readFileSync('competition.json','utf8'));
  report(repo,'REPO');report(data,'PUBLIC');
  for(const [needle,description] of [
    ['function verifiedConditionalWinner(','winner function'],
    ['const buckets=[...Object.values(rows),Object.values(data.results||{})]','winner fallback'],
    ["const progressionRound=String(current||'').replace(/\\s+Replay$/i,'');",'replay progression'],
    ['function nextRoundInfo(','next round']
  ])console.log('PUBLIC CODE:',description,html.includes(needle));
  for(const needle of ['LIVE_COMPETITION_DATA=','LIVE_COMPETITION_DATA =','function liveLookup(','function resultFor(','competition.json','function updateLiveData']){
    let at=0,c=0;const samples=[];
    while((at=html.indexOf(needle,at))>=0){c++;if(samples.length<4)samples.push(html.slice(Math.max(0,at-170),at+240).replace(/\s+/g,' '));at+=needle.length;}
    console.log('PUBLIC LOAD SITE:',needle,c,JSON.stringify(samples));
  }
  function extract(name){
    const start=html.indexOf('function '+name+'(');
    if(start<0)throw Error('missing '+name);
    const brace=html.indexOf('{',start);let depth=0,end=brace;
    for(;end<html.length;end++){if(html[end]==='{')depth++;if(html[end]==='}'&&!--depth){end++;break;}}
    return html.slice(start,end);
  }
  const names=['canonicalClubKey','sameClubIdentity','canonicalResultWinner','drawAlternatives',
    'resolveConditionalSide','verifiedConditionalWinner','resolveLiveFixtureForCarrier','nextRoundInfo'];
  const context={LIVE_COMPETITION_DATA:data,
    ROUND_META:{'Third Round Qualifying':{date:'2026-10-03',drawDate:'2026-09-21'}},
    FA_FIXTURES_URL:'https://www.thefa.com/competitions/thefacup/fixtures',
    resultFor:club=>context.LIVE_COMPETITION_DATA.results?.[club.name]||context.LIVE_COMPETITION_DATA.results?.[club.name.replace(/\s+FC$/,'')]||null,
    liveLookup:(section,name)=>context.LIVE_COMPETITION_DATA[section]?.[name]||context.LIVE_COMPETITION_DATA[section]?.[name.replace(/\s+FC$/,'')]||null,
    VERIFIED_MATCH_VENUE_OVERRIDES:{},candidateClubByName:()=>null,
    groundByClubName:n=>({'crowborough athletic':{ground:'Charles Century Community Stadium',postcode:'TN6 3BU'}}[String(n).toLowerCase().replace(/\s+fc$/,'')]||{}),
    esc:x=>String(x)};
  vm.createContext(context);vm.runInContext(names.map(extract).join('\n'),context);
  for(const [name,entry_round] of [['Crowborough Athletic FC','Second Round Qualifying'],['Wimborne Town FC','First Round Qualifying']]){
    console.log('PUBLIC NEXT:',name,JSON.stringify(context.nextRoundInfo({name,entry_round,fixture:{}})));
  }
})().catch(err=>{console.log('PUBLIC ASSET DIAGNOSTIC UNAVAILABLE:',err.stack);process.exitCode=0;});
