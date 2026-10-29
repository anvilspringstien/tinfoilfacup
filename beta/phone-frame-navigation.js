/* Navigation trial belongs only to the opt-in phone-frame Shed. Reuse the
   Campaign's existing buttons/actions so identity and return handling stay owned
   by the application. */
(()=>{
 'use strict';
 const base=new URL('.',document.currentScript.src);
 const watched=new WeakSet();
 const barryURL='https://barrys-air-traffic-control.anvilspringstien.chatgpt.site/?from=tffac-shed';
 const css=`
 .my-journey-bar.campaign-nav-tiered.phone-frame-nav{gap:12px!important}
 .phone-frame-nav .campaign-primary-nav,.phone-frame-nav .campaign-magic-nav{display:grid!important;grid-template-columns:repeat(2,minmax(0,1fr))!important;gap:8px!important;width:100%}
 .my-journey-bar.phone-frame-nav .campaign-primary-nav button.round,.my-journey-bar.phone-frame-nav .campaign-magic-nav button.round{display:flex;align-items:center;justify-content:center;min-width:0;width:100%;min-height:44px;padding:9px 6px;margin:0;border-radius:10px;font:600 13px/1.25 Poppins,Arial,sans-serif;text-align:center;white-space:normal}
 .phone-frame-nav .campaign-magic-nav{margin-top:4px}
 .my-journey-bar.phone-frame-nav .campaign-magic-nav button.round{background:#e4bb26!important;color:#111!important}
 .my-journey-bar.phone-frame-nav .campaign-primary-nav .barry-air-launch{box-shadow:inset 0 0 0 1px #d4b269;color:#f6e7bf}
 .phone-frame-nav .campaign-secondary-nav{gap:6px;padding-top:2px}
 .my-journey-bar.phone-frame-nav .campaign-secondary-nav button.round{background:#eeeeee!important;color:#454545!important;border:1px solid #bbb;min-height:34px;padding:6px 9px;font-size:10px;border-radius:7px}
 .phone-frame-nav button:focus-visible{outline:2px solid #084c61;outline-offset:3px}
 `;
 window.tffcInstallPhoneFrameNavigation=function(frame){
  let doc;
  try{doc=frame.contentDocument;}catch(_){return;}
  if(!doc)return;
  function decorate(){
   if(!doc.head)return;
   if(!doc.getElementById('phone-frame-navigation-style')){
    const style=doc.createElement('style');style.id='phone-frame-navigation-style';style.textContent=css;doc.head.append(style);
   }
   for(const bar of doc.querySelectorAll('.campaign-nav-tiered:not(.phone-frame-nav)')){
    const core=bar.querySelector('.campaign-primary-nav');
    const controls=bar.querySelector('.campaign-secondary-nav');
    const share=controls?.querySelector('.campaign-share');
    if(!core||!controls||!share)continue;
    bar.classList.add('phone-frame-nav');
    core.setAttribute('aria-label','Your Campaign destinations');
    const barry=doc.createElement('button');
    barry.type='button';barry.className='round barry-air-launch';barry.textContent='Barry Air';
    barry.addEventListener('click',()=>location.assign(barryURL));core.append(barry);
    const magic=doc.createElement('div');magic.className='campaign-magic-nav';magic.setAttribute('aria-label','Keep and share Tin Foil FA Cup');
    const keep=doc.createElement('button');keep.type='button';keep.className='round campaign-keep';keep.textContent='Keep the Magic';
    keep.addEventListener('click',()=>{
     const win=doc.defaultView;
     if(typeof win.tffcOpenShare!=='function')return;
     win.tffcOpenShare();
     const destination=doc.querySelector('#tffcShareHost iframe');
     if(destination)destination.src=new URL('keep-the-magic-shed.html?instructions=1&embedded=1&keep=1',base).href;
    });
    magic.append(keep,share);core.after(magic);
   }
  }
  decorate();
  if(!watched.has(doc)){
   watched.add(doc);
   // Handles saved Campaign restore, View Originals, End/Resume and the
   // existing journey's document.write replacement without polling.
   new MutationObserver(decorate).observe(doc,{childList:true,subtree:true});
  }
 };
})();
