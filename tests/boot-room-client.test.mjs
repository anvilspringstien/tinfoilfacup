import {test} from 'node:test';
import assert from 'node:assert/strict';
import vm from 'node:vm';
import {script} from '../boot-room-worker/ui.mjs';
function browser(pathname='/chat',campaign=null,{search='',responses=[]}={}){
 const elements=new Map(),windowEvents={},documentEvents={},sockets=[],requests=[],posts=[];let nextState={open:true,next:'Tomorrow',until:Date.now()+3600000,you:{id:'a',name:'Checky'},messages:[]},deferred;
 const element=()=>({hidden:false,disabled:false,value:'',textContent:'',children:[],replaceChildren(...c){this.children=c;},append(...c){this.children.push(...c);},prepend(...c){this.children.unshift(...c);},focus(){},style:{},setAttribute(name,value){this[name]=value;},showModal(){this.open=true;},close(){this.open=false;}});
 const document={querySelectorAll(){return [];},querySelector(selector){return this.getElementById(selector);},visibilityState:'visible',getElementById(id){if(!elements.has(id))elements.set(id,element());return elements.get(id);},createElement:element,createTextNode:text=>({textContent:text}),addEventListener:(e,fn)=>documentEvents[e]=fn};
 class WebSocket{static OPEN=1;constructor(){this.readyState=0;sockets.push(this);}close(){this.readyState=3;this.onclose?.();}send(data){this.sent=JSON.parse(data);}open(){this.readyState=1;this.onopen?.();}message(data){this.onmessage?.({data:JSON.stringify(data)});}}
 const context={document,window:{addEventListener:(e,fn)=>windowEvents[e]=fn},location:{pathname,origin:'https://room.example',hash:campaign?'#campaign='+encodeURIComponent(JSON.stringify(campaign)):'',search},history:{replaceState(){}},URLSearchParams,WebSocket,Date,JSON,Error,fetch:async(path,options)=>{requests.push(path);if(options?.body)posts.push(JSON.parse(options.body));if(deferred){const p=deferred;deferred=null;return p;}return responses.shift()??{ok:true,json:async()=>nextState};}};
 vm.createContext(context);vm.runInContext(script,context);
 const settle=async()=>{for(let i=0;i<20;i++)await Promise.resolve();};
 const snapshot=(ws,data=nextState)=>{ws.open();ws.message({type:'snapshot',...data});};
 return {document,windowEvents,documentEvents,sockets,requests,posts,$:id=>document.getElementById(id),settle,snapshot,setState:s=>nextState={...nextState,...s},defer(){let resolve;deferred=new Promise(r=>resolve=r);return state=>resolve({ok:true,json:async()=>state});}};
}
test('composer waits for fresh socket state and disables immediately on connection loss without losing draft',async()=>{const b=browser();await b.settle();assert.equal(b.$('text').disabled,true);b.sockets[0].open();assert.equal(b.$('text').disabled,true);b.snapshot(b.sockets[0]);assert.equal(b.$('text').disabled,false);b.$('text').value='My unfinished pie order';b.sockets[0].close();assert.equal(b.$('text').disabled,true);assert.equal(b.$('send').disabled,true);assert.equal(b.$('text').value,'My unfinished pie order');assert.match(b.$('doors').textContent,/PAUSED/);});
test('returning from background rechecks closure and reconnects once; late old snapshots cannot reopen input',async()=>{const b=browser();await b.settle();const old=b.sockets[0];b.snapshot(old);b.document.visibilityState='hidden';b.documentEvents.visibilitychange();assert.equal(b.$('text').disabled,true);b.setState({open:false});b.document.visibilityState='visible';b.documentEvents.visibilitychange();b.documentEvents.visibilitychange();await b.settle();assert.equal(b.sockets.length,2);assert.match(b.$('doors').textContent,/ROOM CLOSED/);old.message({type:'snapshot',open:true,you:{id:'a',name:'Checky'},messages:[]});assert.equal(b.$('text').disabled,true);b.snapshot(b.sockets[1]);assert.match(b.$('doors').textContent,/ROOM CLOSED/);assert.equal(b.$('send').disabled,true);});
test('back-forward restored pages reconnect and offline pages keep draft disabled',async()=>{const b=browser();await b.settle();b.snapshot(b.sockets[0]);b.$('text').value='Draft';b.windowEvents.pagehide();b.setState({open:false});b.windowEvents.pageshow({persisted:true});await b.settle();assert.equal(b.sockets.length,2);b.snapshot(b.sockets[1]);assert.equal(b.$('text').disabled,true);assert.equal(b.$('text').value,'Draft');b.windowEvents.offline();assert.equal(b.$('send').disabled,true);assert.match(b.$('status').textContent,/Offline/);});
test('a state request completing after pagehide cannot resurrect the socket',async()=>{const b=browser();await b.settle();b.snapshot(b.sockets[0]);const resolve=b.defer();b.$('connect').onclick();b.windowEvents.pagehide();resolve({open:true,you:{id:'a',name:'Checky'},messages:[]});await b.settle();assert.equal(b.sockets.length,1);assert.equal(b.$('send').disabled,true);});
test('report receipt is shown beside the message only after confirmed state and survives a fresh view',async()=>{const b=browser();const message={id:'m1',person:'bert',name:'Bert',text:'Test message',at:Date.now(),hearts:0,hearted:false,reported:false};b.setState({messages:[message]});await b.settle();const ws=b.sockets[0];b.snapshot(ws);const row=b.$('messages').children[0],bubble=row.children[1],meta=bubble.children[2],report=meta.children[3];assert.equal(report.textContent,'Report');report.onclick();assert.equal(ws.sent.type,'report');assert.equal(report.textContent,'Sending…');assert.equal(report.disabled,true);b.setState({messages:[{...message,reported:true}]});b.snapshot(ws);const receiptBubble=b.$('messages').children[0].children[1];assert.equal(receiptBubble.children[2].children[3].textContent,'Undo report');receiptBubble.children[2].children[3].onclick();assert.equal(ws.sent.reported,false);assert.equal(receiptBubble.children[3].textContent,'Sent privately to the landlord.');});
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
test('entrance checks only public opening details, never conversation or a WebSocket',async()=>{
 const b=browser('/');await b.settle();assert.deepEqual(b.requests,['/api/doors']);assert.equal(b.sockets.length,0);
 assert.equal(b.$('entrance').hidden,false);assert.match(b.$('.entrance-enter').textContent,/Invited pigeons: enter/);
 b.setState({open:false,next:'Saturday, before kick-off'});b.$('entrance-refresh').onclick();await b.settle();
 assert.equal(b.$('entrance-state').textContent,'ROOM NOW CLOSED');assert.equal(b.$('entrance-next').textContent,'Saturday, before kick-off');
 assert.match(b.$('.entrance-enter').textContent,/Invited pigeons/);assert.equal(b.sockets.length,0);
 b.document.visibilityState='hidden';b.documentEvents.visibilitychange();b.document.visibilityState='visible';b.documentEvents.visibilitychange();await b.settle();
 assert.deepEqual(b.requests,['/api/doors','/api/doors','/api/doors']);assert.equal(b.sockets.length,0);
});
test('a stale entrance check cannot overwrite status after the page goes offline',async()=>{
 const b=browser('/');await b.settle();const resolve=b.defer();b.$('entrance-refresh').onclick();b.windowEvents.offline();
 resolve({open:true,until:Date.now()+3600000});await b.settle();assert.match(b.$('entrance-state').textContent,/OFFLINE/);
 b.setState({open:false,next:'Tomorrow'});b.windowEvents.online();await b.settle();assert.equal(b.$('entrance-state').textContent,'ROOM NOW CLOSED');
});

 test('the public sample is read-only fiction with no live-room script, requests or credentials',async()=>{
 const {demoPage,sampleMessages}=await import('../boot-room-worker/demo.mjs');
 assert.equal(sampleMessages.length,25);assert.match(demoPage,/fictional/);assert.match(demoPage,/DEMO 01612/);
 assert.doesNotMatch(demoPage,/<script|<form|<textarea|<button|\/api\/|localStorage|__Host-bootroom|WebSocket/);
 assert.equal((demoPage.match(/<article/g)||[]).length,25);
 });

test('the Campaign entry sends a walk-in request from the Join button',async()=>{
 const campaign={name:'Lab Pigeon',callSign:'TF2AC 01001',custodian:'Example Town',fixture:'Example Town v Example United'};
 const b=browser('/chat',campaign);
 await b.settle();
 assert.equal(b.$('walk-in-entry').hidden,false);
 b.setState({you:{id:'lab',name:campaign.name,campaign}});
 await b.$('walk-in-join').onclick();
 assert.deepEqual(b.requests,['/api/state','/api/walk-in','/api/state']);
 assert.deepEqual(b.posts,[{campaign}]);
 assert.match(b.$('you').textContent,/Posting as Lab Pigeon · TF2AC 01001/);
});

test('Campaign visitors see the chalkboard before continuing to chat',async()=>{
 const campaign={callSign:'TF2AC 01938',name:'Flappy Gilmore'};
 const b=browser('/',campaign);
 b.setState({walkIn:true});
 await b.settle();
 assert.deepEqual(b.requests,['/api/doors']);
 assert.equal(b.sockets.length,0);
 assert.equal(b.$('.entrance-enter').href,'/chat?enter=1#campaign='+encodeURIComponent(JSON.stringify(campaign)));
 assert.equal(b.$('.entrance-enter').textContent,'Continue to the Boot Room →');
});

test('the Keep chalkboard stays within the Boot Room path when continuing to chat',async()=>{
 const campaign={callSign:'TF2AC 01938',name:'Flappy Gilmore'};
 const b=browser('/beta/boot-room/',campaign);
 await b.settle();
 assert.deepEqual(b.requests,['/beta/boot-room/api/doors']);
 assert.equal(b.$('.entrance-enter').href,'/beta/boot-room/chat?enter=1#campaign='+encodeURIComponent(JSON.stringify(campaign)));
});

test('entering from the Keep chalkboard joins an open walk-in once and connects',async()=>{
 const campaign={callSign:'TF2AC 01921',name:'Flappy'};
 const response=(data,status=200)=>({ok:status===200,status,json:async()=>data});
 const b=browser('/beta/boot-room/chat',campaign,{search:'?enter=1',responses:[
  response({error:'Invitation required'},401),
  response({open:true,walkIn:true}),
  response({ok:true}),
 ]});
 b.setState({you:{id:'a',name:'Flappy',campaign}});
 await b.settle();
 await b.settle();
 assert.deepEqual(b.posts,[{campaign}]);
 assert.equal(b.sockets.length,1);
});
