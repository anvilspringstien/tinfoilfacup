import {test} from 'node:test';
import assert from 'node:assert/strict';
import vm from 'node:vm';
import {script} from '../boot-room-worker/ui.mjs';
function browser(){
 const elements=new Map(),windowEvents={},documentEvents={},sockets=[],requests=[];let nextState={open:true,next:'Tomorrow',until:Date.now()+3600000,you:{id:'a',name:'Checky'},messages:[]},deferred;
 const element=()=>({hidden:false,disabled:false,value:'',textContent:'',children:[],replaceChildren(...c){this.children=c;},append(...c){this.children.push(...c);},prepend(...c){this.children.unshift(...c);},focus(){},style:{},setAttribute(name,value){this[name]=value;},showModal(){this.open=true;},close(){this.open=false;}});
 const document={visibilityState:'visible',getElementById(id){if(!elements.has(id))elements.set(id,element());return elements.get(id);},createElement:element,createTextNode:text=>({textContent:text}),addEventListener:(e,fn)=>documentEvents[e]=fn};
 class WebSocket{static OPEN=1;constructor(){this.readyState=0;sockets.push(this);}close(){this.readyState=3;this.onclose?.();}send(data){this.sent=JSON.parse(data);}open(){this.readyState=1;this.onopen?.();}message(data){this.onmessage?.({data:JSON.stringify(data)});}}
 const context={document,window:{addEventListener:(e,fn)=>windowEvents[e]=fn},location:{pathname:'/',origin:'https://room.example'},WebSocket,Date,JSON,Error,fetch:async(path)=>{requests.push(path);if(deferred){const p=deferred;deferred=null;return p;}return {ok:true,json:async()=>nextState};}};
 vm.createContext(context);vm.runInContext(script,context);
 const settle=async()=>{for(let i=0;i<20;i++)await Promise.resolve();};
 const snapshot=(ws,data=nextState)=>{ws.open();ws.message({type:'snapshot',...data});};
 return {document,windowEvents,documentEvents,sockets,requests,$:id=>document.getElementById(id),settle,snapshot,setState:s=>nextState={...nextState,...s},defer(){let resolve;deferred=new Promise(r=>resolve=r);return state=>resolve({ok:true,json:async()=>state});}};
}
test('composer waits for fresh socket state and disables immediately on connection loss without losing draft',async()=>{const b=browser();await b.settle();assert.equal(b.$('text').disabled,true);b.sockets[0].open();assert.equal(b.$('text').disabled,true);b.snapshot(b.sockets[0]);assert.equal(b.$('text').disabled,false);b.$('text').value='My unfinished pie order';b.sockets[0].close();assert.equal(b.$('text').disabled,true);assert.equal(b.$('send').disabled,true);assert.equal(b.$('text').value,'My unfinished pie order');assert.match(b.$('doors').textContent,/PAUSED/);});
test('returning from background rechecks closure and reconnects once; late old snapshots cannot reopen input',async()=>{const b=browser();await b.settle();const old=b.sockets[0];b.snapshot(old);b.document.visibilityState='hidden';b.documentEvents.visibilitychange();assert.equal(b.$('text').disabled,true);b.setState({open:false});b.document.visibilityState='visible';b.documentEvents.visibilitychange();b.documentEvents.visibilitychange();await b.settle();assert.equal(b.sockets.length,2);assert.match(b.$('doors').textContent,/ROOM CLOSED/);old.message({type:'snapshot',open:true,you:{id:'a',name:'Checky'},messages:[]});assert.equal(b.$('text').disabled,true);b.snapshot(b.sockets[1]);assert.match(b.$('doors').textContent,/ROOM CLOSED/);assert.equal(b.$('send').disabled,true);});
test('back-forward restored pages reconnect and offline pages keep draft disabled',async()=>{const b=browser();await b.settle();b.snapshot(b.sockets[0]);b.$('text').value='Draft';b.windowEvents.pagehide();b.setState({open:false});b.windowEvents.pageshow({persisted:true});await b.settle();assert.equal(b.sockets.length,2);b.snapshot(b.sockets[1]);assert.equal(b.$('text').disabled,true);assert.equal(b.$('text').value,'Draft');b.windowEvents.offline();assert.equal(b.$('send').disabled,true);assert.match(b.$('status').textContent,/Offline/);});
test('a state request completing after pagehide cannot resurrect the socket',async()=>{const b=browser();await b.settle();b.snapshot(b.sockets[0]);const resolve=b.defer();b.$('connect').onclick();b.windowEvents.pagehide();resolve({open:true,you:{id:'a',name:'Checky'},messages:[]});await b.settle();assert.equal(b.sockets.length,1);assert.equal(b.$('send').disabled,true);});
test('report receipt is shown beside the message only after confirmed state and survives a fresh view',async()=>{const b=browser();const message={id:'m1',person:'bert',name:'Bert',text:'Test message',at:Date.now(),hearts:0,hearted:false,reported:false};b.setState({messages:[message]});await b.settle();const ws=b.sockets[0];b.snapshot(ws);const row=b.$('messages').children[0],bubble=row.children[1],meta=bubble.children[2],report=meta.children[3];assert.equal(report.textContent,'Report');report.onclick();assert.equal(ws.sent.type,'report');assert.equal(report.textContent,'Sending…');assert.equal(report.disabled,true);b.setState({messages:[{...message,reported:true}]});b.snapshot(ws);const receiptBubble=b.$('messages').children[0].children[1];assert.equal(receiptBubble.children[2].children[3].textContent,'Reported ✓');assert.equal(receiptBubble.children[3].textContent,'Sent privately to the landlord.');});
test('live closure hides the composer, keeps its draft and restores it when the room reopens',async()=>{
 const b=browser();await b.settle();const ws=b.sockets[0];b.snapshot(ws);
 b.$('text').value='A pie for later';assert.equal(b.$('composer-wrap').hidden,false);
 b.setState({open:false});b.snapshot(ws);
 assert.equal(b.$('composer-wrap').hidden,true);assert.equal(b.$('send').disabled,true);
 assert.equal(b.$('text').value,'A pie for later');assert.match(b.$('doors').textContent,/ROOM CLOSED/);
 b.setState({open:true});b.snapshot(ws);
 assert.equal(b.$('composer-wrap').hidden,false);assert.equal(b.$('text').disabled,false);
 assert.equal(b.$('text').value,'A pie for later');
});
test('fresh messages preserve an older reading position in the shared header-and-conversation scroller',async()=>{
 const b=browser();await b.settle();const ws=b.sockets[0];b.snapshot(ws);
 const scroll=b.$('room-scroll');scroll.scrollTop=250;scroll.scrollHeight=2400;scroll.clientHeight=500;
 b.setState({messages:[{id:'new',person:'bert',name:'Bert',text:'New pie order',at:Date.now(),hearts:0}]});b.snapshot(ws);
 assert.equal(scroll.scrollTop,250);
 scroll.scrollTop=1880;b.snapshot(ws);assert.equal(scroll.scrollTop,2400);
});
