import assert from 'node:assert/strict';
import {chromium} from 'playwright';

const origin='http://127.0.0.1:8765';
const browser=await chromium.launch();
const sizes=[[1680,889],[1024,768],[390,669],[768,1024]];
try {
 for(const [width,height] of sizes){
  const ctx=await browser.newContext({viewport:{width,height}});
  await ctx.route('https://tffac-clubfinder-counter.anvilspringstien.workers.dev/**',route=>route.abort());
  const page=await ctx.newPage();
  const errors=[];
  page.on('pageerror',e=>errors.push(String(e)));
  /* Public entry frames the approved source; legacy BETA masters remain exact. */
  const publicPage=await ctx.newPage();
  const publicErrors=[];
  publicPage.on('pageerror',e=>publicErrors.push(String(e)));
  await publicPage.goto(origin+'/',{waitUntil:'domcontentloaded'});
  const publicApp=publicPage.frameLocator('#phoneApp');
  await publicApp.locator('.splash-start').waitFor();
  await publicPage.evaluate(()=>document.fonts.ready);
  assert.equal(await publicApp.locator('.splash-start').innerText(),'Start Campaign','new supporters see the original label');
  const publicGeometry=await publicApp.locator('body').evaluate(()=>Object.fromEntries(['.field','.crest','.splash-intro','.splash-message','.splash-start','.splash-grassroots'].map(selector=>{const r=document.querySelector(selector).getBoundingClientRect();return [selector,{x:r.x,y:r.y,width:r.width,height:r.height}]})));
  const publicSplash=await publicApp.locator('.field').boundingBox();
  assert.equal(await publicApp.locator('.splash-start').getAttribute('href'),
   'clubfinder-journey.html','Public Start must open the approved journey');
  assert.ok(await publicPage.locator('link[rel=canonical]').getAttribute('href')==='https://tinfoilfacup.com/');
  await publicApp.locator('.splash-start').click();

  const publicFour=publicApp.frameLocator('iframe.tffc-exact-master-frame');
  await publicFour.locator('.field').waitFor({timeout:25000});
  const publicFourBox=await publicFour.locator('.field').boundingBox();
  assert.ok(Math.abs(publicSplash.width-publicFourBox.width)<1.5,
   width+'x'+height+' public Splash -> Four Laws width drift');
  assert.equal(await publicPage.evaluate(()=>sessionStorage.getItem('tffc.beta.approved-journey')),'1');
  assert.deepEqual(publicErrors,[],width+'x'+height+' public entry produced script errors');
  await publicPage.close();
  await page.goto(origin+'/beta/',{waitUntil:'domcontentloaded'});
  await page.locator('.splash-start').waitFor();
  const before=await page.locator('.field').boundingBox();
  const splashGeometry=await page.evaluate(()=>Object.fromEntries(['.field','.crest','.splash-intro','.splash-message','.splash-start','.splash-grassroots'].map(selector=>{const r=document.querySelector(selector).getBoundingClientRect();return [selector,{x:r.x,y:r.y,width:r.width,height:r.height}]})));

  if(width<700){
   assert.ok(Math.abs(publicSplash.width-before.width)<1.5,'phone public/BETA source width');
   assert.ok(Math.abs(publicSplash.x-before.x)<1.5,'phone public/BETA source alignment');
  }
  const start=page.locator('.splash-start');
  assert.equal(await start.getAttribute('href'),'clubfinder-journey.html');
  await start.click();
  await page.waitForURL('**/beta/clubfinder-journey.html',{timeout:15000});
  const frame=page.frameLocator('iframe.tffc-exact-master-frame');
  await frame.locator('#postcode').waitFor({timeout:25000});
  const after=await frame.locator('.field').boundingBox();
  const delta=Math.abs(before.width-after.width);
  assert.ok(delta<=1.5,width+'x'+height+' Splash vs Four Laws width drift: '+delta);
  assert.equal(await frame.locator('#postcode').getAttribute('placeholder'),'Enter Your Postcode');
  assert.equal(await page.evaluate(()=>sessionStorage.getItem('tffc.beta.approved-journey')),'1');
  assert.equal(await page.evaluate(()=>scrollY),0,'first visit remains at Four Laws');
  await page.evaluate(()=>{
   document.getElementById('postcode').value='NE6 5NL';
   document.querySelector('.tffc-exact-master-frame').contentDocument.getElementById('postcode').value='NE6 5NL';
   const results=document.getElementById('results');
   results.innerHTML='<div class="result" style="min-height:1300px"><h2>Regression fixture — Campaign</h2></div>';
   results.style.display='block';
   document.getElementById('status').textContent=
    '3 Tin Foil FA Cup Campaigns found for NE6 5NL. Dates & times may change. Always check before travelling';
  });
  await page.waitForFunction(()=>!document.getElementById('tffc-results-summary')?.hidden,{timeout:9000});
  const geometry=await page.evaluate(()=>{
   const frame=document.querySelector('iframe.tffc-exact-master-frame');
   const field=frame.contentDocument.querySelector('.field');
   const summary=document.getElementById('tffc-results-summary');
   const campaigns=document.getElementById('clubfinderField');
   const rr=el=>{const b=el.getBoundingClientRect();return{left:b.left,top:b.top,right:b.right,bottom:b.bottom,width:b.width}};
   const f=rr(field),fr=rr(frame),s=rr(summary),c=rr(campaigns);
   return{f:{...f,top:f.top+fr.top,bottom:f.bottom+fr.top},s,c,
    summary:summary.textContent,
    resultsDisplay:getComputedStyle(campaigns).display};
  });
  assert.ok(geometry.resultsDisplay!=='none','Campaigns must display after search');
  assert.match(geometry.summary,/3 Tin Foil FA Cup Campaigns found/);
  for(const name of ['s','c'])assert.ok(Math.abs(geometry[name].width-geometry.f.width)<1.5,
   width+'x'+height+' '+name+' width mismatch '+JSON.stringify(geometry));
  assert.ok(Math.abs(geometry.s.top-geometry.f.bottom-14)<2,
   width+'x'+height+' opening to findings gap wrong '+JSON.stringify(geometry));
  assert.ok(Math.abs(geometry.c.top-geometry.s.bottom-14)<2,
   width+'x'+height+' findings to Campaign gap wrong '+JSON.stringify(geometry));
  await page.evaluate(()=>window.tffcScrollToFinder());
  await page.waitForFunction(()=>Math.abs(document.getElementById('tffc-results-summary').getBoundingClientRect().top-14)<3,
   null,{timeout:6000});
  await page.evaluate(()=>window.resetFinder());
  await page.waitForFunction(()=>{
   const frame=document.querySelector('iframe.tffc-exact-master-frame');
   return frame.contentDocument.getElementById('postcode').value===''&&
      document.getElementById('postcode').value==='';
  },null,{timeout:6000});
  assert.equal(await frame.locator('#postcode').getAttribute('placeholder'),'Enter Your Postcode');
  assert.equal(await page.evaluate(()=>document.getElementById('tffc-results-summary').hidden),true);
  const saved={originName:'Heaton Stannington FC',postcode:'NE6 5NL',searchNumber:1755,callSign:'Tango Foxtrot 2 Alpha Charlie [01755]',pigeonName:'Checky',ended:false};
  await ctx.route('https://api.postcodes.io/**',route=>{
   const url=new URL(route.request().url());
   if(decodeURIComponent(url.pathname).toUpperCase()==='/POSTCODES/NE6 5NL')return route.fulfill({json:{status:200,result:{postcode:'NE6 5NL',latitude:54.99,longitude:-1.56}}});
   return route.abort();
  });
  await page.evaluate(value=>localStorage.setItem('tinFoilFACupJourney_v7',JSON.stringify(value)),saved);
  for(const splash of ['/', '/beta/']){
   await page.goto(origin+splash);await page.evaluate(()=>document.fonts.ready);
   const journey=splash==='/'?await(await page.locator('#phoneApp').elementHandle()).contentFrame():page;
   const baseline=splash==='/'?publicGeometry:splashGeometry;
   const myCampaign=journey.getByRole('link',{name:'My Campaign',exact:true});await myCampaign.waitFor();
   const returningGeometry=await journey.evaluate(()=>Object.fromEntries(['.field','.crest','.splash-intro','.splash-message','.splash-start','.splash-grassroots'].map(selector=>{const r=document.querySelector(selector).getBoundingClientRect();return [selector,{x:r.x,y:r.y,width:r.width,height:r.height}]})));
   for(const selector of Object.keys(baseline))for(const dimension of ['x','y','width','height'])assert(Math.abs(baseline[selector][dimension]-returningGeometry[selector][dimension])<1.5,`${width}x${height} ${selector} ${dimension} must not move when label changes`);
   await page.screenshot({path:`/tmp/tffc-saved-entry-splash-${width}x${height}.png`});
   await myCampaign.click();
   await journey.locator('.pigeon-name-input').waitFor({timeout:30000});
   await journey.waitForFunction(()=>Math.abs(document.getElementById('tffc-results-summary').getBoundingClientRect().top-14)<3,null,{timeout:10000});
   assert.equal(await journey.locator('.pigeon-name-input').inputValue(),'Checky');
   assert.equal(await page.evaluate(()=>JSON.parse(localStorage.getItem('tinFoilFACupJourney_v7')).searchNumber),1755);
   await page.screenshot({path:`/tmp/tffc-saved-entry-${width}x${height}.png`});
  }
  for(const invalid of ['not-json','null',JSON.stringify({originName:'Heaton Stannington FC'}),JSON.stringify({...saved,ended:true})]){
   await page.evaluate(value=>localStorage.setItem('tinFoilFACupJourney_v7',value),invalid);
   await page.goto(origin+'/');
   const fallback=page.frameLocator('#phoneApp');
   await fallback.getByRole('link',{name:'Start Campaign',exact:true}).waitFor();
   assert.equal(await fallback.locator('.splash-start').getAttribute('href'),'clubfinder-journey.html');
  }
  const unexpected=errors.filter(x=>!x.includes('Failed to fetch'));
  assert.deepEqual(unexpected,[],width+'x'+height+' browser script errors');
  console.log(width+'x'+height+': PUBLIC and BETA Splash->master, 3 frames, 14px gaps, Frame 2 scroll and reset passed');
  await ctx.close();
 }
} finally {await browser.close();}
