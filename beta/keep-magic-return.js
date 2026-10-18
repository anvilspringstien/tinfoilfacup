// Reopen the originating application's existing Share popup after installation guidance.
window.addEventListener('load',()=>{
 const url=new URL(location.href);
 if(url.searchParams.get('magicShare')!=='1')return;
 url.searchParams.delete('magicShare');history.replaceState(history.state,'',url.pathname+url.search+url.hash);
 if(typeof window.tffcOpenShare==='function')window.tffcOpenShare();
 else document.getElementById('challengeShareLinkFooter')?.click();
});
