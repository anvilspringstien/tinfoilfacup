import assert from 'node:assert/strict';
import {chromium} from 'playwright';
const browser=await chromium.launch();
try {
 const page=await browser.newPage({viewport:{width:1680,height:889}});
 await page.goto('http://127.0.0.1:8765/beta/clubfinder-journey.html');
 const master=page.frameLocator('.tffc-exact-master-frame');
 await master.locator('#postcode').waitFor();
 await page.evaluate(()=>{
  const results=document.getElementById('results');
  results.innerHTML='<div class="result" style="height:2000px">Campaign</div>';
  results.style.display='block';
  document.getElementById('status').textContent='Your Tin Foil FA Cup Campaign';
 });
 await page.waitForFunction(()=>!document.getElementById('tffc-results-summary').hidden);
 for(const selector of ['.crest','.clubfinder-laws','.clubfinder-machine']){
  await page.evaluate(()=>window.scrollTo(0,0));
  await master.locator(selector).hover();
  await page.mouse.wheel(0,160);
  await page.waitForFunction(()=>window.scrollY>50,{timeout:2000});
  assert.ok(await page.evaluate(()=>window.scrollY)>50,selector+' trapped wheel');
 }
 // A genuinely overflowing inner reading area still consumes its own wheel.
 await page.evaluate(()=>window.scrollTo(0,0));
 await master.locator('.clubfinder-furniture').evaluate(el=>{
  el.style.height='150px';el.style.minHeight='150px';el.style.maxHeight='150px';
  el.insertAdjacentHTML('beforeend','<div style="height:600px;flex:none">Reading</div>');
 });
 await master.locator('.clubfinder-laws').hover();
 await page.mouse.wheel(0,100);
 await page.waitForFunction(()=>document.querySelector('.tffc-exact-master-frame').contentDocument.querySelector('.clubfinder-furniture').scrollTop>0);
 assert.equal(await page.evaluate(()=>window.scrollY),0);
 await master.locator('.clubfinder-furniture').evaluate(el=>el.scrollTop=el.scrollHeight);
 const box=await master.locator('.clubfinder-furniture').boundingBox();
 await page.mouse.move(box.x+box.width/2,box.y+box.height/2);
 await page.mouse.wheel(0,160);
 await page.waitForFunction(()=>window.scrollY>50,{timeout:2000});
 console.log('Four Laws wheel: crest, laws, controls and inner boundary PASS');
} finally {await browser.close();}
