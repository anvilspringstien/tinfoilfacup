// Independent, read-only GitHub Actions ombudsman. Cloudflare Worker (no GitHub scheduler dependency).
const REPO = "anvilspringstien/tinfoilfacup";
const API = "https://api.github.com/repos/" + REPO;
const HOUR = 3600000;
function classify(runs, now, maxAgeHours = 3) {
  if (!Array.isArray(runs)) return { state: "unknown", reason: "no_run_data" };
  const relevant = runs.filter(r => r.event === "schedule").sort((a,b) => Date.parse(b.created_at)-Date.parse(a.created_at));
  if (!relevant.length) return { state: "warning", reason: "no_scheduled_runs" };
  const run = relevant[0], ageMs = now - Date.parse(run.created_at);
  const pendingMs = now - Date.parse(run.run_started_at || run.created_at);
  if (!Number.isFinite(ageMs) || ageMs < -5*60000) return { state:"unknown", reason:"invalid_run_time" };
  if (run.status === "completed" && run.conclusion !== "success") return {state:"critical",reason:"scheduled_run_"+run.conclusion,run_id:run.id,age_hours:Math.round(ageMs/HOUR*10)/10};
  if (run.status !== "completed" && pendingMs > maxAgeHours*HOUR) return {state:"critical",reason:"scheduled_run_stuck",run_id:run.id,age_hours:Math.round(pendingMs/HOUR*10)/10};
  if (ageMs > maxAgeHours*HOUR) return {state:"warning",reason:"no_recent_scheduled_launch",run_id:run.id,age_hours:Math.round(ageMs/HOUR*10)/10};
  if (run.status !== "completed") return {state:"pending",reason:"scheduled_run_"+run.status,run_id:run.id};
  return {state:"healthy",reason:"recent_scheduled_success",run_id:run.id};
}
async function github(path, env) {
  const headers = {"Accept":"application/vnd.github+json","User-Agent":"tffc-independent-ombudsman","X-GitHub-Api-Version":"2022-11-28"};
  if (env.GITHUB_TOKEN) headers.Authorization = "Bearer " + env.GITHUB_TOKEN;
  const res = await fetch(API+path,{headers,cf:{cacheTtl:0}});
  if (!res.ok) throw new Error("GitHub API HTTP "+res.status);
  return res.json();
}
async function check(env) {
  const now=Date.now(), maxAge=Math.max(1,Number(env.MAX_AGE_HOURS||3));
  const targets=[["results",env.RESULTS_WORKFLOW_ID||"scan-results.yml"],["draw",env.DRAW_WORKFLOW_ID||"scan-draw.yml"]];
  if(targets.some(([,id])=>!id)) return {state:"unknown",reason:"workflow_ids_not_configured"};
  const checks={};
  for(const [name,id] of targets) {
    const data=await github("/actions/workflows/"+encodeURIComponent(id)+"/runs?event=schedule&branch=main&per_page=30",env);
    checks[name]=classify(data.workflow_runs,now,maxAge);
  }
  const states=Object.values(checks).map(x=>x.state);
  const state=states.includes("critical")?"critical":states.includes("warning")?"warning":states.includes("unknown")?"unknown":states.includes("pending")?"pending":"healthy";
  return {state,checked_at:new Date(now).toISOString(),checks};
}
function alertText(report) {
  const lines=["TFFC Ombudsman: "+String(report.state||"unknown").toUpperCase(),"Checked: "+(report.checked_at||"unknown")];
  for(const [name,check] of Object.entries(report.checks||{})) {
    lines.push(name+": "+check.state+" ("+check.reason+")"+(check.run_id?" | run "+check.run_id:""));
  }
  if(report.reason) lines.push("Reason: "+report.reason);
  return lines.join("\n");
}
async function deliverEmail(report,env) {
  if(!env.ALERT_RELAY_URL || !env.ALERT_RELAY_SECRET) throw new Error("email_relay_not_configured");
  const response=await fetch(env.ALERT_RELAY_URL,{
    method:"POST",headers:{"Content-Type":"text/plain;charset=utf-8"},
    body:JSON.stringify({secret:env.ALERT_RELAY_SECRET,subject:"TFFC Ombudsman: "+report.state.toUpperCase(),message:alertText(report)}),
    redirect:"follow"
  });
  // Apps Script ContentService can return HTTP 200 even on a caught error.
  if(!response.ok || (await response.text()).trim()!=="OK") throw new Error("email_relay_delivery_unconfirmed");
}
// Notification state is separate from the raw health report. A pending launch is
// not recovery, and switching which scanner is late is not a new incident.
async function publish(report,env,now=Date.now()) {
  if(!env.OMBUDSMAN_KV) return {delivered:false,reason:'no_state_store'};
  const kv=env.OMBUDSMAN_KV;
  const previous=JSON.parse((await kv.get('last_report'))||'null');
  let state=JSON.parse((await kv.get('notification_state_v2'))||'null');
  if(!state) {
    // A legacy warning may already have emailed: retain one recovery, without
    // immediately repeating the warning during migration.
    const old=previous?.report;
    const alerted=old&&['critical','warning','unknown'].includes(old.state);
    const legacyCritical=Object.entries(old?.checks||{}).filter(([,c])=>c.state==='critical').map(([name,c])=>name+':'+c.reason+':'+(c.run_id||''));
    if(old?.state==='critical'&&!legacyCritical.length)legacyCritical.push('overall:'+old.reason);
    state={since:null,unknownSince:null,notified:!!alerted,lastSent:alerted?now:0,criticalKeys:legacyCritical};
  }
  const checks=Object.entries(report.checks||{});
  const problems=checks.filter(([,c])=>['critical','warning','unknown'].includes(c.state));
  const bad=['critical','warning','unknown'].includes(report.state);
  const healthy=report.state==='healthy';
  if(bad&&state.since===null)state.since=now;
  if(report.state==='unknown'||problems.some(([,c])=>c.state==='unknown'))state.unknownSince??=now;
  else state.unknownSince=null;
  const criticalKeys=checks.filter(([,c])=>c.state==='critical').map(([name,c])=>name+':'+c.reason+':'+(c.run_id||''));
  if(report.state==='critical'&&!criticalKeys.length)criticalKeys.push('overall:'+report.reason);
  const newCritical=criticalKeys.some(k=>!state.criticalKeys.includes(k));
  const persistentWarning=problems.some(([,c])=>c.state==='warning'&&
    (Number.isFinite(c.age_hours)?c.age_hours>=6:now-state.since>=3*HOUR));
  const persistentUnknown=state.unknownSince!==null&&now-state.unknownSince>=30*60000;
  const eligible=newCritical||persistentWarning||persistentUnknown;
  const recovery=healthy&&state.notified;
  const reminder=state.notified&&bad&&now-state.lastSent>=24*HOUR;
  const needsAlert=recovery||newCritical||(!state.notified&&eligible)||reminder;
  // Always expose the current true observation; notification deferral never
  // labels a stale or unavailable scanner healthy.
  await kv.put('last_report',JSON.stringify({report}));
  // Persist the unconsumed decision before relay I/O, so a delivery failure
  // cannot be mistaken for a previously notified legacy incident on retry.
  await kv.put('notification_state_v2',JSON.stringify(state));
  let delivered=false;
  if(needsAlert) {
    if(env.ALERT_RELAY_URL&&env.ALERT_RELAY_SECRET) {
      await deliverEmail(report,env);delivered=true;
    } else if(env.ALERT_WEBHOOK_URL&&!env.ALERT_RELAY_URL) {
      const response=await fetch(env.ALERT_WEBHOOK_URL,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({text:'TFFC Ombudsman: '+report.state+'\n'+alertText(report),report})});
      if(!response.ok)throw new Error('alert_delivery_failed_'+response.status);
      delivered=true;
    }
    // Failed or absent delivery must not consume the notification or recovery.
    if(delivered){state.notified=!recovery;state.lastSent=now;state.criticalKeys=[...new Set([...state.criticalKeys,...criticalKeys])];}
  }
  if(healthy&&(!state.notified||delivered))state={since:null,unknownSince:null,notified:false,lastSent:0,criticalKeys:[]};
  await kv.put('notification_state_v2',JSON.stringify(state));
  return {delivered,deferred:bad&&!needsAlert};
}
async function inspect(env) {
  let report;
  try {report=await check(env);} catch(e) {report={state:"unknown",reason:"api_unavailable_or_error",detail:String(e.message||e)};}
  await publish(report,env);
  return report;
}
export default {
  async scheduled(_event,env,ctx){ctx.waitUntil(inspect(env));},
  async fetch(request,env){
    const pathname=new URL(request.url).pathname;
    if(pathname!=="/health" && pathname!=="/test-email") return new Response("Not found",{status:404});
    if(pathname==="/test-email" && request.method!=="POST") return new Response("Method not allowed",{status:405,headers:{"Allow":"POST"}});
    if(!env.STATUS_TOKEN || request.headers.get("Authorization")!=="Bearer "+env.STATUS_TOKEN) return new Response("Unauthorized",{status:401});
    if(pathname==="/test-email") {
      const report={state:"test",checked_at:new Date().toISOString(),reason:"TEST ONLY — email relay delivery check; no scanner failure"};
      try {
        await deliverEmail(report,env);
        return Response.json({status:"sent"});
      } catch(e) {
        console.error("Ombudsman test email failed:",String(e.message||e));
        return Response.json({status:"failed",reason:"email_relay_delivery_unconfirmed"},{status:502});
      }
    }
    const report=env.OMBUDSMAN_KV?JSON.parse((await env.OMBUDSMAN_KV.get("last_report"))||"null"):null;
    return Response.json(report?.report||{state:"unknown",reason:"no_report_yet"});
  }
};
export {classify,check,publish,inspect};
