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
 .my-journey-bar .campaign-barry-nav .barry-air-launch{display:block;width:244px;max-width:100%;min-height:44px;padding:2px;margin:0;border:0;border-radius:4px;background:transparent;box-shadow:none;cursor:pointer}
 .barry-air-launch img{display:block;width:240px;max-width:100%;height:auto;object-fit:contain;filter:drop-shadow(0 0 1px #e4c786aa) drop-shadow(0 6px 12px #0008)}
 .barry-air-launch:hover{filter:brightness(1.1)}
 .barry-air-launch:focus-visible{outline:2px solid #084c61;outline-offset:3px}
 .barry-air-teaser{width:min(350px,calc(100vw - 28px));max-height:calc(100svh - 28px);overflow:auto;padding:22px;border:1px solid #ac9569;border-radius:12px;background:#141210;color:#f6f3e8;text-align:center;font:14px/1.55 Poppins,Arial,sans-serif;box-shadow:0 12px 35px #0008}
 .barry-air-teaser::backdrop{background:#000b}
 .barry-air-teaser img{display:block;width:260px;max-width:100%;height:auto;margin:4px auto 16px;filter:drop-shadow(0 0 1px #e4c786aa) drop-shadow(0 6px 12px #0008)}
 .barry-air-teaser .teaser-kicker{font:700 10px/1.4 Arial,sans-serif;letter-spacing:.15em;color:#d8bc7c}
 .barry-air-teaser h2{margin:8px 0 0;font-size:26px;font-weight:500}
 .barry-air-teaser h3{margin:2px 0 14px;color:#e4c786;font-size:19px;font-weight:400}
 .barry-air-teaser p{margin:12px 0}
 .barry-air-teaser .teaser-captain{font:italic 13px/1.5 Georgia,serif;color:#d8cbb4}
 .barry-air-teaser .teaser-close{display:block;margin:-14px -10px 0 auto;width:36px;height:36px;background:transparent;color:inherit;border:0;font:26px Arial;cursor:pointer}
 .barry-air-teaser .teaser-return{margin:8px auto 0;padding:10px 15px;border:1px solid #d5ad26;border-radius:6px;background:#f0c64f;color:#17110b;font:700 12px/1.4 Arial,sans-serif;cursor:pointer}
 .barry-air-teaser:focus{outline:none}
 .barry-air-teaser button:focus-visible{outline:2px solid #e4c786;outline-offset:3px}
 .tffc-magic-row{gap:10px;flex-wrap:wrap}
 .my-journey-bar .campaign-secondary-nav{justify-content:center}
 .tffc-magic-row button{cursor:pointer;border-radius:6px}
 .deck-sales-coming{background:#c90000;color:#fff;border-color:#c90000;opacity:1}
 .tffc-beta-help button[onclick="tffcOpenShare()"],
 .tffc-beta-help button[onclick="tffcOpenShare()"] + .tffc-beta-help-sep,
 #challengeShareLinkFooter,#challengeShareLinkFooter + .beta-help-sep{display:none}
 .my-journey-bar .campaign-primary-nav button.round{
  background-image:linear-gradient(115deg,transparent 20%,#ffffff14 43%,transparent 66%),linear-gradient(to bottom,#ffffff2b 0%,#ffffff0b 43%,#0000000a 54%,#00000020 100%)!important;
  box-shadow:inset 0 1px 0 #ffe5a4,inset 0 -1px 0 #785222,inset 0 0 0 1px #bd9650,inset 0 2px 1px #ffffff38,0 2px 3px #0005;
 }
 .my-journey-bar .campaign-primary-nav button.round:active{
  box-shadow:inset 0 1px 2px #0005,inset 0 0 0 1px #b38c48,0 1px 1px #0003;
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
  function openBarry(trigger){
   let dialog=doc.querySelector('.barry-air-teaser');
   if(!dialog){
    dialog=doc.createElement('dialog');dialog.className='barry-air-teaser';dialog.tabIndex=-1;dialog.setAttribute('aria-labelledby','barry-teaser-title');dialog.setAttribute('aria-describedby','barry-teaser-copy');
    dialog.innerHTML='<button class="teaser-close" type="button" aria-label="Close Barry Air">×</button><img src="'+badgeURL+'" alt="Barry Air pilot wings" width="260"><p class="teaser-kicker">PREPARING FOR TAKE-OFF</p><h2 id="barry-teaser-title">Barry Air</h2><h3>Coming Soon</h3><p><strong>Your Campaign. In flight.</strong></p><p id="barry-teaser-copy">Captain Barry is preparing Pigeon Control—your pigeon’s own flight board, flight path and occasional announcements from the cockpit.</p><p class="teaser-captain">“Please remain seated. The captain is still arguing with the wind.”</p><button class="teaser-return" type="button">Back to My Campaign</button>';
    doc.body.append(dialog);
    for(const button of dialog.querySelectorAll('button'))button.onclick=()=>dialog.close();
    dialog.addEventListener('click',event=>{if(event.target===dialog){const r=dialog.getBoundingClientRect();if(event.clientX<r.left||event.clientX>r.right||event.clientY<r.top||event.clientY>r.bottom)dialog.close();}});
   }
   dialog.onclose=()=>{if(trigger.isConnected)trigger.focus({preventScroll:true});};
   if(!dialog.open){dialog.showModal();dialog.focus({preventScroll:true});}
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
   for(const barry of doc.querySelectorAll('.phone-frame-nav .barry-air-launch'))barry.onclick=()=>openBarry(barry);
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
