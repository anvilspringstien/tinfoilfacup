import test from "node:test";
import assert from "node:assert/strict";
import {classify,publish} from "./worker.mjs";
const now=Date.parse("2026-10-14T12:00:00Z");
const run=(overrides={})=>({id:123,event:"schedule",created_at:"2026-10-14T11:00:00Z",status:"completed",conclusion:"success",...overrides});
test("fresh successful schedule is healthy",()=>assert.equal(classify([run()],now).state,"healthy"));
test("old successful schedule is a missed-launch warning",()=>assert.equal(classify([run({created_at:"2026-10-14T07:00:00Z"})],now).reason,"no_recent_scheduled_launch"));
test("failed schedule is critical",()=>assert.equal(classify([run({conclusion:"failure"})],now).state,"critical"));
test("cancelled schedule is critical",()=>assert.equal(classify([run({conclusion:"cancelled"})],now).state,"critical"));
test("new pending run is not healthy",()=>assert.equal(classify([run({status:"in_progress",conclusion:null})],now).state,"pending"));
test("manual dispatch cannot masquerade as scheduled run",()=>assert.equal(classify([run({event:"workflow_dispatch"})],now).reason,"no_scheduled_runs"));
test("newest scheduled run wins",()=>assert.equal(classify([run({id:1,created_at:"2026-10-14T06:00:00Z"}),run({id:2})],now).run_id,2));
test("empty run history warns",()=>assert.equal(classify([],now).state,"warning"));
test("bad timestamps are unknown",()=>assert.equal(classify([run({created_at:"invalid"})],now).state,"unknown"));
test("stuck running schedule is critical",()=>assert.equal(classify([run({created_at:"2026-10-14T06:00:00Z",status:"in_progress",conclusion:null})],now).reason,"scheduled_run_stuck"));
test("fresh run following failure is recovery",()=>assert.equal(classify([run({id:1,created_at:"2026-10-14T05:00:00Z",conclusion:"failure"}),run({id:2})],now).state,"healthy"));

test("email warning sent once and recovery sent once",async()=>{
  const values=new Map(),sent=[];
  const kv={get:async k=>values.get(k)||null,put:async(k,v)=>values.set(k,v)};
  const oldFetch=globalThis.fetch;
  globalThis.fetch=async(_url,options)=>{sent.push(JSON.parse(options.body));return {ok:true,text:async()=>"OK"}};
  try {
    const env={OMBUDSMAN_KV:kv,ALERT_RELAY_URL:"https://script.google.com/macros/s/example/exec",ALERT_RELAY_SECRET:"test-secret"};
    const failed={state:"critical",checks:{results:{state:"critical",reason:"scheduled_run_failure"}}};
    const recovered={state:"healthy",checks:{results:{state:"healthy",reason:"recent_scheduled_success"}}};
    await publish(failed,env);await publish(failed,env);await publish(recovered,env);
    assert.equal(sent.length,2);
    assert.deepEqual(sent.map(x=>x.subject),["TFFC Ombudsman: CRITICAL","TFFC Ombudsman: HEALTHY"]);
    assert.equal(sent[0].secret,"test-secret");
    assert.match(sent[0].message,/results: critical/);
  } finally {globalThis.fetch=oldFetch}
});
test("unconfirmed relay response does not mark warning delivered",async()=>{
  const values=new Map(),kv={get:async k=>values.get(k)||null,put:async(k,v)=>values.set(k,v)};
  const oldFetch=globalThis.fetch;
  globalThis.fetch=async()=>({ok:true,text:async()=>"Request not processed"});
  try {
    await assert.rejects(publish({state:"critical"}, {OMBUDSMAN_KV:kv,ALERT_RELAY_URL:"https://example.invalid/relay",ALERT_RELAY_SECRET:"secret"}),/email_relay_delivery_unconfirmed/);
    assert.equal(JSON.parse(values.get("last_report")).report.state,"critical");
    assert.equal(JSON.parse(values.get("notification_state_v2")).notified,false);
  } finally {globalThis.fetch=oldFetch}
});
test("initial healthy report does not email",async()=>{
  const values=new Map(),kv={get:async k=>values.get(k)||null,put:async(k,v)=>values.set(k,v)};
  const oldFetch=globalThis.fetch;
  globalThis.fetch=async()=>{throw new Error("unexpected email")};
  try {
    const result=await publish({state:"healthy",checks:{}},{OMBUDSMAN_KV:kv,ALERT_RELAY_URL:"https://example.invalid/relay",ALERT_RELAY_SECRET:"secret"});
    assert.equal(result.delivered,false);
  } finally {globalThis.fetch=oldFetch}
});

test("test-email endpoint requires POST and bearer token, and never touches KV",async()=>{
  const {default:worker}=await import("./worker.mjs");
  const kv={get:async()=>{throw new Error("KV read")},put:async()=>{throw new Error("KV write")}};
  const env={STATUS_TOKEN:"health-secret",OMBUDSMAN_KV:kv,ALERT_RELAY_URL:"https://example.invalid/relay",ALERT_RELAY_SECRET:"relay-secret"};
  const oldFetch=globalThis.fetch;
  const sent=[];
  globalThis.fetch=async(_url,options)=>{sent.push(JSON.parse(options.body));return {ok:true,text:async()=>"OK"}};
  try {
    const url="https://ombudsman.example/test-email";
    assert.equal((await worker.fetch(new Request(url,{method:"GET",headers:{Authorization:"Bearer health-secret"}}),env)).status,405);
    assert.equal((await worker.fetch(new Request(url,{method:"POST"}),env)).status,401);
    assert.equal((await worker.fetch(new Request(url,{method:"POST",headers:{Authorization:"Bearer wrong"}}),env)).status,401);
    const result=await worker.fetch(new Request(url,{method:"POST",headers:{Authorization:"Bearer health-secret"}}),env);
    assert.equal(result.status,200);
    assert.equal((await result.json()).status,"sent");
    assert.equal(sent.length,1);
    assert.equal(sent[0].subject,"TFFC Ombudsman: TEST");
    assert.match(sent[0].message,/TEST ONLY/);
  } finally {globalThis.fetch=oldFetch}
});
test("test-email endpoint returns failure when relay does not confirm",async()=>{
  const {default:worker}=await import("./worker.mjs");
  const oldFetch=globalThis.fetch;
  globalThis.fetch=async()=>({ok:true,text:async()=>"Request not processed"});
  try {
    const result=await worker.fetch(new Request("https://ombudsman.example/test-email",{method:"POST",headers:{Authorization:"Bearer health-secret"}}),{STATUS_TOKEN:"health-secret",ALERT_RELAY_URL:"https://example.invalid/relay",ALERT_RELAY_SECRET:"relay-secret"});
    assert.equal(result.status,502);
  } finally {globalThis.fetch=oldFetch}
});
async function policy(fn){const values=new Map(),sent=[],old=globalThis.fetch;const env={OMBUDSMAN_KV:{get:async k=>values.get(k)||null,put:async(k,v)=>values.set(k,v)},ALERT_RELAY_URL:'https://example.invalid/relay',ALERT_RELAY_SECRET:'fixture'};globalThis.fetch=async(_u,o)=>{sent.push(JSON.parse(o.body));return {ok:true,text:async()=>'OK'}};try{await fn({values,sent,env});}finally{globalThis.fetch=old;}}
const warning=(name='draw',age=6)=>({state:'warning',checks:{[name]:{state:'warning',reason:'no_recent_scheduled_launch',age_hours:age}}});
test('brief gap and unnotified recovery send no email; raw warning stays visible',()=>policy(async({env,sent,values})=>{await publish(warning('draw',3.2),env,now);assert.equal(JSON.parse(values.get('last_report')).report.state,'warning');await publish(warning('results',4),env,now+600000);await publish({state:'pending'},env,now+1200000);await publish({state:'healthy'},env,now+1800000);assert.equal(sent.length,0);}));
test('persistent gap emails once across alternating scanners and pending launches; one recovery',()=>policy(async({env,sent})=>{await publish(warning(),env,now);await publish(warning('results',7),env,now+600000);await publish({state:'pending'},env,now+1200000);await publish(warning(),env,now+1800000);assert.equal(sent.length,1);await publish({state:'healthy'},env,now+2400000);await publish({state:'healthy'},env,now+3000000);assert.deepEqual(sent.map(x=>x.subject),['TFFC Ombudsman: WARNING','TFFC Ombudsman: HEALTHY']);}));
test('new failed run escalates immediately but unchanged failure does not repeat',()=>policy(async({env,sent})=>{await publish(warning(),env,now);const fail=id=>({state:'critical',checks:{results:{state:'critical',reason:'scheduled_run_failure',run_id:id}}});await publish(fail(99),env,now+1);await publish(fail(99),env,now+2);await publish(fail(100),env,now+3);assert.equal(sent.length,3);assert.match(sent[1].subject,/CRITICAL/);}));
test('unresolved problem sends at most one reminder per day',()=>policy(async({env,sent})=>{await publish(warning(),env,now);await publish(warning(),env,now+23*3600000);assert.equal(sent.length,1);await publish(warning(),env,now+24*3600000);await publish(warning(),env,now+25*3600000);assert.equal(sent.length,2);}));
test('unknown API state waits thirty minutes and never becomes healthy',()=>policy(async({env,sent,values})=>{const r={state:'unknown',reason:'api_unavailable_or_error'};await publish(r,env,now);await publish(r,env,now+29*60000);assert.equal(sent.length,0);await publish(r,env,now+30*60000);assert.equal(sent.length,1);assert.equal(JSON.parse(values.get('last_report')).report.state,'unknown');}));
test('legacy warning migration avoids duplicate alert and retains recovery',()=>policy(async({env,sent,values})=>{values.set('last_report',JSON.stringify({key:'old',report:warning()}));await publish(warning('results',7),env,now);assert.equal(sent.length,0);await publish({state:'healthy'},env,now+1);assert.equal(sent.length,1);assert.match(sent[0].subject,/HEALTHY/);}));

test('an unconfirmed first warning is retried and cannot seed a false legacy delivered state',()=>policy(async({env,sent,values})=>{
 const good=globalThis.fetch;globalThis.fetch=async()=>({ok:true,text:async()=>'NOT OK'});
 await assert.rejects(publish(warning(),env,now),/unconfirmed/);assert.equal(JSON.parse(values.get('notification_state_v2')).notified,false);
 globalThis.fetch=good;await publish(warning(),env,now+1);assert.equal(sent.length,1);
 globalThis.fetch=async()=>({ok:true,text:async()=>'NOT OK'});await assert.rejects(publish({state:'healthy'},env,now+2),/unconfirmed/);
 assert.equal(JSON.parse(values.get('notification_state_v2')).notified,true);globalThis.fetch=good;await publish({state:'healthy'},env,now+3);assert.equal(sent.length,2);
}));
