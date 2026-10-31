/* Compact navigation trial, confined to the opt-in phone-frame Shed. */
(()=>{
 'use strict';
 const base=new URL('.',document.currentScript.src);
 const watched=new WeakSet();
 const badgeURL=new URL('assets/barry-air/badge.webp',base).href;
 const css=`
 .result .actions{display:flex;flex-wrap:wrap;align-items:center;gap:6px}
 .result .actions a.secondary{margin:0}
 .campaign-barry-nav{display:flex;justify-content:center;align-items:center}
 .my-journey-bar .campaign-barry-nav .barry-air-launch{display:block;width:244px;max-width:100%;min-height:44px;padding:2px;margin:0;border:0;border-radius:4px;background:transparent;box-shadow:none;cursor:pointer;overflow:visible;appearance:none;-webkit-appearance:none}
 /* Transparent filter outsets keep WebKit's scrolling paint layer from
    cutting the shadow at the tight source-image edges. Margins cancel the
    outsets so neither the badge nor its navigation row grows. */
 .barry-air-launch img{display:block;box-sizing:border-box;width:calc(100% + 88px);max-width:none;padding:44px;margin:-44px;height:auto;object-fit:contain;pointer-events:none;filter:drop-shadow(0 0 1px #e4c786aa) drop-shadow(0 6px 12px #0008)}
 .barry-air-launch:hover{filter:brightness(1.1)}
 .barry-air-launch:focus-visible{outline:2px solid #084c61;outline-offset:3px}
 .tffc-magic-row{gap:10px;flex-wrap:wrap}
 .my-journey-bar .campaign-secondary-nav{justify-content:center}
 .tffc-magic-row button{cursor:pointer;border-radius:6px}
 .deck-sales-coming{background:#c90000;color:#fff;border-color:#c90000;opacity:1}
 .tffc-beta-help button[onclick="tffcOpenShare()"],
 .tffc-beta-help button[onclick="tffcOpenShare()"] + .tffc-beta-help-sep,
 #challengeShareLinkFooter,#challengeShareLinkFooter + .beta-help-sep{display:none}
 .my-journey-bar .campaign-primary-nav button.round{
  background-image:linear-gradient(115deg,transparent 20%,#ffffff14 43%,transparent 66%),linear-gradient(to bottom,#ffffff2b 0%,#ffffff0b 43%,#0000000a 54%,#00000020 100%)!important;
  box-shadow:inset 0 2px 0 #ffe5a4,inset 0 -2px 0 #785222,inset 0 0 0 2px #bd9650,inset 0 3px 1px #ffffff38,0 2px 3px #0005;
 }
 .my-journey-bar .campaign-primary-nav button.round:active{
  box-shadow:inset 0 1px 2px #0005,inset 0 0 0 2px #b38c48,0 1px 1px #0003;
 }
 `;
 window.tffcInstallPhoneFrameNavigation=function(frame){
  let doc;
  try{doc=frame.contentDocument;}catch(_){return;}
  if(!doc)return;
  function openMagic(keep){
   const win=doc.defaultView;
   if(typeof win.tffcOpenShare==='function')win.tffcOpenShare();
   else doc.getElementById('challengeShareLinkFooter')?.click();
   if(keep){
    const destination=doc.querySelector('#tffcShareHost iframe,#tffcChallengeShareHost iframe');
    if(destination)destination.src=new URL('keep-the-magic-shed.html?instructions=1&embedded=1&keep=1',base).href;
   }
  }
  function decorate(){
   if(!doc.head)return;
   let style=doc.getElementById('phone-frame-navigation-style');
   if(!style){style=doc.createElement('style');style.id='phone-frame-navigation-style';doc.head.append(style);}
   if(style.textContent!==css)style.textContent=css;
   for(const bar of doc.querySelectorAll('.campaign-nav-tiered')){
    const core=bar.querySelector('.campaign-primary-nav');
    const controls=bar.querySelector('.campaign-secondary-nav');
    if(!core||!controls)continue;
    if(!bar.classList.contains('phone-frame-nav'))bar.classList.add('phone-frame-nav');
    if(core.getAttribute('aria-label')!=='Your Campaign destinations')core.setAttribute('aria-label','Your Campaign destinations');
    let badgeRow=bar.querySelector('.campaign-barry-nav');
    if(!badgeRow){badgeRow=doc.createElement('div');badgeRow.className='campaign-barry-nav';core.after(badgeRow);}
    let barry=bar.querySelector('.barry-air-launch');
    if(!barry){barry=doc.createElement('button');barry.type='button';barry.className='barry-air-launch';}
    if(barry.parentNode!==badgeRow)badgeRow.append(barry);
    if(barry.classList.contains('round'))barry.classList.remove('round');
    if(barry.getAttribute('aria-label')!=='Barry Air')barry.setAttribute('aria-label','Barry Air');
    if(!barry.querySelector('img')){
     const image=doc.createElement('img');image.src=badgeURL;image.alt='Barry Air';image.width=240;barry.replaceChildren(image);
    }
    // Clean both original markup and snapshots of the previous six-button trial.
    bar.querySelectorAll('.campaign-share').forEach(button=>button.remove());
    bar.querySelectorAll('.campaign-magic-nav').forEach(row=>row.remove());
    const labels={'View Original Campaigns':'Original Campaigns','End My Campaign':'End Campaign','Resume My Campaign':'Resume Campaign'};
    for(const button of controls.querySelectorAll('button')){
     const replacement=labels[button.textContent.trim()];
     if(replacement)button.textContent=replacement;
    }
    const reset=Array.from(controls.querySelectorAll('button')).find(button=>button.textContent.trim()==='Reset');
    const original=Array.from(controls.querySelectorAll('button')).find(button=>button.textContent.trim()==='Original Campaigns');
    if(reset&&original&&original.nextElementSibling!==reset)original.after(reset);
   }
   for(const support of doc.querySelectorAll('.tffc-support-row:not(.tffc-magic-row)')){
    if(support.previousElementSibling?.classList.contains('tffc-magic-row'))continue;
    const row=doc.createElement('div');row.className='tffc-support-row tffc-magic-row';row.setAttribute('aria-label','Keep and share Tin Foil FA Cup');
    for(const [label,kind] of [['Keep the Magic','keep'],['Share the Magic','share']]){
     const button=doc.createElement('button');button.type='button';button.className='tffc-support-lozenge campaign-'+kind;button.textContent=label;row.append(button);
    }
    support.before(row);
   }
   // Campaign return snapshots preserve HTML but not JS handlers.
   for(const barry of doc.querySelectorAll('.phone-frame-nav .barry-air-launch'))barry.onclick=()=>doc.defaultView.top.location.assign(new URL('barry-air/',base).href);
   for(const keep of doc.querySelectorAll('.tffc-magic-row .campaign-keep'))keep.onclick=()=>openMagic(true);
   for(const share of doc.querySelectorAll('.tffc-magic-row .campaign-share'))share.onclick=()=>openMagic(false);
  }
  decorate();
  if(!watched.has(doc)){
   watched.add(doc);
   new MutationObserver(decorate).observe(doc,{childList:true,subtree:true});
  }
 };
})();
