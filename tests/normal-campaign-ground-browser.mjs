import {chromium} from 'playwright';
import assert from 'node:assert/strict';
import {mkdirSync} from 'node:fs';
const browser=await chromium.launch({headless:true});
const root='http://127.0.0.1:8765';
mkdirSync('/tmp/tffc-normal-ground-ui',{recursive:true});
try {
 for(const [device,width,height] of [['big-boy',1365,860],['iphone',390,844],['ipad-portrait',820,1180]]) {
  const context=await browser.newContext({viewport:{width,height}});
  const page=await context.newPage();
  const errors=[];
  page.on('pageerror',e=>errors.push(String(e)));
  await page.route('https://tffac-clubfinder-counter.anvilspringstien.workers.dev/**',r=>r.abort());
  await page.goto(root+'/beta/phone-frame.html?view=campaign',{waitUntil:'domcontentloaded'});
  const iframe=page.frameLocator('#phoneApp');
  await iframe.locator('iframe.tffc-exact-master-frame').waitFor({timeout:30000});
  await iframe.frameLocator('iframe.tffc-exact-master-frame').locator('#postcode').waitFor({timeout:30000});
  await page.waitForFunction(()=>{
   const d=document.querySelector('#phoneApp')?.contentDocument;
   return !!d && typeof d.defaultView?.findGround==='function';
  },null,{timeout:30000});
  const layout=await page.evaluate(()=>({
   shell:document.querySelector('.phone-shell')?.getBoundingClientRect().width,
   iframe:document.querySelector('#phoneApp')?.getBoundingClientRect().width,
   userWidth:innerWidth
  }));
  assert.ok(layout.shell>0&&layout.shell<=Math.max(width,390),'current phone frame dimension must be valid');
  if(width>=700){
   const expected=390*Math.min(width/390,height/(390*16/9));
   assert.ok(Math.abs(layout.shell-expected)<2,device+' must retain approved scaled 390px composition, expected '+expected+' got '+layout.shell);
  }
  const entrant=await iframe.locator('#postcode').evaluate(el=>({
    orient:el.ownerDocument.defaultView.findGround({name:'Leyton Orient FC'}),
    afc:el.ownerDocument.defaultView.findGround({name:'AFC Liverpool'}),
    liverpool:el.ownerDocument.defaultView.findGround({name:'Liverpool FC'})
  }));
  assert.equal(entrant.orient?.verification,'unverified');
  assert.equal(entrant.orient?.postcode,'E10 5NF');
  assert.equal(entrant.orient?.lat,undefined);
  assert.equal(entrant.orient?.lon,undefined);
  assert.equal(entrant.afc?.name,'AFC Liverpool');
  assert.notEqual(entrant.liverpool?.name,'AFC Liverpool');
  await iframe.locator('#postcode').evaluate(async(el)=>{
   await el.ownerDocument.defaultView.chooseJourney('Bishop Auckland FC','DL14 9AE');
  });
  await iframe.locator('.chosen-campaign-current').getByText('BetWright Stadium', {exact:false}).waitFor({timeout:20000});
  const text=await iframe.locator('.chosen-campaign-current').innerText();
  assert.match(text,/Leyton Orient/);
  assert.match(text,/BetWright Stadium\s*•\s*E10 5NF/);
  assert.match(text,/Ground details recorded\. Verification pending\./);
  assert.doesNotMatch(text,/Unverified Location/);
  assert.match(text,/Port Vale v Leyton Orient/);
  await iframe.locator('.campaign-barry-nav .barry-air-launch').waitFor({timeout:15000});
  assert.equal(await iframe.locator('.campaign-barry-nav .barry-air-launch').getAttribute('aria-label'),'Barry Air');
  const saved=await page.evaluate(()=>localStorage.getItem('tinFoilFACupJourney_v7'));
  assert.ok(saved&&saved.includes('Bishop Auckland'),'Campaign must save origin');
  await page.screenshot({path:'/tmp/tffc-normal-ground-ui/'+device+'.png',fullPage:true});
  await page.reload({waitUntil:'domcontentloaded'});
  await iframe.locator('.chosen-campaign-current').getByText('BetWright Stadium', {exact:false}).waitFor({timeout:25000});
  assert.equal(await page.evaluate(()=>localStorage.getItem('tinFoilFACupJourney_v7')),saved,'reload must preserve saved Campaign');
  await iframe.locator('.campaign-barry-nav .barry-air-launch').waitFor({timeout:15000});
  assert.deepEqual(errors,[],device+' script errors');
  console.log('PASS normal framed Campaign, badges and saved state',device,JSON.stringify(layout));
  await context.close();
 }
}finally {await browser.close()}
