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

try {
  await crestPaint();
  for (const entry of ['/','/beta/','/beta/phone-frame.html']) await journeyPaint(entry);
} finally {
  await browser.close();
}
console.log('Rendered transition paint passed for the cold crest swap and the Public, Shed and installed Four Laws handoffs.');
