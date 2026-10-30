/* Public launch: keep the accepted Splash as the no-JavaScript fallback and
   render the same source within the approved shared phone viewport. */
(()=>{
 'use strict';
 const base=new URL('.',document.currentScript.src);
 const shell=document.createElement('main');shell.className='phone-shell';shell.setAttribute('aria-label','Tin Foil FA Cup');
 const frame=document.createElement('iframe');frame.id='phoneApp';frame.title='Tin Foil FA Cup — phone composition';frame.allow='web-share';shell.append(frame);
 document.body.replaceChildren(shell);
 for(const file of ['phone-frame-navigation.js','phone-frame-shed.js']){
  const script=document.createElement('script');script.src=new URL(file,base).href;script.async=false;document.head.append(script);
 }
})();
