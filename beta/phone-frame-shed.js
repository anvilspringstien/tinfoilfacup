/* Present existing pages through a real phone viewport; do not rewrite their
   layout rules, Campaign storage, counter, competition data or navigation. */
(()=>{
 'use strict';
 const frame=document.getElementById('phoneApp');
 const shell=document.querySelector('.phone-shell');
 const popup=document.documentElement.dataset.statsPopup==='1';
 const base=new URL('.',document.currentScript.src);
 // Explicit opt-in follows this tab across the real app frames.
 if(new URLSearchParams(location.search).get('likePreview')==='1')try{sessionStorage.setItem('tffc.like.shed','1');}catch{}
 const shed=document.documentElement.dataset.tffcEntrance==='shed';
 if(shed)frame.allow="web-share; accelerometer 'self'; gyroscope 'self'";
 const entries={splash:shed?'shed-splash.html':'public-splash.html',campaign:'clubfinder-journey.html',challenges:'challenges-beta.html',stats:'stats-beta.html',share:'keep-the-magic-shed.html',club:'club-details.html'};
 const params=new URLSearchParams(location.search);
 const entry=params.get('view')||'splash';
 const shedRoom=location.pathname.endsWith('/phone-frame-shed.html')&&params.get('bootRoomFrame')==='1'&&entry==='boot-room';
 const framedRoom=shedRoom||(location.pathname.endsWith('/phone-frame.html')&&entry==='boot-room');
 let report=popup||entry==='stats';
 function sizeFrame(targetFrame,targetShell,width,height,isReport){
  const wide=width>=700;
  // A fixed 390 × 693 composition at larger sizes. Phones retain their
  // normal viewport. The report keeps its existing 980px print canvas,
  // fitted within precisely the same outer phone-shaped window.
  const visibleWidth=wide?390:width;
  const visibleHeight=wide?390*16/9:height;
  const scale=wide?Math.min(width/visibleWidth,height/visibleHeight):1;
  const canvasWidth=isReport?980:visibleWidth;
  const canvasHeight=visibleHeight*canvasWidth/visibleWidth;
  targetShell.style.width=visibleWidth*scale+'px';
  targetShell.style.height=visibleHeight*scale+'px';
  targetFrame.style.width=canvasWidth+'px';
  targetFrame.style.height=canvasHeight+'px';
  targetFrame.style.transform='scale('+visibleWidth*scale/canvasWidth+')';
 }
 const watchedDocuments=new WeakSet();
 function hideDesktopEdgeScrollbar(){
  let doc;
  try{doc=frame.contentDocument;}catch(_){return;}
  if(!doc?.documentElement)return;
  const root=doc.documentElement;
  const desktop=matchMedia('(min-width:700px) and (hover:hover) and (pointer:fine)').matches;
  const hide=desktop&&!report&&!doc.querySelector('.stats-actions');
  if(hide){
   root.dataset.phoneFrameScrollbar='hidden';
   root.style.setProperty('scrollbar-width','none','important');
   root.style.setProperty('scrollbar-gutter','auto','important');
   if(doc.head&&!doc.getElementById('phone-frame-scrollbar-style')){
    const style=doc.createElement('style');
    style.id='phone-frame-scrollbar-style';
    style.textContent='html[data-phone-frame-scrollbar="hidden"]::-webkit-scrollbar{display:none!important;width:0!important;height:0!important}';
    doc.head.append(style);
   }
  }else if(root.dataset.phoneFrameScrollbar==='hidden'){
   delete root.dataset.phoneFrameScrollbar;
   root.style.removeProperty('scrollbar-width');
   root.style.removeProperty('scrollbar-gutter');
  }
  // The existing journey rewrites its document after fetching BETA. Follow
  // root replacement before paint, without polling or changing scroll owners.
  if(!watchedDocuments.has(doc)){
   watchedDocuments.add(doc);
   new MutationObserver(hideDesktopEdgeScrollbar).observe(doc,{childList:true});
  }
 }
 function fit(){
  sizeFrame(frame,shell,document.documentElement.clientWidth,document.body.getBoundingClientRect().height,report);
  hideDesktopEdgeScrollbar();
  if(!framedRoom)window.tffcInstallPhoneFrameNavigation?.(frame);
 }
 // Cover only the child viewport during the Splash-to-Four-Laws handoff.
 // WebKit can paint the child document's own white canvas during navigation
 // and document.write, independently of the iframe element's background.
 const journeyUrl=new URL(entries.campaign,base);
 const splashUrl=new URL(entries.splash,base);
 const handoffTimeout=10000;
 const cover=document.createElement('div');
 cover.hidden=true;
 cover.setAttribute('aria-hidden','true');
 cover.style.cssText='position:absolute;inset:0;z-index:1;pointer-events:none;background:#141210';
 shell.append(cover);
 const recovery=document.createElement('section');
 recovery.hidden=true;
 recovery.style.cssText='position:absolute;inset:0;margin:auto;width:80%;height:max-content;max-height:100%;overflow:auto;color:#f6f3e8;text-align:center;font:1rem/1.5 system-ui';
 recovery.innerHTML='<p role="alert">The Four Laws could not load. Try again, or return to the start.</p>'
  +'<button type="button">Try again</button> <button type="button">Return to start</button>';
 cover.append(recovery);
 const [retry,back]=recovery.querySelectorAll('button');
 let handoff=null;
 function clearHandoff(){
  clearTimeout(handoff?.timer);
  handoff=null;
  cover.hidden=true;
  cover.setAttribute('aria-hidden','true');
  cover.style.pointerEvents='none';
  recovery.hidden=true;
  frame.inert=false;
 }
 function readyMaster(attempt){
  const journey=frame.contentDocument;
  if(!journey||journey===attempt.previous||journey.location?.pathname!==journeyUrl.pathname)return null;
  const master=journey.querySelector('.tffc-exact-master-frame')?.contentDocument;
  return master?.readyState==='complete'&&master.getElementById('postcode')&&
   master.querySelector('.clubfinder-search button')&&master.getElementById('clubfinder-status') ? master : null;
 }
 function startHandoff(destination){
  clearHandoff();
  const attempt={destination,previous:frame.contentDocument};
  handoff=attempt;
  cover.hidden=false;
  attempt.timer=setTimeout(()=>{
   if(handoff!==attempt)return;
   if(readyMaster(attempt)){clearHandoff();return;}
   const focusWasInFrame=document.activeElement===frame;
   cover.removeAttribute('aria-hidden');
   cover.style.pointerEvents='auto';
   recovery.hidden=false;
   frame.inert=true;
   if(focusWasInFrame)retry.focus();
  },handoffTimeout);
 }
 retry.addEventListener('click',()=>{
  const destination=handoff.destination;
  startHandoff(destination);
  frame.contentWindow.location.replace(destination.href);
 });
 back.addEventListener('click',()=>{
  clearHandoff();
  frame.contentWindow.location.replace(splashUrl.href);
 });
 window.addEventListener('message',event=>{
  if(handoff&&event.origin===location.origin&&event.source===frame.contentWindow&&
     event.data?.type==='tffc-journey-painted'&&readyMaster(handoff))clearHandoff();
 });
 frame.addEventListener('tffc-splash-start',()=>{
  if(frame.contentDocument?.location.pathname===splashUrl.pathname)startHandoff(journeyUrl);
 });
 function prepareDocument(){
  let win,href;
  try{win=frame.contentWindow;href=new URL(win.location.href);}catch(_){return;}
  if(href.href==='about:blank'){fit();return;}
  if(href.origin!==location.origin){if(handoff)clearHandoff();return;}
  if(handoff&&href.pathname!==journeyUrl.pathname)clearHandoff();
  else if(handoff){
   // A cached pre-handoff wrapper has no paint message. The outer load
   // includes its nested master, so use that completed document as a fallback.
   const attempt=handoff,master=readyMaster(attempt);
   if(master){
    requestAnimationFrame(()=>requestAnimationFrame(()=>{
     if(handoff===attempt&&readyMaster(attempt)===master)clearHandoff();
    }));
   }
  }
  // document.write from the Campaign opener can give Stats its opener's
  // URL. Identify the rendered report as well as canonical Stats routes.
  report=popup||!!win.document.querySelector('.stats-actions')||/\/stats-beta\.html$/.test(href.pathname)||href.searchParams.has('stats');
  fit();
  if(report&&window.opener){
   // Stats still opens in its own tab and returns to the original Campaign.
   win.opener=window.opener;
   win.close=()=>window.close();
   return;
  }
  if(win.tffcPhoneFrameOpen)return;
  const originalOpen=win.open.bind(win);
  win.tffcPhoneFrameOpen=true;
  win.open=function(url='',target='_blank',features){
   const destination=new URL(url||'about:blank',win.location.href);
   const stats=url===''||(destination.origin===location.origin&&/\/stats-beta\.html$/.test(destination.pathname));
   if(!stats||target!=='_blank')return originalOpen(url,target,features);
   // Retain the synchronous popup gesture and real Window object expected
   // by the existing Stats generator, inside a separate scaled outer tab.
   const tab=originalOpen('',target,features);
   if(!tab)return null;
   const css=new URL('phone-frame-shed.css',base).href;
   tab.document.open();
   tab.document.write('<!doctype html><html lang="en-GB" data-stats-popup="1"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Tin Foil FA Cup Stats</title><link rel="stylesheet" href="'+css+'"><style>html,body{margin:0;height:100svh;overflow:hidden;background:#141210}.phone-shell{position:relative;margin:0 auto;overflow:hidden}#phoneApp{display:block;border:0;position:absolute;left:0;top:0;transform-origin:top left;background:#141210}</style></head><body><main class="phone-shell"><iframe id="phoneApp" title="Tin Foil FA Cup Stats" allow="web-share"></iframe></main></body></html>');
   tab.document.close();
   tab.opener=win;
   // Give the outer tab a refreshable route, rather than leaving about:blank.
   const statsRoute=new URL(location.href);statsRoute.search='?view=stats';statsRoute.hash='';
   tab.history.replaceState(null,'',statsRoute.href);
   const reportFrame=tab.document.getElementById('phoneApp');
   const fitReport=()=>sizeFrame(reportFrame,tab.document.querySelector('.phone-shell'),tab.document.documentElement.clientWidth,tab.document.body.getBoundingClientRect().height,true);
   // Size synchronously: Stats writes into the child immediately, before
   // deferred scripts or an outer document load event can be relied on.
   fitReport();
   tab.addEventListener('resize',fitReport,{passive:true});
   const reportWindow=reportFrame.contentWindow;
   reportWindow.opener=win;
   reportWindow.close=()=>tab.close();
   if(url)reportWindow.location.replace(destination.href);
   return reportWindow;
  };
 }
 frame.addEventListener('load',prepareDocument);
 addEventListener('resize',fit,{passive:true});
 fit();
 if(popup)prepareDocument();
 else{
  const groundReview=location.pathname.endsWith('/phone-frame-ground-review.html')&&entry==='ground-review';
  const destination=new URL(groundReview?'clubfinder-ground-review-journey.html':framedRoom?'boot-room/?frame='+(shedRoom?'shed':'campaign'):entries[entry]||entries.splash,base);
  if(framedRoom)destination.hash=location.hash;
  if(entry==='club')destination.searchParams.set('club',new URLSearchParams(location.search).get('club')||'');
  if(destination.pathname===journeyUrl.pathname)startHandoff(destination);
  frame.src=destination.href;
 }
})();
