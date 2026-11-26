import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {chromium} from 'playwright';

const origin = 'http://127.0.0.1:8765';
const experiment = '/beta/floating-cup.html';
const approved = readFileSync('beta/index.html', 'utf8');
const additions = '<meta name="robots" content="noindex"><link rel="stylesheet" href="floating-cup.css?v=3"><script defer src="floating-cup.js?v=3"></script>';
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
  const fixedTime = new Date('2026-11-26T12:00:00Z');
  await phone.clock.install({time: fixedTime});
  await phone.clock.pauseAt(new Date(fixedTime.getTime() + 1000));
  await orientation(phone, 45, 0); // The first sample is the neutral viewing pose.
  assert.equal(await phone.locator(flyingCrest).count(), 1);
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
  const travel = box => Math.hypot(box.x - rest.x, box.y - rest.y);

  await orientation(phone, 56, 11);
  await phone.clock.runFor(176);
  const moved = await cup.boundingBox();
  assert.deepEqual(await backgroundBoxes(), fixed, 'ivory, white and rings remain fixed');
  assert.ok(Math.abs(moved.width - rest.width) < .1 && Math.abs(moved.height - rest.height) < .1);
  assert.equal(await cup.evaluate(image => getComputedStyle(image.parentElement).transform), 'none');

  // Compare with the previous projection of the cup centre at the same diagonal tilt.
  const oldAngle = 7.425 * Math.PI / 180;
  const depth = .204 * crest.width;
  const oldZ = depth * Math.cos(oldAngle) ** 2;
  const oldTravel = Math.hypot(depth * Math.sin(oldAngle), depth * Math.sin(oldAngle) * Math.cos(oldAngle))
    / (1 - oldZ / (1.7 * crest.width));
  const ratio = travel(moved) / oldTravel;
  assert.ok(ratio >= .22 && ratio <= .28, 'cup travels about a quarter as far as before: ' + ratio);

  // Keep sending readings at the changed pose, including slight sensor noise.
  // The new pose should settle without crossing centre or leaving an offset.
  let previous = travel(moved);
  for (const jitter of [.05, -.05, .06, -.06, 0, 0]) {
    await orientation(phone, 56 + jitter, 11 - jitter);
    await phone.clock.runFor(80);
    const held = await cup.boundingBox();
    assert.ok(held.x >= rest.x - .02 && held.y >= rest.y - .02, 'no overshoot');
    const distance = travel(held);
    assert.ok(distance <= previous + .02, 'settles monotonically');
    previous = distance;
  }
  assert.ok(previous < .02, 'a held off-centre pose leaves no displacement');
  const settled = await cup.boundingBox();
  await phone.clock.runFor(600);
  assert.deepEqual(await cup.boundingBox(), settled, 'the viewpoint is stationary after settling');
  assert.deepEqual(await backgroundBoxes(), fixed);

  await orientation(phone, 60, 15);
  await phone.clock.runFor(160);
  assert.ok(travel(await cup.boundingBox()) > .75, 'movement resumes from the new neutral pose');
  await phone.evaluate(() => Object.defineProperty(screen.orientation, 'angle', {value: 90, configurable: true}));
  await orientation(phone, 60, 15);
  assert.ok(travel(await cup.boundingBox()) < .02, 'rotation of the screen recalibrates without a jump');
  await phone.clock.resume();
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
