import {test} from 'node:test';
import assert from 'node:assert/strict';
import vm from 'node:vm';
import {webcrypto} from 'node:crypto';
import {readFile} from 'node:fs/promises';
const source=await readFile(new URL('../beta/like-tffac.js',import.meta.url),'utf8');
const key='tffc.like.identity.v1';
const settle=async()=>{for(let i=0;i<8;i++)await new Promise(resolve=>setImmediate(resolve));};
async function page(storage=new Map(),server=new Map(),blocked=false){
 const calls=[],writes=[],events={},attrs={},handlers={};
 const message={textContent:''};
 const button={disabled:true,setAttribute:(k,v)=>attrs[k]=v,addEventListener:(k,v)=>handlers[k]=v};
 const row={isConnected:true,classList:{contains:()=>true},querySelector:selector=>selector==='button'?button:message};
 const target={previousElementSibling:row};
 const window={addEventListener:(k,v)=>events[k]=v};
 const localStorage={getItem:k=>{if(blocked)throw Error('denied');return storage.get(k)||null;},setItem:(k,v)=>{if(blocked)throw Error('denied');writes.push(k);storage.set(k,v);}};
 const fetch=async(url,options)=>{
  if(String(url).endsWith('like-config.json'))return {ok:true,json:async()=>({enabled:true,endpoint:'https://likes.test'})};
  const path=new URL(url).pathname,body=JSON.parse(options.body);calls.push({path,body});
  if(path==='/reaction')server.set(body.token,body.liked);
  return {ok:true,json:async()=>({liked:server.get(body.token)||false})};
 };
 vm.runInNewContext(source,{window,localStorage,sessionStorage:{getItem:()=>null},document:{currentScript:{src:'https://site.test/beta/like-tffac.js'},head:{append(){}},body:{},createElement:()=>({}),querySelectorAll:()=>[target]},location:{href:'https://site.test/beta/phone-frame.html',origin:'https://site.test'},MutationObserver:class{observe(){}},crypto:webcrypto,URL,fetch,AbortController,setTimeout,clearTimeout});
 await settle();return {storage,server,calls,writes,events,attrs,button,message,click:async()=>{await handlers.click();await settle();}};
}
test('ordinary visit creates no identity, writes no browser state and makes no service call',async()=>{
 const p=await page();assert.equal(p.storage.size,0);assert.deepEqual(p.writes,[]);assert.deepEqual(p.calls,[]);assert.equal(p.button.disabled,false);assert.equal(p.attrs['aria-pressed'],'false');
});
test('first tap creates identity; saved Like and unlike survive new documents',async()=>{
 const p=await page();await p.click();assert.ok(p.storage.get(key));assert.equal(p.calls.length,1);assert.equal(p.calls[0].path,'/reaction');assert.equal(p.attrs['aria-pressed'],'true');
 const restored=await page(p.storage,p.server);assert.equal(restored.calls[0].path,'/state');assert.equal(restored.attrs['aria-pressed'],'true');assert.deepEqual(restored.writes,[]);
 await restored.click();assert.equal(restored.attrs['aria-pressed'],'false');const undone=await page(p.storage,p.server);assert.equal(undone.attrs['aria-pressed'],'false');
});
test('another document learns first-tap identity through storage refresh',async()=>{
 const p=await page(),other=await page(p.storage,p.server);await p.click();await other.events.storage({key:'tffc.like.refresh.v1'});await settle();assert.equal(other.attrs['aria-pressed'],'true');
});
test('blocked storage is reported only on interaction and sends no reaction',async()=>{
 const p=await page(new Map(),new Map(),true);assert.equal(p.message.textContent,'');await p.click();assert.match(p.message.textContent,/couldn’t remember/);assert.equal(p.calls.length,0);assert.equal(p.button.disabled,false);
});
