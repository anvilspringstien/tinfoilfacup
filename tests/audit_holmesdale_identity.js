#!/usr/bin/env node
// Read-only live-data identity diagnostic; deliberately changes no Clubfinder files.
'use strict';
const fs=require('node:fs'),vm=require('node:vm');
const competition=JSON.parse(fs.readFileSync('competition.json','utf8'));
const both={production:'clubfinder.html',beta:'beta/clubfinder-beta.html'};
const hit=s=>/holmesdale|petts wood/i.test(String(s||''));
const brief=r=>r?{round:r.round,date:r.date,home:r.home,away:r.away,home_score:r.home_score,away_score:r.away_score,winner:r.winner,venue:r.venue}:null;
const results=Object.entries(competition.results||{}).filter(([k,v])=>hit(k)||hit(v.home)||hit(v.away));
const history=Object.entries(competition.result_history||{}).filter(([k,rows])=>hit(k)||(rows||[]).some(r=>hit(r.home)||hit(r.away)));
const fixtures=Object.entries(competition.fixtures||{}).filter(([k,v])=>hit(k)||hit(v.home)||hit(v.away));
console.log('CANONICAL '+JSON.stringify({updated_at:competition.updated_at,
  resultKeys:results.map(([key,r])=>({key,...brief(r)})),
  historyKeys:history.map(([key,rows])=>({key,rows:(rows||[]).filter(r=>hit(r.home)||hit(r.away)).map(brief)})),
  fixtureKeys:fixtures.map(([key,r])=>({key,round:r.round,date:r.date,home:r.home,away:r.away}))}));
const makeNode=()=>({value:'',textContent:'',innerHTML:'',hidden:false,style:{},dataset:{},children:[],
  addEventListener(){},removeEventListener(){},focus(){},setAttribute(){},removeAttribute(){},
  appendChild(){},remove(){},insertAdjacentElement(){},querySelectorAll(){return []},
  classList:{add(){},remove(){}}});
function harness(label,path){
  const html=fs.readFileSync(path,'utf8');
  const scripts=[...html.matchAll(/<script[^>]*>([\s\S]*?)<\/script>/gi)].map(m=>m[1]).join('\n');
  const elements=new Proxy({}, {get:(o,k)=>o[k]||(o[k]=makeNode())});
  const document={readyState:'complete',activeElement:null,getElementById:id=>elements[id],
    querySelector:()=>makeNode(),querySelectorAll:()=>[],createElement:()=>makeNode(),
    addEventListener(){},removeEventListener(){},body:makeNode()};
  const local={},session={};
  const store=o=>({getItem:k=>o[k]??null,setItem:(k,v)=>o[k]=String(v),removeItem:k=>delete o[k]});
  const ctx={console,process,document,navigator:{},localStorage:store(local),sessionStorage:store(session),
    MutationObserver:undefined,URL,URLSearchParams,TextEncoder,TextDecoder,setTimeout,clearTimeout,
    location:{href:label==='beta'?'https://example.test/beta/clubfinder-beta.html':'https://example.test/clubfinder.html',replace(v){this.href=v}},
    open:()=>({document:{open(){},write(){},close(){},body:{innerHTML:''},documentElement:{innerHTML:''}},focus(){},print(){},close(){}}),
    fetch:async url=>{
      const s=String(url);
      if(s.includes('competition.json'))return {ok:true,status:200,json:async()=>JSON.parse(JSON.stringify(competition)),text:async()=>JSON.stringify(competition)};
      if(s.includes('counter-config.json'))return {ok:true,status:200,json:async()=>({increment_url:'https://counter.invalid/increment'})};
      throw Error('Unexpected fetch during '+label+' identity diagnostic: '+s);
    }};
  ctx.window=ctx;ctx.globalThis=ctx;
  vm.createContext(ctx);
  vm.runInContext(scripts,ctx,{filename:path,timeout:25000});
  return {ctx,probe:(expression)=>vm.runInContext(expression,ctx,{timeout:25000})};
}
(async()=>{
  for(const [label,path] of Object.entries(both)){
    const m=harness(label,path);
    await m.probe("typeof refreshCompetitionData==='function'?refreshCompetitionData(false):Promise.resolve()");
    const data=m.probe('('+function(){
      const origins=ELIGIBLE.filter(c=>/holmesdale/i.test(c.name));
      const compactResult=x=>x?{round:x.round,date:x.date,home:x.home,away:x.away,home_score:x.home_score,away_score:x.away_score,winner:x.winner}:null;
      const each=origins.map(o=>{
        const r=resultFor(o),j=buildJourney(o),custodian=j.carrier||o;
        const n=nextRoundInfo(custodian),f=currentDisplayFixture(o);
        return {eligibleName:o.name,entry:o.entry_round,canonical:canonicalClubKey(o.name),
          sameAs2026Name:sameClubIdentity(o.name,'Petts Wood & Holmesdale'),
          directResult:compactResult(liveLookup('results',o.name)),
          resultFor:compactResult(r),
          campaign:{custodian:custodian.name,history:(j.breadcrumbs||[]).map(x=>compactResult(x.result)),
            next:n?{name:n.name,fixture:n.knownFixture?{home:n.knownFixture.home,away:n.knownFixture.away,date:n.knownFixture.date}:null}:null,
            display:f?{tie:f.tie,round:f.round,completed:f.completed}:null}};
      });
      return {rawIdentity:sameClubIdentity('Holmesdale FC','Petts Wood & Holmesdale'),origins:each};
    }.toString()+')()');
    console.log('RUNTIME_'+label.toUpperCase()+' '+JSON.stringify(data));
  }
})().catch(e=>{console.error('HOLMESDALE_DIAGNOSTIC_ERROR',e.stack||e);process.exitCode=1});
