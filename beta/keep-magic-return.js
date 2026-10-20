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
  if(!share)return;
  if(typeof window.tffcOpenShare==='function')window.tffcOpenShare();
  else document.getElementById('challengeShareLinkFooter')?.click();
 };
 requestAnimationFrame(()=>requestAnimationFrame(finish));
});
