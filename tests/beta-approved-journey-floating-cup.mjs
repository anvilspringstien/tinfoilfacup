import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {chromium} from 'playwright';

const origin = 'http://127.0.0.1:8765';
const experiment = '/beta/floating-cup.html';
const approved = readFileSync('beta/index.html', 'utf8');
const additions = '<meta name="robots" content="noindex"><link rel="stylesheet" href="floating-cup.css?v=2"><script defer src="floating-cup.js?v=2"></script>';
assert.equal(readFileSync('beta/floating-cup.html', 'utf8').replace(additions, ''), approved);

const browser = await chromium.launch();
const orientation = (page, beta, gamma) => page.evaluate(([beta, gamma]) => {
  window.dispatchEvent(new DeviceOrientationEvent('deviceorientation', {beta, gamma}));
}, [beta, gamma]);
const staticCrest = '.floating-cup-original';
const flyingCrest = '.floating-cup[data-moving]';

async function mobile(permission, path = experiment) {
  const page = await browser.newPage({viewport: {width: 390, height: 844}, isMobile: true, hasTouch: true});
  await page.addInitScript(result => {
    window.motionRequests = 0;
    DeviceOrientationEvent.requestPermission = async () => {
      if (!navigator.userActivation.isActive) throw new Error('Permission requested outside user activation');
      window.motionRequests += 1;
      return result;
    };
  }, permission);
  await page.goto(origin + path);
  return page;
}

try {
  const phone = await mobile('granted');
  const enable = phone.getByRole('button', {name: 'Enable tilt'});
  await enable.waitFor();
  assert.equal(await phone.evaluate(() => window.motionRequests), 0);
  await orientation(phone, 45, 0);
  assert.equal(await phone.locator(flyingCrest).count(), 0);
  assert.equal(await phone.getByRole('img', {name: 'Tin Foil FA Cup crest'}).count(), 1);
  const layout = await phone.locator('.splash-start').boundingBox();
  const crest = await phone.locator(staticCrest).boundingBox();

  await enable.tap();
  assert.equal(await phone.evaluate(() => window.motionRequests), 1);
  await orientation(phone, 45, 0); // Neutral is the position held when the first reading arrives.
  await phone.locator(flyingCrest).waitFor();
  const background = phone.locator('.floating-cup-view > img');
  const cup = phone.locator('.floating-cup-depth img');
  const backgroundBoxes = () => background.evaluateAll(images =>
    images.map(image => image.getBoundingClientRect().toJSON()));
  const fixed = await backgroundBoxes();
  assert.equal(fixed.length, 3);
  const rest = await cup.boundingBox();
  for (const key of ['x', 'y', 'width', 'height']) {
    assert.ok(Math.abs(rest[key] - crest[key]) < .1, 'neutral cup alignment: ' + key);
  }

  await orientation(phone, 56, 11);
  await phone.waitForFunction(() => {
    const depth = document.querySelector('.floating-cup-depth');
    return Math.abs(parseFloat(depth.style.getPropertyValue('--view-y')) - 7.425) < .05;
  });
  const [travel, originalTravel] = await cup.evaluate(image => {
    // Track the projected center at the cup's depth. A rotated image's
    // bounding box also moves when its outside corners change perspective.
    const depth = image.parentElement;
    const z = new DOMMatrix(getComputedStyle(image).transform).m43;
    const center = document.createElement('span');
    Object.assign(center.style, {
      position: 'absolute', left: '50%', top: '50%', transform: 'translateZ(' + z + 'px)',
    });
    depth.append(center);
    const original = depth.style.transform;
    const moved = center.getBoundingClientRect();
    depth.style.transform = 'none';
    const neutral = center.getBoundingClientRect();
    depth.style.transform = 'rotateX(-14.85deg) rotateY(14.85deg)';
    const legacy = center.getBoundingClientRect();
    depth.style.transform = original;
    center.remove();
    const distance = point => Math.hypot(point.x - neutral.x, point.y - neutral.y);
    return [distance(moved), distance(legacy)];
  });
  assert.ok(travel > 4, 'cup still has perceptible relative parallax');
  assert.deepEqual(await backgroundBoxes(), fixed, 'ivory, white and rings remain fixed');
  const ratio = travel / originalTravel;
  assert.ok(ratio >= .45 && ratio <= .55, 'cup travels about half as far as before: ' + ratio);

  await orientation(phone, 45, 0);
  await phone.waitForFunction(() => {
    const depth = document.querySelector('.floating-cup-depth');
    return Math.abs(parseFloat(depth.style.getPropertyValue('--view-y'))) < .05;
  });
  const settled = await cup.boundingBox();
  assert.ok(Math.hypot(settled.x - rest.x, settled.y - rest.y) < .25, 'cup settles back to neutral');
  assert.deepEqual(await backgroundBoxes(), fixed);
  assert.deepEqual(await phone.locator('.splash-start').boundingBox(), layout);
  assert.deepEqual(await phone.locator(staticCrest).boundingBox(), crest);
  assert.equal(await phone.locator('.splash-start').getAttribute('href'), 'clubfinder-journey.html');

  await phone.getByRole('button', {name: 'Tilt off'}).tap();
  await orientation(phone, 36, -5);
  assert.equal(await phone.locator(flyingCrest).count(), 0);
  assert.equal(await phone.locator(staticCrest).evaluate(el => getComputedStyle(el).opacity), '1');

  await phone.emulateMedia({reducedMotion: 'reduce'});
  await enable.waitFor({state: 'hidden'});
  assert.equal(await phone.locator(flyingCrest).count(), 0);
  await phone.close();

  const denied = await mobile('denied');
  await denied.getByRole('button', {name: 'Enable tilt'}).tap();
  await denied.getByRole('button', {name: 'Tilt blocked'}).waitFor();
  await orientation(denied, 50, 10);
  assert.equal(await denied.locator(flyingCrest).count(), 0);
  await denied.close();

  const ordinary = await mobile('granted', '/beta/');
  assert.equal(await ordinary.locator('.floating-cup').count(), 0);
  assert.equal(await ordinary.evaluate(() => window.motionRequests), 0);
  await ordinary.close();

  const desktop = await browser.newPage();
  await desktop.route('**/assets/floating-cup/ICONIC_CUP_TOP_LAYER.png', route => route.abort());
  await desktop.goto(origin + experiment, {waitUntil: 'networkidle'});
  assert.equal(await desktop.locator('.floating-cup').count(), 0);
  assert.equal(await desktop.getByRole('img', {name: 'Tin Foil FA Cup crest'}).count(), 1);
  await desktop.unrouteAll();
  await desktop.reload();
  const box = await desktop.locator('.floating-cup').boundingBox();
  await desktop.mouse.move(box.x + box.width * .8, box.y + box.height * .8);
  await desktop.locator(flyingCrest).waitFor();
  await desktop.mouse.move(0, 0);
  await desktop.locator(flyingCrest).waitFor({state: 'detached'});
  await desktop.close();
} finally {
  await browser.close();
}
console.log('Floating Cup: relative parallax, layout, opt-in, permission denial, static and reduced-motion fallbacks passed.');
