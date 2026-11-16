/* Barry's Post Office. Loaded on demand; no Campaign data is read or sent. */
(function(root){
 'use strict';
 var active=null, script=document.currentScript;
 var assetBase=new URL('.',script?script.src:location.href).href;
 function uuid(){
  if(root.crypto.randomUUID)return root.crypto.randomUUID();
  var bytes=root.crypto.getRandomValues(new Uint8Array(16));bytes[6]=(bytes[6]&15)|64;bytes[8]=(bytes[8]&63)|128;
  var h=Array.from(bytes,function(b){return b.toString(16).padStart(2,'0')}).join('');return h.slice(0,8)+'-'+h.slice(8,12)+'-'+h.slice(12,16)+'-'+h.slice(16,20)+'-'+h.slice(20);
 }
 function create(options){
  var overlay=document.createElement('div');overlay.className='barry-post';overlay.hidden=true;
  overlay.innerHTML='<section class="post-frame" role="dialog" aria-modal="true" aria-labelledby="post-title" tabindex="-1">'+
   '<button type="button" class="post-close" aria-label="Close Barry’s Post Office">×</button>'+
   '<img class="post-brand" alt="Tin Foil FA Cup" width="86" height="86">'+
   '<div class="post-masthead"><img class="post-barry" alt="Barry the Mail Pigeon" width="90" height="96"><h1 id="post-title">Barry’s<br>Post Office</h1></div>'+
   '<p class="post-intro">Got a thought? Spotted a wobble?<br>Send a message to Tin Foil FA Cup.</p>'+
   '<p class="post-demo" hidden>Design preview — no message will be sent.</p>'+
   '<form onsubmit="return false"><div class="post-field"><label class="post-label" for="post-kind">What’s on your mind?</label><select id="post-kind" name="kind"><option value="feedback">Feedback</option><option value="issue">Report an Issue</option></select></div>'+
   '<div class="post-field"><label class="post-label" for="post-name">Your name <span class="post-optional">(optional)</span></label><input id="post-name" name="name" autocomplete="name" maxlength="80"></div>'+
   '<div class="post-field"><label class="post-label" for="post-email">Your email</label><input id="post-email" name="email" type="email" autocomplete="email" inputmode="email" maxlength="254" required></div>'+
   '<div class="post-field"><label class="post-label" for="post-message">Your message</label><textarea id="post-message" name="message" rows="4" maxlength="5000" required></textarea></div>'+
   '<div class="post-trap" aria-hidden="true"><label>Leave this empty<input name="website" tabindex="-1" autocomplete="off"></label></div>'+
   '<p class="post-note">Your message goes to our inbox. We’ll use your email to reply.</p>'+
   '<div class="post-challenge"></div><p class="post-status" role="status" aria-live="polite" hidden></p>'+
   '<button class="post-send" type="submit">Send with Barry</button></form>'+
   '<div class="post-success" hidden><h2>Handed to Barry.</h2><p>Thanks for getting in touch.<br>Your message has been accepted for delivery.</p><p class="post-reference"></p><button class="post-finish" type="button">Back to the Cup</button></div>'+
   '<p class="post-footer">Prefer email? <a href="mailto:tinfoilfacup@gmail.com">tinfoilfacup@gmail.com</a></p></section>';
  overlay.querySelector('.post-brand').src=new URL('tffc-splash-logo-q80.webp',assetBase).href;
  overlay.querySelector('.post-barry').src=new URL('barry-pigeon-mail-small.webp',assetBase).href;
  document.body.appendChild(overlay);
  return {overlay:overlay,options:options};
 }
 function loadChallenge(){
  if(root.turnstile)return Promise.resolve();
  if(root.__tffcPostChallenge)return root.__tffcPostChallenge;
  root.__tffcPostChallenge=new Promise(function(resolve,reject){
   var s=document.createElement('script');s.src='https://challenges.cloudflare.com/turnstile/v0/api.js?render=explicit';s.async=true;s.onload=resolve;s.onerror=function(){root.__tffcPostChallenge=null;s.remove();reject(new Error('challenge'))};document.head.appendChild(s);
  });return root.__tffcPostChallenge;
 }
 root.tffcOpenPostOffice=function(kind,options){
  if(active)return;
  options=options||root.TFFC_POST_OFFICE||{};
  var ui=create(options),o=ui.overlay,frame=o.querySelector('.post-frame'),form=o.querySelector('form');
  var previous=document.activeElement,scrollX=root.scrollX,scrollY=root.scrollY;
  var bodyStyle={position:document.body.style.position,top:document.body.style.top,left:document.body.style.left,width:document.body.style.width,overflow:document.body.style.overflow};
  var siblings=Array.from(document.body.children).filter(function(el){return el!==o&&el.tagName!=='SCRIPT'&&el.tagName!=='STYLE'}).map(function(el){var old=el.inert;el.inert=true;return [el,old]});
  document.body.style.position='fixed';document.body.style.top=-scrollY+'px';document.body.style.left=-scrollX+'px';document.body.style.width='100%';document.body.style.overflow='hidden';
  o.hidden=false;active=ui;
  var status=o.querySelector('.post-status'),send=o.querySelector('.post-send'),widget=null,token='',pending=false,uncertain=false;
  var id=uuid(),snapshot=null,endpoint=options.endpoint||'',sitekey=options.sitekey||'';
  o.querySelector('#post-kind').value=kind==='issue'?'issue':'feedback';
  function say(text){status.textContent=text;status.hidden=false}
  function resetChallenge(){token='';if(widget!==null&&root.turnstile)root.turnstile.reset(widget)}
  function finish(){
   if(pending)return;
   document.removeEventListener('keydown',onKey);if(widget!==null&&root.turnstile)root.turnstile.remove(widget);
   o.remove();siblings.forEach(function(pair){pair[0].inert=pair[1]});Object.assign(document.body.style,bodyStyle);root.scrollTo(scrollX,scrollY);active=null;
   if(previous&&previous.isConnected&&previous.focus)previous.focus({preventScroll:true});
  }
  function onKey(e){
   if(e.key==='Escape'){e.preventDefault();finish();return}
   if(e.key!=='Tab')return;
   var focusable=Array.from(o.querySelectorAll('button,input,select,textarea,a[href],iframe')).filter(function(el){return !el.disabled&&el.tabIndex!==-1&&el.getClientRects().length});
   var first=focusable[0],last=focusable[focusable.length-1];
   if(e.shiftKey&&(document.activeElement===first||document.activeElement===frame)){e.preventDefault();last.focus()}
   else if(!e.shiftKey&&document.activeElement===last){e.preventDefault();first.focus()}
  }
  o.querySelector('.post-close').onclick=finish;o.querySelector('.post-finish').onclick=finish;
  document.addEventListener('keydown',onKey);frame.focus({preventScroll:true});
  if(options.preview){o.querySelector('.post-demo').hidden=false;send.textContent='Preview Barry’s delivery';}
  else if(!endpoint||!sitekey){send.disabled=true;say('Barry’s counter isn’t open yet. You can still reach us using the email link below.');}
  else loadChallenge().then(function(){if(active!==ui)return;widget=root.turnstile.render(o.querySelector('.post-challenge'),{sitekey:sitekey,action:'post-office',callback:function(t){token=t},'expired-callback':function(){token=''},'error-callback':function(){token='';say('The security check couldn’t load. Please try again or use the email link below.')}})}).catch(function(){if(active===ui)say('The security check couldn’t load. Please use the email link below.');});
  form.onsubmit=async function(e){
   e.preventDefault();if(pending||uncertain||!form.reportValidity())return;
   var data=new FormData(form),payload={kind:data.get('kind'),name:data.get('name').trim(),email:data.get('email').trim(),message:data.get('message').trim(),website:data.get('website'),id:id,token:token};
   if(!payload.message){say('Please add your message.');o.querySelector('#post-message').focus();return}
   if(options.preview){form.hidden=true;o.querySelector('.post-success').hidden=false;o.querySelector('.post-success h2').textContent='A little practice flight.';o.querySelector('.post-success p').textContent='This is the delivery screen. No message has been sent.';o.querySelector('.post-finish').focus();return}
   if(!endpoint||!sitekey)return;
   if(!token){say('Please complete the security check first.');return}
   var content=JSON.stringify([payload.kind,payload.name,payload.email,payload.message]);
   if(snapshot!==null&&snapshot!==content){id=uuid();payload.id=id}snapshot=content;
   pending=true;send.disabled=true;send.textContent='Barry’s collecting your message…';status.hidden=true;
   var controller=new AbortController(),timer=setTimeout(function(){controller.abort()},20000);
   try{
    var response=await fetch(endpoint,{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify(payload),signal:controller.signal,credentials:'omit'});
    var result=await response.json();
    if(response.ok&&result.ok===true&&result.id===id){form.hidden=true;o.querySelector('.post-success').hidden=false;o.querySelector('.post-reference').textContent='Delivery reference: '+id;o.querySelector('.post-finish').focus();}
    else if(result.error==='uncertain'){uncertain=true;say('We couldn’t confirm delivery. Please don’t send again yet. To check, email us quoting '+id+'.');}
    else {resetChallenge();say(response.status===429?'Barry’s carrying a full mailbag. Please wait a minute and try again.':'Barry couldn’t collect your message. Your words are still here; please try again or use the email link below.');}
   }catch(err){uncertain=true;say('We couldn’t confirm delivery. Please don’t send again yet. To check, email us quoting '+id+'.');}
   finally{clearTimeout(timer);pending=false;send.disabled=uncertain;send.textContent='Send with Barry';}
  };
 };
})(window);
