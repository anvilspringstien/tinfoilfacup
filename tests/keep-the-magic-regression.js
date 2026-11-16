'use strict';
const assert=require('node:assert/strict');
const {KEYS,create,validate,restore}=require('../beta/keep-the-magic-data.js');
function memory(seed={}){
 const m={...seed};
 return {getItem:k=>Object.prototype.hasOwnProperty.call(m,k)?m[k]:null,
 setItem:(k,v)=>{m[k]=String(v)},removeItem:k=>{delete m[k]}};
}
const data={
 [KEYS[0]]:JSON.stringify({searchNumber:1234,pigeonName:'Barry'}),
 [KEYS[1]]:JSON.stringify({version:1,completed:[1,2]}),
 [KEYS[2]]:JSON.stringify({campaignKey:'a'}),
 [KEYS[3]]:JSON.stringify({searchNumber:1234})
};
const original=memory(data);const doc=create(original,new Date('2026-10-13T08:00:00Z'));
assert.equal(doc.created_at,'2026-10-13T08:00:00.000Z');
assert.equal(Object.keys(doc.data).length,4);
assert.deepEqual({...validate(JSON.stringify(doc))},data);
const target=memory({[KEYS[0]]:JSON.stringify({pigeonName:'Old'}),extra:'untouched'});
assert.equal(restore(target,JSON.stringify(doc)),4);
assert.deepEqual(Object.fromEntries(KEYS.map(k=>[k,target.getItem(k)])),data);
assert.equal(target.getItem('extra'),'untouched');
assert.throws(()=>validate(JSON.stringify({...doc,version:2})),/supported/);
assert.throws(()=>validate(JSON.stringify({...doc,data:{'__evil':'{}'}})),/Unexpected storage key/);
assert.throws(()=>validate(JSON.stringify({...doc,data:{[KEYS[0]]:'not-json'}})),/Invalid saved progress/);
const partial={...doc,data:{[KEYS[0]]:data[KEYS[0]]}};
restore(target,partial);assert.equal(target.getItem(KEYS[1]),null);
assert.equal(target.getItem(KEYS[0]),data[KEYS[0]]);
assert.deepEqual(create(memory()).data,{});
console.log('Keep the Magic backup/restore regression passed.');