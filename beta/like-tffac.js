/* Site-wide appreciation. Independent service; browser identity begins on first interaction. */
(()=>{
 'use strict';
 if(window.__tffcLikeLoaded)return;window.__tffcLikeLoaded=true;
 const base=new URL('.',document.currentScript.src),KEY='tffc.like.identity.v1';
 let preview=false;try{if(new URL(location.href).searchParams.get('likePreview')==='1')sessionStorage.setItem('tffc.like.shed','1');preview=sessionStorage.getItem('tffc.like.shed')==='1';}catch{}
 let config,token,liked=false,busy=true,message='',ready=false;
 const rows=new Set();
 const validToken=value=>/^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i.test(value||'');
 const readToken=()=>{try{const saved=localStorage.getItem(KEY);return validToken(saved)?saved:null;}catch{return null;}};
 const uuid=()=>{if(typeof crypto.randomUUID==='function')return crypto.randomUUID();const b=crypto.getRandomValues(new Uint8Array(16));b[6]=(b[6]&15)|64;b[8]=(b[8]&63)|128;const h=Array.from(b,n=>n.toString(16).padStart(2,'0')).join('');return [h.slice(0,8),h.slice(8,12),h.slice(12,16),h.slice(16,20),h.slice(20)].join('-');};
 const style=document.createElement('link');style.rel='stylesheet';style.href=new URL('like-tffac.css',base);document.head.append(style);
 const text=(node,value)=>{if(node.textContent!==value)node.textContent=value;};
 const update=()=>{for(const row of rows){if(!row.isConnected){rows.delete(row);continue;}const button=row.querySelector('button');button.disabled=busy||!ready;button.setAttribute('aria-pressed',String(liked));button.setAttribute('aria-busy',String(busy));text(row.querySelector('.tffc-like-message'),message);}};
 const request=async(path,body)=>{
  const controller=new AbortController(),timer=setTimeout(()=>controller.abort(),8000);
  try{const r=await fetch(config.endpoint.replace(/\/$/,'')+path,{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify(body),signal:controller.signal,credentials:'omit'});if(!r.ok)throw Error('Unavailable');const v=await r.json();if(typeof v.liked!=='boolean')throw Error('Invalid response');return v;}finally{clearTimeout(timer);}
 };
 async function refresh(){
  if(busy||!ready)return;
  token=readToken();
  if(!token){liked=false;message='';update();return;}
  busy=true;update();
  try{liked=(await request('/state',{token})).liked;message='';}catch{message='Couldn’t check your Like. Please try again.';}finally{busy=false;update();}
 }
 async function toggle(){
  if(busy||!ready)return;busy=true;message='';update();
  try{token=readToken();if(!token){token=uuid();try{localStorage.setItem(KEY,token);if(localStorage.getItem(KEY)!==token)throw Error('Storage unavailable');}catch{message='Your browser couldn’t remember this Like.';return;}}const next=await request('/reaction',{token,liked:!liked});liked=next.liked;try{localStorage.setItem('tffc.like.refresh.v1',String(Date.now()));}catch{}}
  catch{message='Couldn’t save that. Please try again.';}
  finally{busy=false;update();}
 }
 const privacyHtml="<p>Clubfinder uses your postcode to find nearby clubs. Your Campaign and Challenge progress is stored on your device. See our full Privacy Policy or contact us for details.</p><p><strong>I ♥ TFFAC</strong></p><p>If you use the heart, we save a random identifier in your browser to remember your choice. Our Like service stores a scrambled version of that identifier and the overall Like total. It does not receive your name, email, postcode or Campaign details.</p><p>Tap the heart again to remove your Like. Clearing your browser storage removes its memory of your choice, but does not automatically remove a Like already counted. Different browsers or devices can each register a Like.</p><p>Cloudflare hosts this service and processes connection information, such as your IP address, to deliver and protect it.</p>";
 function privacy(){
  for(const node of document.querySelectorAll('#tinFoilPrivacyMessage,#tffcPrivacyMessage,.barry-info-dialog .barry-info-copy')){
   if(node.classList.contains('barry-info-copy')&&node.closest('dialog')?.querySelector('h2')?.textContent!=='Privacy')continue;
   if(node.innerHTML!==privacyHtml)node.innerHTML=privacyHtml;
   if(node.style.maxHeight!=='55vh'){node.style.maxHeight='55vh';node.style.overflowY='auto';node.style.textAlign='left';}
  }
 }
 function mount(){
  if(!config||(!config.enabled&&!preview))return;
  privacy();
  for(const target of document.querySelectorAll('.tffc-magic-row')){
   const existing=target.previousElementSibling;
   if(existing?.classList.contains('tffc-like-row')){if(!rows.has(existing)){existing.querySelector('button').addEventListener('click',toggle);rows.add(existing);}continue;}
   const row=document.createElement('div');row.className='tffc-like-row';row.setAttribute('aria-label','Like Tin Foil FA Cup');
   row.innerHTML='<button type="button" class="tffc-like-button" aria-label="I love TFFAC" aria-pressed="false"><span aria-hidden="true">I</span><svg class="tffc-like-heart" viewBox="0 0 24 24" width="21" height="21" aria-hidden="true"><path d="M12 21 3.5 12.7C-2 7.1 5.8-.9 12 5.3 18.2-.9 26 7.1 20.5 12.7Z"/></svg><span class="tffc-like-label" aria-hidden="true">TFFAC</span></button><span class="tffc-like-message" role="status" aria-live="polite"></span>';
   row.querySelector('button').addEventListener('click',toggle);target.before(row);rows.add(row);
  }
  update();
 }
 (async()=>{
  try{const response=await fetch(new URL('like-config.json',base),{cache:'no-store'});if(!response.ok)return;config=await response.json();if(!config.enabled&&!preview)return;
   if(config.endpoint){const u=new URL(config.endpoint,location.href);if(u.protocol!=='https:'&&u.origin!==location.origin)throw Error('Invalid endpoint');config.endpoint=u.href;}
   mount();new MutationObserver(records=>{if(records.some(r=>r.addedNodes.length))mount();}).observe(document.body,{subtree:true,childList:true});
   if(!config.endpoint){message='Likes are unavailable just now.';busy=false;update();return;}
   token=readToken();
   ready=true;busy=false;await refresh();
  }catch{message='Likes are unavailable just now.';busy=false;update();}
 })();
 window.addEventListener('storage',e=>{if(e.key==='tffc.like.refresh.v1'&&ready&&!busy)refresh();});
 window.addEventListener('pageshow',()=>{if(ready&&!busy)refresh();});
})();
