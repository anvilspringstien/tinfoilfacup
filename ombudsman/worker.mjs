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
async function publish(report,env) {
  if(!env.OMBUDSMAN_KV) return {delivered:false,reason:"no_state_store"};
  const key=JSON.stringify({state:report.state,reason:report.reason,checks:Object.fromEntries(Object.entries(report.checks||{}).map(([k,v])=>[k,{state:v.state,reason:v.reason}]))});
  const prev=await env.OMBUDSMAN_KV.get("last_report");
  const old=prev?JSON.parse(prev):null;
  const changed=!old||old.key!==key;
  const oldState=old?.report?.state;
  const needsEmail=changed && (["critical","warning","unknown"].includes(report.state) || (report.state==="healthy" && ["critical","warning","unknown"].includes(oldState)));
  let delivered=false;
  if(needsEmail && env.ALERT_RELAY_URL && env.ALERT_RELAY_SECRET) {
    await deliverEmail(report,env);
    delivered=true;
  } else if(changed && env.ALERT_WEBHOOK_URL && !env.ALERT_RELAY_URL) {
    const response=await fetch(env.ALERT_WEBHOOK_URL,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({text:"TFFC Ombudsman: "+report.state+"\\n"+JSON.stringify(report),report})});
    if(!response.ok) throw new Error("alert_delivery_failed_"+response.status);
    delivered=true;
  }
  await env.OMBUDSMAN_KV.put("last_report",JSON.stringify({key,report}));
  return {delivered,changed};
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
    if(new URL(request.url).pathname!=="/health") return new Response("Not found",{status:404});
    if(!env.STATUS_TOKEN || request.headers.get("Authorization")!=="Bearer "+env.STATUS_TOKEN) return new Response("Unauthorized",{status:401});
    const report=env.OMBUDSMAN_KV?JSON.parse((await env.OMBUDSMAN_KV.get("last_report"))||"null"):null;
    return Response.json(report?.report||{state:"unknown",reason:"no_report_yet"});
  }
};
export {classify,check,publish,inspect};
