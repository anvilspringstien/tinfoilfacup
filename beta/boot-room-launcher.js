/* Public door checks are anonymous. Campaign details travel only on explicit entry. */
(()=>{
 'use strict';
 const home='https://tffac-boot-room-shed.anvilspringstien.workers.dev';
 let state=null,checked=0,epoch=0,controller=null,timer=null,paused=false;
 const style=document.createElement('style');
 style.textContent=`
 .campaign-boot-room-nav{display:flex;justify-content:center;margin:4px 0 -4px}
 .my-journey-bar .campaign-boot-room-nav .boot-room-launch{width:270px;max-width:100%;min-height:65px;padding:9px 16px;border:2px solid #b59a5d;border-radius:5px;box-sizing:border-box;appearance:none;-webkit-appearance:none;-webkit-tap-highlight-color:transparent;background:#203c32;color:#f8f0d9;box-shadow:inset 0 1px 0 #f1d99466,inset 0 -2px 0 #07180f,0 3px 5px #0005;cursor:pointer;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:5px}
 .boot-room-launch .boot-room-label{font:normal 23px/1.1 Georgia,serif;letter-spacing:.2px;white-space:nowrap}
 .boot-room-launch .boot-room-status{font:600 8px/1.4 Arial,sans-serif;letter-spacing:1.35px;color:#d6bc7c;display:flex;align-items:center;gap:6px}
 .boot-room-launch .boot-room-status:before{content:'';width:5px;height:5px;border-radius:50%;background:currentColor}
 .boot-room-launch[data-room-state=open] .boot-room-status{color:#b5d9bb}
 .boot-room-launch[data-room-state=unknown] .boot-room-status{color:#c8c6b8}
 @media (hover:hover){.my-journey-bar .campaign-boot-room-nav .boot-room-launch:hover{background-color:#29483b}}.boot-room-launch:focus-visible{outline:3px solid #d6bc7c;outline-offset:4px}.boot-room-launch:active{transform:translateY(1px)}
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
  return home+'/#campaign='+encodeURIComponent(JSON.stringify(detail));
 }
 function openEntrance(){
  window.top.location.href=campaignEntry()||home+'/';
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
  for(const b of buttons())b.onclick=openEntrance;
  paint();if(!controller&&!timer&&buttons().length)refresh();
 }
 new MutationObserver(install).observe(document.body,{childList:true,subtree:true});
 document.addEventListener('visibilitychange',()=>document.visibilityState==='hidden'?pause():resume());
 window.addEventListener('pagehide',pause);
 window.addEventListener('pageshow',resume);window.addEventListener('online',resume);window.addEventListener('offline',pause);
 install();
})();
