import assert from 'node:assert/strict';
import {chromium} from 'playwright';
const base=process.env.TFFC_PREVIEW_BASE||'http://127.0.0.1:8765';
const browser=await chromium.launch({headless:true,args:['--no-sandbox']});
try{
 for(const [width,height] of [[390,669],[1680,889]]){
  const context=await browser.newContext({viewport:{width,height}});
  await context.route('https://tffac-clubfinder-counter.anvilspringstien.workers.dev/**',route=>route.abort());
  await context.route('https://fonts.googleapis.com/**',route=>route.abort());
  let releaseHost,releaseMaster,hostRequested,masterRequested;
  const hostSeen=new Promise(resolve=>hostRequested=resolve),masterSeen=new Promise(resolve=>masterRequested=resolve);
  const hostGate=new Promise(resolve=>releaseHost=resolve),masterGate=new Promise(resolve=>releaseMaster=resolve);
  await context.route('**/clubfinder-journey.css',async route=>{hostRequested();await hostGate;await route.continue()});
  await context.route('**/two-rooms.css',async route=>{masterRequested();await masterGate;await route.continue()});
  const page=await context.newPage();await page.goto(base+'/');
  const app=page.frameLocator('#phoneApp');
  await app.locator('.splash-start').click({noWaitAfter:true});await hostSeen;
  assert.equal(await app.locator('html').evaluate(e=>getComputedStyle(e).backgroundColor),'rgb(20, 18, 16)','rewritten host remains dark while CSS is stalled');
  await page.screenshot({path:`/tmp/tffc-host-loading-${width}.png`});
  releaseHost();await masterSeen;
  const frame=app.locator('iframe.tffc-exact-master-frame');
  assert.deepEqual(await frame.evaluate(e=>[getComputedStyle(e).backgroundColor,getComputedStyle(e).colorScheme]),['rgb(20, 18, 16)','dark'],'new iframe has a dark canvas before its stylesheet arrives');
  const shot=await page.screenshot();
  const corners=await page.evaluate(async data=>{const image=new Image();image.src='data:image/png;base64,'+data;await image.decode();const c=document.createElement('canvas');c.width=image.width;c.height=image.height;const x=c.getContext('2d');x.drawImage(image,0,0);return [[0,0],[c.width-1,c.height-1]].map(([a,b])=>Array.from(x.getImageData(a,b,1,1).data).slice(0,3));},shot.toString('base64'));
  assert(corners.every(rgb=>Math.max(...rgb)<70),'no white outer canvas during the iframe handover');
  releaseMaster();await app.frameLocator('iframe.tffc-exact-master-frame').locator('#postcode').waitFor();
  await context.close();
 }
 console.log('DARK JOURNEY HANDOFF: PASS — stalled host and Four Laws stylesheets preserve dark canvases on phone and desktop.');
}finally{await browser.close()}
