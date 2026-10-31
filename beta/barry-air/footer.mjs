import {adminHtml,aboutBody,privacyBody,supportURL} from './footer-content.mjs';

const host=document.querySelector('#barry-site-footer');
const base=new URL('../',import.meta.url);
host.innerHTML='<div class="tffc-support-row tffc-magic-row" aria-label="Keep and share Tin Foil FA Cup"><button class="tffc-support-lozenge" type="button" data-magic="keep">Keep the Magic</button><button class="tffc-support-lozenge" type="button" data-magic="share">Share the Magic</button></div><div class="tffc-support-row"><a class="tffc-support-lozenge" target="_blank" rel="noopener noreferrer" aria-label="Support Tin Foil FA Cup (opens Stripe in a new tab)">Support Tin Foil FA Cup</a></div><nav class="tffc-support-footer" aria-label="Tin Foil FA Cup information">'+adminHtml+'</nav>';
host.querySelector('a.tffc-support-lozenge').href=supportURL;
const redundantShare=host.querySelector('[onclick="tffcOpenShare()"]');
redundantShare?.nextElementSibling?.remove();redundantShare?.remove();
host.querySelector('.tffc-beta-help').setAttribute('aria-label','Tin Foil FA Cup support links');

let active=null;
function showDialog(dialog){
 if(active)return false;
 active=dialog;const previous=document.activeElement,keyboard=previous?.matches(':focus-visible');
 const room=document.querySelector('.field'),scroll=room.scrollTop,overflow=room.style.overflowY;
 room.style.overflowY='hidden';document.body.append(dialog);
 dialog.addEventListener('close',()=>{
  active=null;room.style.overflowY=overflow;room.scrollTop=scroll;dialog.remove();
  if(previous?.isConnected){previous.focus({preventScroll:true});if(!keyboard)previous.blur();}
 },{once:true});
 dialog.showModal();return true;
}
function openInfo(title,html){
 const dialog=document.createElement('dialog');dialog.className='barry-info-dialog';dialog.setAttribute('aria-labelledby','barry-footer-title');
 dialog.innerHTML='<h2 id="barry-footer-title" tabindex="-1"></h2><div class="barry-info-copy"></div><div class="barry-info-actions"><button type="button">Close</button></div>';
 dialog.querySelector('h2').textContent=title;dialog.querySelector('.barry-info-copy').innerHTML=html;
 dialog.querySelector('button').onclick=()=>dialog.close();
 dialog.addEventListener('click',event=>{if(event.target===dialog){const r=dialog.getBoundingClientRect();if(event.clientX<r.left||event.clientX>r.right||event.clientY<r.top||event.clientY>r.bottom)dialog.close();}});
 if(showDialog(dialog))dialog.querySelector('h2').focus({preventScroll:true});
}
function openMagic(keep){
 const dialog=document.createElement('dialog');dialog.className='barry-magic-dialog';dialog.setAttribute('aria-label',keep?'Keep the Magic':'Share the Magic');
 const frame=document.createElement('iframe');frame.title='Share Tin Foil FA Cup';frame.allow='clipboard-write; web-share';
 const url=new URL('keep-the-magic-shed.html?instructions=1&embedded=1',base);if(keep)url.searchParams.set('keep','1');frame.src=url.href;
 dialog.append(frame);
 const onMessage=event=>{if(event.origin===location.origin&&event.source===frame.contentWindow&&event.data?.type==='tffc-share-close')dialog.close();};
 if(!showDialog(dialog))return;
 window.addEventListener('message',onMessage);dialog.addEventListener('close',()=>window.removeEventListener('message',onMessage),{once:true});frame.focus({preventScroll:true});
}
for(const button of host.querySelectorAll('[data-magic]'))button.onclick=()=>openMagic(button.dataset.magic==='keep');
for(const button of host.querySelectorAll('[onclick]')){
 const action=button.getAttribute('onclick');button.removeAttribute('onclick');
 if(action==='tffcAboutUs()')button.onclick=()=>openInfo('About Us',aboutBody);
 if(action==='tinFoilPrivacyNotice()')button.onclick=()=>openInfo('Privacy',privacyBody);
}
// Reuse the existing Post Office launcher for Feedback and Report an Issue.
const postOffice=document.createElement('script');postOffice.src=new URL('post-office-launcher.js',base).href;document.head.append(postOffice);
// A deferred native install prompt belongs to this top-level page.
window.addEventListener('beforeinstallprompt',event=>{event.preventDefault();window.__tffcMagicInstallPrompt=event;active?.querySelector('iframe')?.contentWindow.postMessage({type:'tffc-install-ready'},location.origin);});
window.addEventListener('appinstalled',()=>{window.__tffcMagicInstallPrompt=null;active?.querySelector('iframe')?.contentWindow.postMessage({type:'tffc-app-installed'},location.origin);});
