import {test} from 'node:test';
import assert from 'node:assert/strict';
import {DatabaseSync} from 'node:sqlite';
import {RoomStore,RoomError,digest,token,DAY} from '../boot-room-worker/store.mjs';
function fixture(start=Date.now()){const db=new DatabaseSync(':memory:');const storage={sql:{exec(query,...args){const statement=db.prepare(query);return {toArray:()=>statement.all(...args)};}},transactionSync(fn){db.exec('BEGIN');try{const r=fn();db.exec('COMMIT');return r;}catch(e){db.exec('ROLLBACK');throw e;}}};storage.sql.exec=(query,...args)=>{const statement=db.prepare(query);if(statement.columns().length)return {toArray:()=>statement.all(...args)};statement.run(...args);return {toArray:()=>[]};};let time=start;const clock=()=>time;return {storage,room:new RoomStore(storage,clock),advance:n=>time+=n,now:clock};}
function join(f,name='Checky',i='invite',s='session'){f.room.invite(name,i);f.room.redeem(i,s);return s;}
function open(f){f.room.admin({type:'doors',open:true,until:f.now()+3600000,next:'Next matchday'});}
test('closed by default, invitations are single-use and credentials are hashed',async()=>{const f=fixture();const raw=token(),hash=await digest(raw);assert.equal(raw.length,64);assert.notEqual(hash,raw);f.room.invite('Checky',hash);assert.throws(()=>f.room.redeem(raw,'session'),RoomError);f.room.redeem(hash,'session');assert.throws(()=>f.room.redeem(hash,'other'));assert.equal(f.room.snapshot('session').open,false);assert.throws(()=>f.room.action('session',{type:'message',text:'hello'}),/closed/);});
test('two identities see persistent messages/replies/hearts; content is attributed by server',()=>{const f=fixture();const a=join(f),b=join(f,'Bert','invite2','session2');open(f);const m=f.room.action(a,{type:'message',text:'A pie please',name:'Fake Barry'});f.room.action(b,{type:'message',text:'Make that two',replyTo:m.id});f.room.action(b,{type:'heart',id:m.id,liked:true});f.room.action(b,{type:'heart',id:m.id,liked:true});const restarted=new RoomStore(f.storage,f.now);const d=restarted.snapshot(a);assert.equal(d.messages.length,2);assert.equal(d.messages[0].name,'Checky');assert.equal(d.messages[0].hearts,1);assert.equal(d.messages[1].replyTo,m.id);assert.equal(restarted.snapshot(b).messages[0].hearted,true);});
test('closing and closing deadline reject writes including hearts; history remains readable',()=>{const f=fixture();const a=join(f);open(f);const m=f.room.action(a,{type:'message',text:'Hello'});f.advance(3600001);assert.throws(()=>f.room.action(a,{type:'message',text:'Too late'}),/closed/);assert.equal(f.room.snapshot(a).messages.length,1);open(f);f.room.admin({type:'doors',open:false,next:'Tomorrow'});assert.throws(()=>f.room.action(a,{type:'heart',id:m.id,liked:true}),/closed/);});
test('report, remove, suspend: existing credentials cannot post or read afterwards',()=>{const f=fixture();const a=join(f),b=join(f,'Bert','i2','s2');open(f);const m=f.room.action(a,{type:'message',text:'bad text'});f.room.action(b,{type:'report',id:m.id});let admin=f.room.admin({type:'status'});assert.equal(admin.reports.length,1);f.room.admin({type:'delete',id:m.id});assert.equal(f.room.snapshot(b).messages[0].text,'Message removed by the landlord');assert.throws(()=>f.room.action(b,{type:'message',text:'reply',replyTo:m.id}),/no longer/);f.room.admin({type:'suspend',id:admin.people[0].id});assert.throws(()=>f.room.snapshot(a),/expired/);assert.throws(()=>f.room.action(a,{type:'message',text:'bypass'}),/expired/);assert.equal(f.room.snapshot(b).messages.length,1);});
test('bounded messages, text, rates, membership and retention',()=>{const f=fixture();const a=join(f);open(f);assert.throws(()=>f.room.action(a,{type:'message',text:'x'.repeat(501)}));for(let i=0;i<5;i++)f.room.action(a,{type:'message',text:'Hi'});assert.throws(()=>f.room.action(a,{type:'message',text:'Sixth'}),e=>e.status===429);f.advance(10001);f.room.action(a,{type:'message',text:'Allowed'});for(let i=1;i<10;i++)f.room.invite('Pigeon '+i,'i'+i);assert.throws(()=>f.room.invite('Eleventh','i11'),/Ten/);f.advance(7*DAY+1);const d=f.room.admin({type:'status'});assert.equal(d.messages.length,0);assert.equal(d.people.length,0);});
test('room retains at most 200 messages, global daily actions and joins are bounded',()=>{const f=fixture();const a=join(f);open(f);for(let i=0;i<201;i++){f.advance(10001);f.room.action(a,{type:'message',text:String(i)});}assert.equal(f.room.snapshot(a).messages.length,200);for(let i=0;i<200;i++)f.room.join(a);assert.throws(()=>f.room.join(a),e=>e.status===429);});

test('room daily action cap persists and resets the following day; logout revokes identity',()=>{const f=fixture(Date.UTC(2026,10,6));const a=join(f);f.room.admin({type:'doors',open:true,until:f.now()+12*3600000,next:'Tomorrow'});for(let i=0;i<2000;i++){f.advance(10001);f.room.action(a,{type:'message',text:'Message'});}assert.throws(()=>f.room.action(a,{type:'message',text:'Over allowance'}),e=>e.status===429);f.advance(DAY);open(f);f.room.action(a,{type:'message',text:'New day'});assert.equal(f.room.admin({type:'status'}).usage.actions,1);f.room.logout(a);assert.throws(()=>f.room.snapshot(a),e=>e.status===401);});

test('report receipts survive reconnect and are private to the reporting participant',()=>{const f=fixture();const a=join(f),b=join(f,'Bert','i2','s2');open(f);const m=f.room.action(a,{type:'message',text:'A test message'});f.room.admin({type:'doors',open:false,next:'Tomorrow'});const receipt=f.room.action(b,{type:'report',id:m.id});assert.equal(receipt.id,m.id);assert.equal(f.room.snapshot(b).messages[0].reported,true);assert.equal(f.room.snapshot(a).messages[0].reported,false);const reloaded=new RoomStore(f.storage,f.now);assert.equal(reloaded.snapshot(b).messages[0].reported,true);assert.equal(reloaded.admin({type:'status'}).reports.length,1);});
test('public door details expose no people, credentials, messages, reports or usage and respect expiry',()=>{
 const f=fixture();const a=join(f);open(f);const m=f.room.action(a,{type:'message',text:'Private conversation'});f.room.action(a,{type:'report',id:m.id});
 const doors=f.room.doors();assert.deepEqual(Object.keys(doors).sort(),['next','open','until']);assert.equal(doors.open,true);
 f.advance(3600001);assert.equal(f.room.doors().open,false);assert.equal(f.room.snapshot(a).messages.length,1);
});

// The advertised 09:00–23:45 day must fit one bounded landlord opening.
test('a full matchday closes exactly at the deadline and openings beyond sixteen hours are rejected',()=>{
 const f=fixture(),a=join(f),duration=(14*60+45)*60000;
 f.room.admin({type:'doors',open:true,until:f.now()+duration,next:'Monday draw'});
 f.advance(duration-1);assert.equal(f.room.doors().open,true);
 f.advance(1);assert.equal(f.room.doors().open,false);
 assert.throws(()=>f.room.action(a,{type:'message',text:'Too late'}),/closed/);
 assert.throws(()=>f.room.admin({type:'doors',open:true,until:f.now()+16*3600000+1,next:'Later'}),/16 hours/);
});

test('Campaign enrollment matches the invitation, and only the landlord assigns the badge',()=>{
 const f=fixture();
 const campaign={callSign:'TF2AC 01001',name:'Test Pigeon',custodian:'Example Town',fixture:'Example Town v Example United'};
 f.room.invite(campaign.name,'campaign-invite',campaign.callSign,true);
 assert.throws(()=>f.room.redeem('campaign-invite','wrong',{...campaign,callSign:'TF2AC 01002'}),e=>e.status===403);
 assert.throws(()=>f.room.redeem('campaign-invite','wrong'),e=>e.status===403);
 f.room.redeem('campaign-invite','campaign-session',campaign);
 const member=join(f,'Other Pigeon','ordinary-invite','ordinary-session');
 open(f);
 f.room.action('campaign-session',{type:'message',text:'Campaign check'});
 f.room.action(member,{type:'message',text:'Ordinary check',moderator:true,campaign});
 const [first,second]=f.room.snapshot(member).messages;
 assert.equal(first.campaign.callSign,campaign.callSign);
 assert.equal(first.campaign.fixture,campaign.fixture);
 assert.equal(first.moderator,true);
 assert.equal(second.moderator,undefined);
 assert.equal(second.campaign,undefined);
});

test('walk-in needs an enabled opening, remembers the Campaign and prevents suspended rejoining',()=>{
 const f=fixture();
 const claim={name:'Lab Pigeon',callSign:'TF2AC 01001',custodian:'Example Town',fixture:'Example Town v Example United',moderator:true};
 const walkIn=()=>f.room.walkIn(claim,'session');
 assert.throws(walkIn,e=>e.status===403);
 open(f);
 assert.throws(walkIn,e=>e.status===403);
 f.room.admin({type:'doors',open:true,walkIn:true,until:f.now()+3600000,next:'Next opening to be announced'});
 assert.equal(f.room.doors().walkIn,true);
 const guest=walkIn();
 const saved=f.room.snapshot('session').you;
 assert.equal(saved.campaign.callSign,claim.callSign);
 assert.equal(saved.moderator,false);
 assert.throws(walkIn,e=>e.status===409);
 f.room.action('session',{type:'message',text:'Lab reporting in'});
 f.room.admin({type:'suspend',id:guest.id});
 assert.throws(()=>f.room.snapshot('session'),e=>e.status===401);
 assert.throws(walkIn,e=>e.status===403);
 f.room.admin({type:'doors',open:false,next:'Check back for the next opening'});
 assert.equal(f.room.doors().walkIn,undefined);
});

test('reinstating a walk-in keeps the old session revoked and allows a fresh join',()=>{
 const f=fixture();
 const claim={name:'Test Pigeon',callSign:'TF2AC 01001',custodian:'Example Town',fixture:'Example Town v Example United'};
 f.room.admin({type:'doors',open:true,walkIn:true,until:f.now()+3600000,next:'Tomorrow'});
 const {id}=f.room.walkIn(claim,'old');
 f.room.admin({type:'suspend',id});
 const status=f.room.admin({type:'reinstate',id});
 assert.equal(status.people[0].callSign,claim.callSign);
 assert.throws(()=>f.room.snapshot('old'),e=>e.status===401);
 assert.equal(f.room.walkIn(claim,'fresh').id,id);
 assert.equal(f.room.snapshot('fresh').you.campaign.callSign,claim.callSign);
});

test('undo is private to the reporting pigeon and dismiss keeps the post',()=>{
 const f=fixture(),a=join(f),b=join(f,'Second','second-invite','second-session');
 open(f);
 const {id}=f.room.action(a,{type:'message',text:'Still here'});
 f.room.action(a,{type:'report',id});
 f.room.action(b,{type:'report',id});
 f.room.action(a,{type:'report',id,reported:false});
 assert.equal(f.room.snapshot(a).messages[0].reported,false);
 assert.equal(f.room.snapshot(b).messages[0].reported,true);
 const reviewed=f.room.admin({type:'dismiss-reports',id});
 assert.equal(reviewed.reports.length,0);
 assert.equal(reviewed.messages[0].text,'Still here');
});

test('saving the advertised opening keeps the live doors and timer separate',()=>{
 const f=fixture();
 const board={title:'First Round Proper',date:'Saturday 7 November',hours:'11am–11pm',followingTitle:'Monday’s Draw',followingDetails:'Details to follow'};
 f.room.admin({type:'chalkboard',board});
 assert.deepEqual(f.room.doors(),{open:false,next:'Opening time to be announced',until:0,chalkboard:board});
 open(f);
 const {until}=f.room.doors();
 f.room.admin({type:'chalkboard',board:{...board,hours:'Noon–11pm'}});
 assert.equal(f.room.doors().until,until);
 assert.equal(f.room.doors().open,true);
});

test('closed-room reading excludes removed messages and private member data',()=>{
 const f=fixture(),a=join(f);
 open(f);
 f.room.action(a,{type:'message',text:'See you next time'});
 assert.throws(()=>f.room.readClosed(),e=>e.status===409);
 f.room.admin({type:'doors',open:false,next:'Tomorrow'});
 const view=f.room.readClosed();
 assert.equal(view.you,null);
 assert.equal(view.messages[0].text,'See you next time');
 assert.deepEqual(Object.keys(view.messages[0]).sort(),['at','campaign','hearts','id','name','replyTo','text']);
});

test('public walk-ins accept fresh browsers and more than ten guests during an opening',()=>{
 const f=fixture();
 const claim={name:'Lab Pigeon',callSign:'TF2AC 01001',custodian:'Example Town',fixture:'Example Town v Example United'};
 f.room.admin({type:'doors',open:true,walkIn:true,until:f.now()+3600000,next:'Tomorrow'});
 const first=f.room.walkIn(claim,'browser',true);
 const kept=f.room.walkIn(claim,'home-screen',true);
 assert.notEqual(first.id,kept.id);
 assert.equal(f.room.snapshot('browser').you.id,first.id);
 assert.equal(f.room.snapshot('home-screen').you.moderator,false);
 for(let i=2;i<=12;i++)f.room.walkIn({...claim,callSign:'TF2AC '+String(1000+i).padStart(5,'0')},'guest-'+i,true);
 f.room.action('home-screen',{type:'message',text:'Home Screen reporting in'});
 f.room.admin({type:'suspend',id:first.id});
 assert.throws(()=>f.room.snapshot('home-screen'),e=>e.status===401);
 assert.throws(()=>f.room.walkIn(claim,'another-browser',true),e=>e.status===403);
 f.room.admin({type:'doors',open:false,next:'Tomorrow'});
 assert.throws(()=>f.room.walkIn({...claim,callSign:'TF2AC 01099'},'closed',true),e=>e.status===403);
});
