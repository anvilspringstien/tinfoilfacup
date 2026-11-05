/* First visual pass: an explicit, safe manual refresh, never an unverified
   "Up to date" promise. Release detection and quiet data refresh follow later. */
(()=>{
 'use strict';
 const root=new URL('../',document.currentScript.src);
 let busy=false,controller=null,feedback='Refresh for the latest version';
 const style=document.createElement('style');
 style.textContent=`.tffc-refresh-row{display:flex;flex-wrap:wrap;align-items:center;justify-content:center;gap:5px 12px;margin:12px 0 8px;padding:8px 6px;border-top:1px solid #b6a57b55;font:11px/1.5 Arial,sans-serif;color:#77715f}.tffc-refresh-row .tffc-refresh-button{min-height:38px;border:1px solid #ad965f;border-radius:5px;background:#f5edd5;color:#084c61;padding:7px 13px;font:600 12px/1.4 Arial,sans-serif;cursor:pointer;white-space:nowrap}.tffc-refresh-button:hover{background:#eee1b9}.tffc-refresh-button:focus-visible{outline:2px solid #084c61;outline-offset:3px}.tffc-refresh-button:disabled{opacity:.6;cursor:wait}.tffc-refresh-feedback{max-width:250px;text-align:center}`;
 document.head.append(style);
 const rows=()=>Array.from(document.querySelectorAll('.tffc-refresh-row'));
 function paint(){for(const row of rows()){row.querySelector('button').disabled=busy;const status=row.querySelector('[role=status]');if(status.textContent!==feedback)status.textContent=feedback;}}
 function protectedEdit(){
  const saved=typeof window.loadSavedJourney==='function'?window.loadSavedJourney():null;
  const pc=document.getElementById('postcode');
  const norm=s=>String(s||'').toUpperCase().replace(/\s/g,'');
  if(saved?.postcode&&pc&&norm(pc.value)!==norm(saved.postcode))return 'Finish your postcode search before refreshing.';
  const pigeon=document.querySelector('input[aria-label="Pigeon name"]');
  if(saved&&pigeon&&pigeon.value.trim()!==String(saved.pigeonName||'').trim())return 'Finish editing your pigeon name before refreshing.';
  if(document.querySelector('dialog[open]'))return 'Close the open window before refreshing.';
  return '';
 }
 async function refresh(){
  if(busy)return;
  const blocked=protectedEdit();if(blocked){feedback=blocked;paint();return;}
  if(navigator.onLine===false){feedback='Offline · reconnect before refreshing';paint();return;}
  busy=true;feedback='Refreshing TFFAC…';paint();
  const request=new AbortController();controller=request;
  const timeout=setTimeout(()=>request.abort(),8000);let navigating=false;
  try{
   const url=new URL(root);url.searchParams.set('view','campaign');url.searchParams.set('tffc-refresh',String(Date.now()));
   // Verify a real current page can be reached before leaving the working one.
   const response=await fetch(url.href,{cache:'no-store',credentials:'same-origin',signal:request.signal});
   if(!response.ok)throw Error('Unavailable');
   const html=await response.text();if(!html.includes('phone-frame-launch.js'))throw Error('Invalid page');
   if(controller!==request)return;
   // Re-check after the network wait: edits may have started meanwhile.
   const editing=protectedEdit();if(editing){feedback=editing;return;}
   navigating=true;window.top.location.assign(url.href);
  }catch(_){if(controller===request)feedback='Couldn’t refresh · please try again';}
  finally{clearTimeout(timeout);if(controller===request){controller=null;if(!navigating)busy=false;paint();}}
 }
 function install(){
  const visible=!!document.querySelector('.campaign-nav-tiered');
  for(const footer of document.querySelectorAll('.tffc-support-footer')){
   let row=footer.previousElementSibling?.classList.contains('tffc-refresh-row')?footer.previousElementSibling:null;
   if(!visible){row?.remove();continue;}
   if(!row){row=document.createElement('div');row.className='tffc-refresh-row';row.innerHTML='<button type="button" class="tffc-refresh-button">Refresh TFFAC</button><span class="tffc-refresh-feedback" role="status" aria-live="polite"></span>';footer.before(row);}
   row.querySelector('button').onclick=refresh;
  }
  paint();
 }
 new MutationObserver(install).observe(document.body,{childList:true,subtree:true});
 window.addEventListener('pagehide',()=>{controller?.abort();controller=null;busy=false;});
 window.addEventListener('pageshow',()=>{busy=false;feedback='Refresh for the latest version';install();});
 window.addEventListener('offline',()=>{feedback='Offline · reconnect before refreshing';paint();});
 window.addEventListener('online',()=>{feedback='Refresh for the latest version';paint();});
 install();
})();
