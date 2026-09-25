#!/usr/bin/env node
'use strict';
// BETA-only three-tap Trophy Cabinet inspection regression. Exercise the full standalone Deck script,
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
assert(/id="trophyViewer"/.test(html),'Independent Trophy Viewer must be present');
assert(/id="trophyViewerMat"/.test(html),'Trophy Viewer flip target missing');
assert(/id="trophyViewerHint"/.test(html),'Minimal discoverability hint missing');
assert(/id="exitBtn"/.test(html),'Explicit Exit button must be retained');

const scripts=[...html.matchAll(/<script[^>]*>([\s\S]*?)<\/script>/gi)].map(m=>m[1]).join('\n');
assert(scripts.length>20000,'Standalone Challenge Deck script missing');
new vm.Script(scripts,{filename:'beta/challenges-beta.html'});

function stub(){
  const flags=new Set(),node={
    style:{},dataset:{},children:[],textContent:'',innerHTML:'',value:'0',selectedIndex:0,disabled:false,
    options:Array.from({length:14},(_,i)=>({textContent:i?'Round '+i:'Extra Preliminary Round',text:i?'Round '+i:'Extra Preliminary Round'})),
    classList:{add(k){flags.add(k)},remove(k){flags.delete(k)},contains(k){return flags.has(k)},toggle(k,on){if(on===undefined)on=!flags.has(k);if(on)flags.add(k);else flags.delete(k);return on}},
    setAttribute(){},removeAttribute(){},remove(){},focus(){this.focused=true},isConnected:true,listeners:{},
    addEventListener(name,fn){(this.listeners[name]||=[]).push(fn)},
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
  })
};
const app=boot('',local,{});
const {nodes,ctx,listeners,location}=app;
assert(nodes.overlay.classList.contains('open'),'Underlying Deck must open normally');
const slot=nodes.deckCabinet.children[0];
assert(slot.className.includes('completed'),'First trophy must be earned');
assert.equal(typeof slot.onclick,'function','Achieved Trophy Cabinet mat must be interactive');
const snapshot=local['tffc.challengeDeck.v1'];
const initialIndex=vm.runInContext('index',ctx);
const initialFlipped=vm.runInContext('flipped',ctx);

// Tap 1: enlarge front image in a separate viewer without moving/flipping the Deck.
slot.onclick();
assert(nodes.trophyViewer.classList.contains('open'),'First tap must open Trophy Viewer');
assert.equal(nodes.trophyViewer.hidden,false,'Viewer must be visible');
assert.match(nodes.trophyViewerFront.src,/mat-01-front\\.webp$/,'Must reuse existing front artwork');
assert.match(nodes.trophyViewerBack.src,/mat-01-back\\.webp$/,'Must reuse existing back artwork');
assert.equal(nodes.trophyViewerHint.textContent,'Tap to flip','First hint should be understated');
assert(nodes.trophyViewerMat.focused,'Keyboard focus should move into trophy inspection');
assert.equal(vm.runInContext('index',ctx),initialIndex,'Trophy tap changed underlying selected card');
assert.equal(vm.runInContext('flipped',ctx),initialFlipped,'Trophy tap flipped the hidden Deck');

// Tap 2: reverse; tap 3: dismiss, focus returns to the same achieved cabinet slot.
nodes.trophyViewerMat.onclick();
assert(nodes.trophyViewerCard.classList.contains('flipped'),'Second tap must show reverse');
assert.equal(nodes.trophyViewerHint.textContent,'Tap to return','Second hint must describe final tap');
nodes.trophyViewerMat.onclick();
assert(!nodes.trophyViewer.classList.contains('open'),'Third tap must close inspection');
assert.equal(nodes.trophyViewer.hidden,true,'Third tap must hide independent viewer');
assert(slot.focused,'Focus must return to the original cabinet trophy');
assert(nodes.overlay.classList.contains('open'),'Closing inspection must not exit the Deck');

// Tapping the dark backdrop dismisses, without activating the Deck backdrop.
slot.onclick();
nodes.trophyViewer.onclick({target:nodes.trophyViewer});
assert.equal(nodes.trophyViewer.hidden,true,'Viewer backdrop must dismiss inspection');
assert(nodes.overlay.classList.contains('open'),'Viewer backdrop must not exit the Deck');

// Escape closes only the viewer; Escape with no viewer retains existing Exit behaviour.
slot.onclick();
const docKey=listeners.keydown.find(fn=>fn.toString().includes('trophyViewerOpen'));
assert(docKey,'Dedicated Escape precedence is missing');
docKey({key:'Escape',preventDefault(){}});
assert.equal(nodes.trophyViewer.hidden,true,'Escape should close trophy inspection');
assert(nodes.overlay.classList.contains('open'),'Escape from inspection must not exit the Deck');

// Accessible keyboard equivalents for second/third tap.
slot.onclick();
const matKey=nodes.trophyViewerMat.listeners.keydown[0];
assert(matKey,'Trophy mat must offer keyboard access');
const keyboardEvent=key=>({key,preventDefault(){},stopPropagation(){}});
matKey(keyboardEvent('Enter'));
assert(nodes.trophyViewerCard.classList.contains('flipped'),'Enter must flip');
matKey(keyboardEvent(' '));
assert.equal(nodes.trophyViewer.hidden,true,'Space must dismiss after flip');

// No storage writes or browser navigation from any inspection action.
assert.equal(vm.runInContext('index',ctx),initialIndex,'Inspection changed Deck index');
assert.equal(vm.runInContext('flipped',ctx),initialFlipped,'Inspection changed Deck orientation');
assert.equal(local['tffc.challengeDeck.v1'],snapshot,'Inspection modified persisted Challenge state');
assert.equal(location.href,'https://example.test/beta/challenges-beta.html','Inspection navigated unexpectedly');
assert.equal(nodes.deckCabinet.children.length,27,'Inspection modified Trophy Cabinet contents');
console.log('BETA TROPHY VIEWER: PASS');
console.log('Three taps, backdrop, Escape, keyboard, focus, persistent state and Deck isolation: PASS');
