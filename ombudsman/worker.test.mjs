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
    assert.equal(values.has("last_report"),false);
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
