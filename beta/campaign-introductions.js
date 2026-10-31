// Campaign-scoped introductions. Preparation is read-only until Got It!.
(function(){
'use strict';
// Keep the identity itself prominent while its descriptive label stays light.
const identityStyle=document.createElement('style');
identityStyle.textContent='.campaign-identity .campaign-call-sign-label{font-weight:300}';
document.head.append(identityStyle);
const introBase=new URL('.',document.currentScript.src);
const openBarry=()=>window.top.location.assign(new URL('barry-air/',introBase).href);
let active=null;
const copy={
 barry:{title:'Barry Air',message:"Welcome aboard Barry Air — your Tin Foil FA Cup Campaign, in flight.\n\nYour boarding pass carries your pigeon’s name, Call Sign, Miles Flown and next destination. Tick Check In when you’re ready for the next adventure.\n\nDepartures & Arrivals records the grounds on your journey. Tap a flight, a map marker or a ground button to explore its details. Use + and − to zoom the map, and ⌖ to fit the whole route.\n\nThe map follows your Campaign from ground to ground. Miles Flown counts your pigeon’s journeys from home and back, just as My Stats does.\n\nFlight details update with your Campaign. Check-in is saved on this device for each flight.\n\nPlease remain seated. All Barry Air pigeons are pie-fed pigeons — guaranteed."},
 campaign:{title:'My Campaign',message:"This is your Tin Foil FA Cup Campaign. There are many like this, but this one is yours.\n\nIt’s saved on this device, in your browser, along with your Pigeon Call Sign & Pigeon Name. Everything will be here when you return from your Campaign travels, and your pigeon, whatever its gender may be, will faithfully record the miles it has flown.\n\nYour pigeon’s unique Call Sign identifies its flight path in Barry Air.\n\nRemember: Your progress is stored locally. Clearing browser data or using another browser or device may mean it isn’t available there. Entering the same postcode and choosing the same Campaign again will rebuild your competition Stats, but you’ll receive a new Call Sign and pigeon. Your old pigeon identity and locally saved Challenge progress won’t be recovered."},
 stats:{title:'My Stats',message:"This is the permanent home of your Campaign’s progress through the FA Cup.\n\nIt can be saved as a .PDF, sent as part of a failed job application, or printed out and framed beautifully on your Mother’s wall.\n\nIt updates automatically as you move from round to round and can tell you pretty much everything there is to know about your Campaign. That’s why it’s called Stats!\n\nSome say that it has been known to predict the future, or the winners in major sporting events. Sadly, none of this is true.\n\nBut it will tell you how many miles your pigeon has flown!"},
 challenges:{title:'My Challenges',message:"This is where the real fun begins.\n\nExplore the Challenge Deck by flipping your way through our Beer Mats - with each mat containing a unique Challenge for you to complete.\n\nSome rely on you being an honourable footie fan, while others are awarded automatically by our Master Computer here at Tin Foil FA Cup Headquarters.\n\nEvery successful Challenge is placed in your Trophy Cabinet so others can look on and merely drool jealously at the size of your glorious achievements.\n\nKeep an eye out for Barry, our Staff Pigeon. He’s absolutely full of it."}
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
 if(!copy[kind]||(!origin&&kind!=='barry')||active)return;
 const saved=loadSavedJourney();
 if(saved&&saved.introDismissed&&saved.introDismissed[kind]===true){
  return kind==='barry'?openBarry():kind==='campaign'?undefined:kind==='stats'?journeyCertificate(origin):openChallenges(origin);
 }
 const original=JSON.stringify(saved),previous=document.activeElement;
 const dialog=document.createElement('dialog');dialog.id='tffc-campaign-intro';
 dialog.className='tin-foil-confirm-box';dialog.setAttribute('aria-labelledby','tffc-intro-title');dialog.setAttribute('aria-describedby','tffc-intro-message');
 dialog.innerHTML='<style>#tffc-campaign-intro{width:min(420px,calc(100vw - 40px));height:min(410px,calc(100svh - 40px));box-sizing:border-box;display:flex;flex-direction:column;overflow:auto;overscroll-behavior:contain;margin:auto}#tffc-campaign-intro::backdrop{background:rgba(0,0,0,.48)}#tffc-campaign-intro .intro-head{display:flex;align-items:center;justify-content:space-between;gap:12px}#tffc-campaign-intro .intro-close{border:0;background:transparent;color:#084c61;font-size:28px;min-width:44px;min-height:44px;cursor:pointer}#tffc-campaign-intro #tffc-intro-message{flex:1;min-height:0;overflow:auto;overscroll-behavior:contain;touch-action:pan-y;-webkit-overflow-scrolling:touch}#tffc-intro-title:focus{outline:none}#tffc-campaign-intro button:focus-visible{outline:3px solid #e5ce80;outline-offset:3px}#tffc-campaign-intro .intro-head,#tffc-campaign-intro .intro-actions,#tffc-campaign-intro label{flex-shrink:0}#tffc-campaign-intro label{display:flex;align-items:flex-start;gap:8px;margin:16px 0}#tffc-campaign-intro input{width:20px;height:20px;flex:none;margin:0;color-scheme:light}#tffc-campaign-intro .intro-actions{display:flex;justify-content:flex-end}#tffc-campaign-intro .intro-carry{background:#084c61;color:#fafafa;border:2px solid #084c61;border-radius:10px;min-width:74px;height:36px;padding:0 14px;font:400 13px Poppins,Arial,sans-serif;cursor:pointer}#tffc-campaign-intro .intro-state:empty{display:none}</style><div class="intro-head"><h2 id="tffc-intro-title" tabindex="-1" class="tin-foil-confirm-title"></h2><button type="button" class="intro-close" aria-label="Close">×</button></div><p id="tffc-intro-message" class="tin-foil-confirm-message"></p><p class="intro-state" role="status" aria-live="polite"></p><label><input type="checkbox">Don’t show this again this Campaign</label><div class="intro-actions"><button type="button" class="intro-carry">Got It!</button></div>';
 dialog.querySelector('h2').textContent=copy[kind].title;
 dialog.querySelector('#tffc-intro-message').textContent=copy[kind].message;
 const carry=dialog.querySelector('.intro-carry'),status=dialog.querySelector('.intro-state');
 const scroll={x:window.scrollX,y:window.scrollY},bodyStyle=document.body.getAttribute('style'),rootOverflow=document.documentElement.style.overflow;
 document.body.style.position='fixed';document.body.style.top=-scroll.y+'px';document.body.style.left=-scroll.x+'px';document.body.style.right='0';document.body.style.width='100%';document.documentElement.style.overflow='hidden';
 let finished=false;active=dialog;document.body.append(dialog);dialog.showModal();dialog.querySelector('#tffc-intro-title').focus({preventScroll:true});
 const finish=()=>{
  if(finished)return;finished=true;active=null;window.removeEventListener('pagehide',cancel);
  dialog.close();dialog.remove();if(bodyStyle===null)document.body.removeAttribute('style');else document.body.setAttribute('style',bodyStyle);document.documentElement.style.overflow=rootOverflow;window.scrollTo(scroll.x,scroll.y);if(previous&&previous.isConnected)previous.focus({preventScroll:true});
 };
 const cancel=()=>finish();
 dialog.querySelector('.intro-close').onclick=cancel;
 dialog.addEventListener('cancel',event=>{event.preventDefault();cancel()});
 dialog.addEventListener('click',event=>{const r=dialog.getBoundingClientRect();if(event.target===dialog&&(event.clientX<r.left||event.clientX>r.right||event.clientY<r.top||event.clientY>r.bottom))cancel()});
 window.addEventListener('pagehide',cancel);
 // Paint the explanation before calculating mileage, generating Stats or warming Deck assets.
 const work=new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))).then(async()=>{
  if(kind==='campaign'||kind==='barry')return null;
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
  if(kind==='barry'){openBarry();return;}
  if(kind==='campaign')return;
  const prepared=work.then(result=>{if(!result.ok)throw Error('Preparation failed');return result.value});
  // Stats still opens synchronously in this user gesture, avoiding popup blockers.
  if(kind==='stats')journeyCertificate(origin,null,'clubfinder',prepared);
  else openChallenges(origin,prepared);
 };
};
})();
