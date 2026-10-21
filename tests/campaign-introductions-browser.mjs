import {createRequire} from 'node:module';
import assert from 'node:assert/strict';
const engines=createRequire(import.meta.url)('playwright');
const browser=await engines[process.env.TFFC_BROWSER||'chromium'].launch({headless:true});
const base=process.env.TFFC_PREVIEW_BASE||'http://127.0.0.1:8765';
try{
 const context=await browser.newContext({viewport:{width:390,height:669}});
 let counters=0;await context.route('https://tffac-clubfinder-counter.anvilspringstien.workers.dev/**',route=>{counters++;return route.abort()});
 await context.route('https://api.postcodes.io/**',route=>{
  const url=new URL(route.request().url());
  return decodeURIComponent(url.pathname).toUpperCase()==='/POSTCODES/NE6 5NL'?route.fulfill({json:{status:200,result:{postcode:'NE6 5NL',latitude:54.99,longitude:-1.56}}}):route.abort();
 });
 const page=await context.newPage(),errors=[];page.on('pageerror',error=>errors.push(String(error)));
 const saved={originName:'Heaton Stannington FC',postcode:'NE6 5NL',ended:false,selectedAt:'2026-10-20T13:00:00Z',searchNumber:1755,callSign:'Tango Foxtrot 2 Alpha Charlie [01755]',pigeonName:'Checky'};
 await page.goto(base+'/beta/keep-the-magic-shed.html');
 await page.evaluate(value=>localStorage.setItem('tinFoilFACupJourney_v7',JSON.stringify(value)),saved);
 await page.goto(base+'/beta/clubfinder-journey.html');await page.locator('.pigeon-name-input').waitFor({timeout:30000});await page.evaluate(()=>document.fonts.ready);
 // Keep the complete call sign together and give both clubs equal prominence.
 for(const [width,height] of [[320,669],[390,669],[768,1024],[1680,889]]){
  await page.setViewportSize({width,height});
  const value=page.locator('.campaign-identity .campaign-call-sign-value');
  assert.equal(await value.evaluate(e=>getComputedStyle(e).fontWeight),'700','Call Sign is bold');
  assert.equal(await value.innerText(),saved.callSign,'full original call sign including number is preserved');
  if(width<=600){
   const geometry=await value.evaluate(e=>{const r=e.getBoundingClientRect(),label=document.querySelector('.campaign-call-sign-label').getBoundingClientRect(),parent=e.parentElement.getBoundingClientRect(),range=document.createRange();range.selectNodeContents(e);const lines=[...range.getClientRects()];return {top:r.top,labelBottom:label.bottom,right:lines[0].right,parentRight:parent.right,lines:lines.length}});
   assert(geometry.top>=geometry.labelBottom-1,'Call Sign label has its own line');
   assert.equal(geometry.lines,1,'complete call sign and number stay together');
   assert(geometry.right<=geometry.parentRight+1,'complete call sign fits inside the phone identity panel');
  }
  const styles=await page.evaluate(()=>{
   const pick=selector=>{const s=getComputedStyle(document.querySelector(selector));return [s.fontSize,s.fontFamily,s.fontWeight,s.lineHeight,s.letterSpacing,s.color]};
   return {custodian:pick('.chosen-campaign-current .custodian-name'),origin:pick('.campaign-origin-name'),custodianLabel:pick('.chosen-campaign-current .carrier'),originLabel:pick('.campaign-origin-title')};
  });
  assert.deepEqual(styles.origin,styles.custodian,'origin and custodian club names have equal prominence');
  assert.deepEqual(styles.originLabel,styles.custodianLabel,'origin and custodian introductions use the same type');
  assert.equal(await page.locator('.campaign-origin-title').innerText(),'Your Tin Foil FA Cup Campaign started with:');
  await page.locator('.campaign-identity').scrollIntoViewIfNeeded();
  await page.screenshot({path:`/tmp/tffc-campaign-identity-${width}x${height}.png`});
  await page.locator('.campaign-origin').scrollIntoViewIfNeeded();
  await page.screenshot({path:`/tmp/tffc-campaign-origin-${width}x${height}.png`});
 }
 await page.setViewportSize({width:390,height:669});
 const original=await page.evaluate(()=>JSON.stringify({...localStorage}));
 for(const [width,height] of [[390,669],[390,560],[1680,889]]){
  await page.setViewportSize({width,height});let first;
  for(const name of ['My Campaign','My Stats','My Challenges']){
   const priorScroll=await page.evaluate(()=>scrollY);
   await page.getByRole('button',{name,exact:true}).click();
   const intro=page.locator('#tffc-campaign-intro');await intro.waitFor();
   assert.equal(await intro.getByRole('button',{name:'Got It!',exact:true}).count(),1);
   assert.equal(await intro.getByRole('checkbox').count(),1);
   assert.match(await intro.locator('label').innerText(),/Don’t show this again this Campaign/);
   const rect=await intro.boundingBox(),button=await intro.getByRole('button',{name:'Got It!',exact:true}).boundingBox();
   const geometry=[rect.width,rect.height,button.width,button.height];
   if(first)assert.deepEqual(geometry,first,'all three popups/buttons have equal dimensions');else first=geometry;
   assert(rect.x>=0&&rect.y>=0&&rect.x+rect.width<=width+1&&rect.y+rect.height<=height+1);
   assert(await intro.evaluate(e=>e.scrollHeight<=e.clientHeight+1),'popup frame fits viewport');
   assert(await intro.locator('#tffc-intro-title').evaluate(e=>e===document.activeElement&&getComputedStyle(e).outlineStyle==='none'),'opening focus announces the heading without a box');
   assert.equal(await page.evaluate(()=>document.body.style.position),'fixed','background is locked while reading');
   const message=intro.locator('#tffc-intro-message');
   const endings={
    'My Campaign':'Your old pigeon identity and locally saved Challenge progress won’t be recovered.',
    'My Stats':'But it will tell you how many miles your pigeon has flown!',
    'My Challenges':'Keep an eye out for Barry, our Staff Pigeon. He’s absolutely full of it.'
   };
   assert((await message.innerText()).endsWith(endings[name]),'approved final paragraph is present');
   await message.evaluate(e=>e.scrollTop=e.scrollHeight);
   assert(await message.evaluate(e=>e.scrollTop+e.clientHeight>=e.scrollHeight-1),'all introduction copy can be reached');
   const lockedScroll=await page.evaluate(()=>scrollY);await message.hover();await page.mouse.wheel(0,800);
   await page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
   assert.equal(await page.evaluate(()=>scrollY),lockedScroll,'scrolling past the final paragraph cannot move the background');
   assert.deepEqual(await intro.getByRole('button',{name:'Got It!',exact:true}).boundingBox(),button,'reading longer copy does not move confirmation controls');
   await page.screenshot({path:`/tmp/tffc-campaign-intro-${name.replace('My ','').toLowerCase()}-end-${width}x${height}.png`});
   await message.evaluate(e=>e.scrollTop=0);
   await page.screenshot({path:`/tmp/tffc-campaign-intro-${name.replace('My ','').toLowerCase()}-${width}x${height}.png`});
   await intro.getByRole('checkbox').check();await intro.getByRole('button',{name:'Close',exact:true}).click();
   assert.notEqual(await page.evaluate(()=>document.body.style.position),'fixed','closing releases the background lock');
   assert.equal(page.url(),base+'/beta/clubfinder-journey.html');
  }
 }
 assert.equal(await page.evaluate(()=>JSON.stringify({...localStorage})),original,'closing introductions changes no saved progress/preferences');
 await page.setViewportSize({width:390,height:669});
 // Gate real Stats preparation so cancellation and early confirmation are tested cold.
 await page.evaluate(()=>{
  window.__realStats=tinFoilPrepareStatsDocument;window.__statsCalls=0;
  window.__resetStatsGate=()=>{window.__statsGate=new Promise(resolve=>{window.__releaseStats=resolve})};window.__resetStatsGate();
  tinFoilPrepareStatsDocument=async(...args)=>{window.__statsCalls++;await window.__statsGate;return window.__realStats(...args)};
 });
 await page.getByRole('button',{name:'My Stats',exact:true}).click();
 await page.waitForFunction(()=>window.__statsCalls>0);
 assert.equal(context.pages().length,1,'background preparation does not open a Stats window');
 await page.keyboard.press('Escape');await page.evaluate(()=>window.__releaseStats());
 assert.equal(await page.locator('#tffc-campaign-intro').count(),0);
 assert.equal(page.url(),base+'/beta/clubfinder-journey.html');
 await page.evaluate(()=>window.__resetStatsGate());
 await page.getByRole('button',{name:'My Stats',exact:true}).click();
 await page.locator('#tffc-campaign-intro input').check();
 const opened=page.waitForEvent('popup');await page.getByRole('button',{name:'Got It!',exact:true}).click();const stats=await opened;
 await stats.getByText('Preparing Your Stats…',{exact:true}).waitFor();
 assert(await stats.locator('.prep-rollers').isVisible(),'existing Stats preparation counter remains during loading');
 await page.evaluate(()=>window.__releaseStats());await stats.locator('.sheet').waitFor({timeout:30000});
 assert.equal(await stats.locator('.stats-pigeon-editor').inputValue(),'Checky');
 assert.equal(await page.evaluate(()=>JSON.parse(localStorage.getItem('tinFoilFACupJourney_v7')).introDismissed.stats),true);
 await Promise.all([stats.waitForEvent('close'),stats.locator('.stats-return button').click()]);
 const again=page.waitForEvent('popup');await page.getByRole('button',{name:'My Stats',exact:true}).click();const repeated=await again;
 assert.equal(await page.locator('#tffc-campaign-intro').count(),0,'Stats preference skips only Stats');await repeated.locator('.sheet').waitFor({timeout:30000});await repeated.close();
 // A cold Challenges confirmation shows the retained counter and only then navigates.
 await page.evaluate(()=>{
  window.__realChallenges=tinFoilPrepareChallenges;window.__challengeCalls=0;
  window.__challengeGate=new Promise(resolve=>{window.__releaseChallenges=resolve});
  tinFoilPrepareChallenges=async(...args)=>{window.__challengeCalls++;await window.__challengeGate;return window.__realChallenges(...args)};
 });
 await page.getByRole('button',{name:'My Challenges',exact:true}).click();await page.waitForFunction(()=>window.__challengeCalls>0);
 assert(await page.locator('#tffc-campaign-intro').isVisible(),'Stats opt-out does not suppress Challenges');
 await page.locator('#tffc-campaign-intro input').check();await page.getByRole('button',{name:'Got It!',exact:true}).click();
 await page.locator('#tffc-challenges-prep .prep-rollers').waitFor();
 await page.evaluate(()=>window.__releaseChallenges());await page.waitForURL('**/beta/challenges-beta.html');
 await page.locator('#overlay').waitFor();
 // Browser history is the operation Safari's edge swipe performs.
 await page.goBack();await page.locator('.pigeon-name-input').waitFor({timeout:30000});
 const atFrameTwo=()=>page.waitForFunction(()=>Math.abs(document.getElementById('tffc-results-summary').getBoundingClientRect().top-14)<3,null,{timeout:10000});
 await atFrameTwo();assert.equal(await page.locator('.pigeon-name-input').inputValue(),'Checky');
 // Explicitly exercise a page revived with its old viewport from BFCache too.
 await page.evaluate(()=>{scrollTo(0,100);sessionStorage.setItem('tffc.challengeOrigin','clubfinder-beta');dispatchEvent(new PageTransitionEvent('pageshow',{persisted:true}))});
 await atFrameTwo();assert.equal(await page.evaluate(()=>sessionStorage.getItem('tffc.challengeOrigin')),null);
 await page.getByRole('button',{name:'My Challenges',exact:true}).click();await page.waitForURL('**/beta/challenges-beta.html');
 await page.locator('#exitBtn').click();await page.waitForURL('**/beta/clubfinder-journey.html');await atFrameTwo();
 const prefs=await page.evaluate(()=>JSON.parse(localStorage.getItem('tinFoilFACupJourney_v7')).introDismissed);
 assert.deepEqual(prefs,{stats:true,challenges:true});
 // New Campaign, new introductions. Cancellation never carries an old preference across.
 await page.evaluate(value=>localStorage.setItem('tinFoilFACupJourney_v7',JSON.stringify(value)),{...saved,searchNumber:1756,selectedAt:'2026-10-20T13:20:00Z'});
 await page.reload();await page.locator('.pigeon-name-input').waitFor({timeout:30000});
 await page.getByRole('button',{name:'My Stats',exact:true}).click();await page.locator('#tffc-campaign-intro').waitFor();await page.keyboard.press('Escape');
 assert.equal(counters,0,'introductions, Stats, Challenges and returns never allocate another identity');
 assert.deepEqual(errors,[]);
 await context.close();console.log('CAMPAIGN INTRODUCTIONS: PASS — matching geometry, cancellation, real background preparation, pending counters, per-Campaign opt-outs, history/BFCache Frame 2 returns, stable identity.');
}finally{await browser.close()}
