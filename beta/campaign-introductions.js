// Campaign-scoped introductions. Preparation is read-only until Got It!.
(function(){
'use strict';
let active=null;
const copy={
 campaign:{title:'My Campaign',message:'Your Tin Foil FA Cup Campaign is saved on this device, in this browser.\n\nYour Campaign choice, Pigeon Call Sign and Pigeon Name will be here when you return.\n\nYour progress is stored locally. Clearing browser data or using another browser or device may mean it isn’t available there.'},
 stats:{title:'My Stats',message:'Follow your Campaign’s progress through the FA Cup, discover how far your pigeon has flown, and collect the achievements you’ve earned along the way.\n\nYour Stats grow as your Campaign progresses. We’re getting your Stats ready behind the scenes.'},
 challenges:{title:'My Challenges',message:'Explore the Challenge Deck, take on Challenges along your Cup Run, and collect the achievements you’ve earned in your Trophy Cabinet.\n\nYour verified Campaign progress updates your achievements and Pigeon Miles. We’re getting your Challenges ready behind the scenes.'}
};
async function warmDeck(){
 try{
  const response=await fetch('challenges-beta.html',{cache:'force-cache'});
  if(!response.ok)return;
  const html=await response.text(),match=html.match(/const ART = (\{[^\n]+\});/);
  const art=match?JSON.parse(match[1]):{};
  const sources=new Set([art['00']&&art['00'].front]);
  const deck=JSON.parse(localStorage.getItem('tffc.challengeDeck.v1')||'null');
  for(const id of Object.keys(deck&&deck.completed||{}).slice(0,12))if(/^\d+$/.test(id))sources.add('assets/challenge-thumbs/mat-'+id+'-front.webp');
  await Promise.all([...sources].filter(src=>/^assets\/(challenge-mats|challenge-thumbs)\/[\w-]+\.webp$/.test(src||'')).map(src=>new Promise(resolve=>{
   const img=new Image(),timer=setTimeout(resolve,8000);const finish=()=>{clearTimeout(timer);resolve()};img.onload=finish;img.onerror=finish;img.src=src;if(img.complete)finish();
  })));
 }catch(_){} // Artwork/cache failures must not block the existing Deck route.
}
window.tffcCampaignIntroduction=function(kind,origin){
 if(!copy[kind]||!origin||active)return;
 const saved=loadSavedJourney();
 if(saved&&saved.introDismissed&&saved.introDismissed[kind]===true){
  return kind==='campaign'?undefined:kind==='stats'?journeyCertificate(origin):openChallenges(origin);
 }
 const original=JSON.stringify(saved),previous=document.activeElement;
 const dialog=document.createElement('dialog');dialog.id='tffc-campaign-intro';
 dialog.className='tin-foil-confirm-box';dialog.setAttribute('aria-labelledby','tffc-intro-title');dialog.setAttribute('aria-describedby','tffc-intro-message');
 dialog.innerHTML='<style>#tffc-campaign-intro{width:min(420px,calc(100vw - 40px));height:min(410px,calc(100svh - 40px));box-sizing:border-box;display:flex;flex-direction:column;overflow:auto;overscroll-behavior:contain;margin:auto}#tffc-campaign-intro::backdrop{background:rgba(0,0,0,.48)}#tffc-campaign-intro .intro-head{display:flex;align-items:center;justify-content:space-between;gap:12px}#tffc-campaign-intro .intro-close{border:0;background:transparent;color:#084c61;font-size:28px;min-width:44px;min-height:44px;cursor:pointer}#tffc-campaign-intro #tffc-intro-message{flex:1;min-height:0;overflow:auto}#tffc-campaign-intro .intro-head,#tffc-campaign-intro .intro-actions,#tffc-campaign-intro label{flex-shrink:0}#tffc-campaign-intro label{display:flex;align-items:flex-start;gap:8px;margin:16px 0}#tffc-campaign-intro input{width:20px;height:20px;flex:none;margin:0}#tffc-campaign-intro .intro-actions{display:flex;justify-content:flex-end}#tffc-campaign-intro .intro-carry{background:#084c61;color:#fafafa;border:2px solid #084c61;border-radius:10px;min-width:74px;height:36px;padding:0 14px;font:400 13px Poppins,Arial,sans-serif;cursor:pointer}#tffc-campaign-intro .intro-state:empty{display:none}</style><div class="intro-head"><h2 id="tffc-intro-title" class="tin-foil-confirm-title"></h2><button type="button" class="intro-close" aria-label="Close">×</button></div><p id="tffc-intro-message" class="tin-foil-confirm-message"></p><p class="intro-state" role="status" aria-live="polite"></p><label><input type="checkbox">Don’t show this again this Campaign</label><div class="intro-actions"><button type="button" class="intro-carry">Got It!</button></div>';
 dialog.querySelector('h2').textContent=copy[kind].title;
 dialog.querySelector('#tffc-intro-message').textContent=copy[kind].message;
 const carry=dialog.querySelector('.intro-carry'),status=dialog.querySelector('.intro-state');
 let finished=false;active=dialog;document.body.append(dialog);dialog.showModal();
 const finish=()=>{
  if(finished)return;finished=true;active=null;window.removeEventListener('pagehide',cancel);
  dialog.close();dialog.remove();if(previous&&previous.isConnected)previous.focus({preventScroll:true});
 };
 const cancel=()=>finish();
 dialog.querySelector('.intro-close').onclick=cancel;
 dialog.addEventListener('cancel',event=>{event.preventDefault();cancel()});
 dialog.addEventListener('click',event=>{const r=dialog.getBoundingClientRect();if(event.target===dialog&&(event.clientX<r.left||event.clientX>r.right||event.clientY<r.top||event.clientY>r.bottom))cancel()});
 window.addEventListener('pagehide',cancel);
 // Paint the explanation before calculating mileage, generating Stats or warming Deck assets.
 const work=new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))).then(async()=>{
  if(kind==='campaign')return null;
  await tinFoilEnsureCompetitionReady();
  if(kind==='stats')return tinFoilPrepareStatsDocument(origin,'clubfinder');
  const [truth]=await Promise.all([tinFoilPrepareChallenges(origin),warmDeck()]);return truth;
 }).then(value=>({ok:true,value}),()=>({ok:false}));
 work.then(result=>{if(!finished&&!result.ok){status.textContent='We couldn’t get this ready. Please close this message and try again.';carry.disabled=true;}});
 carry.onclick=()=>{
  if(finished)return;
  if(JSON.stringify(loadSavedJourney())!==original){status.textContent='Your Campaign changed while this message was open. Please close it and try again.';carry.disabled=true;return;}
  carry.disabled=true;
  if(dialog.querySelector('input').checked&&saved){try{updateSavedJourney({introDismissed:{...saved.introDismissed,[kind]:true}})}catch(_){}}
  finish();
  if(kind==='campaign')return;
  const prepared=work.then(result=>{if(!result.ok)throw Error('Preparation failed');return result.value});
  // Stats still opens synchronously in this user gesture, avoiding popup blockers.
  if(kind==='stats')journeyCertificate(origin,null,'clubfinder',prepared);
  else openChallenges(origin,prepared);
 };
};
})();
