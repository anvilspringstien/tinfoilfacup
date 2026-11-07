import {test} from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
const source=fs.readFileSync(new URL('../beta/boot-room-launcher.js',import.meta.url),'utf8');
function fixture(){
 let visible=true,observe=null,row=null,answer={open:false,until:0},pending=null;const events={},win={},calls=[],timers=new Map();let next=0;
 const element=()=>({dataset:{},textContent:'',title:'',isConnected:true,children:[],attrs:{},append(child){this.children.push(child);},setAttribute(k,v){this.attrs[k]=v;},getAttribute(k){return this.attrs[k];},querySelector(selector){return (this.nodes??={})[selector]??=element();},showModal(){this.open=true;},close(){this.open=false;},remove(){this.isConnected=false;},addEventListener(k,v){this[k]=v;},focus(){}});
 const nav={querySelector:()=>row};const barry={parentNode:nav,before(r){row=r;row.nextElementSibling=this;}};
 const document={head:element(),body:element(),activeElement:element(),visibilityState:'visible',createElement:element,querySelectorAll(selector){if(!visible)return [];return selector==='.boot-room-launch'?(row?row.children:[]):selector.includes('campaign-barry-nav')?[barry]:[];},addEventListener:(k,v)=>events[k]=v};
 const location={};const context={document,URL,URLSearchParams,window:{top:{location},addEventListener:(k,v)=>win[k]=v},Date,AbortController,MutationObserver:class{constructor(fn){observe=fn;}observe(){}},setTimeout(fn,ms){const id=++next;timers.set(id,{fn,ms});return id;},clearTimeout(id){timers.delete(id);},fetch:async(url,options)=>{calls.push({url,options});if(pending){const p=pending;pending=null;return p;}if(answer instanceof Error)throw answer;return {ok:true,json:async()=>answer};},localStorage:{setItem(){throw Error('Campaign must not change');},getItem(){throw Error('Identity must not be read');}}};
 vm.runInNewContext(source,context);const settle=async()=>{for(let i=0;i<20;i++)await Promise.resolve();};
 return {location,document,events,win,calls,timers,settle,setVisible(v){visible=v;observe();},tick(){const [id,t]=timers.entries().next().value;timers.delete(id);t.fn();},button:()=>row.children[0],label:()=>row.children[0].querySelector('.boot-room-status').textContent,setAnswer:a=>answer=a,defer(){let resolve;pending=new Promise(r=>resolve=r);return data=>resolve({ok:true,json:async()=>data});}};
}
test('badge reads only public doors with no credentials or Campaign identity',async()=>{
 const f=fixture();await f.settle();assert.equal(f.label(),'DOORS CLOSED');assert.equal(f.calls.length,1);
 assert.equal(f.calls[0].url,'https://tinfoilfacup.com/beta/boot-room/api/doors');assert.equal(f.calls[0].options.credentials,'omit');assert.equal(f.calls[0].options.referrerPolicy,'no-referrer');assert.equal(f.calls[0].options.body,undefined);
 f.setAnswer({open:true,until:Date.now()+500000});f.win.online();await f.settle();assert.equal(f.label(),'DOORS OPEN');
 f.setAnswer(Error('Unavailable'));f.win.online();await f.settle();assert.equal(f.label(),'CHECK THE DOORS');
});
test('background/offline clears stale status and ignores obsolete responses',async()=>{
 const f=fixture();await f.settle();const resolve=f.defer();f.win.online();f.win.offline();resolve({open:true,until:Date.now()+500000});await f.settle();assert.equal(f.label(),'CHECK THE DOORS');assert.equal(f.timers.size,0);
 const n=f.calls.length;f.document.visibilityState='hidden';f.events.visibilitychange();f.win.online();await f.settle();assert.equal(f.calls.length,n);
 f.document.visibilityState='visible';f.setAnswer({open:false,until:0});f.events.visibilitychange();await f.settle();assert.equal(f.label(),'DOORS CLOSED');
});
test('one visible refresh timer follows the room deadline, and pagehide stops it',async()=>{
 const f=fixture();await f.settle();assert.equal(f.timers.size,1);assert.equal([...f.timers.values()][0].ms,60000);
 f.setAnswer({open:true,until:Date.now()+20000});f.win.online();await f.settle();assert.equal(f.timers.size,1);assert.ok([...f.timers.values()][0].ms<=20100);
 f.win.pagehide();assert.equal(f.timers.size,0);assert.equal(f.label(),'CHECK THE DOORS');
});
test('the badge opens the chalkboard directly',async()=>{
 const f=fixture();await f.settle();f.button().onclick();
 assert.equal(f.location.href,'/beta/phone-frame.html?view=boot-room');
});

test('returning to restored Campaign markup restarts status checks after its previous timer expired',async()=>{
 const f=fixture();await f.settle();const n=f.calls.length;f.setVisible(false);f.tick();await f.settle();assert.equal(f.calls.length,n);f.setAnswer({open:true,until:Date.now()+500000});f.setVisible(true);await f.settle();assert.equal(f.label(),'DOORS OPEN');assert.equal(f.calls.length,n+1);
});

test('client clock ahead of server does not cause a rapid deadline polling loop',async()=>{const f=fixture();await f.settle();f.setAnswer({open:true,until:Date.now()-60000});f.win.online();await f.settle();assert.equal([...f.timers.values()][0].ms,60000);});

test('opt-in Shed Campaign opens the Boot Room in the shared frame',()=>{
 const f=fixture();
 Object.assign(f.location,{pathname:'/beta/phone-frame-shed.html',search:'?view=campaign&bootRoomFrame=1'});
 f.button().onclick();
 assert.equal(f.location.href,'/beta/phone-frame-shed.html?view=boot-room&bootRoomFrame=1');
});
