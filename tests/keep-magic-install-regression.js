'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const backup=require('../beta/keep-the-magic-data.js');
const source=fs.readFileSync('beta/keep-magic-install.js','utf8');
function environment(seed={},cookieSeed={}){
 const data={...seed},jar={...cookieSeed},writes=[];
 const storage={getItem:k=>data[k]??null,setItem:(k,v)=>{data[k]=v},removeItem:k=>{delete data[k]}};
 const doc={get cookie(){return Object.entries(jar).map(([k,v])=>k+'='+v).join('; ')},set cookie(value){writes.push(value);const [pair,...flags]=value.split('; '),[k,v]=pair.split('=');if(flags.includes('Max-Age=0'))delete jar[k];else jar[k]=v;}};
 const ctx={window:{TffcMagicBackup:backup},localStorage:storage,document:doc,location:{protocol:'https:'},Blob,CompressionStream,DecompressionStream,TextEncoder,TextDecoder,Uint8Array,btoa,atob};
 vm.createContext(ctx);vm.runInContext(source,ctx);return {api:ctx.window.TffcMagicInstall,data,jar,writes,storage,ctx};
}
(async()=>{
 const state={
  [backup.KEYS[0]]:JSON.stringify({originName:'Heaton Stannington FC',postcode:'NE6 5NL',searchNumber:1755,callSign:'Tango Foxtrot 2 Alpha Charlie [01755]',pigeonName:'Checky'}),
  [backup.KEYS[1]]:JSON.stringify({version:1,campaignKey:'heaton',completed:{one:true,two:true,three:true,four:true},pigeonMiles:766,campaignRound:4}),
  [backup.KEYS[2]]:JSON.stringify({campaignKey:'heaton',pigeonName:'Checky'}),
  [backup.KEYS[3]]:JSON.stringify({searchNumber:1755,pigeonName:'Checky'})
 };
 const browser=environment(state);assert.equal(await browser.api.prepare(),'ready');
 assert(browser.writes.every(s=>s.includes('Path=/beta/keep-the-magic-shed.html')&&s.includes('SameSite=Strict')&&s.includes('Secure')));
 assert(Object.entries(browser.jar).reduce((n,[k,v])=>n+k.length+v.length+2,0)<6000);
 const app=environment({},browser.jar);assert.equal(await app.api.restore(),'restored');
 assert.deepEqual(app.data,state);assert.deepEqual(app.jar,{});assert.equal(await app.api.restore(),'empty');
 // An installed app's later progress takes precedence over the install copy.
 const later=environment({[backup.KEYS[0]]:'{"pigeonName":"Later"}'},browser.jar);
 assert.equal(await later.api.restore(),'existing');assert.equal(later.data[backup.KEYS[0]],'{"pigeonName":"Later"}');assert.deepEqual(later.jar,{});
 // Corruption and missing chunks cannot produce a partial new Campaign.
 for(const jar of [{...browser.jar,tffc_keep_v1:'2'},{...browser.jar,tffc_keep_v1_0:'invalid'},{tffc_keep_v1_0:'orphan'}]){
  const broken=environment({},jar);await assert.rejects(()=>broken.api.restore());assert.deepEqual(broken.data,{});assert(broken.api.present());
 }
 const quota=environment({},browser.jar);let fail=true;
 quota.storage.setItem=(k,v)=>{if(fail&&k===backup.KEYS[1]){fail=false;throw Error('Quota')}quota.data[k]=v;};
 await assert.rejects(()=>quota.api.restore(),/Restore/);assert.deepEqual(quota.data,{});assert(quota.api.present());
 const expired=environment(state);
 // factory captures its API; replace create temporarily for this controlled producer.
 const create=backup.create;try{backup.create=storage=>create(storage,new Date('2020-01-01'));await expired.api.prepare();}finally{backup.create=create;}
 const stale=environment({},expired.jar);await assert.rejects(()=>stale.api.restore(),/expired/);assert.deepEqual(stale.data,{});
 // A large history must fail visibly rather than copy only its identity.
 const huge=environment({...state,[backup.KEYS[1]]:JSON.stringify({records:require('node:crypto').randomBytes(12000).toString('hex')})});
 await assert.rejects(()=>huge.api.prepare(),/backup file/);assert.deepEqual(huge.jar,{});
 const blocked=environment(state);Object.defineProperty(blocked.ctx.document,'cookie',{get:()=>'',set:()=>{}});
 await assert.rejects(()=>blocked.api.prepare(),/unavailable/);
 const empty=environment({},browser.jar);assert.equal(await empty.api.prepare(),'empty');assert.deepEqual(empty.jar,{});
 console.log('KEEP INSTALL HANDOVER: PASS — cookies only into empty storage; identity, Pigeon and Challenge bytes preserved; existing progress, partial/invalid/expired data, quota, size and blocked cookies protected.');
})().catch(e=>{console.error(e);process.exitCode=1});
