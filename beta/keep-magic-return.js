// Share and Keep X returns use the same landing as the surrounding app.
function tffcMagicReturnToStart(){
 if(typeof window.tffcScrollToFinder==='function'){window.tffcScrollToFinder();return}
 const deck=document.querySelector('#overlay .deck');
 if(deck){document.getElementById('overlay').scrollTop=0;deck.querySelector('.deckbody').scrollTop=0;window.scrollTo(0,0)}
}
// Capture the trusted iframe's close before its host removes it, then land
// after the host has restored scrolling and focus.
window.addEventListener('message',event=>{
 const frame=document.querySelector('#tffcShareHost iframe,#tffcChallengeShareHost iframe');
 if(event.origin===location.origin&&frame&&event.source===frame.contentWindow&&event.data?.type==='tffc-share-close')requestAnimationFrame(tffcMagicReturnToStart);
},true);
// Return from Keep to the originating view, optionally reopening Share.
window.addEventListener('load',()=>{
 const url=new URL(location.href),share=url.searchParams.get('magicShare')==='1';
 if(!share&&url.searchParams.get('magicReturn')!=='1')return;
 url.searchParams.delete('magicShare');url.searchParams.delete('magicReturn');
 history.replaceState(history.state,'',url.pathname+url.search+url.hash);
 let view=window.__tffcShareReturnView;
 try{
  if(!view){const saved=JSON.parse(sessionStorage.getItem('tffc.shareReturnView.v1')||'null');if(saved&&saved.path===location.pathname&&saved.savedCampaign===localStorage.getItem('tinFoilFACupJourney_v7'))view=saved}
  sessionStorage.removeItem('tffc.shareReturnView.v1');
 }catch(_){}
 const finish=()=>{
  if(view){
   if(view.searchNumber&&typeof window.tinFoilSetCurrentSearchNumber==='function')window.tinFoilSetCurrentSearchNumber(view.searchNumber);
   window.scrollTo(0,Number(view.scrollY)||0);
  }
  if(!share){tffcMagicReturnToStart();return}
  if(typeof window.tffcOpenShare==='function')window.tffcOpenShare();
  else document.getElementById('challengeShareLinkFooter')?.click();
 };
 requestAnimationFrame(()=>requestAnimationFrame(finish));
});

// Keep installation identity on the app host while Share and Keep use one iframe.
// The existing installed-entry URL and cookie handover remain unchanged.
(function(){
 for(const [selector,tag,attributes] of [
  ['link[rel="manifest"]','link',{rel:'manifest',href:'keep-the-magic-shed.webmanifest'}],
  ['link[rel="apple-touch-icon"]','link',{rel:'apple-touch-icon',href:'assets/keep-magic/apple-touch-icon.png'}],
  ['meta[name="apple-mobile-web-app-capable"]','meta',{name:'apple-mobile-web-app-capable',content:'yes'}],
  ['meta[name="apple-mobile-web-app-title"]','meta',{name:'apple-mobile-web-app-title',content:'Tin Foil FA Cup'}]
 ]){if(!document.querySelector(selector)){const node=document.createElement(tag);for(const [key,value] of Object.entries(attributes))node.setAttribute(key,value);document.head.append(node);}}
 const tellShare=type=>document.querySelector('#tffcShareHost iframe,#tffcChallengeShareHost iframe')?.contentWindow?.postMessage({type},location.origin);
 window.addEventListener('beforeinstallprompt',event=>{event.preventDefault();window.__tffcMagicInstallPrompt=event;tellShare('tffc-install-ready');});
 window.addEventListener('appinstalled',()=>{window.__tffcMagicInstallPrompt=null;tellShare('tffc-app-installed');});
})();
