/* Public door checks are anonymous. Campaign details travel only on explicit entry. */
(()=>{
 'use strict';
 const home='https://tffac-boot-room-shed.anvilspringstien.workers.dev';
 let state=null,checked=0,epoch=0,controller=null,timer=null,dialog=null,paused=false;
 const style=document.createElement('style');
 style.textContent=`
 .campaign-boot-room-nav{display:flex;justify-content:center;margin:4px 0 -4px}
 .my-journey-bar .campaign-boot-room-nav .boot-room-launch{width:270px;max-width:100%;min-height:65px;padding:9px 16px;border:2px solid #b59a5d;border-radius:5px;box-sizing:border-box;background:linear-gradient(145deg,#264639,#142b23);color:#f8f0d9;box-shadow:inset 0 1px 0 #f1d99466,inset 0 -2px 0 #07180f,0 3px 5px #0005;cursor:pointer;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:5px}
 .boot-room-launch .boot-room-label{font:normal 23px/1.1 Georgia,serif;letter-spacing:.2px;white-space:nowrap}
 .boot-room-launch .boot-room-status{font:600 8px/1.4 Arial,sans-serif;letter-spacing:1.35px;color:#d6bc7c;display:flex;align-items:center;gap:6px}
 .boot-room-launch .boot-room-status:before{content:'';width:5px;height:5px;border-radius:50%;background:currentColor}
 .boot-room-launch[data-room-state=open] .boot-room-status{color:#b5d9bb}
 .boot-room-launch[data-room-state=unknown] .boot-room-status{color:#c8c6b8}
 .boot-room-launch:hover{filter:brightness(1.1)}.boot-room-launch:focus-visible{outline:3px solid #d6bc7c;outline-offset:4px}.boot-room-launch:active{transform:translateY(1px)}
 #boot-room-welcome{box-sizing:border-box;width:min(390px,calc(100vw - 30px));max-height:calc(100svh - 32px);padding:25px 23px;border:1px solid #b59a5d;border-radius:12px;background:#fffbee;color:#20372f;overflow:auto;margin:auto;font:14px/1.65 Arial,sans-serif;box-shadow:0 14px 60px #0005}
 #boot-room-welcome h2:focus{outline:none;box-shadow:none}#boot-room-welcome h2,#boot-room-welcome button,#boot-room-welcome a{-webkit-tap-highlight-color:transparent}
 #boot-room-welcome::backdrop{background:#0008}#boot-room-welcome .boot-welcome-top{display:flex;align-items:start;gap:12px;justify-content:space-between}#boot-room-welcome h2{font:normal 27px/1.15 Georgia,serif;margin:0;color:#084c61}#boot-room-welcome .boot-welcome-close{font:25px/1 Arial,sans-serif;padding:0 3px;min-width:32px;min-height:32px;border:0;background:none;color:#084c61;cursor:pointer}#boot-room-welcome p{margin:16px 0}#boot-room-welcome .boot-welcome-small{font-size:11px;color:#68685b}#boot-room-welcome .boot-welcome-go{display:block;text-align:center;background:#173c30;color:#fff7df;border:1px solid #b59a5d;border-radius:6px;padding:10px 16px;text-decoration:none;font-weight:bold}#boot-room-welcome a:focus-visible,#boot-room-welcome button:focus-visible{outline:3px solid #bd9650;outline-offset:3px}
 `;
 document.head.append(style);
 const buttons=()=>Array.from(document.querySelectorAll('.boot-room-launch'));
 function paint(){
  const fresh=state&&Date.now()-checked<90000,kind=fresh?(state.open?'open':'closed'):'unknown';
  const label=fresh?(state.open?'DOORS OPEN':'DOORS CLOSED'):'CHECK THE DOORS';
  for(const b of buttons()){
   if(b.dataset.roomState!==kind)b.dataset.roomState=kind;
   const text=b.querySelector('.boot-room-status');if(text.textContent!==label)text.textContent=label;
   const title=fresh?'Room status checked '+new Date(checked).toLocaleTimeString('en-GB',{hour:'2-digit',minute:'2-digit'})+'.':'Room status needs checking. You can still visit the entrance.';
   if(b.title!==title)b.title=title;
   const aria='The Boot Room · '+(fresh?(state.open?'doors open':'doors closed'):'status unavailable');if(b.getAttribute('aria-label')!==aria)b.setAttribute('aria-label',aria);
  }
 }
 function schedule(){clearTimeout(timer);if(!paused&&document.visibilityState!=='hidden'&&buttons().length)timer=setTimeout(()=>{timer=null;refresh();},state?.open&&state.until>Date.now()?Math.max(1000,Math.min(60000,state.until-Date.now()+50)):60000);}
 async function refresh(){
  if(paused||document.visibilityState==='hidden'||!buttons().length||controller)return;
  const e=++epoch,request=new AbortController();controller=request;
  const timeout=setTimeout(()=>request.abort(),5000);
  try{
   const r=await fetch(home+'/api/doors',{cache:'no-store',credentials:'omit',referrerPolicy:'no-referrer',signal:request.signal});
   if(!r.ok)throw Error('Status unavailable');const d=await r.json();
   if(typeof d.open!=='boolean'||!Number.isFinite(d.until))throw Error('Invalid room status');
   if(e!==epoch)return;state={open:d.open,until:d.until};checked=Date.now();
  }catch(_){if(e===epoch){state=null;checked=0;}}
  finally{clearTimeout(timeout);if(controller===request)controller=null;if(e===epoch){paint();schedule();}}
 }
 function pause(){paused=true;epoch++;controller?.abort();controller=null;clearTimeout(timer);state=null;paint();}
 function resume(){paused=false;paint();refresh();}
 function campaignEntry(){
  if(typeof loadSavedJourney!=='function'||typeof tinFoilSavedCallSign!=='function'||typeof candidateClubByName!=='function'||typeof nextRoundInfo!=='function')return null;
  const saved=loadSavedJourney();
  if(!saved||saved.ended)return null;
  const callSign=/^(?:Tango Foxtrot 2 Alpha Charlie|TF2AC) (?:(\d{5})|\[(\d{5})\])$/i.exec(tinFoilSavedCallSign(saved));
  const custodian=document.querySelector('.chosen-campaign-current .custodian-name')?.textContent.trim();
  if(!callSign||!custodian)return null;
  const digits=callSign[1]||callSign[2];
  const name=tinFoilSavedPigeonName(saved)||'Pigeon '+digits;
  const club=candidateClubByName(custodian);
  const fixture=club&&nextRoundInfo(club)?.knownFixture;
  const detail={callSign:'TF2AC '+digits,name,custodian,fixture:fixture?.home&&fixture?.away?fixture.home+' v '+fixture.away:'Fixture to be announced'};
  return home+'/chat#campaign='+encodeURIComponent(JSON.stringify(detail));
 }
 function welcome(){
  refresh();if(dialog)return;
  const previous=document.activeElement;
  const box=document.createElement('dialog');box.id='boot-room-welcome';box.setAttribute('aria-labelledby','boot-room-welcome-title');
  box.innerHTML='<div class="boot-welcome-top"><h2 id="boot-room-welcome-title" tabindex="-1">The Boot Room is taking shape.</h2><button type="button" class="boot-welcome-close" aria-label="Close Boot Room welcome">×</button></div><p>Come in and have a peek. Read a sample conversation, or join with My Campaign when Barry opens the doors.</p><p>We’re still moving the furniture about.</p><p class="boot-welcome-small">This is an experimental opening. If the doors are closed, we’re still working on the room. Check back to try posting at the next opening. Your Campaign stays saved here.</p><a class="boot-welcome-go" href="'+home+'/" target="_top" rel="noreferrer">Have a look →</a>';
  const entry=campaignEntry();
  if(entry){
   const link=document.createElement('a');link.className='boot-welcome-go';
   link.href=entry;link.target='_top';link.rel='noreferrer';
   link.textContent='Join with My Campaign →';box.append(link);
  }
  dialog=box;document.body.append(box);box.showModal();box.querySelector('h2').focus({preventScroll:true});
  const close=()=>{if(dialog!==box)return;dialog=null;box.close();box.remove();if(previous?.isConnected)previous.focus({preventScroll:true});};
  box.querySelector('button').onclick=close;box.addEventListener('cancel',e=>{e.preventDefault();close();});
 }
 function install(){
  let added=false;
  for(const barry of document.querySelectorAll('.campaign-nav-tiered .campaign-barry-nav')){
   const nav=barry.parentNode,existing=nav.querySelector('.campaign-boot-room-nav');if(existing){if(existing.nextElementSibling!==barry)barry.before(existing);continue;}
   const row=document.createElement('div');row.className='campaign-boot-room-nav';
   const button=document.createElement('button');button.type='button';button.className='boot-room-launch';button.dataset.roomState='unknown';
   button.innerHTML='<span class="boot-room-label">The Boot Room</span><span class="boot-room-status">CHECK THE DOORS</span>';row.append(button);barry.before(row);added=true;
  }
  // Restored Campaign HTML has no handlers: always attach to its current button.
  for(const b of buttons())b.onclick=welcome;
  paint();if(!controller&&!timer&&buttons().length)refresh();
 }
 new MutationObserver(install).observe(document.body,{childList:true,subtree:true});
 document.addEventListener('visibilitychange',()=>document.visibilityState==='hidden'?pause():resume());
 window.addEventListener('pagehide',()=>{pause();if(dialog){dialog.close();dialog.remove();dialog=null;}});
 window.addEventListener('pageshow',resume);window.addEventListener('online',resume);window.addEventListener('offline',pause);
 install();
})();
