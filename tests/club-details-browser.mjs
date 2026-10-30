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
  await checkStorage();
  await page.goto(origin+'/?view=club&club=Reading');
  await app.getByRole('heading',{name:'Reading',exact:true}).waitFor();
  assert.equal(await app.locator('#venue').innerText(),'Weston Homes Stadium');
  assert.equal(await app.locator('#postcode').innerText(),'PE2 8AL');
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
 console.log('PASS: public York/away-club details, unknown club, phone/desktop layout, Explore navigation and byte-preserved storage without counter calls.');
}finally{await browser.close()}
