/* Present existing pages through a real phone viewport; do not rewrite their
   layout rules, Campaign storage, counter, competition data or navigation. */
(()=>{
 'use strict';
 const frame=document.getElementById('phoneApp');
 const shell=document.querySelector('.phone-shell');
 const popup=document.documentElement.dataset.statsPopup==='1';
 const base=new URL('.',document.currentScript.src);
 const entries={splash:'index.html',campaign:'clubfinder-journey.html',challenges:'challenges-beta.html',stats:'stats-beta.html',share:'keep-the-magic-shed.html'};
 let report=popup;
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
 function fit(){sizeFrame(frame,shell,document.documentElement.clientWidth,document.body.getBoundingClientRect().height,report)}
 function prepareDocument(){
  let win,href;
  try{win=frame.contentWindow;href=new URL(win.location.href);}catch(_){return;}
  if(href.origin!==location.origin&&href.href!=='about:blank')return;
  report=popup||/\/stats-beta\.html$/.test(href.pathname)||href.searchParams.has('stats');
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
   tab.document.write('<!doctype html><html lang="en-GB" data-stats-popup="1"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Tin Foil FA Cup Stats</title><link rel="stylesheet" href="'+css+'"><style>html,body{margin:0;height:100svh;overflow:hidden;background:#141210}.phone-shell{position:relative;margin:0 auto;overflow:hidden}#phoneApp{display:block;border:0;position:absolute;left:0;top:0;transform-origin:top left;background:#141210}</style></head><body><main class="phone-shell"><iframe id="phoneApp" title="Tin Foil FA Cup Stats"></iframe></main></body></html>');
   tab.document.close();
   // Give the outer tab a refreshable route, rather than leaving about:blank.
   tab.history.replaceState(null,'',new URL('phone-frame-shed.html?view=stats',base).href);
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
  const entry=new URLSearchParams(location.search).get('view')||'splash';
  frame.src=new URL(entries[entry]||entries.splash,base).href;
 }
})();
