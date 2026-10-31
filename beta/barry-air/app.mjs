import './footer.mjs';
import {buildCampaign,dateLabel,JOURNEY_KEY,identityKey,roundCode} from './campaign-model.mjs';
const $=s=>document.querySelector(s),svgNS='http://www.w3.org/2000/svg';let model,selected=0,zoom=1,mapPromise;
let camera={x:300,y:260},cameraStops=new Map(),pan=null,suppressMapClickUntil=0;
async function flightFetch(url,options={}){const controller=new AbortController(),timer=setTimeout(()=>controller.abort(),12000);try{return await fetch(url,{...options,signal:controller.signal});}finally{clearTimeout(timer);}}
function node(tag,attrs={},text){const e=document.createElementNS(svgNS,tag);for(const [k,v]of Object.entries(attrs))e.setAttribute(k,String(v));if(text!==undefined)e.textContent=text;return e;}
function text(selector,value){$(selector).textContent=value;}
function unavailable(message){$('.field').classList.remove('data-pending');$('.field').classList.add('data-unavailable');$('.field').setAttribute('aria-busy','false');text('#campaign-status',message);$('#campaign-status').hidden=false;$('#retry-flight').hidden=false;}
function readSaved(){try{return JSON.parse(localStorage.getItem(JOURNEY_KEY)||'null');}catch{return null;}}
function shortDestination(name){const t=name.replace(/\s+(FC|AFC|CFC)$/i,'').toUpperCase();return t.length>21?t.slice(0,20)+'…':t;}
function choose(i,flight=null){if(!model?.stops[i])return;selected=i;const d=model.stops[i],next=flight?flight.status==='NEXT FLIGHT':!!d.next;
 text('#detail-number',String(i+1).padStart(2,'0'));text('#detail-tag',next?'Next flight · '+model.nextRound:d.tag||'Landing');text('#detail-name',d.name);text('#selected-ground-name',d.short);text('#detail-ground',d.ground+' · '+d.pc);text('#detail-result',flight?.result||(next?d.nextResult:d.result)||'Flight details to be confirmed');text('#detail-round',flight?dateLabel(flight.date):next?d.nextRound:d.round);text('#detail-status',next?'NEXT FLIGHT':d.status);
 document.querySelectorAll('[data-stop]').forEach(e=>e.setAttribute('aria-pressed',String(Number(e.dataset.stop)===i)));if(zoom>1)focusMapStop(i);}
function render(m){model=m;text('#pigeon-name',m.name);text('#call-sign',m.digits==='00000'?(m.callSign||'Call sign not saved'):'TF2AC '+m.digits);text('#departure-postcode',m.saved.postcode||'Postcode not saved');text('#miles',m.miles.display);$('#miles').classList.toggle('miles-unresolved',!Number.isFinite(m.miles.miles));$('#miles').title='The same round-trip straight-line mileage as My Stats.';text('#campaign-name','CAMPAIGN · '+m.origin.replace(/\s+(FC|AFC|CFC)$/i,''));text('#board-call-sign',m.digits==='00000'?'BARRY AIR':'BA / '+m.digits);
 const f=m.upcoming;text('#next-heading',f?'NEXT FLIGHT · '+m.nextRound:'NEXT FLIGHT · AWAITING DETAILS');text('#next-fixture',f?f.home+' v '+f.away:'Next destination to be confirmed');text('#next-date',f?dateLabel(f.date)+' · '+(f.kickoff||'Kick-off to be confirmed'):'Your flight board will update when the next fixture is published.');text('#next-venue',f?(f.venue?.ground||'Venue to be confirmed')+' · '+(f.venue?.postcode||'Postcode to be confirmed'):'');text('#flight-code',f?roundCode(m.nextRound)+' / '+(f.date?new Date(f.date+'T12:00:00').toLocaleDateString('en-GB',{day:'2-digit',month:'short'}).toUpperCase():'DATE TBC'):'AWAITING DESTINATION');
 $('#check-in').disabled=!m.canCheckIn;try{$('#check-in').checked=!!m.flightKey&&localStorage.getItem('tffc.barry.check-in.v1:'+m.flightKey)==='1';}catch{}paintCheckIn();
 $('#flight-rows').replaceChildren();for(const [index,flight]of m.flights.entries()){const b=document.createElement('button');b.type='button';b.className='flight-row'+(flight.status==='NEXT FLIGHT'?' next':'');b.dataset.stop=flight.stop;b.dataset.flight=index;b.setAttribute('aria-label',flight.round+', '+flight.destination+', '+flight.status);for(const [klass,value]of [['flight-round',flight.round],['flight-destination',shortDestination(flight.destination)],['flight-status',flight.status]]){const s=document.createElement('span');s.className=klass;if(klass==='flight-round')s.textContent=value;else for(const char of value){const cell=document.createElement('span');cell.className='flip-cell';cell.textContent=char===' '?'\u00a0':char;cell.setAttribute('aria-hidden','true');s.append(cell);}b.append(s);}const item=document.createElement('div');item.setAttribute('role','listitem');item.append(b);$('#flight-rows').append(item);}
 if(!m.flights.length){const p=document.createElement('p');p.className='empty-flight-board';p.textContent='Your first flight will appear here when its fixture is published.';$('#flight-rows').append(p);}
 $('#stop-list').replaceChildren();m.stops.forEach((d,i)=>{const b=document.createElement('button');b.type='button';b.textContent=(d.next?'↗ ':i===0?'⌂ ':String(i).padStart(2,'0')+' ')+d.short;b.dataset.stop=i;$('#stop-list').append(b);});
 $('.field').classList.remove('data-pending');$('.field').setAttribute('aria-busy','false');$('#campaign-status').hidden=true;choose(m.lastLanded||m.nextStop||0);
}
function paintCheckIn(){text('#check-in-label',!model?.canCheckIn?'AWAITING FLIGHT DETAILS':$('#check-in').checked?"CHECKED IN · YOU'RE FLYING BARRY AIR - VERMIN FREE SINCE 2022":'CHECK IN FOR YOUR FLIGHT');}
$('#check-in').addEventListener('change',()=>{if(!model?.canCheckIn)return;paintCheckIn();try{localStorage.setItem('tffc.barry.check-in.v1:'+model.flightKey,$('#check-in').checked?'1':'0');}catch{}});
function toast(value){text('#toast',value);$('#toast').hidden=false;setTimeout(()=>$('#toast').hidden=true,2400);}
$('#edit-name').addEventListener('click',()=>{if(!model)return;$('#name-form').hidden=false;$('#edit-name').hidden=true;$('#name-input').value=readSaved()?.pigeonName||'';$('#name-input').focus();$('#name-input').select();});
function closeName(){$('#name-form').hidden=true;$('#edit-name').hidden=false;$('#edit-name').focus();}
$('#cancel-name').addEventListener('click',closeName);$('#name-input').addEventListener('input',()=>$('#name-input').setCustomValidity(''));$('#name-input').addEventListener('keydown',e=>{if(e.key==='Escape'){e.preventDefault();closeName();}});
$('#name-form').addEventListener('submit',e=>{e.preventDefault();const saved=readSaved();if(!saved||identityKey(saved)!==model.identity){unavailable('Your Campaign has changed. Reload Barry Air for your current pigeon.');return;}const name=$('#name-input').value.replace(/\s+/g,' ').trim().slice(0,20);if(!name){$('#name-input').setCustomValidity('Give your pigeon a name.');$('#name-input').reportValidity();return;}
 try{localStorage.setItem(JOURNEY_KEY,JSON.stringify({...saved,pigeonName:name}));const key='tffc.clubfinderCampaignIdentity.v1',backup=JSON.parse(localStorage.getItem(key)||'null');if(backup&&backup.searchNumber===saved.searchNumber&&backup.originName===saved.originName)localStorage.setItem(key,JSON.stringify({...backup,pigeonName:name}));text('#pigeon-name',name);toast('Pigeon name saved.');}catch{toast('Your browser could not save the pigeon name.');}closeName();});
document.addEventListener('click',e=>{const b=e.target.closest('[data-stop]');if(b)choose(Number(b.dataset.stop),b.dataset.flight===undefined?null:model.flights[Number(b.dataset.flight)]);});document.addEventListener('keydown',e=>{if((e.key==='Enter'||e.key===' ')&&e.target.matches('.map-stop')){e.preventDefault();choose(Number(e.target.dataset.stop));}});
$('#view-ground').addEventListener('click',()=>{const target=$('#ground-detail');target.focus({preventScroll:true});target.scrollIntoView({behavior:'auto',block:'center'});});
$('.landing-nav a[href="#flight-path"]').addEventListener('click',event=>{event.preventDefault();if(!model)return;choose(model.nextStop??model.lastLanded);const target=$('#flight-path'),frame=target.closest('.field');target.focus({preventScroll:true});if(getComputedStyle(frame).overflowY==='auto'){const scale=frame.getBoundingClientRect().width/frame.offsetWidth;const desired=frame.scrollTop+(target.getBoundingClientRect().top-frame.getBoundingClientRect().top)/scale-21;const shortfall=Math.max(0,desired-(frame.scrollHeight-frame.clientHeight));if(shortfall>0)frame.style.paddingBottom=(parseFloat(getComputedStyle(frame).paddingBottom)+Math.ceil(shortfall))+'px';}target.scrollIntoView({behavior:'auto',block:'start'});});
function projected(d){const k=(377.1-233.4)/(-1.557261+2.736535),merc=lat=>Math.log(Math.tan(Math.PI/4+lat*Math.PI/360))*180/Math.PI;return {x:377.1+(d.lon+1.557261)*k,y:175.6-(merc(d.lat)-merc(54.617311))*k};}
async function loadMap(){if(!model)return;if(mapPromise)return mapPromise;mapPromise=(async()=>{try{const r=await flightFetch('assets/route-map.svg');if(!r.ok)throw Error('Map unavailable');const doc=new DOMParser().parseFromString(await r.text(),'image/svg+xml'),svg=doc.documentElement;if(svg.tagName.toLowerCase()!=='svg')throw Error('Invalid map');svg.setAttribute('aria-label','Your Tin Foil FA Cup flight path');svg.querySelectorAll('.route-line,[data-stop]').forEach(e=>e.remove());const outer=svg.querySelector('.map-content');const fit=node('g');while(outer.firstChild)fit.append(outer.firstChild);outer.append(fit);
 const located=model.stops.map((d,i)=>({...d,i})).filter(d=>Number.isFinite(d.lat)&&Number.isFinite(d.lon));if(!located.length)throw Error('Awaiting ground locations');const points=located.map(d=>({...d,...projected(d)}));const base=points.find(d=>d.i===0);let xs=points.map(p=>p.x),ys=points.map(p=>p.y),cx=(Math.min(...xs)+Math.max(...xs))/2,cy=(Math.min(...ys)+Math.max(...ys))/2;const scale=Math.min(440/Math.max(60,Math.max(...xs)-Math.min(...xs)),340/Math.max(60,Math.max(...ys)-Math.min(...ys)));fit.setAttribute('transform',`translate(${300-cx*scale} ${250-cy*scale}) scale(${scale})`);cameraStops=new Map(points.map(p=>[p.i,{x:300+(p.x-cx)*scale,y:250+(p.y-cy)*scale}]));svg.setAttribute('tabindex','0');svg.setAttribute('aria-describedby','map-hint');
 // Trace the Campaign from ground to ground; mileage still counts home round trips.
 let previous=base;for(const flight of model.flights){const destination=points.find(p=>p.i===flight.stop);if(previous&&destination&&previous.i!==destination.i){fit.append(node('path',{class:'route-line'+(flight.status==='NEXT FLIGHT'?' future-line':''),'data-from':previous.i,'data-to':destination.i,d:`M${previous.x},${previous.y}L${destination.x},${destination.y}`}));}previous=destination;}
 for(const p of points){const g=node('g',{'data-stop':p.i,class:'map-stop',tabindex:0,role:'button','aria-label':p.short,transform:`translate(${p.x} ${p.y})`});g.append(node('circle',{class:'hit',r:22/scale}),node('circle',{class:'halo',r:15/scale}),node('circle',{class:'point'+(p.next?' future-point':''),r:6/scale}));const label=node('text',{class:'stop-label',x:(p.x>cx?-12:12)/scale,y:(p.i%2?-12:18)/scale,'text-anchor':p.x>cx?'end':'start','font-size':12/scale},p.short);if(p.i===0&&points.some(q=>q.i!==0&&Math.hypot(q.x-p.x,q.y-p.y)*scale<28))label.setAttribute('visibility','hidden');label.style.fontSize=12/scale+'px';label.style.strokeWidth=3/scale+'px';g.append(label);fit.append(g);}$('#map-host').replaceChildren(document.importNode(svg,true));choose(selected);
 if(located.length<model.stops.length){$('.map-stamp').textContent='Some ground locations await confirmation';}
 }catch{const p=document.createElement('p');p.className='map-loading';p.textContent='The map is awaiting location details. Your flight board and ground details are still here.';$('#map-host').replaceChildren(p);}})();return mapPromise;}
function paintMapCamera(){
 const layer=$('#map-host .map-content');if(!layer)return;
 camera.x=Math.max(0,Math.min(600,camera.x));camera.y=Math.max(0,Math.min(520,camera.y));
 layer.setAttribute('transform',`translate(${300-camera.x*zoom} ${260-camera.y*zoom}) scale(${zoom})`);
 $('#map-host').classList.toggle('map-zoomed',zoom>1);
 $('#zoom-in').disabled=zoom>=4;$('#zoom-out').disabled=zoom<=1;
}
function focusMapStop(i){const point=cameraStops.get(i);if(!point)return;camera={...point};paintMapCamera();}
function setZoom(n){
 const before=zoom;zoom=Math.max(1,Math.min(4,n));
 if(zoom===1)camera={x:300,y:260};else if(before===1)camera={...(cameraStops.get(selected)||camera)};
 paintMapCamera();
}
function mapPosition(event){const svg=$('#map-host svg'),matrix=svg?.getScreenCTM();if(!matrix)return null;const point=svg.createSVGPoint();point.x=event.clientX;point.y=event.clientY;return point.matrixTransform(matrix.inverse());}
const mapHost=$('#map-host');
mapHost.addEventListener('pointerdown',event=>{
 if(!event.isPrimary){if(pan)finishMapPan({pointerId:pan.id});return;}
 if(zoom<=1||event.button!==0||(window.visualViewport?.scale||1)>1.01)return;
 const point=mapPosition(event);if(point)pan={id:event.pointerId,point,clientX:event.clientX,clientY:event.clientY,camera:{...camera},moved:false};
});
mapHost.addEventListener('pointermove',event=>{
 if(!pan||pan.id!==event.pointerId)return;
 const point=mapPosition(event);if(!point)return;
 if(!pan.moved&&Math.hypot(event.clientX-pan.clientX,event.clientY-pan.clientY)<5)return;
 if(!pan.moved){pan.moved=true;mapHost.setPointerCapture(event.pointerId);mapHost.classList.add('map-dragging');}
 camera={x:pan.camera.x-(point.x-pan.point.x)/zoom,y:pan.camera.y-(point.y-pan.point.y)/zoom};paintMapCamera();
});
function finishMapPan(event){if(!pan||pan.id!==event.pointerId)return;if(pan.moved)suppressMapClickUntil=performance.now()+400;pan=null;mapHost.classList.remove('map-dragging');if(mapHost.hasPointerCapture(event.pointerId))mapHost.releasePointerCapture(event.pointerId);}
for(const name of ['pointerup','pointercancel','lostpointercapture'])mapHost.addEventListener(name,finishMapPan);
mapHost.addEventListener('click',event=>{if(event.detail&&performance.now()<suppressMapClickUntil){event.preventDefault();event.stopImmediatePropagation();}},true);
mapHost.addEventListener('keydown',event=>{
 const direction={ArrowLeft:[-1,0],ArrowRight:[1,0],ArrowUp:[0,-1],ArrowDown:[0,1]}[event.key];if(zoom<=1||!direction)return;
 event.preventDefault();camera.x+=direction[0]*40/zoom;camera.y+=direction[1]*40/zoom;paintMapCamera();
});
$('#zoom-in').addEventListener('click',async()=>{await loadMap();setZoom(zoom+.25);});$('#zoom-out').addEventListener('click',()=>setZoom(zoom-.25));$('#zoom-reset').addEventListener('click',()=>setZoom(1));$('#zoom-out').disabled=true;
const announcements=['Please remain seated, and do not use the onboard toilet above windscreens or pedestrians.','Cargo: one Tin Foil FA Cup. Destination: Wembley. Eventually.','In the unlikely event of a water landing, please remember: I am a pigeon, not a duck.','Cabin crew, prepare for landing. Somebody find out where the ground is.','Thank you for flying Barry Air. Please check beneath your seat for scarves, programmes and abandoned pies.'];let announcementIndex=0;try{const s=sessionStorage.getItem('barry-air-last-announcement'),last=s===null?-1:Number(s);announcementIndex=Number.isInteger(last)&&last>=0?(last+1)%announcements.length:0;}catch{}
function showAnnouncement(){text('#captain-announcement','“'+announcements[announcementIndex]+'”');try{sessionStorage.setItem('barry-air-last-announcement',String(announcementIndex));}catch{}}$('#next-announcement').addEventListener('click',()=>{announcementIndex=(announcementIndex+1)%announcements.length;showAnnouncement();});showAnnouncement();
$('#retry-flight').addEventListener('click',()=>location.reload());
async function start(){try{const saved=readSaved();if(!saved?.originName||saved.ended)throw Error('Choose a Campaign in My Campaign, then come aboard Barry Air.');let data;for(const url of ['../../competition.json','../competition.json']){try{const r=await flightFetch(url,{cache:'no-store'});if(!r.ok)continue;const d=await r.json();if(Number(d.schema_version)===1&&d.updated_at&&d.results&&d.fixtures){data=d;break;}}catch{}}if(!data)throw Error('Your flight details are temporarily unavailable. Please try again.');render(await buildCampaign(saved,data,{fetcher:flightFetch}));if('IntersectionObserver'in window){const ob=new IntersectionObserver(entries=>{if(entries.some(e=>e.isIntersecting)){loadMap();ob.disconnect();}},{root:$('.field'),rootMargin:'100px'});ob.observe($('#map-host'));}else loadMap();}catch(e){unavailable(e.message||'Your flight details are temporarily unavailable. Please try again.');}}
addEventListener('storage',e=>{if(e.key===JOURNEY_KEY)location.reload();});start();

// Preserve the same phone composition on iPad; rotation changes only its scale.
const tabletFrameQuery=matchMedia('(min-width:700px)');
function fitTabletFrame(){
 // Pinch zoom changes the visual viewport, not the page's layout viewport.
 // Never resize the scrolling room (or tablet composition) during that gesture.
 const viewport=window.visualViewport;
 if(viewport&&Math.abs(viewport.scale-1)>.01)return;
 if(tabletFrameQuery.matches){
  document.documentElement.style.removeProperty('--phone-viewport-height');
  const scale=Math.min(document.documentElement.clientWidth/390,document.body.getBoundingClientRect().height/(390*16/9));
  document.documentElement.style.setProperty('--tablet-scale',String(scale));
 }else{
  document.documentElement.style.removeProperty('--tablet-scale');
  const height=viewport?viewport.height:window.innerHeight;
  document.documentElement.style.setProperty('--phone-viewport-height',height+'px');
 }
}
fitTabletFrame();
addEventListener('resize',fitTabletFrame,{passive:true});
tabletFrameQuery.addEventListener('change',fitTabletFrame);
window.visualViewport?.addEventListener('resize',fitTabletFrame,{passive:true});
addEventListener('pageshow',event=>{
 fitTabletFrame();
 if(!event.persisted&&!location.hash){document.querySelector('.field').scrollTop=0;window.scrollTo(0,0);}
});

