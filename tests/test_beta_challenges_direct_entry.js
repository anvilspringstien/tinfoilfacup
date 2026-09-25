#!/usr/bin/env node
'use strict';
// BETA-only navigation regression. Exercise the full standalone Deck script,
// including preserved browser storage and the legacy return-from-Stats URL.
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const html=fs.readFileSync('beta/challenges-beta.html','utf8');

for(const id of ['openDeck','maybeLater','deckStatsBtn','statsOpenDeck','statsCompleted','statsAvailable','statsJourney']){
  assert(!new RegExp('id=["\\x27]'+id+'["\\x27]').test(html),id+' must not remain in Challenges UI');
}
assert(!/<section[^>]*class="hero beta-splash"/.test(html),'Splash remains in the page');
assert(!/<section[^>]*class="stats"/.test(html),'Detached Challenge Stats remains');
assert(/id="deckCabinet"/.test(html),'Trophy Cabinet must be retained');
assert(/id="exitBtn"/.test(html),'Explicit Exit button must be retained');

const scripts=[...html.matchAll(/<script[^>]*>([\s\S]*?)<\/script>/gi)].map(m=>m[1]).join('\n');
assert(scripts.length>20000,'Standalone Challenge Deck script missing');
new vm.Script(scripts,{filename:'beta/challenges-beta.html'});

function stub(){
  const flags=new Set(),node={
    style:{},dataset:{},children:[],textContent:'',innerHTML:'',value:'0',selectedIndex:0,disabled:false,
    options:['Extra Preliminary Round','Preliminary Round','1st Qualifying Round','2nd Qualifying Round','3rd Qualifying Round','4th Qualifying Round','First Round Proper','Second Round Proper','Third Round Proper','Fourth Round Proper','Fifth Round Proper','Quarter Finals','Semi Finals','Final'].map(text=>({textContent:text,text})),
    classList:{add(k){flags.add(k)},remove(k){flags.delete(k)},contains(k){return flags.has(k)},toggle(k,on){if(on===undefined)on=!flags.has(k);if(on)flags.add(k);else flags.delete(k);return on}},
    setAttribute(){},removeAttribute(){},remove(){},focus(){},addEventListener(){},
    querySelector(){return null},querySelectorAll(){return []},appendChild(child){this.children.push(child);return child},
    append(...children){this.children.push(...children)},replaceChildren(...children){this.children=children}
  };
  return node;
}
function boot(search,local,session){
  const nodes=new Proxy({}, {get(o,k){return o[k]||(o[k]=stub())}});
  const listeners={};
  const document={
    body:stub(),activeElement:null,readyState:'complete',
    getElementById:id=>nodes[id],createElement:()=>stub(),querySelector:()=>null,querySelectorAll:()=>[],
    addEventListener(name,fn){(listeners[name]||=[]).push(fn)},removeEventListener(){}
  };
  const store=data=>({
    getItem:k=>Object.hasOwn(data,k)?data[k]:null,
    setItem(k,v){data[k]=String(v)},removeItem(k){delete data[k]}
  });
  const location={href:'https://example.test/beta/challenges-beta.html'+search,search,pathname:'/beta/challenges-beta.html',hash:'',
    replace(path){this.href=path}};
  const ctx={
    console,document,navigator:{},location,history:{replaceState(){location.search=''}},
    localStorage:store(local),sessionStorage:store(session),
    URL,URLSearchParams,requestAnimationFrame:fn=>fn(),setTimeout:()=>0,clearTimeout(){},
    Image:class{set src(path){this._src=path}},MutationObserver:undefined
  };
  ctx.window=ctx;ctx.globalThis=ctx;
  vm.createContext(ctx);
  vm.runInContext(scripts,ctx,{filename:'beta/challenges-beta.html',timeout:25000});
  return {ctx,nodes,location,listeners};
}
const local={
  'tffc.challengeDeck.v1':JSON.stringify({
    version:1,accepted:{'01':true},completed:{'01':true},records:{},
    tiesPlayed:2,awayTies:1,pigeonMiles:40,campaignRound:0,
    giantKillAchieved:false,campaignStatus:'ACTIVE'
  }),
  'tffc.clubfinderCampaign.v1':JSON.stringify({
    source:'Clubfinder v7.6',originName:'Amersham Town FC',selectedAt:'2026-09-25T09:00:00.000Z',
    callSign:'Tango Foxtrot 2 Alpha Charlie 01123',tiesPlayed:5,awayTies:2,pigeonMiles:314,campaignRound:4
  }),
  'tffc.clubfinderCampaignIdentity.v1':JSON.stringify({
    originName:'Amersham Town FC',selectedAt:'2026-09-25T09:00:00.000Z',
    searchNumber:1123,callSign:'Tango Foxtrot 2 Alpha Charlie 01123',pigeonName:'Esmeralda'
  })
};
const first=boot('',local,{});
assert(first.nodes.overlay.classList.contains('open'),'Deck must open immediately, without Splash');
assert.equal(vm.runInContext('index',first.ctx),0,'Direct launch must show first mat');
assert.equal(vm.runInContext('state.completed["01"]',first.ctx),true,'Previously completed trophy lost');
assert.equal(first.nodes.deckCabinet.children.length,27,'Trophy Cabinet cards lost during navigation change');
assert.equal(first.nodes.cabinetCount.textContent,'2 / 27','Verified Third Qualifying progress should award the campaign milestone trophy');
assert.equal(first.nodes.truthCallSign.textContent,'Tango Foxtrot 2 Alpha Charlie 01123','Challenge Deck Call Sign did not follow Clubfinder identity');
assert.equal(first.nodes.truthPigeonName.textContent,'Esmeralda','Challenge Deck Pigeon Name did not follow Clubfinder identity');
assert.equal(first.nodes.truthPigeonMiles.textContent,'314','Pigeon Miles Flown did not follow Clubfinder truth');
assert.equal(first.nodes.truthCampaignRound.textContent,'3rd Qualifying Round','Current Campaign Round did not follow Clubfinder truth');
assert(!html.includes('Pigeon Miles Travelled'),'Legacy Pigeon Miles Travelled wording remains');
assert(html.includes('Miles Flown:'),'Challenge Deck must use Miles Flown wording');
assert(/class="campaign-truth-line"/.test(html),'Campaign identity must use stacked truth-frame lines');
first.nodes.exitBtn.onclick({preventDefault(){},stopPropagation(){},stopImmediatePropagation(){}});
assert.equal(first.location.href,'clubfinder-beta.html?from=challenges-exit-v3','Exit must return to BETA Clubfinder');
assert(local['tffc.challengeDeck.v1'],'Exiting must not erase saved Challenge data');

const session={'tffc.challengeReturnIndex':'4'};
const returning=boot('?from=stats-return-v2',local,session);
assert(returning.nodes.overlay.classList.contains('open'),'Legacy Stats-return tab must open Deck');
assert.equal(vm.runInContext('index',returning.ctx),4,'Legacy Stats-return selected mat lost');
assert.equal(session['tffc.challengeReturnIndex'],undefined,'Legacy route return token not consumed');
const esc=returning.listeners.keydown.find(fn=>fn.toString().includes('Escape'));
assert(esc,'Escape handler absent');
esc({key:'Escape',preventDefault(){}});
assert.equal(returning.location.href,'clubfinder-beta.html?from=challenges-exit-v3',
  'Escape must not leave an empty page after Splash removal');

console.log('BETA CHALLENGES DIRECT ENTRY: PASS');
console.log('Splash + detached Stats removed; direct Deck, Trophy Cabinet, saved progress, Exit and legacy return: PASS');
