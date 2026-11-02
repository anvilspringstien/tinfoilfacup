import {test} from 'node:test';
import assert from 'node:assert/strict';
import {randomUUID} from 'node:crypto';
import {LikeStore} from '../likes-worker/store.mjs';
import {openStorage} from '../likes-worker/sqlite-node.mjs';
import {handleLikes} from '../likes-worker/service.mjs';
const origin='https://tinfoilfacup.com';
function setup(){const storage=openStorage(),store=new LikeStore(storage);return {storage,store,fetch:(path,options={})=>handleLikes(new Request('https://likes.example'+path,options),{ALLOWED_ORIGINS:origin,ADMIN_TOKEN:'test-secret'},(op,hash,liked)=>store[op](hash,liked))};}
const post=(body,extra={})=>({method:'POST',headers:{origin,'content-type':'application/json',...extra},body:JSON.stringify(body)});
test('retries, unlike and relike change one shared total exactly once',async()=>{
 const {fetch,store,storage}=setup(),token=randomUUID();
 assert.deepEqual(await (await fetch('/state',post({token}))).json(),{liked:false});
 for(let i=0;i<5;i++)assert.deepEqual(await (await fetch('/reaction',post({token,liked:true}))).json(),{liked:true});
 assert.deepEqual(store.count(),{total:1});
 const stored=storage.sql.exec('SELECT token_hash FROM reactions').toArray()[0].token_hash;
 assert.equal(stored.length,64);assert.notEqual(stored,token);
 assert.deepEqual(await (await fetch('/state',post({token}))).json(),{liked:true});
 for(let i=0;i<3;i++)await fetch('/reaction',post({token,liked:false}));assert.equal(store.count().total,0);
 await fetch('/reaction',post({token,liked:true}));assert.equal(store.count().total,1);
});
test('independent browsers and concurrent requests preserve counts',async()=>{
 const {fetch,store}=setup();const tokens=Array.from({length:50},()=>randomUUID());
 await Promise.all(tokens.flatMap(token=>[fetch('/reaction',post({token,liked:true})),fetch('/reaction',post({token,liked:true}))]));
 assert.equal(store.count().total,50);
 await Promise.all(tokens.slice(0,25).map(token=>fetch('/reaction',post({token,liked:false}))));assert.equal(store.count().total,25);
});
test('count is private and unknown routes cannot mutate',async()=>{
 const {fetch,store}=setup();assert.equal((await fetch('/admin/count')).status,401);
 assert.equal((await fetch('/admin/count',{headers:{authorization:'Bearer wrong'}})).status,401);
 assert.deepEqual(await (await fetch('/admin/count',{headers:{authorization:'Bearer test-secret'}})).json(),{total:0});
 assert.equal((await fetch('/increment',post({}))).status,404);assert.equal((await fetch('/__shed/count')).status,404);assert.equal(store.count().total,0);
});
test('CORS is enforced before storage and allows the exact approved origin',async()=>{
 const {fetch,store}=setup(),token=randomUUID();
 assert.equal((await fetch('/reaction',post({token,liked:true},{origin:'https://evil.example'}))).status,403);
 const noOrigin=post({token,liked:true});delete noOrigin.headers.origin;assert.equal((await fetch('/reaction',noOrigin)).status,403);
 const preflight=await fetch('/reaction',{method:'OPTIONS',headers:{origin}});assert.equal(preflight.status,204);assert.equal(preflight.headers.get('access-control-allow-origin'),origin);assert.equal(store.count().total,0);
});
test('malformed, oversized and extra personal-data fields are rejected',async()=>{
 const {fetch,store}=setup(),token=randomUUID();
 for(const body of [{token,liked:'yes'},{token:'bad',liked:true},{token,liked:true,postcode:'NE6 5NL'},null])assert.equal((await fetch('/reaction',post(body))).status,400);
 assert.equal((await fetch('/reaction',post({token,liked:true},{'content-type':'text/plain'}))).status,415);
 assert.equal((await fetch('/reaction',post({token,liked:true,padding:'x'.repeat(600)}))).status,413);
 assert.equal(store.count().total,0);
});
test('quota/storage failure cannot acknowledge a Like',async()=>{
 const request=new Request('https://likes.example/reaction',post({token:randomUUID(),liked:true}));
 const response=await handleLikes(request,{ALLOWED_ORIGINS:origin},()=>{throw Error('Quota exceeded')});assert.equal(response.status,503);assert.deepEqual(await response.json(),{error:'temporarily_unavailable'});
});
test('stored Like survives a new service instance',async()=>{
 const storage=openStorage();const a=new LikeStore(storage);a.set('a'.repeat(64),true);const b=new LikeStore(storage);assert.equal(b.state('a'.repeat(64)).liked,true);assert.equal(b.count().total,1);
});
