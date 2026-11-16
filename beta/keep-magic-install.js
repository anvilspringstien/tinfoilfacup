/* One-time browser -> Home Screen handover. iOS 17.2+ copies cookies, not
   localStorage. Limit cookies to the installed entry path and consume them
   before Splash; never put Campaign details in the shared URL or manifest. */
(function(root){
'use strict';
const PREFIX='tffc_keep_v1',PATH='/beta/keep-the-magic-shed.html';
const LIMIT=5600,CHUNK=2800,AGE=7*24*60*60;
const backup=root.TffcMagicBackup;
function cookies(){return Object.fromEntries(document.cookie.split(';').map(s=>s.trim().split(/=(.*)/s)).filter(a=>a[0]));}
function write(name,value,age){document.cookie=name+'='+value+'; Path='+PATH+'; Max-Age='+age+'; SameSite=Strict'+(location.protocol==='https:'?'; Secure':'');}
function clear(){for(const name of [PREFIX,PREFIX+'_0',PREFIX+'_1'])write(name,'',0);}
function present(){return Object.keys(cookies()).some(k=>k===PREFIX||k.startsWith(PREFIX+'_'));}
async function transform(bytes,type){
 const stream=new Blob([bytes]).stream().pipeThrough(type==='pack'?new CompressionStream('gzip'):new DecompressionStream('gzip'));
 const reader=stream.getReader(),parts=[];let size=0;
 try{for(;;){const {value,done}=await reader.read();if(done)break;size+=value.length;if(size>2000000)throw Error('Saved progress is too large');parts.push(value);}}finally{reader.releaseLock();}
 const result=new Uint8Array(size);let offset=0;for(const part of parts){result.set(part,offset);offset+=part.length;}return result;
}
async function prepare(){
 clear();
 const doc=backup.create(localStorage);
 if(!Object.keys(doc.data).length)return 'empty';
 const packed=await transform(new TextEncoder().encode(JSON.stringify(doc)),'pack');
 const value=btoa(Array.from(packed,b=>String.fromCharCode(b)).join('')).replace(/\+/g,'-').replace(/\//g,'_').replace(/=+$/,'');
 if(value.length>LIMIT)throw Error('Saved progress needs a backup file');
 const count=Math.ceil(value.length/CHUNK);
 for(let i=0;i<count;i++)write(PREFIX+'_'+i,value.slice(i*CHUNK,(i+1)*CHUNK),AGE);
 write(PREFIX,String(count),AGE);
 const saved=cookies();
 if(saved[PREFIX]!==String(count)||Array.from({length:count},(_,i)=>saved[PREFIX+'_'+i]||'').join('')!==value){clear();throw Error('Installation cookies are unavailable');}
 return 'ready';
}
async function restore(){
 if(!present())return 'empty';
 // Existing installed progress always wins, including a later hard reset's
 // surviving identity/Challenge records. Never replay an old install snapshot.
 if(backup.KEYS.some(key=>localStorage.getItem(key)!==null)){clear();return 'existing';}
 const saved=cookies(),count=Number(saved[PREFIX]);
 if(!Number.isInteger(count)||count<1||count>2)throw Error('Incomplete installation handover');
 const value=Array.from({length:count},(_,i)=>saved[PREFIX+'_'+i]||'').join('');
 if(!value||value.length>LIMIT||Array.from({length:count},(_,i)=>saved[PREFIX+'_'+i]).some(x=>!x)||!/^[\w-]+$/.test(value))throw Error('Incomplete installation handover');
 const packed=Uint8Array.from(atob(value.replace(/-/g,'+').replace(/_/g,'/')),c=>c.charCodeAt(0));
 const raw=new TextDecoder('utf-8',{fatal:true}).decode(await transform(packed,'unpack'));
 const doc=JSON.parse(raw),created=Date.parse(doc.created_at);
 if(!Number.isFinite(created)||Date.now()-created>AGE*1000||created>Date.now()+60000)throw Error('Installation handover has expired');
 backup.restore(localStorage,doc);
 clear();return 'restored';
}
root.TffcMagicInstall={prepare,restore,present,clear};
})(window);
