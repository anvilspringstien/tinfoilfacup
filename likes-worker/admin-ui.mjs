// The page contains no credentials or counts. Only the authenticated count route reads storage.
export const adminDocument = `<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>TFFAC · Your Likes</title><link rel="stylesheet" href="/admin/dashboard.css"><script type="module" src="/admin/dashboard.js"></script></head>
<body><main class="panel"><p class="eyebrow">TIN FOIL FA CUP · OWNER’S VIEW</p><h1>A little love for TFFAC.</h1>
<svg class="heart" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 21 3.5 12.7C-2 7.1 5.8-.9 12 5.3 18.2-.9 26 7.1 20.5 12.7Z"/></svg>
<p class="total" id="total" aria-label="Current Likes total">—</p><p class="caption">CURRENT LIKES</p>
<p id="checked" class="checked">Not checked yet</p>
<form id="unlock-form"><label for="password">Admin password</label><div class="unlock-row"><input id="password" name="password" type="password" autocomplete="current-password" required spellcheck="false" autocapitalize="none"><button id="unlock" type="submit">Unlock</button></div><p class="hint">Use the password saved for your TFFAC Likes service.</p></form>
<div id="controls" class="controls" hidden><button id="refresh" type="button">Refresh total</button><button id="lock" class="quiet" type="button">Lock</button></div>
<p id="status" class="status" role="status" aria-live="polite">Enter your password to see the total.</p>
<p class="note">One Like per browser.<br>A little appreciation, rather than a visitor count.</p></main></body></html>`;

export const adminStyle = `:root{color-scheme:dark;font-family:Arial,Helvetica,sans-serif;background:#191612;color:#f3efdf}*{box-sizing:border-box}body{margin:0;min-height:100svh;display:grid;place-items:center;padding:24px 16px}.panel{width:min(100%,430px);padding:32px 24px 24px;text-align:center;border:1px solid #77766c;border-radius:16px;background:#10100d}.eyebrow{font-size:10px;letter-spacing:2px;color:#d5b56c;margin:0 0 18px}h1{font:normal clamp(25px,7vw,32px)/1.2 Georgia,serif;margin:0 0 24px}.heart{display:block;width:68px;height:68px;margin:0 auto;fill:#cb343b;stroke:#d3575b;stroke-width:.7;overflow:visible}.total{font:normal 76px/1.05 Georgia,serif;margin:12px 0 5px;font-variant-numeric:tabular-nums;overflow-wrap:anywhere}.caption{font-size:11px;letter-spacing:3px;color:#d5b56c;margin:0 0 16px}.checked{font-size:12px;color:#bcb9ac;margin:0 0 25px}form{text-align:left}label{display:block;font-size:13px;margin-bottom:8px}.unlock-row{display:flex;gap:8px}input{width:0;flex:1;min-width:0;background:#201f19;border:1px solid #77766c;border-radius:7px;color:#f3efdf;font:16px Arial;padding:12px}button{min-height:44px;border:1px solid #d5b56c;background:#d5b56c;border-radius:7px;color:#16140f;font:15px Arial;padding:10px 16px;cursor:pointer}button:disabled{opacity:.55;cursor:wait}.hint{font-size:11px;line-height:1.5;color:#bcb9ac;margin:9px 0 0}.controls{display:flex;justify-content:center;gap:10px}.quiet{color:#f3efdf;background:transparent;border-color:#77766c}.status{min-height:32px;font-size:12px;line-height:1.5;margin:18px 0;color:#d5b56c}.note{border-top:1px solid #454338;padding-top:18px;font-size:11px;line-height:1.6;color:#bcb9ac;margin:0}[hidden]{display:none!important}:focus-visible{outline:2px solid #f3efdf;outline-offset:4px}@media(max-width:350px){.panel{padding:26px 16px}.unlock-row{flex-wrap:wrap}.unlock-row input{flex-basis:100%;width:100%}.unlock-row button{width:100%}}`;

export const adminScript = `const byId=id=>document.getElementById(id);
const form=byId('unlock-form'),password=byId('password'),controls=byId('controls'),total=byId('total'),checked=byId('checked'),status=byId('status'),refresh=byId('refresh'),unlock=byId('unlock');
let credential='',busy=false;
function lock(message='Locked. Enter your password to see the total.'){
 credential='';password.value='';total.textContent='—';checked.textContent='Not checked yet';form.hidden=false;controls.hidden=true;status.textContent=message;
}
async function update(){
 if(busy||!credential)return;
 busy=true;refresh.disabled=true;unlock.disabled=true;status.textContent='Checking the total…';
 const sentCredential=credential;
 try{
  const response=await fetch('/admin/count',{method:'GET',headers:{Authorization:'Bearer '+sentCredential},cache:'no-store',credentials:'omit',redirect:'error'});
  if(credential!==sentCredential)return;
  if(response.status===401){lock('That password wasn’t accepted. Please try again.');return;}
  if(!response.ok)throw Error('Count unavailable');
  const data=await response.json();
  if(credential!==sentCredential)return;
  if(!Number.isSafeInteger(data.total)||data.total<0)throw Error('Invalid count');
  total.textContent=new Intl.NumberFormat('en-GB').format(data.total);
  checked.textContent='Last checked: '+new Intl.DateTimeFormat('en-GB',{day:'numeric',month:'short',hour:'2-digit',minute:'2-digit',second:'2-digit'}).format(new Date());
  form.hidden=true;controls.hidden=false;status.textContent='Up to date.';
 }catch{
  if(credential===sentCredential)status.textContent='Couldn’t refresh the total. Please try again; any displayed total is from the last successful check.';
 }finally{busy=false;refresh.disabled=false;unlock.disabled=false;}
}
form.addEventListener('submit',event=>{event.preventDefault();if(busy)return;credential=password.value.trim();password.value='';update();});
refresh.addEventListener('click',update);
byId('lock').addEventListener('click',()=>lock());
window.addEventListener('pagehide',()=>lock());
window.addEventListener('pageshow',event=>{if(event.persisted)lock();});`;

export function adminPage(path,method){
 const routes={'/admin':[adminDocument,'text/html; charset=utf-8'],'/admin/':[adminDocument,'text/html; charset=utf-8'],'/admin/dashboard.css':[adminStyle,'text/css; charset=utf-8'],'/admin/dashboard.js':[adminScript,'text/javascript; charset=utf-8']};
 const asset=routes[path];if(!asset)return null;
 const headers={'cache-control':'no-store','referrer-policy':'no-referrer','x-content-type-options':'nosniff','cross-origin-resource-policy':'same-origin','content-security-policy':"default-src 'none'; script-src 'self'; style-src 'self'; connect-src 'self'; frame-ancestors 'none'; form-action 'none'; base-uri 'none'"};
 if(!['GET','HEAD'].includes(method))return new Response(null,{status:405,headers:{...headers,allow:'GET, HEAD'}});
 return new Response(method==='HEAD'?null:asset[0],{headers:{...headers,'content-type':asset[1]}});
}
