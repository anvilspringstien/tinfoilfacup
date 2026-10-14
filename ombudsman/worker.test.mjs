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

test("failure alert is sent once, recovery sends a fresh alert",async()=>{
  const values=new Map(), sent=[];
  const kv={get:async k=>values.get(k)||null,put:async(k,v)=>{values.set(k,v)}};
  const oldFetch=globalThis.fetch;
  globalThis.fetch=async(_url,options)=>{sent.push(JSON.parse(options.body));return {ok:true}};
  try {
    const env={OMBUDSMAN_KV:kv,ALERT_WEBHOOK_URL:"https://example.invalid/hook"};
    const failed={state:"critical",checks:{results:{state:"critical",reason:"scheduled_run_failure"}}};
    const recovered={state:"healthy",checks:{results:{state:"healthy",reason:"recent_scheduled_success"}}};
    await publish(failed,env);await publish(failed,env);await publish(recovered,env);
    assert.equal(sent.length,2);
    assert.deepEqual(sent.map(x=>x.report.state),["critical","healthy"]);
  } finally {globalThis.fetch=oldFetch}
});
test("failed webhook delivery does not mark alert delivered",async()=>{
  const values=new Map(), kv={get:async k=>values.get(k)||null,put:async(k,v)=>values.set(k,v)};
  const oldFetch=globalThis.fetch;
  globalThis.fetch=async()=>({ok:false,status:503});
  try {
    await assert.rejects(publish({state:"critical"}, {OMBUDSMAN_KV:kv,ALERT_WEBHOOK_URL:"https://example.invalid/hook"}),/alert_delivery_failed_503/);
    assert.equal(values.has("last_report"),false);
  } finally {globalThis.fetch=oldFetch}
});
