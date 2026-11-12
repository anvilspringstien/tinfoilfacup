// Local-only Worker integration check. Supply the installed ws module path as argv[3].
import assert from 'node:assert/strict';
import {createRequire} from 'node:module';
const base=process.argv[2]||'http://127.0.0.1:8789';
assert.equal(new URL(base).hostname,'127.0.0.1','This check uses fixture credentials and must only target loopback');
const require=createRequire(import.meta.url);const WebSocket=require(process.argv[3]||'ws');
async function api(path,body,{admin=false,cookie='',origin=base}={}){const r=await fetch(base+path,{method:body?'POST':'GET',headers:{...(body?{'content-type':'application/json',origin}:{}),...(cookie?{cookie}:{}),...(admin?{authorization:'Bearer local-test-only'}:{})},body:body?JSON.stringify(body):undefined});const data=await r.json();return {status:r.status,data,cookie:r.headers.get('set-cookie')?.split(';')[0]};}
const admin=body=>api('/api/admin',body,{admin:true});
assert.equal((await admin({type:'doors',open:false,next:'Test opening'})).status,200);
const sample=await fetch(base+'/demo');assert.equal(sample.status,200);assert.match(await sample.text(),/25 sample posts/);
for(const prefix of ['', '/beta/boot-room']){
 const renderer=await fetch(base+prefix+'/flight-path-share.mjs?v=4');
 assert.equal(renderer.status,200);
 assert.match(renderer.headers.get('content-type'),/javascript/);
 assert.match(await renderer.text(),/export async function bootRoomFlightImage/);
 const map=await fetch(base+prefix+'/assets/route-map.svg');
 assert.equal(map.status,200);
 assert.match(await map.text(),/<svg\b/);
}
assert.equal((await fetch(base+'/boarding-pass-share.mjs')).status,404);
const publicDoors=await api('/api/doors');assert.equal(publicDoors.status,200);assert.deepEqual(Object.keys(publicDoors.data).sort(),['next','open','until']);assert.equal(publicDoors.data.open,false);assert.equal(publicDoors.data.next,'Test opening');
for(const origin of ['https://tinfoilfacup.com','https://www.tinfoilfacup.com','https://elsewhere.example']){
 const r=await fetch(base+'/api/doors',{headers:{origin}});
 assert.equal(r.status,200);assert.equal(r.headers.get('access-control-allow-origin'),origin.includes('elsewhere')?null:origin);
 assert.equal(r.headers.get('access-control-allow-credentials'),null);
 assert.deepEqual(Object.keys(await r.json()).sort(),['next','open','until']);
}
assert.equal((await api('/api/state')).status,401);
for(const path of ['/','/chat']){const r=await fetch(base+path);assert.equal(r.status,200);assert.match(r.headers.get('content-type'),/text\/html/);assert.equal(r.headers.get('cache-control'),'no-store');}
assert.equal((await api('/api/admin',{type:'status'})).status,401);
assert.equal((await api('/api/invite',{name:'Wrong origin'},{admin:true,origin:'https://elsewhere.example'})).status,403);
async function person(name,campaign){const invitation=await api('/api/invite',{name,callSign:campaign?.callSign},{admin:true});assert.equal(invitation.status,200);const joined=await api('/api/join',{invite:invitation.data.invite,campaign});assert.equal(joined.status,200);assert.equal((await api('/api/join',{invite:invitation.data.invite})).status,401);return {...joined,id:invitation.data.id};}
const a=await person('Checky',{name:'Checky',callSign:'TF2AC 01001',custodian:'Example Town',fixture:'Example Town v Example United'}),b=await person('Bert');
function socket(p){return new Promise((resolve,reject)=>{const ws=new WebSocket(base.replace('http','ws')+'/api/socket',{headers:{origin:base,cookie:p.cookie}});ws.events=[];ws.on('message',raw=>ws.events.push(JSON.parse(String(raw))));ws.on('open',()=>resolve(ws));ws.on('error',reject);});}
const sockets=[];
async function wait(predicate,label){for(let i=0;i<100;i++){if(await predicate())return;await new Promise(r=>setTimeout(r,20));}throw Error('Timed out: '+label);}
try{
 const wa=await socket(a),wb=await socket(b);sockets.push(wa,wb);await wait(()=>wa.events.length&&wb.events.length,'initial snapshots');
 assert.equal(wa.events.at(-1).open,false);wa.send(JSON.stringify({type:'message',text:'Closed bypass'}));await wait(()=>wa.events.some(x=>x.type==='error'),'closed rejection');
 await admin({type:'doors',open:true,until:Date.now()+3600000,next:'Later'});await wait(()=>wa.events.at(-1).open,'opening broadcast');
 assert.equal((await api('/api/doors')).data.open,true);
 const flightPath={stops:[{lat:51.6332,lon:-.5559,short:'Home'},{lat:52,lon:-1,short:'Example Town',next:true}],flights:[{stop:1,status:'NEXT FLIGHT'}]};
 wa.send(JSON.stringify({type:'message',text:'Hello from device A',flightPath}));await wait(()=>wb.events.at(-1).messages?.some(x=>x.text==='Hello from device A'),'cross-client delivery');const m=wb.events.at(-1).messages.find(x=>x.text==='Hello from device A');
 const mapURL='/beta/boot-room/api/flight-path?post='+m.id;
 assert.equal(m.hasFlightPath,true);assert.equal(m.flightPath,undefined);
 assert.equal((await api(mapURL)).status,401);
 const shared=await api(mapURL,undefined,{cookie:b.cookie});
 assert.equal(shared.status,200);
 assert.deepEqual(shared.data.stops[0],{lat:51.5,lon:-.5,short:'Home area',approximate:true});
 wb.send(JSON.stringify({type:'message',text:'Reply from B',replyTo:m.id}));await wait(()=>wa.events.at(-1).messages?.some(x=>x.text==='Reply from B'),'reply delivery');
 wb.send(JSON.stringify({type:'heart',id:m.id,liked:true}));await wait(()=>wa.events.at(-1).messages?.find(x=>x.id===m.id)?.hearts===1,'heart delivery');
 wb.send(JSON.stringify({type:'report',id:m.id}));await wait(async()=>((await admin({type:'status'})).data.reports.some(r=>r.message===m.id)),'report submission');
 await admin({type:'delete',id:m.id});await wait(()=>wa.events.at(-1).messages?.find(x=>x.id===m.id)?.deleted,'removal broadcast');
 assert.equal((await api(mapURL,undefined,{cookie:b.cookie})).status,404);
 const reloaded=await api('/api/state',undefined,{cookie:b.cookie});assert.equal(reloaded.status,200);assert(reloaded.data.messages.some(x=>x.text==='Reply from B'));
 await admin({type:'suspend',id:a.id});await wait(()=>wa.readyState===WebSocket.CLOSED,'suspended socket closed');assert.equal((await api('/api/state',undefined,{cookie:a.cookie})).status,401);
 await admin({type:'doors',open:false,next:'Tomorrow'});await wait(()=>wb.events.at(-1).open===false,'closure broadcast');
 const closedMessage=(await api('/api/state',undefined,{cookie:b.cookie})).data.messages.find(x=>x.text==='Reply from B');wb.send(JSON.stringify({type:'report',id:closedMessage.id}));await wait(async()=>((await admin({type:'status'})).data.reports.some(r=>r.message===closedMessage.id)),'closed-room report recorded');assert.equal((await api('/api/state',undefined,{cookie:b.cookie})).data.messages.find(x=>x.id===closedMessage.id).reported,true);
 wb.send(JSON.stringify({type:'delete-own',id:closedMessage.id}));
 await wait(()=>wb.events.some(event=>event.type==='ack'&&event.action==='delete-own'),'closed-room author deletion');
 assert.equal((await api('/api/state',undefined,{cookie:b.cookie})).data.messages.find(x=>x.id===closedMessage.id).deleted,true);
 wb.send(JSON.stringify({type:'message',text:'After closing'}));await wait(()=>wb.events.at(-1).type==='error','post-close denial');assert(!((await api('/api/state',undefined,{cookie:b.cookie})).data.messages.some(x=>x.text==='After closing')));assert.equal((await api('/api/logout',{},{cookie:b.cookie})).status,200);assert.equal((await api('/api/state',undefined,{cookie:b.cookie})).status,401);
 console.log('PASS: two separate WebSocket clients, invitation replay, origin/auth boundaries, messages, replies, hearts, reload persistence, removal, suspension and closing.');
}finally{for(const s of sockets)s.close();await admin({type:'doors',open:false,next:'Opening time to be announced'});}
