import assert from 'node:assert/strict';import fs from 'node:fs/promises';import {chromium,webkit} from 'playwright';import {buildCampaign} from '../beta/barry-air/campaign-model.mjs';
const origin='http://127.0.0.1:8765',competition=JSON.parse(await fs.readFile('competition.json'));const saved={originName:'Amersham Town FC',postcode:'HP7 0EJ',searchNumber:12345,callSign:'Tango Foxtrot 2 Alpha Charlie 12345',pigeonName:'Sky Pie',selectedAt:'2026-10-31T10:00:00Z',ended:false};
const nextFixtureLabel=({upcoming})=>upcoming?upcoming.home+' v '+upcoming.away:'Next destination to be confirmed';
const geocode=url=>{const pc=decodeURIComponent(String(url).split('/').at(-1)).replace(/\s/g,'');let n=[...pc].reduce((n,c)=>n*17+c.charCodeAt(0),1)%1000;return {result:{latitude:50+n/200,longitude:-5+n/170}};};const expected=await buildCampaign(saved,competition,{fetcher:async u=>new Response(JSON.stringify(geocode(u)))});
const browser=await (process.env.TFFC_BROWSER==='webkit'?webkit:chromium).launch();await fs.mkdir('phone-frame-evidence',{recursive:true});try{
 let browserLanding;
 for(const [width,height]of [[390,669],[390,797],[390,844],[320,568],[768,1024],[1024,768]]){
  const context=await browser.newContext({viewport:{width,height}});let counters=0;
  await context.route('**/*workers.dev/**',r=>{counters++;return r.abort()});await context.route('https://api.postcodes.io/**',r=>r.fulfill({json:geocode(r.request().url())}));await context.addInitScript(value=>{if(!localStorage.getItem('tinFoilFACupJourney_v7'))localStorage.setItem('tinFoilFACupJourney_v7',JSON.stringify(value));},saved);
  let releaseFlight;const flightGate=new Promise(resolve=>releaseFlight=resolve);await context.route('**/competition.json',async route=>{await flightGate;await route.continue();});
  await context.route('https://challenges.cloudflare.com/**',r=>r.fulfill({contentType:'application/javascript',body:'window.turnstile={render(){return 1},remove(){},reset(){}};'}));
  const p=await context.newPage();await p.goto(origin+'/beta/barry-air/');await p.locator('.airline img').evaluate(img=>img.decode());
  const welcomeGeometry=()=>p.locator('.masthead').evaluate(e=>[e,...e.children].map(n=>{const r=n.getBoundingClientRect();return [r.top,r.height];}));const beforeData=await welcomeGeometry();
  releaseFlight();await p.locator('.field[aria-busy="false"]').waitFor();assert.deepEqual(await welcomeGeometry(),beforeData,'welcome and crest must not shift when the boarding pass loads');assert.equal(await p.locator('#pigeon-name').innerText(),'Sky Pie');assert.equal(await p.locator('#call-sign').innerText(),'TF2AC 12345');assert.equal(await p.locator('#miles').innerText(),expected.miles.display);assert.equal(await p.locator('.flight-row').count(),expected.flights.length);assert.equal(await p.locator('#next-fixture').innerText(),nextFixtureLabel(expected));assert.equal(await p.locator('.masthead .intro').innerText(),'Straight there. Straight back.\nNo messing about!');
  const fit=await p.locator('.field').evaluate(e=>{const r=e.getBoundingClientRect(),a=e.querySelector('#landing').getBoundingClientRect(),b=e.querySelector('#departures').getBoundingClientRect();return {room:r.height,landing:a.height,next:b.top,bottom:r.bottom,scroll:e.scrollTop,navBottom:e.querySelector('.landing-nav').getBoundingClientRect().bottom};});assert.ok(fit.landing>=fit.room-1);assert.ok(fit.next>=fit.bottom,'frame2 must not peek into the initial viewport');assert.equal(fit.scroll,0);const welcomeToPass=await p.locator('.field').evaluate(e=>{const scale=e.getBoundingClientRect().width/e.offsetWidth;return (e.querySelector('.boarding-pass').getBoundingClientRect().top-e.querySelector('.masthead').getBoundingClientRect().bottom)/scale;});const extraWelcomeGap=width<700?Math.min(20,Math.max(0,(height-669)*.5)):0;assert.ok(welcomeToPass-extraWelcomeGap>=3.5&&welcomeToPass-extraWelcomeGap<=12.5,'welcome-to-pass gap must gain only the requested taller-phone spacing: '+welcomeToPass);if(fit.navBottom>fit.bottom+1)console.log('Landing parts',JSON.stringify(await p.locator('#landing').evaluate(e=>Array.from(e.querySelectorAll('.airline,.masthead,.boarding-pass,.pass-brand,.pass-body,.pass-body>* , .boarding-stub,.landing-nav')).map(n=>({class:n.className,top:n.getBoundingClientRect().top,height:n.getBoundingClientRect().height,width:n.getBoundingClientRect().width,margin:getComputedStyle(n).margin,gap:getComputedStyle(n).gap,display:getComputedStyle(n).display})))));assert.ok(fit.navBottom<=fit.bottom+1,'boarding pass and navigation must fit the opening frame: '+JSON.stringify({width,height,...fit}));const landingBalance=await p.locator('#landing').evaluate(e=>{const scale=e.getBoundingClientRect().width/e.offsetWidth;const r=s=>e.querySelector(s).getBoundingClientRect();return {badgeGap:(r('.masthead').top-r('.airline').bottom)/scale,visibleGap:(r('.boarding-pass').top-Math.max(r('.crest').bottom,r('.welcome').bottom))/scale,pass:r('.boarding-pass').height/scale};});if(width===390){if(height===669){browserLanding=landingBalance;assert.ok(Math.abs(landingBalance.badgeGap-5)<.5,'normal browser badge-to-welcome gap must stay unchanged');}else{const spare=height-669;assert.ok(Math.abs(landingBalance.badgeGap-browserLanding.badgeGap-(Math.min(88,spare*.5)-extraWelcomeGap))<.5,'welcome must move up by the extra ticket gap');assert.ok(Math.abs(landingBalance.visibleGap-40)<.5,'tall phone visible welcome-to-ticket gap must double from 20px to 40px');assert.ok(landingBalance.pass-browserLanding.pass<spare*.65,'boarding pass must no longer absorb all extra height');}}await p.screenshot({path:`phone-frame-evidence/barry-air-${width}x${height}.png`});
  const checkIn=p.getByRole('checkbox');
  const sharePass=p.getByRole('button',{name:'Share Boarding Pass'});
  const sharePath=p.getByRole('button',{name:'Share Flight Path'});
  assert.equal(await sharePath.isVisible(),false,'Flight Path sharing starts locked');
  assert.equal(await sharePass.isVisible(),false,'sharing starts locked');
  assert.equal(await checkIn.isEnabled(),expected.canCheckIn);
  if(expected.canCheckIn){await checkIn.check();const checkedFit=await p.locator('.field').evaluate(e=>{const row=e.querySelector('.pass-checkin'),label=e.querySelector('#check-in-label'),range=document.createRange();range.selectNodeContents(label);return {lines:range.getClientRects().length,rowFits:row.scrollWidth<=row.clientWidth,navBottom:e.querySelector('.landing-nav').getBoundingClientRect().bottom,bottom:e.getBoundingClientRect().bottom};});assert.equal(await p.locator('#check-in-label').innerText(),"CHECKED IN · YOU'RE FLYING BARRY AIR - VERMIN FREE SINCE 2022");assert.ok(checkedFit.lines===1&&checkedFit.rowFits&&checkedFit.navBottom<=checkedFit.bottom+1,'checked-in message must occupy one line without overflow and keep navigation visible: '+JSON.stringify(checkedFit));}
  if(expected.canCheckIn&&width===390&&height===669){
    await p.evaluate(()=>{
      window.boardingShareText=[];
      const fillText=CanvasRenderingContext2D.prototype.fillText;
      CanvasRenderingContext2D.prototype.fillText=function(value,...args){
        window.boardingShareText.push(value);
        return fillText.call(this,value,...args);
      };
    });
    const {passWidth,tearY}=await p.locator('.boarding-pass').evaluate(pass=>{
      const bounds=pass.getBoundingClientRect();
      const stub=pass.querySelector('.boarding-stub').getBoundingClientRect();
      return {passWidth:pass.offsetWidth,tearY:Math.round((stub.top-bounds.top)*pass.offsetWidth/bounds.width*3)};
    });
    await sharePass.click();
    const preview=p.getByRole('dialog',{name:'Share the Magic'});
    await preview.waitFor();
    assert.equal(await preview.locator('img').evaluate(async img=>{await img.decode();return img.naturalWidth;}),passWidth*3);
    const save=preview.getByRole('link',{name:'Save image'});
    assert.equal(await save.evaluate(async link=>(await fetch(link.href)).headers.get('content-type')),'image/png');
    const fields=await p.evaluate(()=>window.boardingShareText);
    for(const value of ['BARRY AIR','BOARDING PASS','Sky Pie','DEPARTURE CODE','F0O T1E',"CHECKED IN · YOU'RE FLYING BARRY AIR - VERMIN FREE SINCE 2022"])assert.ok(fields.includes(value),value);
    assert.ok(!fields.join(' ').includes(saved.postcode),'shared PNG must omit the departure postcode');
    assert.equal(await p.locator('#departure-postcode').textContent(),saved.postcode);
    assert.deepEqual(await preview.locator('img').evaluate((img,tearY)=>{
      const canvas=document.createElement('canvas');
      canvas.width=img.naturalWidth;
      canvas.height=img.naturalHeight;
      const ctx=canvas.getContext('2d');
      ctx.drawImage(img,0,0);
      return [[0,0],[50,8],[2,tearY],[canvas.width-3,tearY]].map(([x,y])=>Array.from(ctx.getImageData(x,y,1,1).data));
    },tearY),[[0,0,0,0],[8,76,97,255],[0,0,0,0],[0,0,0,0]],'PNG must retain the rounded corner, teal header and both tear indents');
    await preview.locator('form button').click();
    await checkIn.uncheck();
    await p.reload();
    await p.locator('.field[aria-busy="false"]').waitFor();
    assert.ok(await sharePass.isVisible(),'first check-in must unlock sharing across reload and uncheck');
    await checkIn.check();
    await p.getByRole('link',{name:'Flight Path',exact:true}).click();
    const map=p.locator('#map-host svg');
    await map.waitFor();
    const exactHome=await map.locator('[data-stop="0"]').getAttribute('transform');
    await p.getByRole('button',{name:'Zoom map in',exact:true}).click();
    const camera=await map.locator('.map-content').getAttribute('transform');
    const futureLegs=await map.locator('.route-line.future-line').count();
    await p.evaluate(()=>{
      const create=URL.createObjectURL;
      URL.createObjectURL=function(blob){
        if(blob.type==='image/svg+xml')window.sharedRoute=blob.text();
        return create.call(this,blob);
      };
    });
    await sharePath.click();
    await preview.waitFor();
    assert.equal(await preview.locator('img').evaluate(async img=>{await img.decode();return img.naturalWidth;}),1200);
    assert.equal(await save.getAttribute('download'),'barry-air-flight-path.png');
    const route=await p.evaluate(async()=>{
      const text=await window.sharedRoute;
      const svg=new DOMParser().parseFromString(text,'image/svg+xml');
      return {text,home:svg.querySelector('[data-stop="0"]').getAttribute('transform'),
        broad:!!svg.querySelector('[data-stop="0"] .home-area'),futureLegs:svg.querySelectorAll('.route-line.future-line').length,
        nextGround:!!svg.querySelector('.future-point'),
        camera:svg.querySelector('.map-content').getAttribute('transform')};
    });
    assert.ok(route.broad,'the shared map must show a broad Home area');
    assert.ok(route.nextGround,'the shared map must mark the next ground');
    assert.equal(route.futureLegs,futureLegs,'sharing must preserve upcoming legs, including a return to the same ground');
    assert.notEqual(route.home,exactHome,'export must use rounded coordinates before fitting the map');
    assert.notEqual(route.camera,camera,'export must show the whole route independently of live zoom');
    const bootRoomImage=await p.evaluate(async()=>{
      const {route}=JSON.parse(localStorage.getItem('tffc.barry.boot-flight.v1'));
      const {bootRoomFlightImage}=await import('/beta/barry-air/flight-path-share.mjs?v=4');
      const labels=[],fillText=CanvasRenderingContext2D.prototype.fillText;
      CanvasRenderingContext2D.prototype.fillText=function(text,...args){
        labels.push(text);
        return fillText.call(this,text,...args);
      };
      try {
        const image=await bootRoomFlightImage(route,{name:'Guest Pigeon',callSign:'TF2AC 12345'});
        return {type:image.type,bytes:image.size,route,labels};
      } finally {CanvasRenderingContext2D.prototype.fillText=fillText;}
    });
    assert.equal(bootRoomImage.type,'image/png');
    assert.ok(bootRoomImage.bytes>0);
    assert.equal(bootRoomImage.route.stops[0].short,'Home area');
    assert.equal(bootRoomImage.route.milesFlown,Number.isFinite(expected.miles.miles)?Math.round(expected.miles.miles):undefined);
    assert.ok(bootRoomImage.labels.includes('Guest Pigeon'));
    const miles=bootRoomImage.route.milesFlown;
    assert.ok(bootRoomImage.labels.includes('TF2AC 12345 · '+(miles===undefined?'Miles flown unavailable':miles.toLocaleString('en-GB')+' miles flown')));
    assert.ok(bootRoomImage.labels.every(label=>!label.includes(saved.postcode)));
    assert.ok(!JSON.stringify(bootRoomImage.route).includes(saved.postcode));
    assert.ok(!route.text.includes(saved.postcode));
    await preview.locator('form button').click();
    assert.equal(await map.locator('.map-content').getAttribute('transform'),camera);
  }
  if(process.env.TFFC_LANDING_ONLY==='1'){await context.close();continue;}await p.reload();await p.locator('.field[aria-busy="false"]').waitFor();assert.equal(await checkIn.isChecked(),expected.canCheckIn);
  await p.getByRole('button',{name:'Edit pigeon name',exact:true}).click();await p.getByRole('textbox',{name:'Pigeon name',exact:true}).fill('Pie Captain');await p.getByRole('button',{name:'Save',exact:true}).click();const identity=await p.evaluate(()=>JSON.parse(localStorage.getItem('tinFoilFACupJourney_v7')));assert.equal(identity.searchNumber,12345);assert.equal(identity.pigeonName,'Pie Captain');assert.equal(identity.originName,saved.originName);
  await p.getByRole('link',{name:'Flight Path',exact:true}).click();await p.locator('#map-host svg').waitFor();assert.equal(await p.locator('#map-host [data-stop]').count(),expected.stops.filter(s=>Number.isFinite(s.lat)&&Number.isFinite(s.lon)).length);const route=await p.locator('#map-host .route-line').evaluateAll(lines=>lines.map(e=>[Number(e.dataset.from),Number(e.dataset.to),e.classList.contains('future-line')]));const expectedRoute=[];let previous=0;for(const flight of expected.flights){if(previous!==flight.stop)expectedRoute.push([previous,flight.stop,flight.status==='NEXT FLIGHT']);previous=flight.stop;}assert.deepEqual(route,expectedRoute,'map must follow the Campaign between venues, including replay order');const selectedStop=expected.nextStop??expected.lastLanded;
  const selectedResult=expected.upcoming?nextFixtureLabel(expected):expected.stops[selectedStop]?.result||'Flight details to be confirmed';
  assert.equal(await p.locator('#detail-result').innerText(),selectedResult);await p.getByRole('button',{name:'Zoom map in',exact:true}).click();
  async function assertGroundCentered(stop){const delta=await p.locator(`#map-host [data-stop="${stop}"] .point`).evaluate(e=>{const r=e.getBoundingClientRect(),svg=e.ownerSVGElement,pt=svg.createSVGPoint();pt.x=300;pt.y=260;const c=pt.matrixTransform(svg.getScreenCTM());return {x:r.x+r.width/2-c.x,y:r.y+r.height/2-c.y};});assert.ok(Math.abs(delta.x)<1&&Math.abs(delta.y)<1,'selected ground must remain centred: '+JSON.stringify(delta));}
  await assertGroundCentered(selectedStop);await p.locator('#stop-list [data-stop="1"]').click();await assertGroundCentered(1);
  const layer=p.locator('#map-host .map-content'),beforeDrag=await layer.getAttribute('transform');const mapBox=await p.locator('#map-host svg').boundingBox(),scrollBeforeDrag=await p.locator('.field').evaluate(e=>e.scrollTop);
  await p.mouse.move(mapBox.x+25,mapBox.y+mapBox.height/2);await p.mouse.down();await p.mouse.move(mapBox.x+70,mapBox.y+mapBox.height/2+30,{steps:5});await p.mouse.up();assert.notEqual(await layer.getAttribute('transform'),beforeDrag,'drag must move the map');assert.equal(await p.locator('.field').evaluate(e=>e.scrollTop),scrollBeforeDrag,'map drag must not scroll the page');assert.equal(await p.locator('#stop-list [data-stop="1"]').getAttribute('aria-pressed'),'true','drag must not select an accidental ground');
  await p.locator('#stop-list [data-stop="2"]').click();await assertGroundCentered(2);await p.locator('#map-host svg').focus();const beforeArrow=await layer.getAttribute('transform');await p.keyboard.press('ArrowRight');assert.notEqual(await layer.getAttribute('transform'),beforeArrow,'keyboard must pan the enlarged map');
  await p.getByRole('button',{name:'Fit whole route',exact:true}).click();assert.equal(await layer.getAttribute('transform'),'translate(0 0) scale(1)','fit must reset both zoom and pan');assert.equal(await p.getByRole('button',{name:'Zoom map out',exact:true}).isDisabled(),true);

  const beforePinch=await p.locator('.field').evaluate(e=>({height:e.offsetHeight,scroll:e.scrollTop,style:document.documentElement.getAttribute('style')}));const cdp=await context.newCDPSession(p);
  for(const scale of [1.5,2,3]){await cdp.send('Emulation.setPageScaleFactor',{pageScaleFactor:scale});await p.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));assert.equal(await p.evaluate(()=>visualViewport.scale)>1,true);assert.deepEqual(await p.locator('.field').evaluate(e=>({height:e.offsetHeight,scroll:e.scrollTop,style:document.documentElement.getAttribute('style')})),beforePinch,'native pinch must not resize or reposition the scrolling room');}
  await cdp.send('Emulation.setPageScaleFactor',{pageScaleFactor:1});await cdp.detach();await p.locator('.flight-row').first().click();assert.equal(await p.locator('#detail-result').innerText(),expected.flights[0].result);
  await p.getByRole('button',{name:'More from Captain Barry',exact:true}).click();assert.equal(await p.locator('.captain-roundel').getAttribute('src'),'assets/barry-crest.webp');assert.equal(await p.getByText(/Demonstration flight/).count(),0);assert.equal(counters,0,'Barry Air must never allocate an identity');
  const footer=p.locator('#barry-site-footer'),savedBeforeFooter=await p.evaluate(()=>localStorage.getItem('tinFoilFACupJourney_v7'));
  assert.deepEqual(await footer.locator('.tffc-magic-row button').allTextContents(),['Keep the Magic','Share the Magic']);assert.equal(await footer.locator('.tffc-support-row>a').getAttribute('href'),'https://buy.stripe.com/dRm28s2yZdhAgBG4L36EU01');assert.equal(await footer.locator('.tffc-support-row>a').getAttribute('target'),'_blank');
  await footer.getByRole('button',{name:'Share the Magic',exact:true}).scrollIntoViewIfNeeded();const footerScroll=await p.locator('.field').evaluate(e=>e.scrollTop);
  await footer.getByRole('button',{name:'Share the Magic',exact:true}).click();const magic=p.frameLocator('iframe[title="Share Tin Foil FA Cup"]');await magic.getByRole('heading',{name:'Share the Magic',exact:true}).waitFor();await magic.getByRole('button',{name:'Close',exact:true}).click();await p.locator('.barry-magic-dialog').waitFor({state:'detached'});assert.equal(await p.locator('.field').evaluate(e=>e.scrollTop),footerScroll,'closing Share must preserve Barry Air position');
  await footer.getByRole('button',{name:'Keep the Magic',exact:true}).click();await magic.getByRole('heading',{name:'Keep the Magic',exact:true}).waitFor();await magic.locator('#platform').selectOption('apple');assert.match(await magic.locator('#steps').innerText(),/Add to Home Screen/);await magic.getByRole('button',{name:'Back to Share',exact:true}).click();await magic.getByRole('heading',{name:'Share the Magic',exact:true}).waitFor();await magic.getByRole('button',{name:'Close',exact:true}).click();await p.locator('.barry-magic-dialog').waitFor({state:'detached'});
  await footer.getByRole('button',{name:'About Us',exact:true}).click();await p.getByRole('dialog',{name:'About Us',exact:true}).waitFor();assert.match(await p.locator('.barry-info-copy').innerText(),/The Four Laws/);await p.getByRole('button',{name:'Close',exact:true}).click();await footer.getByRole('button',{name:'Privacy',exact:true}).click();await p.getByRole('dialog',{name:'Privacy',exact:true}).waitFor();assert.match(await p.locator('.barry-info-copy').innerText(),/stored on your device/);await p.keyboard.press('Escape');await p.locator('dialog[aria-labelledby="barry-footer-title"]').waitFor({state:'detached'});
  for(const [label,kind]of [['Feedback','feedback'],['Report an Issue','issue']]){await footer.getByRole('link',{name:label,exact:true}).click();await p.locator('.barry-post:not([hidden])').waitFor();assert.equal(await p.locator('#post-kind').inputValue(),kind);await p.getByRole('button',{name:'Close Barry’s Post Office',exact:true}).click();}
  assert.equal(await p.evaluate(()=>localStorage.getItem('tinFoilFACupJourney_v7')),savedBeforeFooter,'footer must preserve the Campaign');assert.equal(counters,0,'footer must never allocate an identity');await p.screenshot({path:`phone-frame-evidence/barry-air-footer-${width}x${height}.png`});
  const other={originName:'Newton Aycliffe FC',postcode:'DL5 4RQ',searchNumber:12346,pigeonName:'Other Pigeon'};
  const otherExpected=await buildCampaign(other,competition,{fetcher:async u=>new Response(JSON.stringify(geocode(u)))});
  await p.evaluate(value=>localStorage.setItem('tinFoilFACupJourney_v7',JSON.stringify(value)),other);await p.goto(origin+'/beta/barry-air/');await p.locator('.field[aria-busy="false"]').waitFor();assert.equal(await p.locator('#pigeon-name').innerText(),'Other Pigeon');assert.equal(await p.getByRole('checkbox').isChecked(),false,'a different Campaign must not inherit check-in');assert.equal(await sharePass.isVisible(),false,'a different Campaign must not inherit sharing');assert.equal(await sharePath.isVisible(),false,'a different Campaign must not inherit map sharing');assert.equal(await p.locator('#next-fixture').innerText(),nextFixtureLabel(otherExpected));await p.getByRole('link',{name:'Flight Path',exact:true}).click();await p.locator('#map-host svg').waitFor();const stan=p.getByRole('button',{name:'03 Heaton Stannington',exact:true});await stan.click();await p.getByRole('button',{name:'Zoom map in',exact:true}).click();await p.getByRole('button',{name:'Zoom map in',exact:true}).click();await assertGroundCentered(3);await p.screenshot({path:`phone-frame-evidence/barry-air-selected-ground-${width}x${height}.png`});
  await context.close();
 }
 const empty=await browser.newContext();const e=await empty.newPage();await e.goto(origin+'/beta/barry-air/');await e.getByText('Choose a Campaign in My Campaign, then come aboard Barry Air.',{exact:true}).waitFor();assert.equal(await e.locator('.boarding-pass').isVisible(),false);assert.equal(await e.getByText('TF2AC 01001',{exact:true}).count(),0);await empty.close();
 const offline=await browser.newContext();await offline.addInitScript(v=>localStorage.setItem('tinFoilFACupJourney_v7',JSON.stringify(v)),saved);await offline.route('**/competition.json',r=>r.abort());const o=await offline.newPage();await o.goto(origin+'/beta/barry-air/');await o.getByText('Your flight details are temporarily unavailable. Please try again.',{exact:true}).waitFor();assert.equal(await o.locator('.boarding-pass').isVisible(),false);await offline.close();
 if(process.env.TFFC_LANDING_ONLY==='1')console.log('PASS: browser and taller Home Screen landing gaps, complete frame/navigation fit, loading stability and unavailable states in WebKit.');else console.log('PASS: personal boarding pass, canonical mileage, four viewport fits, scoped check-in, name persistence, live route/board/panel interactions, missing Campaign and unavailable-data states; no counter allocations.');
}finally{await browser.close();}
