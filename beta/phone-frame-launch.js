/* Mount the shared frame for the explicit Public and Shed entrances. */
(()=>{
 'use strict';
 const base=new URL('.',document.currentScript.src);
 // An older cached shell can still request /beta/index.html as its Splash.
 // Keep one frame and select artwork from that shell's actual entrance.
 if(window!==window.top&&document.documentElement.dataset.tffcEntrance==='shed'){
  let shed=false;
  try{
   shed=window.parent.document.documentElement.dataset.tffcEntrance==='shed'
    || window.parent.location.pathname==='/beta/phone-frame-shed.html';
  }catch(_){}
  location.replace(new URL(shed?'shed-splash.html':'public-splash.html',base));
  return;
 }
 const shell=document.createElement('main');shell.className='phone-shell';shell.setAttribute('aria-label','Tin Foil FA Cup');
 const frame=document.createElement('iframe');frame.id='phoneApp';frame.title='Tin Foil FA Cup — phone composition';frame.allow='web-share';shell.append(frame);
 document.body.replaceChildren(shell);
 for(const file of ['phone-frame-navigation.js','phone-frame-shed.js']){
  const script=document.createElement('script');const url=new URL(file,base);url.searchParams.set('v',file==='phone-frame-shed.js'?'journey-paint-20261128':'entrance-boundary-20261127');const refresh=new URLSearchParams(location.search).get('tffc-refresh');if(refresh&&/^\d{10,16}$/.test(refresh))url.searchParams.set('refresh',refresh);script.src=url.href;script.async=false;document.head.append(script);
 }
})();
