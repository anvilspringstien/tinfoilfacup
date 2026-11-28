import assert from 'node:assert/strict';
import {chromium, devices, webkit} from 'playwright';
import {PNG} from 'pngjs';

const origin = process.env.TFFC_PREVIEW_BASE || 'http://127.0.0.1:8765';
const engine = process.env.TFFC_BROWSER === 'webkit' ? webkit : chromium;
const browser = await engine.launch();
const app = page => page.frameLocator('#phoneApp');

function gate(page, url) {
  let observed, release;
  const requested = new Promise(resolve => {observed = resolve;});
  const open = new Promise(resolve => {release = resolve;});
  return page.route(url, async route => {
    observed();
    await open;
    await route.continue();
  }).then(() => ({requested, release}));
}

async function pixel(page, x, y) {
  const screenshot = await page.screenshot({scale:'css', clip:{x:Math.floor(x),y:Math.floor(y),width:6,height:6}});
  const {data} = PNG.sync.read(screenshot);
  const rgb = [0,0,0];
  for (let i = 0; i < data.length; i += 4) {
    for (let channel = 0; channel < 3; channel++) rgb[channel] += data[i + channel];
  }
  return rgb.map(value => Math.round(value / (data.length / 4)));
}

async function context(options) {
  const c = await browser.newContext(options);
  c.setDefaultTimeout(8000);
  // Routing disables the HTTP cache. Never call live data, counters or fonts.
  await c.route('https://**/*', route => route.abort());
  return c;
}

async function crestPaint() {
  const c = await context({viewport:{width:1440,height:900}});
  try {
    const page = await c.newPage();
    // Give a CSS-only request its own cache identity. This makes the cold
    // gap visible even on engines that normally reuse the decoded PNG.
    await page.route('**/astral-portal.css*', async route => {
      const response = await route.fetch();
      const body = (await response.text()).replace('CREST_BASE_RING_INNER_WHITE.png', 'CREST_BASE_RING_INNER_WHITE.png?style-mask');
      await route.fulfill({response,body});
    });
    await page.route('**/*?style-mask', route => route.abort());
    const sky = await gate(page,'**/assets/astral-portal/full-sky.webp');
    await page.goto(origin+'/beta/');
    const crest = app(page).locator('.shed-astral-crest');
    await crest.waitFor();
    const box = await crest.boundingBox();
    const inspect = async label => {
      const rgb = await pixel(page, box.x + box.width*.73, box.y + box.height*.52);
      assert.ok(rgb[2] > rgb[0]+15 && rgb[0]<80, label+' must paint blue sky; RGB '+rgb);
    };
    await inspect('Static crest');
    await page.mouse.move(box.x+box.width*.79,box.y+box.height*.58);
    await sky.requested;
    await inspect('First hovered frame with sky held');
    await inspect('Next frame with sky held');
    sky.release();
    await app(page).locator('.astral-layers-visible').waitFor();
    await inspect('First composed motion frame');
    await inspect('Next composed motion frame');
  } finally {
    await c.close();
  }
}

async function journeyPaint(entry) {
  const c = await context(devices['iPad Pro 11']);
  try {
    const page = await c.newPage();
    const engineDownload = await gate(page,'**/beta/clubfinder-beta.html');
    const masterDownload = await gate(page,'**/beta/two-rooms-clubfinder.html');
    await page.goto(origin+entry);
    const frame = page.locator('#phoneApp');
    const box = await frame.boundingBox();
    const dark = async phase => {
      for (let frame = 0; frame < 2; frame++){
        for (const vertical of [.16,.52,.83]){
          const rgb = await pixel(page,box.x+box.width*.8,box.y+box.height*vertical);
          assert.ok(rgb.every(channel=>channel<60),entry+' '+phase+' must paint dark; RGB '+rgb);
        }
      }
    };

    // Supply a visible white child during a real stalled wrapper fetch.
    // Headless engines need not reproduce the physical WebKit flash timing.
    const open = app(page).getByRole('link',{name:'Start Campaign'}).click();
    await engineDownload.requested;
    const doc = app(page).locator('html');
    const original = await doc.evaluate(root=>{
      const css = root.style.cssText;
      root.style.setProperty('background','#fff','important');
      root.style.setProperty('color-scheme','light','important');
      root.ownerDocument.body.style.setProperty('background','#fff','important');
      return css;
    });
    await dark('pending engine handoff');
    await doc.evaluate((root,css)=>{
      root.style.cssText = css;
      root.ownerDocument.body.style.removeProperty('background');
    },original);
    engineDownload.release();
    await masterDownload.requested;
    await dark('rewritten document waiting for its nested Four Laws page');
    masterDownload.release();
    await open;
    await app(page).frameLocator('.tffc-exact-master-frame').getByRole('heading',{name:'The Four Laws',exact:true}).waitFor();
    await page.waitForFunction(()=>document.querySelector('.phone-shell > div[aria-hidden=true]')?.hidden===true);
    const rgb = await pixel(page,box.x+box.width*.86,box.y+box.height*.51);
    assert.ok(rgb.every(channel=>channel<60),entry+' must return to the approved dark frame');
  } finally {
    await c.close();
  }
}

async function journeyRecovery(scenario) {
  const c = await context(devices['iPad Pro 11']);
  let release = () => {};
  try {
    const page = await c.newPage();
    await page.clock.install();
    const masterPath = '**/beta/two-rooms-clubfinder.html';
    if (scenario === 'failed') {
      await page.route(masterPath, route => route.fulfill({
        status:503, contentType:'text/html', body:'<body style="background:white">Unavailable</body>'
      }), {times:1});
    }
    if (scenario === 'stalled' || scenario === 'interrupted') {
      let request;
      const requested = new Promise(resolve => {request = resolve;});
      const pending = new Promise(resolve => {release = resolve;});
      await page.route(masterPath, async route => {
        request();
        await pending;
        await route.abort().catch(() => {});
      }, {times:1});
      // The handler acknowledges receipt while the real child remains stalled.
      await page.goto(origin+'/beta/', {waitUntil:'domcontentloaded'});
      const start = app(page).getByRole('link',{name:'Start Campaign'});
      await start.click({noWaitAfter:true});
      await requested;
    } else {
      if (scenario === 'missing message' || scenario === 'cached wrapper') {
        await page.route('**/beta/clubfinder-journey.html', async route => {
          const response = await route.fetch();
          let body = (await response.text()).replaceAll(
            "if(parent!==window)parent.postMessage({type:'tffc-journey-painted'},location.origin);", ''
          );
          if (scenario === 'cached wrapper') {
            // The pre-handoff wrapper also lacked the initial dark hints.
            body = body.replaceAll('<meta name="color-scheme" content="dark">','');
          }
          await route.fulfill({response,body});
        });
      }
      // Exercise both framed startup and a real Splash click.
      await page.goto(origin+(scenario === 'failed'?'/beta/phone-frame.html?view=campaign':'/'));
      if (scenario !== 'failed') await app(page).getByRole('link',{name:'Start Campaign'}).click();
    }
    const frame = page.locator('#phoneApp');
    const cover = page.locator('.phone-shell > div').first();
    const retry = page.getByRole('button',{name:'Try again'});
    const back = page.getByRole('button',{name:'Return to start'});
    const fourLaws = app(page).frameLocator('.tffc-exact-master-frame').getByRole('heading',{name:'The Four Laws',exact:true});
    if (scenario === 'missing message' || scenario === 'cached wrapper') {
      await fourLaws.waitFor();
      await cover.waitFor({state:'hidden'});
      // The load fallback releases immediately, before the ten-second deadline.
      assert.equal(await retry.count(),0);
      return;
    }
    if (scenario === 'interrupted') {
      await frame.evaluate(element=>element.contentWindow.location.replace('/beta/shed-splash.html'));
      await app(page).getByRole('link',{name:'Start Campaign'}).waitFor();
      await cover.waitFor({state:'hidden'});
      await page.clock.fastForward(10001);
      assert.equal(await retry.count(),0,'the previous deadline must not cover the Splash');
      await app(page).getByRole('link',{name:'Start Campaign'}).click();
      await fourLaws.waitFor();
      await cover.waitFor({state:'hidden'});
      return;
    }
    await cover.waitFor();
    assert.equal(await retry.count(),0,'loading should not show an error immediately');
    await page.clock.fastForward(10001);
    await retry.waitFor();
    assert.match(await page.getByRole('alert').innerText(),/The Four Laws could not load/);
    assert.equal(await frame.evaluate(element=>element.inert),true);
    const box = await frame.boundingBox();
    assert.ok((await pixel(page,box.x+box.width*.8,box.y+box.height*.23)).every(channel=>channel<60),
      'Recovery must retain the dark canvas over a failed or stalled child');
    if (scenario === 'stalled') {
      await back.click();
      await app(page).getByRole('link',{name:'Start Campaign'}).waitFor();
      await app(page).getByRole('link',{name:'Start Campaign'}).click();
    } else {
      await retry.click();
    }
    await fourLaws.waitFor();
    await cover.waitFor({state:'hidden'});
    assert.equal(await frame.evaluate(element=>element.inert),false);
  } finally {
    release();
    await c.close();
  }
}

try {
  await crestPaint();
  for (const entry of ['/','/beta/','/beta/phone-frame.html']) await journeyPaint(entry);
  for (const scenario of ['failed','stalled','missing message','cached wrapper','interrupted']) await journeyRecovery(scenario);
} finally {
  await browser.close();
}
console.log('Rendered transition paint and bounded recovery passed for the crest and Four Laws handoffs.');
