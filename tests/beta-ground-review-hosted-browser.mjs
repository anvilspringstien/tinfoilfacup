import {chromium} from 'playwright';
import assert from 'node:assert/strict';
import {mkdirSync} from 'node:fs';
const browser=await chromium.launch({headless:true});
const root='http://127.0.0.1:8765';
mkdirSync('/tmp/tffc-ground-optin',{recursive:true});
try {
 for(const [device,width,height] of [['big-boy',1365,860],['iphone',390,844],['ipad-portrait',820,1180]]) {
  const context=await browser.newContext({viewport:{width,height}});
  const page=await context.newPage();
  const errors=[];
  page.on('pageerror',e=>errors.push(String(e)));
  await page.route('https://tffac-clubfinder-counter.anvilspringstien.workers.dev/**',r=>r.abort());
  await page.goto(root+'/beta/clubfinder-ground-review-journey.html',{waitUntil:'domcontentloaded'});
  await page.waitForFunction(()=>typeof window.findGround==='function',null,{timeout:25000});
  assert.equal(await page.locator('iframe.tffc-exact-master-frame').count(),1);
  const leyton=await page.evaluate(()=>findGround({name:'Leyton Orient FC'}));
  assert.equal(leyton.postcode,'E10 5NF');
  assert.equal(leyton.verification,'unverified');
  assert.equal(leyton.lat,undefined);
  const afc=await page.evaluate(()=>findGround({name:'AFC Liverpool'}));
  const other=await page.evaluate(()=>findGround({name:'Liverpool FC'}));
  assert.equal(afc?.name,'AFC Liverpool');
  assert.notEqual(other?.name,'AFC Liverpool');
  await page.evaluate(()=>chooseJourney('Bishop Auckland FC','DL14 9AE'));
  await page.waitForFunction(()=>/BetWright Stadium.*E10 5NF/s.test(
    document.querySelector('.chosen-campaign-current')?.innerText||''),null,{timeout:18000});
  const chosen=await page.locator('.chosen-campaign-current').innerText();
  assert.match(chosen,/Ground details recorded\. Verification pending\./);
  assert.match(chosen,/Port Vale v Leyton Orient/);
  const saved=await page.evaluate(()=>localStorage.getItem('tinFoilFACupJourney_v7'));
  assert.ok(saved?.includes('Bishop Auckland'));
  await page.reload({waitUntil:'domcontentloaded'});
  await page.waitForFunction(()=>/BetWright Stadium.*E10 5NF/s.test(
    document.querySelector('.chosen-campaign-current')?.innerText||''),null,{timeout:20000});
  assert.equal(await page.evaluate(()=>localStorage.getItem('tinFoilFACupJourney_v7')),saved);
  assert.deepEqual(errors,[]);
  await page.screenshot({path:'/tmp/tffc-ground-optin/'+device+'.png',fullPage:true});
  console.log('PASS opt-in real Shed route, full Campaign and reload',device);
  await context.close();
 }
} finally {await browser.close()}
