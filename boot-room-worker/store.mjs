import {validateFlightPath} from './flight-path.mjs';
export class RoomError extends Error {constructor(message,status=400){super(message);this.status=status;}}
export const DAY=86400000;
export const token=()=>Array.from(crypto.getRandomValues(new Uint8Array(32)),b=>b.toString(16).padStart(2,'0')).join('');
export async function digest(value){return Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',new TextEncoder().encode(value))),b=>b.toString(16).padStart(2,'0')).join('');}
const clean=(value,max)=>typeof value==='string'&&value.trim().length>0&&value.trim().length<=max&&!/[\u0000-\u0008\u000b-\u001f\u007f]/.test(value)?value.trim():null;
const validCallSign=value=>typeof value==='string'&&/^TF2AC [0-9]{5}$/.test(value);
const identity=p=>p.campaign?{campaign:p.campaign,moderator:p.moderator===true}:{};
function removeMessage(state,message,text){
 message.text=text;
 message.deleted=true;
 delete message.flightPath;
 message.hearts=[];
 state.reports=state.reports.filter(report=>report.message!==message.id);
}
export class RoomStore {
 constructor(storage,clock=Date.now){this.storage=storage;this.clock=clock;storage.sql.exec('CREATE TABLE IF NOT EXISTS room (id INTEGER PRIMARY KEY CHECK(id=1), data TEXT NOT NULL)');storage.sql.exec('INSERT OR IGNORE INTO room VALUES (1,?)',JSON.stringify({open:false,next:'Opening time to be announced',until:0,people:[],messages:[],reports:[],day:'',actions:0,joins:0}));}
 run(change){return this.storage.transactionSync(()=>{const s=JSON.parse(this.storage.sql.exec('SELECT data FROM room WHERE id=1').toArray()[0].data);const n=this.clock();s.messages=s.messages.filter(m=>m.at>n-7*DAY);s.reports=s.reports.filter(r=>r.at>n-7*DAY);s.people=s.people.filter(p=>p.expires>n);if(s.until<=n)s.open=false;const day=new Date(n).toISOString().slice(0,10);if(s.day!==day){s.day=day;s.actions=0;s.joins=0;}const result=change(s,n);this.storage.sql.exec('UPDATE room SET data=? WHERE id=1',JSON.stringify(s));return result;});}
 person(s,hash,n){const p=s.people.find(p=>p.session===hash&&p.expires>n&&!p.suspended);if(!p||(p.callSign&&s.people.some(other=>other.callSign===p.callSign&&other.suspended)))throw new RoomError('Invitation or session expired',401);return p;}
 view(s,p,n){const reported=new Set(s.reports.filter(r=>r.person===p.id).map(r=>r.message));return {open:s.open&&s.until>n,next:s.next,until:s.until,you:{id:p.id,name:p.name,...identity(p)},messages:s.messages.map(({flightPath,...m})=>({...m,...(flightPath?{hasFlightPath:true}:{}),hearts:m.hearts.length,hearted:m.hearts.includes(p.id),reported:reported.has(m.id)}))};}
 invite(name,hash,callSign,moderator=false){if(callSign&&!validCallSign(callSign))throw new RoomError('Use a Call Sign like TF2AC 01922');if(moderator===true&&!callSign)throw new RoomError('A moderator invitation needs a Call Sign');if(!(name=clean(name,40)))throw new RoomError('Use a pigeon name of 1–40 characters');return this.run((s,n)=>{if(callSign&&s.people.some(p=>p.callSign===callSign))throw new RoomError('That Call Sign already has a place',409);if(s.people.filter(p=>!p.walkIn).length>=10)throw new RoomError('Ten test places are already reserved',409);const p={id:crypto.randomUUID(),name,callSign:callSign||null,moderator:moderator===true,invite:hash,session:null,expires:n+7*DAY,suspended:false,last:0,burst:0};s.people.push(p);return {id:p.id,name,expires:p.expires};});}
 redeem(invite,session,claim){return this.run((s,n)=>{const p=s.people.find(p=>p.invite===invite&&!p.suspended&&p.expires>n);if(!p)throw new RoomError('Invitation is invalid, used or expired',401);if(p.callSign){
   const custodian=clean(claim?.custodian,100),fixture=clean(claim?.fixture,200);
   if(claim?.callSign!==p.callSign||claim?.name!==p.name||!custodian||!fixture)throw new RoomError('Open the Boot Room from the Campaign named on your invitation',403);
   p.campaign={callSign:p.callSign,custodian,fixture};
  }else if(claim)throw new RoomError('Use an invitation issued for this Campaign',403);
  p.invite=null;p.session=session;return {id:p.id,name:p.name};});}
 walkIn(claim,session,publicEntry=false){return this.run((s,n)=>{
  if(!s.open||!s.walkIn||s.until<=n)throw new RoomError('The Boot Room is still taking shape. Check the door for the next opening.',403);
  const name=clean(claim?.name,20),custodian=clean(claim?.custodian,100),fixture=clean(claim?.fixture,200),callSign=claim?.callSign;
  if(!name||!custodian||!fixture||!validCallSign(callSign))throw new RoomError('Open the Boot Room from your saved Campaign');
  const matches=s.people.filter(p=>p.callSign===callSign);
  const existing=publicEntry?matches.find(p=>p.walkIn&&(!p.session||p.session===session)):matches[0];
  if(matches.some(p=>p.suspended))throw new RoomError('This Campaign is suspended from the Boot Room',403);
  if(!publicEntry&&existing&&(existing.session||!existing.walkIn))throw new RoomError('This Call Sign already has a place. Reopen the room in the browser that joined.',409);
  if(!publicEntry&&!existing&&s.people.filter(p=>p.walkIn).length>=10)throw new RoomError('The first opening is full. Please check back for another opening.',409);
  const p=existing||{id:crypto.randomUUID(),walkIn:true,callSign,suspended:false,last:0,burst:0,expires:n+7*DAY};
  Object.assign(p,{name,campaign:{callSign,custodian,fixture},session,moderator:false});
  if(!existing)s.people.push(p);
  return {id:p.id,name};
 });}
 logout(hash){return this.run((s,n)=>{const p=this.person(s,hash,n);p.session=null;return {ok:true};});}
 snapshot(hash){return this.run((s,n)=>this.view(s,this.person(s,hash,n),n));}
 readClosed(){return this.run((s,n)=>{
  if(s.open&&s.until>n)throw new RoomError('The room is open. Join from My Campaign.',409);
  const messages=s.messages.filter(m=>!m.deleted).map(({id,name,campaign,text,at,replyTo,hearts,flightPath})=>({id,name,campaign,text,at,replyTo,hearts:hearts.length,...(flightPath?{hasFlightPath:true}:{})}));
  return {open:false,next:s.next,until:s.until,you:null,messages};
 });}
 flightPath(id,hash,publicRead){return this.run((s,n)=>{
  if(s.open||!publicRead)this.person(s,hash,n);
  const post=s.messages.find(m=>m.id===id&&!m.deleted&&m.flightPath);
  if(!post)throw new RoomError('This Flight Path is no longer available.',404);
  return post.flightPath;
 });}
 doors(){return this.run((s,n)=>({open:s.open&&s.until>n,next:s.next,until:s.until,...(s.open&&s.walkIn?{walkIn:true}:{}),...(s.chalkboard?{chalkboard:s.chalkboard}:{})}));}
 join(hash){return this.run((s,n)=>{const p=this.person(s,hash,n);if(s.joins>=200)throw new RoomError('Test connection allowance reached for today',429);s.joins++;return {id:p.id,hash};});}
 action(hash,a){return this.run((s,n)=>{const p=this.person(s,hash,n);if(!['report','delete-own'].includes(a?.type)&&(!s.open||s.until<=n))throw new RoomError('Barry has closed the room',403);if(n-p.last>=10000){p.last=n;p.burst=0;}if(p.burst>=5||s.actions>=2000)throw new RoomError('Easy, pigeon. Please pause before trying again.',429);if(!a||typeof a!=='object')throw new RoomError('Invalid action');let result;
 if(a.type==='message'){const text=clean(a.text,500);if(!text)throw new RoomError('Messages must contain 1–500 characters');const parent=a.replyTo?s.messages.find(m=>m.id===a.replyTo&&!m.deleted):null;if(a.replyTo&&!parent)throw new RoomError('Reply target is no longer available');let flightPath;
 if(a.flightPath!==undefined){
  if(!p.campaign)throw new RoomError('Open the Boot Room from your Campaign to attach a Flight Path.');
  try{flightPath=validateFlightPath(a.flightPath);}catch(error){throw new RoomError(error.message);}
 }
 const m={id:crypto.randomUUID(),person:p.id,name:p.name,...identity(p),text,at:n,replyTo:parent?.id||null,hearts:[],deleted:false,...(flightPath?{flightPath}:{})};s.messages.push(m);s.messages=s.messages.slice(-200);result={id:m.id};}
 else if(a.type==='heart'){const m=s.messages.find(m=>m.id===a.id&&!m.deleted);if(!m||typeof a.liked!=='boolean')throw new RoomError('Message unavailable');m.hearts=m.hearts.filter(id=>id!==p.id);if(a.liked)m.hearts.push(p.id);result={id:m.id};}
 else if(a.type==='delete-own'){
  const m=s.messages.find(m=>m.id===a.id&&m.person===p.id);
  if(!m)throw new RoomError('Message unavailable',404);
  if(!m.deleted)removeMessage(s,m,'Message deleted by its author');
  result={id:m.id};
 }
 else if(a.type==='report'){
  const m=s.messages.find(m=>m.id===a.id&&!m.deleted);
  if(!m)throw new RoomError('Message unavailable');
  const owns=r=>r.message===m.id&&r.person===p.id;
  if(a.reported===false)s.reports=s.reports.filter(r=>!owns(r));
  else if(!s.reports.some(owns)){
   s.reports.push({message:m.id,person:p.id,at:n});
   s.reports=s.reports.slice(-200);
  }
  result={reported:a.reported!==false,id:m.id};
 }
 else throw new RoomError('Unknown action');p.burst++;s.actions++;return result;});}
 admin(a){return this.run((s,n)=>{if(a.type==='doors'){if(typeof a.open!=='boolean'||typeof a.next!=='string'||a.next.length>100)throw new RoomError('Invalid opening details');if(a.open&&(!Number.isSafeInteger(a.until)||a.until<=n||a.until>n+16*3600000))throw new RoomError('Choose a closing time within the next 16 hours');s.open=a.open;s.walkIn=a.open&&a.walkIn===true;s.until=a.open?a.until:0;s.next=a.next;}
 else if(a.type==='delete'){const m=s.messages.find(m=>m.id===a.id);if(!m)throw new RoomError('Message unavailable',404);removeMessage(s,m,'Message removed by the landlord');}
 else if(a.type==='dismiss-reports'){
  s.reports=s.reports.filter(r=>r.message!==a.id);
 }
 else if(a.type==='chalkboard'){
  const limits={title:80,date:80,hours:80,followingTitle:80,followingDetails:160};
  const board={};
  for(const [key,max] of Object.entries(limits)){
   const raw=a.board?.[key];
   const value=clean(raw,max);
   if(!value&&(typeof raw!=='string'||raw.trim()||['title','date','hours'].includes(key)))throw new RoomError('Check the chalkboard fields');
   board[key]=value||'';
  }
  if(board.followingDetails&&!board.followingTitle)throw new RoomError('Give the following opening a title');
  s.chalkboard=board;
 }
 else if(a.type==='suspend'){const p=s.people.find(p=>p.id===a.id);if(!p)throw new RoomError('Participant unavailable',404);p.suspended=true;p.session=null;p.invite=null;}
 else if(a.type==='reinstate'){
  const p=s.people.find(p=>p.id===a.id);
  if(!p||!p.walkIn)throw new RoomError('Walk-in participant unavailable',404);
  p.suspended=false;
 }
 else if(a.type!=='status')throw new RoomError('Unknown action');return {open:s.open,next:s.next,until:s.until,walkIn:!!(s.open&&s.walkIn),chalkboard:s.chalkboard||null,people:s.people.map(({id,name,callSign,walkIn,suspended,expires})=>({id,name,callSign,walkIn,suspended,expires})),reports:s.reports.filter(r=>s.messages.some(m=>m.id===r.message&&!m.deleted)),messages:s.messages.map(({id,name,text,at,deleted})=>({id,name,text,at,deleted})),usage:{day:s.day,actions:s.actions,joins:s.joins}};});}
}
