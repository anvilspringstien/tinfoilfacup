// Recognise a returning supporter without changing the approved Splash geometry.
(function(){
'use strict';
let button,sizer,label;
function update(){
 if(!button)button=document.querySelector('.splash-start');
 if(!button)return;
 let current=false;
 try{
  const saved=JSON.parse(localStorage.getItem('tinFoilFACupJourney_v7')||'null');
  current=!!(saved&&!saved.ended&&typeof saved.originName==='string'&&saved.originName.trim()&&typeof saved.postcode==='string'&&saved.postcode.trim());
 }catch(_){}
 if(current&&!label){
  // The invisible original text retains exactly the same intrinsic size as
  // before, including while the approved font loads. Only the label changes.
  sizer=document.createElement('span');sizer.textContent=button.textContent;
  sizer.setAttribute('aria-hidden','true');sizer.style.visibility='hidden';
  label=document.createElement('span');label.textContent='My Campaign';
  label.style.cssText='position:absolute;inset:0;display:flex;align-items:center;justify-content:center';
  button.style.position='relative';button.replaceChildren(sizer,label);
 }else if(!current&&label){
  button.textContent=sizer.textContent;button.style.removeProperty('position');sizer=label=null;
 }
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',update,{once:true});else update();
window.addEventListener('pageshow',update);
window.addEventListener('storage',event=>{if(event.key===null||event.key==='tinFoilFACupJourney_v7')update()});
})();
