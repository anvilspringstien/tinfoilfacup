import assert from 'node:assert/strict';
import {chromium} from 'playwright';
const browser=await chromium.launch();
const origin='http://127.0.0.1:8765';
try{
 for(const width of [390,1024]){
  const context=await browser.newContext({viewport:{width,height:768}});let counter=0;
  await context.route('https://tffac-clubfinder-counter.anvilspringstien.workers.dev/**',r=>{counter++;return r.abort()});
  await context.addInitScript(()=>{localStorage.setItem('tinFoilFACupJourney_v7','{"originName":"Keep existing","pigeonName":"Checky"}');localStorage.setItem('tffc.challengeDeck.v1','preserve-cabinet');});
  const page=await context.newPage();
  const checkStorage=async()=>assert.deepEqual(await page.evaluate(()=>[localStorage.getItem('tinFoilFACupJourney_v7'),localStorage.getItem('tffc.challengeDeck.v1')]),['{"originName":"Keep existing","pigeonName":"Checky"}','preserve-cabinet']);
  await page.goto(origin+'/?view=club&club=York%20City');const app=page.frameLocator('#phoneApp');
  await app.getByRole('heading',{name:'York City',exact:true}).waitFor();
  assert.equal(await app.locator('#postcode').innerText(),'YO32 9AF');assert.equal(await app.locator('#tie').innerText(),'York City v Northampton Town');
  assert.equal(await app.locator('#website a').getAttribute('href'),'https://www.yorkcityfootballclub.co.uk/');
  assert.equal(await page.locator('#phoneApp').evaluate(f=>f.clientWidth),390);
  assert.equal(await app.locator('body').evaluate(b=>b.scrollWidth<=b.clientWidth),true);
  await app.locator('#story-content').waitFor({state:'visible',timeout:60000});
  assert.match(await app.locator('#story-heading').innerText(),/How a Tin Foil Cup could reach York City/);
  assert.equal(await app.locator('#example-label').isVisible(),true);
  assert.equal(await app.locator('#campaign-origin').innerText(),'Newton Aycliffe FC');
  assert.ok(await app.locator('#campaign-history li').count()>0);
  assert.match(await app.locator('#club-role-copy').innerText(),/not a confirmed route or a prediction/);
  assert.equal(await app.locator('body').evaluate(b=>b.scrollWidth<=b.clientWidth),true);
  await checkStorage();
  await page.goto(origin+'/?view=club&club=Reading');
  await app.getByRole('heading',{name:'Reading',exact:true}).waitFor();
  assert.equal(await app.locator('#venue').innerText(),'Weston Homes Stadium');
  assert.equal(await app.locator('#postcode').innerText(),'PE2 8AL');
  await checkStorage();
  await page.goto(origin+'/?view=club&club=AFC%20Fylde');
  await app.locator('#story-content').waitFor({state:'visible',timeout:60000});
  assert.equal(await app.locator('#story-heading').innerText(),'Your club is carrying the Cup');
  assert.equal(await app.locator('#example-label').isVisible(),false);
  assert.equal(await app.locator('#origin-choice').isVisible(),true);
  const options=await app.locator('#origin-choice option').allTextContents();assert.ok(options.length>1);
  await app.locator('#origin-choice').selectOption('1');
  assert.equal(await app.locator('#campaign-origin').innerText(),options[1]);
  await checkStorage();
  await page.goto(origin+'/?view=club&club=No%20such%20club');
  await app.getByRole('status').filter({hasText:'unique published listing'}).waitFor();
  assert.equal(await app.locator('#details').isVisible(),false);
  assert.deepEqual(await page.evaluate(()=>[localStorage.getItem('tinFoilFACupJourney_v7'),localStorage.getItem('tffc.challengeDeck.v1')]),['{"originName":"Keep existing","pigeonName":"Checky"}','preserve-cabinet']);
  assert.equal(counter,0,'read-only details never issue an identity');
  await app.locator('.explore').click();
  await app.getByRole('link',{name:'Start Campaign',exact:true}).waitFor();
  await context.close();
 }
 // Reproduce unsupported and silent background Workers instead of relying on
 // the successful default browser path that missed the reported loading state.
 for(const mode of ['throws','silent','network-error']){
  const context=await browser.newContext({viewport:{width:390,height:768}});
  await context.addInitScript(mode=>{
   localStorage.setItem('tinFoilFACupJourney_v7','preserve-my-campaign');
   if(mode==='silent')window.Worker=class{postMessage(){}terminate(){}};
   else window.Worker=class{constructor(){throw new Error('Worker unavailable')}};
  },mode);
  if(mode==='network-error')await context.route('**/club-details-campaigns.mjs*',r=>r.abort());
  const page=await context.newPage();await page.goto(origin+'/?view=club&club=York%20City');const app=page.frameLocator('#phoneApp');
  if(mode==='network-error'){
   await app.locator('#story-retry').waitFor({state:'visible'});
   assert.match(await app.locator('#story-status').innerText(),/could not be loaded/);
   await context.unroute('**/club-details-campaigns.mjs*');
   await app.locator('#story-retry').click();
  }
  await app.locator('#story-content').waitFor({state:'visible',timeout:30000});
  assert.equal(await app.locator('#campaign-origin').innerText(),'Newton Aycliffe FC');
  assert.equal(await app.locator('#story-status').isVisible(),false);
  assert.equal(await page.evaluate(()=>localStorage.getItem('tinFoilFACupJourney_v7')),'preserve-my-campaign');
  await context.close();
 }
 console.log('PASS: club stories, phone/desktop layout, saved data, unavailable/silent Workers and recovery from failed module loading.');
}finally{await browser.close()}
