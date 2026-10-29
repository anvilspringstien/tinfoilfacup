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
 function fit(){
  const width=document.documentElement.clientWidth;
  const height=document.body.getBoundingClientRect().height;
  const wide=width>=700;
  // A fixed 390 × 693 composition at larger sizes. Phones retain their
  // normal viewport. The report keeps its existing 980px print canvas,
  // fitted within precisely the same outer phone-shaped window.
  const visibleWidth=wide?390:width;
  const visibleHeight=wide?390*16/9:height;
  const scale=wide?Math.min(width/visibleWidth,height/visibleHeight):1;
  const canvasWidth=report?980:visibleWidth;
  const canvasHeight=visibleHeight*canvasWidth/visibleWidth;
  shell.style.width=visibleWidth*scale+'px';
  shell.style.height=visibleHeight*scale+'px';
  frame.style.width=canvasWidth+'px';
  frame.style.height=canvasHeight+'px';
  frame.style.transform='scale('+visibleWidth*scale/canvasWidth+')';
 }
 function prepareDocument(){
  let win,href;
  try{win=frame.contentWindow;href=new URL(win.location.href);}catch(_){return;}
  if(href.origin!==location.origin&&href.href!=='about:blank')return;
  report=popup||/\/stats-beta\.html$/.test(href.pathname)||href.searchParams.has('stats');
  fit();
  if(popup){
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
   const js=new URL('phone-frame-shed.js',base).href;
   tab.document.open();
   tab.document.write('<!doctype html><html lang="en-GB" data-stats-popup="1"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Tin Foil FA Cup Stats</title><link rel="stylesheet" href="'+css+'"><script defer src="'+js+'"><'+'/script></head><body><main class="phone-shell"><iframe id="phoneApp" title="Tin Foil FA Cup Stats"></iframe></main></body></html>');
   tab.document.close();
   const reportWindow=tab.document.getElementById('phoneApp').contentWindow;
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
