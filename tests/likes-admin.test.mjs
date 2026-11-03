import {test} from 'node:test';
import assert from 'node:assert/strict';
import vm from 'node:vm';
import {handleLikes} from '../likes-worker/service.mjs';
import {adminScript} from '../likes-worker/admin-ui.mjs';

test('dashboard assets expose neither credentials nor counts; all count reads require Bearer auth',async()=>{
 let reads=0;const env={ADMIN_TOKEN:'private-test-value'};
 const request=(path,options)=>handleLikes(new Request('https://likes.example'+path,options),env,()=>{reads++;return {total:7};});
 for(const path of ['/admin','/admin/','/admin/dashboard.css','/admin/dashboard.js']){
  const r=await request(path);assert.equal(r.status,200);assert.equal(r.headers.get('cache-control'),'no-store');
  assert.match(r.headers.get('content-security-policy'),/frame-ancestors 'none'/);
  assert.equal(r.headers.get('referrer-policy'),'no-referrer');assert.doesNotMatch(await r.text(),/private-test-value/);
  assert.equal(await (await request(path,{method:'HEAD'})).text(),'');
  assert.equal((await request(path,{method:'POST'})).status,405);
 }
 assert.equal(reads,0);
 for(const options of [{},{headers:{authorization:'Bearer incorrect'}},{method:'POST',headers:{authorization:'Bearer private-test-value'}},{method:'OPTIONS',headers:{origin:'https://elsewhere.example'}}])assert.notEqual((await request('/admin/count',options)).status,200);
 assert.equal(reads,0);
 const r=await request('/admin/count',{headers:{authorization:'Bearer private-test-value'}});assert.deepEqual(await r.json(),{total:7});assert.equal(reads,1);assert.equal(r.headers.get('access-control-allow-origin'),null);
});

test('private count storage failure returns an unavailable response, never a fabricated zero',async()=>{
 const r=await handleLikes(new Request('https://likes.example/admin/count',{headers:{authorization:'Bearer test'}}),{ADMIN_TOKEN:'test'},()=>{throw Error('unavailable')});
 assert.equal(r.status,503);assert.deepEqual(await r.json(),{error:'temporarily_unavailable'});
});

function page(fetcher){
 const elements=new Map();const windowEvents={};
 const document={getElementById(id){if(!elements.has(id))elements.set(id,{value:'',textContent:'',hidden:['controls'].includes(id),disabled:false,listeners:{},addEventListener(event,handler){this.listeners[event]=handler;}});return elements.get(id);}};
 const requests=[];const context={document,window:{addEventListener:(e,h)=>windowEvents[e]=h},Intl,Date,Number,Error,fetch:async(...args)=>{requests.push(args);return fetcher(...args);}};
 vm.createContext(context);vm.runInContext(adminScript,context);
 const element=id=>document.getElementById(id);
 const settle=async()=>{for(let i=0;i<10;i++)await Promise.resolve();};
 const submit=async(value)=>{element('password').value=value;element('unlock-form').listeners.submit({preventDefault(){}});await settle();};
 return {element,requests,submit,settle,windowEvents};
}

test('only an explicit unlock requests the count; refresh is read-only and locking forgets the credential',async()=>{
 const p=page(async()=>({ok:true,status:200,json:async()=>({total:1234})}));
 assert.equal(p.requests.length,0);await p.submit('test-password');
 assert.equal(p.element('total').textContent,'1,234');assert.equal(p.element('password').value,'');assert.equal(p.element('controls').hidden,false);
 const [url,options]=p.requests[0];assert.equal(url,'/admin/count');assert.equal(options.method,'GET');assert.equal(options.headers.Authorization,'Bearer test-password');assert.equal(options.cache,'no-store');assert.equal(options.redirect,'error');assert.equal(options.credentials,'omit');
 await p.element('refresh').listeners.click();assert.equal(p.requests.length,2);
 p.element('lock').listeners.click();assert.equal(p.element('total').textContent,'—');assert.equal(p.element('controls').hidden,true);
 await p.element('refresh').listeners.click();assert.equal(p.requests.length,2);
 assert.doesNotMatch(adminScript,/localStorage|sessionStorage|document\.cookie|console\./);
});

test('bad passwords, malformed counts and network failures cannot display an invented total',async()=>{
 for(const result of [{ok:false,status:401},{ok:true,status:200,json:async()=>({total:-1})},{ok:true,status:200,json:async()=>({total:'12'})},null]){
  const p=page(async()=>{if(!result)throw Error('offline');return result;});p.element('total').textContent='—';await p.submit('test');
  assert.equal(p.element('total').textContent,'—');assert.equal(p.element('controls').hidden,true);assert.equal(p.element('password').value,'');
  assert.match(p.element('status').textContent,result?.status===401?/wasn’t accepted/:/Couldn’t refresh/);
 }
});

test('a late response after Lock or pagehide cannot reveal the count again',async()=>{
 for(const action of ['lock','pagehide']){
  let respond;const p=page(()=>new Promise(resolve=>respond=resolve));await p.submit('test');
  if(action==='lock')p.element('lock').listeners.click();else p.windowEvents.pagehide();
  respond({ok:true,status:200,json:async()=>({total:9})});await p.settle();
  assert.equal(p.element('total').textContent,'—');assert.equal(p.element('controls').hidden,true);
 }
});
