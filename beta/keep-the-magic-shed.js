(function(){
'use strict';
const standalone=()=>matchMedia('(display-mode: standalone)').matches||navigator.standalone===true;
if(window.tffcInstalledEntry)return;
const URL_TO_SHARE='https://tinfoilfacup.com/';
const QR_ROWS='111111101110010111000001101111111/100000101010101011100110101000001/101110101010101110100101101011101/101110100000110100110011101011101/101110100010010010100000001011101/100000101111010101000111101000001/111111101010101010101010101111111/000000001000000100011111000000000/001110101001001010100001111100111/100111000011001101000101011000101/001101101011101000111100010101010/011110011001000100110111001001100/010001110110000111101101110001010/001000010011000101001011001100101/101001101010100100100010011001110/010001010010000111111110101100110/001100111001010110100001010111101/101111010111111001011101101100000/010010110110100111100010011100111/010010010010110010010101101101101/011000100000000100000010011111011/101011000101101000101000100000001/100111100110100010101010000111110/101001000100001000011110100011110/100111101010010110101100111110000/000000001100101110010000100011111/111111100000011100101011101011110/100000100110010010011001100011111/101110101111011010001110111111011/101110101001100111000001010011010/101110101101001011011110111000000/100000100001111010010100011101000/111111100011100101111101111000110'.split('/');const ns='http://www.w3.org/2000/svg';const QR_SIZE=QR_ROWS.length;const svg=document.createElementNS(ns,'svg');svg.setAttribute('viewBox','-4 -4 '+(QR_SIZE+8)+' '+(QR_SIZE+8));svg.setAttribute('role','img');svg.setAttribute('aria-label','QR code for Tin Foil FA Cup homepage');svg.setAttribute('shape-rendering','geometricPrecision');const INK='#084c61',PAPER='#fffff2';function addQrRect(x,y,width,height,fill,radius){const el=document.createElementNS(ns,'rect');el.setAttribute('x',x);el.setAttribute('y',y);el.setAttribute('width',width);el.setAttribute('height',height);el.setAttribute('fill',fill);if(radius)el.setAttribute('rx',radius);svg.append(el);}addQrRect(-4,-4,QR_SIZE+8,QR_SIZE+8,PAPER,0);const finderPositions=[[0,0],[QR_SIZE-7,0],[0,QR_SIZE-7]];function insideFinder(x,y){return finderPositions.some(([fx,fy])=>x>=fx&&x<fx+7&&y>=fy&&y<fy+7)}QR_ROWS.forEach((row,y)=>[...row].forEach((v,x)=>{if(v==='1'&&!insideFinder(x,y))addQrRect(x,y,1,1,INK,.23)}));finderPositions.forEach(([x,y])=>{addQrRect(x,y,7,7,INK,1.05);addQrRect(x+1,y+1,5,5,PAPER,.65);addQrRect(x+2,y+2,3,3,INK,.52)});document.getElementById('qr').append(svg);
let returnTo=null;
try{
 const candidate=new URL(new URLSearchParams(location.search).get('return')||'',location.href);
 if(candidate.origin===location.origin&&['/beta/clubfinder-beta.html','/beta/clubfinder-journey.html','/beta/challenges-beta.html'].includes(candidate.pathname))returnTo=candidate.href;
}catch(_){}
const returnToShare=()=>{if(returnTo){location.replace(returnTo);return true}return false};
const dialog=document.getElementById('magic');
const heading=document.getElementById('heading');
const shareView=document.getElementById('share-view'),keepView=document.getElementById('keep-view');
const keepButton=document.getElementById('keep');
const platform=document.getElementById('platform'),steps=document.getElementById('steps');
const install=document.getElementById('install'),installStatus=document.getElementById('install-status');
let pendingInstall=null,installPrepared=false;
const instructions={
 apple:['In Safari, see the little square icon with the arrow pointing up? It’s on that bar at the bottom of your screen. Tap that.','Scroll down to ‘Add to Home Screen’ and tap that.','Tap ‘Add’. You’re done!'],
 android:['In Chrome, tap the three dots by the address bar.','Look for ‘Install and create shortcut’, ‘Install app’ or ‘Add to Home screen’. Tap it and follow the prompts.','Look for the Tin Foil FA Cup icon. Tap it whenever you’re ready for more Cup magic!'],
 computer:['Open your browser’s menu — usually the three dots at the top right.','In Chrome, try ‘Cast, save, and share’. In Edge, look under ‘More tools’, then ‘Apps’.','Choose ‘Install page as app’ or ‘Install this site as an app’, then confirm. You’re done!']
};
function renderInstructions(){document.getElementById('platform-note').hidden=platform.value==='apple'||standalone();steps.replaceChildren(...instructions[platform.value].map(text=>{const li=document.createElement('li');li.textContent=text;return li}));}
function updateInstall(){const isInstalled=standalone();if(dialog.classList.contains('keeping'))heading.textContent=isInstalled?'You Kept the Magic!':'Keep the Magic';document.getElementById('keep-intro').textContent=isInstalled?'See. We told you it was easy.':'Adding Tin Foil FA Cup to your Home Screen has never been easier.';document.getElementById('installed-celebration').hidden=!isInstalled;install.hidden=isInstalled||!pendingInstall||!installPrepared;platform.hidden=isInstalled;document.querySelector('label[for="platform"]').hidden=isInstalled;steps.hidden=isInstalled;if(isInstalled)installStatus.textContent='You’re already opening Tin Foil FA Cup as an app.';installStatus.classList.toggle('installed',isInstalled);}
function showShare(){dialog.style.removeProperty('--phone-share-crest-size');dialog.classList.remove('keeping');heading.textContent='Share the Magic';shareView.hidden=false;keepView.hidden=true;dialog.scrollTop=0;}
async function prepareInstall(){
 if(standalone())return;
 installPrepared=false;install.disabled=true;installStatus.textContent='Preparing your saved Campaign…';
 try{await TffcMagicInstall.prepare();installPrepared=true;installStatus.textContent='';install.disabled=false;updateInstall();}
 catch(_){
  install.hidden=true;installStatus.textContent='Before adding to Home Screen, save a backup of your Campaign and Challenges. ';
  const link=document.createElement('a');link.href='keep-the-magic.html';link.textContent='Save or restore a backup';installStatus.append(link);
 }
}
function showKeep(){if(!dialog.classList.contains('keeping')&&matchMedia('(max-width:600px) and (min-height:500px)').matches)dialog.style.setProperty('--phone-share-crest-size',document.querySelector('.brand').getBoundingClientRect().width+'px');dialog.classList.add('keeping');heading.textContent='Keep the Magic';shareView.hidden=true;keepView.hidden=false;renderInstructions();updateInstall();dialog.scrollTop=0;(standalone()?heading:document.getElementById(install.hidden?'platform':'install')).focus();prepareInstall();}
document.getElementById('close').onclick=()=>dialog.close();
dialog.addEventListener('click',e=>{const box=dialog.getBoundingClientRect();if(e.target===dialog&&(e.clientX<box.left||e.clientX>box.right||e.clientY<box.top||e.clientY>box.bottom))dialog.close()});
dialog.addEventListener('close',()=>{
 const destination=new URL(returnTo||'./',location.href);
 if(returnTo){destination.searchParams.delete('magicShare');destination.searchParams.set('magicReturn','1')}
 location.replace(destination.href);
});
keepButton.onclick=showKeep;document.getElementById('back').onclick=()=>{if(!returnToShare()){showShare();keepButton.focus()}};
platform.value=/iPad|iPhone|iPod/.test(navigator.userAgent)||(navigator.platform==='MacIntel'&&navigator.maxTouchPoints>1)?'apple':/Android/.test(navigator.userAgent)?'android':'computer';
platform.onchange=renderInstructions;
document.getElementById('copy').onclick=async()=>{const status=document.getElementById('feedback');try{await navigator.clipboard.writeText(URL_TO_SHARE);status.textContent='Link copied'}catch{status.textContent='Copy unavailable. Our address is tinfoilfacup.com'}};
document.getElementById('share').onclick=async()=>{const status=document.getElementById('feedback');if(!navigator.share){status.textContent='Sharing unavailable — try Copy Link';return}try{await navigator.share({title:'Tin Foil FA Cup — Start Your Journey Here',url:URL_TO_SHARE})}catch(e){if(e.name!=='AbortError')status.textContent='Sharing unavailable — try Copy Link'}};
window.addEventListener('beforeinstallprompt',e=>{e.preventDefault();pendingInstall=e;updateInstall()});
window.addEventListener('appinstalled',()=>{pendingInstall=null;updateInstall();installStatus.textContent='Added. Look for Tin Foil FA Cup in your apps.'});
install.onclick=async()=>{const request=pendingInstall;if(!request)return;pendingInstall=null;install.disabled=true;try{await request.prompt();const choice=await request.userChoice;installStatus.textContent=choice.outcome==='accepted'?'Installation requested. Try the Tin Foil FA Cup icon once it appears.':'You can add it later using your browser menu.'}catch{installStatus.textContent='Please use your browser menu to add this page.'}finally{install.hidden=true;install.disabled=false}};
window.addEventListener('DOMContentLoaded',()=>{renderInstructions();showShare();dialog.showModal();heading.focus({preventScroll:true});if(new URLSearchParams(location.search).get('keep')==='1')showKeep()});

})();
