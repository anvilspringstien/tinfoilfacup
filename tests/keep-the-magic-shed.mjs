import { createRequire } from 'node:module';
const { chromium } = createRequire(import.meta.url)('playwright');
import assert from 'node:assert/strict';
const base=process.env.TFFC_PREVIEW_BASE||'http://127.0.0.1:8765';
const browser=await chromium.launch({headless:true,args:['--no-sandbox']});
try{
 const context=await browser.newContext({viewport:{width:390,height:669},deviceScaleFactor:3});
 const page=await context.newPage();const errors=[];page.on('pageerror',e=>errors.push(String(e)));
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
 await page.locator('#back').click();
 await page.evaluate(()=>{Object.defineProperty(navigator,'share',{configurable:true,value:undefined})});
 await page.locator('#share').click();assert.match(await page.locator('#feedback').innerText(),/Copy Link/);
 await page.evaluate(()=>{Object.defineProperty(navigator,'clipboard',{configurable:true,value:{writeText:async value=>{window.copiedURL=value}}})});
 await page.locator('#copy').click();assert.equal(await page.evaluate(()=>window.copiedURL),'https://tinfoilfacup.com/');
 await page.keyboard.press('Escape');assert.equal(await page.locator('#magic').evaluate(d=>d.open),false);
 await page.locator('#open').click();assert(await page.locator('#magic').evaluate(d=>d.open));
 assert.equal(await page.evaluate(()=>localStorage.getItem('tffc-test-campaign')),'preserve-me');
 assert.equal(await page.evaluate(async()=>('serviceWorker' in navigator)?(await navigator.serviceWorker.getRegistrations()).length:0),0);
 const manifest=await page.evaluate(async()=>{const r=await fetch(document.querySelector('link[rel="manifest"]').href);return r.json()});
 assert.equal(manifest.start_url,'/beta/keep-the-magic-shed.html');assert.equal(manifest.display,'standalone');
 for(const icon of manifest.icons){const response=await page.request.get(base+'/beta/'+icon.src);assert.equal(response.status(),200)}
 await page.setViewportSize({width:1440,height:900});await page.locator('#keep').click();await fits();
 await page.screenshot({path:'/tmp/tffc-keep-magic-desktop.png'});
 await page.mouse.click(10,10);assert.equal(await page.locator('#magic').evaluate(d=>d.open),false);
 await page.setViewportSize({width:844,height:390});await page.locator('#open').click();
 assert(await page.locator('#close').isVisible());await page.locator('#keep').click();await page.locator('#back').scrollIntoViewIfNeeded();await page.locator('#back').click();
 assert.equal(await page.locator('#heading').innerText(),'Share the Magic');
 await page.addInitScript(()=>Object.defineProperty(navigator,'standalone',{value:true}));
 await page.reload();await page.locator('#keep').click();assert.match(await page.locator('#install-status').innerText(),/already/);assert(await page.locator('#install').isHidden());
 assert.deepEqual(errors,[]);console.log('KEEP THE MAGIC SHED: PASS — phone/desktop geometry, platform guidance, simulated install dismissal, share/copy, keyboard/backdrop, storage unchanged, no worker, manifest/assets.');
 await context.close();
}finally{await browser.close()}
