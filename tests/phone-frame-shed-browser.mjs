import assert from 'node:assert/strict';
import {mkdir} from 'node:fs/promises';
import {chromium} from 'playwright';

const origin='http://127.0.0.1:8765';
const saved={originName:'Newton Aycliffe FC',postcode:'DL5 4RQ',searchNumber:12345,callSign:'Tango Foxtrot 2 Alpha Charlie [12345]',pigeonName:'Shed Pigeon',ended:false};
const browser=await chromium.launch();
await mkdir('phone-frame-evidence',{recursive:true});
try{
 for(const [width,height] of [[1680,889],[1024,768],[768,1024],[390,669]]){
  const context=await browser.newContext({viewport:{width,height}});
  const page=await context.newPage();
  await page.goto(origin+'/beta/phone-frame-shed.html');
  const app=page.frameLocator('#phoneApp');
  await app.getByRole('link',{name:'Start Campaign',exact:true}).waitFor();
  await app.locator('.crest').evaluate(img=>img.decode());
  const geometry=await page.locator('#phoneApp').evaluate(f=>{
   const r=f.getBoundingClientRect();
   return {width:r.width,height:r.height,left:r.left,canvas:f.clientWidth};
  });
  assert.equal(geometry.canvas,390);
  assert.ok(geometry.width<=width+.5&&geometry.height<=height+.5);
  assert.ok(Math.abs(geometry.left-(width-geometry.width)/2)<1);
  if(width>=700)assert.ok(Math.abs(geometry.width/geometry.height-9/16)<.001);
  else assert.ok(Math.abs(geometry.height-height)<1);
  const splashField=await app.locator('.field').boundingBox();
  await page.screenshot({path:`phone-frame-evidence/splash-${width}x${height}.png`});
  await app.getByRole('link',{name:'Start Campaign',exact:true}).click();
  await app.frameLocator('.tffc-exact-master-frame').getByRole('textbox',{name:'Enter Your Postcode'}).waitFor();
  const lawsField=await app.frameLocator('.tffc-exact-master-frame').locator('.field').boundingBox();
  assert.ok(Math.abs(splashField.width-lawsField.width)<1.5,'Splash → Four Laws must not change frame width');
  assert.ok(Math.abs(splashField.x-lawsField.x)<1.5,'Splash → Four Laws must not shift sideways');
  assert.equal(await page.locator('#phoneApp').evaluate(f=>f.clientWidth),390);
  await context.close();
 }
 const context=await browser.newContext({viewport:{width:1024,height:768}});
 let counterCalls=0;
 await context.route('https://tffac-clubfinder-counter.anvilspringstien.workers.dev/**',r=>{counterCalls++;return r.abort()});
 await context.route('https://api.postcodes.io/**',r=>r.fulfill({json:{status:200,result:{postcode:'DL5 4RQ',latitude:54.618,longitude:-1.571}}}));
 await context.addInitScript(value=>{
  // Seed once, so navigation and returns must preserve subsequent state.
  if(!localStorage.getItem('tinFoilFACupJourney_v7'))localStorage.setItem('tinFoilFACupJourney_v7',JSON.stringify(value));
 },saved);
 const page=await context.newPage();
 await page.goto(origin+'/beta/phone-frame-shed.html');
 const app=page.frameLocator('#phoneApp');
 await app.getByRole('link',{name:'My Campaign',exact:true}).click();
 await app.getByRole('textbox',{name:'Pigeon name',exact:true}).waitFor();
 assert.equal(await app.getByRole('textbox',{name:'Pigeon name',exact:true}).inputValue(),'Shed Pigeon');
 // A long Campaign must retain the full phone width, yet still scroll.
 assert.equal(await app.locator('html').evaluate(h=>h.clientWidth),390);
 assert.equal(await app.locator('html').evaluate(h=>getComputedStyle(h).scrollbarWidth),'none');
 const beforeWheel=await app.locator('body').evaluate(b=>b.ownerDocument.scrollingElement.scrollTop);
 await page.locator('#phoneApp').hover();
 await page.mouse.wheel(0,240);
 await page.waitForFunction(before=>document.getElementById('phoneApp').contentDocument.scrollingElement.scrollTop>before,beforeWheel);
 await app.getByRole('button',{name:'My Stats',exact:true}).click();
 const opened=context.waitForEvent('page');
 await app.getByRole('button',{name:'Got It!',exact:true}).click();
 const stats=await opened;
 stats.on('pageerror',e=>console.error('Stats wrapper error:',String(e)));
 async function waitForReportFrame(){
  try{await stats.waitForFunction(()=>document.getElementById('phoneApp')?.clientWidth===980,{},{timeout:10000});}
  catch(error){console.error('Stats frame diagnostic:',await stats.locator('html').evaluate(h=>({url:location.href,ready:document.readyState,html:h.outerHTML.slice(0,2000),innerURL:h.querySelector('iframe')?.contentWindow?.location?.href})));throw error;}
 }
 await stats.frameLocator('#phoneApp').getByRole('button',{name:'Print / Save as PDF',exact:true}).waitFor({timeout:30000});
 // The report can render before the outer tab's deferred frame script loads.
 await waitForReportFrame();
 assert.equal(await stats.locator('#phoneApp').evaluate(f=>f.clientWidth),980);
 const statsRatio=await stats.locator('#phoneApp').evaluate(f=>{const r=f.getBoundingClientRect();return r.width/r.height});
 assert.ok(Math.abs(statsRatio-9/16)<.001);
 assert.match(stats.url(),/phone-frame-shed\.html\?view=stats$/);
 await stats.reload();
 await stats.frameLocator('#phoneApp').getByRole('button',{name:'Print / Save as PDF',exact:true}).waitFor({timeout:30000});
 await waitForReportFrame();
 // Existing Stats returns to its opener when available; after a refresh
 // without one, it opens Campaign in the same tab. Both must stay usable.
 const hasOpener=await stats.frameLocator('#phoneApp').locator('body').evaluate(()=>!!window.opener&&!window.opener.closed);
 if(hasOpener){
  const closed=stats.waitForEvent('close');
  await stats.frameLocator('#phoneApp').getByRole('button',{name:'Back to My Campaign',exact:true}).click();
  await closed;
 }else{
  await stats.frameLocator('#phoneApp').getByRole('button',{name:'Back to My Campaign',exact:true}).click();
  await stats.frameLocator('#phoneApp').getByRole('button',{name:'My Stats',exact:true}).waitFor({timeout:30000});
  await stats.close();
 }
 await app.getByRole('button',{name:'My Challenges',exact:true}).click();
 await app.getByRole('button',{name:'Got It!',exact:true}).click();
 await app.getByRole('button',{name:'Exit',exact:true}).waitFor({timeout:30000});
 await app.getByRole('button',{name:'Exit',exact:true}).click();
 await app.getByRole('button',{name:'Share the Magic',exact:true}).click();
 const share=app.frameLocator('iframe[title="Share Tin Foil FA Cup"]');
 await share.getByRole('button',{name:'Keep the Magic',exact:true}).click();
 await share.getByRole('heading',{name:'Keep the Magic',exact:true}).waitFor();
 await share.getByRole('button',{name:'Back to Share',exact:true}).click();
 await share.getByRole('button',{name:'Close',exact:true}).click();
 await page.setViewportSize({width:768,height:1024});
 assert.equal(await page.locator('#phoneApp').evaluate(f=>f.clientWidth),390);
 const identity=await app.locator('body').evaluate(()=>JSON.parse(localStorage.getItem('tinFoilFACupJourney_v7')));
 for(const key of ['originName','searchNumber','callSign','pigeonName'])assert.equal(identity[key],saved[key]);
 assert.equal(counterCalls,0,'saved Campaign and all returns must allocate no counter');
 await context.close();
 console.log('PASS: shared frame at four viewports; Four Laws, saved Campaign, Stats tab/return, Challenges, Share/Keep, rotation and identity without counter calls');
}finally{await browser.close()}
