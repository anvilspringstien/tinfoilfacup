import { checkInstalledHandover } from './keep-magic-install-browser.mjs';
import { createRequire } from 'node:module';
const { chromium } = createRequire(import.meta.url)('playwright');
import assert from 'node:assert/strict';
const base=process.env.TFFC_PREVIEW_BASE||'http://127.0.0.1:8765';
const browser=await chromium.launch({headless:true,args:['--no-sandbox']});
try{
 const context=await browser.newContext({viewport:{width:390,height:669},deviceScaleFactor:3});
 const page=await context.newPage();const errors=[];page.on('pageerror',e=>errors.push(String(e)));
 // The destination frame follows the actual approved front door at each size.
 for(const [width,height] of [[390,669],[390,645],[390,620],[390,560],[768,1024],[1024,768],[1680,889]]){
  await page.setViewportSize({width,height});
  await page.goto(base+'/index.html');
  const front=await page.locator('.field').boundingBox();
  await page.goto(base+'/beta/share-popup-embed.html');
  const share=await page.locator('.panel').boundingBox();
  for(const key of ['x','y','width','height'])assert(Math.abs(front[key]-share[key])<2,`Share frame ${key} matches Splash at ${width}×${height}`);
  assert(await page.locator('.panel').evaluate(p=>p.scrollHeight<=p.clientHeight+1),'Share furniture fits destination frame');
  assert(await page.locator('.keep-card').isVisible());
  await page.screenshot({path:`/tmp/tffc-destination-magic-${width}x${height}.png`});
  const crest=await page.locator('.crest').boundingBox();
  if(width===390&&height>=500){
   assert(crest.width>({669:179,645:155,620:130,560:100}[height]),'phone crest grows into spare space');
   const gaps=await page.locator('.panel').evaluate(()=>{const note=document.querySelector('.note').getBoundingClientRect(),buttons=document.querySelector('.buttons').getBoundingClientRect(),keep=document.querySelector('.keep-card').getBoundingClientRect();return [buttons.top-note.bottom,keep.top-buttons.bottom]});
   assert(Math.abs(gaps[0]-gaps[1])<1,'equal gaps above and below sharing buttons');
  }
  const type=await page.locator('.heading').evaluate(e=>{const s=getComputedStyle(e);return [s.fontSize,s.fontFamily,s.fontWeight]});
  await page.goto(base+'/beta/keep-the-magic-shed.html?instructions=1&keep=1');
  await page.selectOption('#platform','apple');
  if(height>=620){const margins=await page.locator('#platform').evaluate(e=>[getComputedStyle(e).marginTop,getComputedStyle(e).marginBottom]);assert.deepEqual(margins,['8px','8px'],'equal extra space around the device selector')}
  const keep=await page.locator('#magic').boundingBox();
  const keepCrest=await page.locator('.brand').boundingBox();
  for(const key of ['x','y','width','height']){
   assert(Math.abs(share[key]-keep[key])<2,`Keep frame ${key} matches Share`);
   assert(Math.abs(crest[key]-keepCrest[key])<2,`Keep crest ${key} matches Share`);
  }
  assert.deepEqual(await page.locator('.heading').evaluate(e=>{const s=getComputedStyle(e);return [s.fontSize,s.fontFamily,s.fontWeight]}),type);
  assert(await page.locator('#magic').evaluate(p=>p.scrollHeight<=p.clientHeight+1),'Apple instructions fit the frame');
  assert.equal(await page.locator('#steps li').count(),3);
  await page.screenshot({path:`/tmp/tffc-instructions-magic-${width}x${height}.png`});
  for(const platform of ['android','computer']){
   await page.selectOption('#platform',platform);
   assert(await page.locator('#magic').evaluate(p=>p.scrollHeight<=p.clientHeight+1),platform+' instructions fit the frame '+width+'×'+height);
   assert(!/Shed|BETA|preview/.test(await page.locator('#magic').innerText()),'no build scaffolding in instructions');
   await page.screenshot({path:`/tmp/tffc-${platform}-magic-${width}x${height}.png`});
  }
 }
 // Follow the real iframe -> top-level transition: direct-page comparisons
 // cannot detect a gutter reserved by both the Campaign host and Share iframe.
 await context.route('https://tffac-clubfinder-counter.anvilspringstien.workers.dev/**',route=>route.abort());
 await context.addInitScript(()=>Object.defineProperty(navigator,'share',{configurable:true,value:async()=>{}}));
 for(const [width,height] of [[390,669],[390,560],[1680,889]]){
  await page.setViewportSize({width,height});
  await page.goto(base+'/beta/clubfinder-journey.html?magicShare=1');
  const frame=page.frameLocator('iframe[title="Share Tin Foil FA Cup"]');
  await frame.locator('.keep-magic').waitFor();
  const before=await frame.locator('.panel').evaluate(e=>{
   const box=s=>{const r=document.querySelector(s).getBoundingClientRect();return {x:r.x,y:r.y,width:r.width,height:r.height}};
   return {frame:box('.panel'),crest:box('.crest'),surround:getComputedStyle(document.querySelector('.overlay')).backgroundColor,fill:getComputedStyle(e).backgroundColor,border:getComputedStyle(e).borderColor};
  });
  await frame.locator('.keep-magic').click();await page.waitForURL('**/keep-the-magic-shed.html?**');
  const after=await page.locator('#magic').evaluate(e=>{
   const r=e.getBoundingClientRect(),c=document.querySelector('.brand').getBoundingClientRect();
   return {frame:{x:r.x,y:r.y,width:r.width,height:r.height},crest:{x:c.x,y:c.y,width:c.width,height:c.height},surround:getComputedStyle(e,'::backdrop').backgroundColor,fill:getComputedStyle(e).backgroundColor,border:getComputedStyle(e).borderColor};
  });
  for(const element of ['frame','crest'])for(const key of ['x','y','width','height'])assert(Math.abs(before[element][key]-after[element][key])<1,'real transition preserves '+element+' '+key);
  for(const key of ['surround','fill','border'])assert.equal(after[key],before[key],'real transition preserves '+key);
 }
 // Actual application hosts, native sharing visible, short Safari-sized viewport.
 await context.route('https://tffac-clubfinder-counter.anvilspringstien.workers.dev/**',route=>route.abort());
 await context.addInitScript(()=>Object.defineProperty(navigator,'share',{configurable:true,value:async()=>{}}));
 for(const host of ['clubfinder-journey.html','clubfinder-beta.html','challenges-beta.html']){
  await page.setViewportSize({width:390,height:560});
  await page.goto(base+'/beta/'+host+'?magicShare=1');
  const shareFrame=page.frameLocator('iframe[title="Share Tin Foil FA Cup"]');
  const keepEntry=shareFrame.getByRole('link',{name:'Keep the Magic'});
  await keepEntry.waitFor();
  assert(await shareFrame.locator('#native').isVisible());
  assert(await shareFrame.locator('.panel').evaluate(panel=>panel.scrollHeight<=panel.clientHeight+1),'real Share host fits short phone with all actions');
  await page.screenshot({path:'/tmp/tffc-embedded-magic-phone.png'});
  await keepEntry.click();
  await page.waitForURL('**/keep-the-magic-shed.html?**');
  assert.equal(await page.locator('#heading').innerText(),'Keep the Magic');
  await page.selectOption('#platform','apple');
  assert.match(await page.locator('#steps').innerText(),/square icon with the arrow pointing up/);
  await page.locator('#back').click();
  await page.waitForURL('**/beta/'+host);
  await shareFrame.locator('#copy').waitFor();
  assert.equal(await shareFrame.locator('#shareHeading').innerText(),'Share the Magic');
  assert(await shareFrame.locator('#shareHeading').evaluate(e=>e===document.activeElement&&getComputedStyle(e).outlineStyle==='none'),'return focuses the Share title without a box');
  await keepEntry.click();
  await page.waitForURL('**/keep-the-magic-shed.html?**');
  await page.locator('#close').click();
  await page.waitForURL('**/beta/'+host);
  assert(await page.locator('iframe[title="Share Tin Foil FA Cup"]').isHidden(),'closing Keep returns to the originating page without reopening Share');
 }
 await page.setViewportSize({width:390,height:669});
 await page.goto(base+'/beta/keep-the-magic-shed.html');
 await page.evaluate(()=>localStorage.setItem('tffc-test-campaign','preserve-me'));
 await page.reload();
 assert(await page.locator('#magic').evaluate(d=>d.open));
 async function fits(){assert(await page.locator('#magic').evaluate(d=>d.scrollHeight<=d.clientHeight+1),'popup should fit phone height');assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'no horizontal overflow');}
 await fits();await page.screenshot({path:'/tmp/tffc-share-magic-phone.png'});
 await page.locator('#keep').click();await fits();
 assert.equal(await page.locator('#heading').innerText(),'Keep the Magic');
 assert(await page.locator('#install').isHidden(),'no fake install button without event');
 await page.selectOption('#platform','apple');assert.match(await page.locator('#steps').innerText(),/Safari/);
 await page.screenshot({path:'/tmp/tffc-keep-magic-phone.png'});
 await page.selectOption('#platform','android');assert.match(await page.locator('#steps').innerText(),/Add to Home screen/);
 await page.evaluate(()=>{const e=new Event('beforeinstallprompt',{cancelable:true});e.prompt=async()=>{window.promptCalls=(window.promptCalls||0)+1};e.userChoice=Promise.resolve({outcome:'dismissed'});dispatchEvent(e)});
 assert(await page.locator('#install').isVisible());await page.locator('#install').click();
 assert.equal(await page.evaluate(()=>window.promptCalls),1);assert.match(await page.locator('#install-status').innerText(),/later/);
 assert(await page.locator('#install').isHidden());
 await page.evaluate(()=>{const e=new Event('beforeinstallprompt',{cancelable:true});e.prompt=async()=>{};e.userChoice=Promise.resolve({outcome:'accepted'});dispatchEvent(e)});
 await page.locator('#install').click();assert.match(await page.locator('#install-status').innerText(),/Tin Foil FA Cup icon/);
 await page.evaluate(()=>dispatchEvent(new Event('appinstalled')));
 assert.equal(await page.locator('#install-status').innerText(),'Added. Look for Tin Foil FA Cup in your apps.');
 await page.locator('#back').click();
 await page.evaluate(()=>{Object.defineProperty(navigator,'share',{configurable:true,value:undefined})});
 await page.locator('#share').click();assert.match(await page.locator('#feedback').innerText(),/Copy Link/);
 await page.evaluate(()=>{Object.defineProperty(navigator,'clipboard',{configurable:true,value:{writeText:async value=>{window.copiedURL=value}}})});
 await page.locator('#copy').click();assert.equal(await page.evaluate(()=>window.copiedURL),'https://tinfoilfacup.com/');
 assert.equal(await page.locator('.launch,#open,#open-shed').count(),0,'old launcher controls are removed');
 assert.equal(await page.evaluate(()=>localStorage.getItem('tffc-test-campaign')),'preserve-me');
 assert.equal(await page.evaluate(async()=>('serviceWorker' in navigator)?(await navigator.serviceWorker.getRegistrations()).length:0),0);
 const manifest=await page.evaluate(async()=>{const r=await fetch(document.querySelector('link[rel="manifest"]').href);return r.json()});
 assert.equal(manifest.id,'/beta/keep-the-magic-shed');assert.equal(manifest.name,'Tin Foil FA Cup');assert.equal(manifest.short_name,'Tin Foil FA Cup');assert.equal(manifest.start_url,'/beta/keep-the-magic-shed.html');assert.equal(manifest.display,'standalone');
 for(const icon of manifest.icons){const response=await page.request.get(base+'/beta/'+icon.src);assert.equal(response.status(),200)}
 await page.keyboard.press('Escape');await page.waitForURL(base+'/beta/');
 await page.goto(base+'/beta/keep-the-magic-shed.html');
 await page.setViewportSize({width:1440,height:900});await page.locator('#keep').click();await fits();
 await page.screenshot({path:'/tmp/tffc-keep-magic-desktop.png'});
 await page.mouse.click(10,10);await page.waitForURL(base+'/beta/');
 await page.goto(base+'/beta/keep-the-magic-shed.html');
 await page.setViewportSize({width:844,height:390});
 assert(await page.locator('#close').isVisible());await page.locator('#keep').click();await page.locator('#back').scrollIntoViewIfNeeded();await page.locator('#back').click();
 assert.equal(await page.locator('#heading').innerText(),'Share the Magic');
 await page.locator('#close').click();await page.waitForURL(base+'/beta/');
 await page.addInitScript(()=>Object.defineProperty(navigator,'standalone',{value:true}));
 await page.goto(base+'/beta/keep-the-magic-shed.html?instructions=1');
 await page.locator('#keep').click();assert.match(await page.locator('#install-status').innerText(),/already/);assert(await page.locator('#install').isHidden());
 assert.equal(await page.locator('#heading').innerText(),'You Kept the Magic!');
 assert.equal(await page.locator('#keep-intro').innerText(),'See. We told you it was easy.');
 assert.equal(await page.locator('#installed-celebration').innerText(),'Congratulations!');
 assert(await page.locator('#installed-celebration').isVisible());
 assert(await page.locator('#heading').evaluate(e=>e===document.activeElement&&getComputedStyle(e).outlineStyle==='none'),'installed title has no focus box');
 for(const [width,height] of [[390,669],[390,560],[1680,889]]){
  await page.setViewportSize({width,height});
  await page.goto(base+'/beta/keep-the-magic-shed.html?instructions=1&keep=1');
  await page.screenshot({path:`/tmp/tffc-installed-magic-${width}x${height}.png`});
  assert(await page.locator('#magic').evaluate(d=>d.scrollHeight<=d.clientHeight+1),'installed confirmation fits '+width+'×'+height);
  await fits();
 }
 await page.setViewportSize({width:390,height:669});
 await page.goto(base+'/beta/keep-the-magic-shed.html?instructions=1&keep=1');
 await page.keyboard.press('Tab');
 assert(await page.locator('#back').evaluate(e=>e===document.activeElement&&getComputedStyle(e).outlineStyle!=='none'),'keyboard focus remains visible');
 await page.locator('#back').click();
 assert(await page.locator('#installed-celebration').isHidden());
 await page.keyboard.press('Shift+Tab');
 // The title is not a tab stop; keyboard navigation can still reach Close.
 await page.locator('#close').focus();
 assert(await page.locator('#close').evaluate(e=>getComputedStyle(e).outlineStyle!=='none'),'Close retains its keyboard outline');
 await page.goto(base+'/beta/keep-the-magic-shed.html');
 await page.waitForURL(base+'/beta/');
 assert.equal(await page.locator('.splash-start').getAttribute('href'),'clubfinder-journey.html');
 const saved={originName:'Newton Aycliffe FC',postcode:'DL5 4RQ',ended:false,selectedAt:'2026-10-18T12:00:00.000Z',searchNumber:12345,callSign:'Tango Foxtrot 2 Alpha Charlie [12345]',pigeonName:'Shed Pigeon'};
 await page.evaluate(value=>localStorage.setItem('tinFoilFACupJourney_v7',JSON.stringify(value)),saved);
 const stored=await context.storageState();
 assert.deepEqual(errors,[]);
 await context.close();
 // Reopen a separate browser context with the same saved storage. This checks
 // our route and real BETA restore logic; physical OS storage is a device gate.
 const reopened=await browser.newContext({storageState:stored,viewport:{width:390,height:669}});
 await reopened.addInitScript(()=>Object.defineProperty(navigator,'standalone',{value:true}));
 let counterCalls=0;
 await reopened.route('https://tffac-clubfinder-counter.anvilspringstien.workers.dev/**',route=>{counterCalls++;return route.abort()});
 await reopened.route('https://api.postcodes.io/**',route=>{
  const url=new URL(route.request().url());
  if(decodeURIComponent(url.pathname).toUpperCase()==='/POSTCODES/DL5 4RQ')return route.fulfill({json:{status:200,result:{postcode:'DL5 4RQ',latitude:54.619,longitude:-1.57}}});
  return route.abort();
 });
 const app=await reopened.newPage();const appErrors=[];app.on('pageerror',e=>appErrors.push(String(e)));
 for(let attempt=0;attempt<2;attempt++){
  await app.goto(base+'/beta/keep-the-magic-shed.html');await app.waitForURL(base+'/beta/');
  await app.locator('.splash-start').click();await app.waitForURL('**/beta/clubfinder-journey.html');
  await app.locator('#results .result').first().waitFor({timeout:30000});
  assert.match(await app.locator('#results').innerText(),/Newton Aycliffe/);
  assert.equal(await app.locator('.pigeon-name-input').inputValue(),'Shed Pigeon');
  const actual=await app.evaluate(()=>JSON.parse(localStorage.getItem('tinFoilFACupJourney_v7')));
  for(const key of ['originName','postcode','searchNumber','callSign','pigeonName','selectedAt'])assert.equal(actual[key],saved[key],key+' must survive installed entry');
  assert.equal(await app.evaluate(()=>localStorage.getItem('tffc-test-campaign')),'preserve-me');
 }
 assert.equal(counterCalls,0,'restoring an existing identity must never issue a fresh counter');
 // Campaign entry uses the existing overlay and restores the exact reading
 // position/identity, with a smaller yellow fifth secondary control.
 for(const [width,height] of [[390,669],[390,560],[1680,889]]){
  await app.setViewportSize({width,height});
  const button=app.getByRole('button',{name:'Share the Magic',exact:true});
  assert.equal(await app.locator('.campaign-secondary-nav button').count(),5);
  assert.equal(await app.locator('.campaign-primary-nav button').count(),3);
  assert.equal(await app.locator('#results > .tffc-support-footer').count(),1,'Campaign uses the same external footer as choices');
  assert.equal(await app.locator('#results > .result .tffc-beta-help').count(),0);
  await app.locator('#results > .tffc-support-footer').scrollIntoViewIfNeeded();
  await app.screenshot({path:`/tmp/tffc-campaign-footer-magic-${width}x${height}.png`});
  await button.scrollIntoViewIfNeeded();
  const geometry=await button.evaluate(e=>{
   const r=e.getBoundingClientRect(),p=document.querySelector('.campaign-primary-nav button').getBoundingClientRect();
   return {x:r.x,right:r.right,height:r.height,primaryHeight:p.height,bg:getComputedStyle(e).backgroundColor,color:getComputedStyle(e).color};
  });
  assert(geometry.height<geometry.primaryHeight,'Share retains secondary prominence');
  assert(geometry.x>=0&&geometry.right<=width,'Share button stays inside the viewport');
  assert.equal(geometry.bg,'rgb(228, 187, 38)');assert.equal(geometry.color,'rgb(17, 17, 17)');
  const scroll=await app.evaluate(()=>scrollY);
  const identity=await app.evaluate(()=>localStorage.getItem('tinFoilFACupJourney_v7'));
  await app.screenshot({path:`/tmp/tffc-campaign-share-magic-${width}x${height}.png`});
  await button.click();
  const share=app.frameLocator('iframe[title="Share Tin Foil FA Cup"]');
  await share.locator('#copy').waitFor();
  assert.equal(await share.locator('#shareHeading').innerText(),'Share the Magic');
  await app.evaluate(()=>tffcCloseShare());
  assert(Math.abs(await app.evaluate(()=>scrollY)-scroll)<2,'close restores Campaign reading position');
  assert(await button.evaluate(e=>e===document.activeElement),'close restores the Share button focus');
  assert.equal(await app.evaluate(()=>localStorage.getItem('tinFoilFACupJourney_v7')),identity);
 }
 // One shared footer beneath all three choices, for both an existing
 // Campaign's original choices and a visitor who has not selected one.
 for(const selected of [true,false]){
  await app.setViewportSize({width:390,height:669});
  if(selected)await app.getByRole('button',{name:'View Original Campaigns',exact:true}).click();
  else await app.evaluate(async()=>{localStorage.removeItem('tinFoilFACupJourney_v7');window.__showOriginalTinFoilJourneys=false;tinFoilSetCurrentSearchNumber(54321);await go(false)});
  await app.waitForFunction(()=>document.querySelectorAll('#results > .result').length===3);
  assert.equal(await app.locator('#results .tffc-beta-help').count(),1);
  const footer=app.locator('#results > .tffc-support-footer');
  await footer.scrollIntoViewIfNeeded();
  assert.equal(await footer.locator('a,button').allTextContents().then(a=>a.join('|')),'Share|Feedback|Report an Issue|Privacy|About Us');
  const cards=await app.locator('#results > .result h2').allTextContents();
  const identity=await app.evaluate(()=>localStorage.getItem('tinFoilFACupJourney_v7'));
  const searchNumber=await app.evaluate(()=>tinFoilCurrentSearchNumber());
  await app.screenshot({path:`/tmp/tffc-choices-magic-${selected?'saved':'new'}.png`});
  await footer.getByRole('button',{name:'Share',exact:true}).click();
  const share=app.frameLocator('iframe[title="Share Tin Foil FA Cup"]');
  await share.locator('.keep-magic').click();await app.waitForURL('**/keep-the-magic-shed.html?**');
  await app.locator('#back').click();await app.waitForURL('**/beta/clubfinder-journey.html');
  await share.locator('#copy').waitFor();
  await app.evaluate(()=>tffcCloseShare());
  assert.equal(await app.locator('#results > .result').count(),3,'return preserves the three choices');
  assert.deepEqual(await app.locator('#results > .result h2').allTextContents(),cards);
  assert.equal(await app.evaluate(()=>localStorage.getItem('tinFoilFACupJourney_v7')),identity);
  await footer.getByRole('button',{name:'Share',exact:true}).click();
  await share.locator('.keep-magic').click();await app.waitForURL('**/keep-the-magic-shed.html?**');
  await app.locator('#close').click();await app.waitForURL('**/beta/clubfinder-journey.html');
  assert(await app.locator('iframe[title="Share Tin Foil FA Cup"]').isHidden());
  assert.equal(await app.locator('#results > .result').count(),3,'closing Keep restores the choices directly');
  assert.equal(await app.evaluate(()=>tinFoilCurrentSearchNumber()),searchNumber,'unselected search identity survives Keep');
  if(!selected){await app.locator('.journey-lozenge').first().click();assert.equal(await app.evaluate(()=>JSON.parse(localStorage.getItem('tinFoilFACupJourney_v7')).searchNumber),searchNumber)}
 }
 assert.equal(counterCalls,0,'Share/Keep returns never allocate a new identity');
 assert.deepEqual(appErrors,[]);
 await app.screenshot({path:'/tmp/tffc-campaign-magic-phone.png'});
 await reopened.close();
 // Stall the destination and block external launch JS. The head handoff must
 // already hide all launcher furniture before the destination is released.
 const launchContext=await browser.newContext({viewport:{width:390,height:669}});
 let recordLaunch;
 const launchRecorded=new Promise(resolve=>{recordLaunch=resolve});
 await launchContext.exposeBinding('recordInstalledLaunch',(_,value)=>recordLaunch(value));
 await launchContext.addInitScript(()=>{
  Object.defineProperty(navigator,'standalone',{value:true});
  const observer=new MutationObserver(()=>{
   if(!document.documentElement?.classList.contains('tffc-installed-launch'))return;
   // Record in the old document's own execution context: automation cannot
   // evaluate that context while its replacement navigation is pending.
   const hiddenRule=[...document.querySelectorAll('style')].some(s=>s.textContent.includes('html.tffc-installed-launch body{visibility:hidden}'));
   window.recordInstalledLaunch({hiddenRule,bodyHidden:!document.body||getComputedStyle(document.body).visibility==='hidden'});
   observer.disconnect();
  });
  observer.observe(document,{childList:true,subtree:true,attributes:true,attributeFilter:['class']});
 });
 const launchPage=await launchContext.newPage();
 let releaseSplash;
 const splashGate=new Promise(resolve=>{releaseSplash=resolve});
 await launchPage.route(base+'/beta/',async route=>{await splashGate;await route.continue()});
 await launchPage.route('**/keep-the-magic-shed.js',route=>route.abort());
 const destinationRequested=launchPage.waitForRequest(base+'/beta/');
 await launchPage.goto(base+'/beta/keep-the-magic-shed.html',{waitUntil:'commit'});
 await destinationRequested;
 const hiddenState=await Promise.race([launchRecorded,new Promise((_,reject)=>setTimeout(()=>reject(new Error('Installed launch was not recorded before navigation')),10000))]);
 assert(hiddenState.hiddenRule&&hiddenState.bodyHidden,'launcher cannot paint while the destination waits');
 releaseSplash();await launchPage.waitForURL(base+'/beta/');
 await launchPage.locator('.splash-start').waitFor();
 await launchContext.close();
 await checkInstalledHandover(browser,base);
 console.log('KEEP THE MAGIC SHED: PASS — geometry, navigation and cookies-only migration into empty installed storage; Checky, 01755, Challenge awards and miles persist without a new counter. Physical iPhone installation remains the device acceptance check.');

}finally{await browser.close()}
