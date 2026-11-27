import assert from 'node:assert/strict';
import {acceptedSplash} from './beta-approved-journey-splash-reference.mjs';
import {createHash} from 'node:crypto';
import {readFileSync} from 'node:fs';
import {chromium, devices} from 'playwright';

const origin = 'http://127.0.0.1:8765';
const experiment = '/beta/astral-portal.html';
const skyPath = '/beta/assets/astral-portal/full-sky.webp';
const additions = '<meta name="robots" content="noindex"><link rel="stylesheet" href="astral-portal.css?v=full-sky"><script defer src="astral-portal.js?v=full-sky"></script>';
assert.equal(readFileSync('beta/astral-portal.html', 'utf8').replace(additions, '')
  .replace('Tin Foil FA Cup — Astral Portal (Shed)', 'Tin Foil FA Cup — BETA'), acceptedSplash);
assert.equal(createHash('sha256').update(readFileSync('.' + skyPath)).digest('hex'),
  '06c6ed2c539149874fca787908c88eca4fbb68395e496c7367d835da02e9abe8');

const browser = await chromium.launch();
const cup = '.astral-near img';
const stars = '.astral-opening img';
const staticLayers = '.astral-art > img, .astral-opening';
const orient = (page, beta, gamma) => page.evaluate(([beta, gamma]) => {
  window.dispatchEvent(new DeviceOrientationEvent('deviceorientation', {beta, gamma}));
}, [beta, gamma]);
const rect = (page, selector) => page.locator(selector).boundingBox();
const distance = (a, b) => Math.hypot(a.x - b.x, a.y - b.y);
const freeze = async page => {
  const start = new Date('2026-11-27T12:00:00Z');
  await page.clock.install({time: start});
  await page.clock.pauseAt(new Date(start.getTime() + 100));
};

async function phone(permission, path = experiment) {
  const page = await browser.newPage(devices['iPhone 14']);
  page.setDefaultTimeout(5000);
  await page.addInitScript(permission => {
    window.motionRequests = 0;
    DeviceOrientationEvent.requestPermission = async () => {
      if (!navigator.userActivation.isActive) throw new Error('Unexpected motion permission request');
      window.motionRequests++;
      return permission;
    };
  }, permission);
  await page.goto(origin + path);
  await page.getByRole('button', {name: 'Enable tilt'}).waitFor();
  return page;
}

try {
  const page = await phone('granted');
  const neutralCup = await rect(page, cup);
  const neutralSky = await rect(page, stars);
  const original = await rect(page, '.astral-portal-ready');
  const readBackground = () => page.locator(staticLayers).evaluateAll(
    elements => elements.map(element => element.getBoundingClientRect().toJSON()));
  const background = await readBackground();
  assert.equal(background.length, 3);
  assert.ok(await page.locator('.astral-opening').evaluate(element =>
    getComputedStyle(element).maskImage.includes('CREST_BASE_RING_INNER_WHITE.png')));
  const uncovered = await page.locator('.astral-opening').evaluate(async opening => {
    const mask = new Image();
    mask.src = getComputedStyle(opening).maskImage.slice(5, -2);
    await mask.decode();

    const canvas = document.createElement('canvas');
    canvas.width = mask.naturalWidth;
    canvas.height = mask.naturalHeight;
    const context = canvas.getContext('2d', {willReadFrequently: true});
    context.drawImage(mask, 0, 0);
    const rings = opening.nextElementSibling;
    // The fixed black ring conceals the disc's outermost pixels.
    context.globalCompositeOperation = 'destination-out';
    context.drawImage(rings, 0, 0, canvas.width, canvas.height);
    context.globalCompositeOperation = 'source-over';
    const aperturePixels = context.getImageData(0, 0, canvas.width, canvas.height).data;
    if (!aperturePixels.some((alpha, index) => index % 4 === 3 && alpha === 255)) {
      throw new Error('The visible aperture is empty');
    }
    const sky = opening.querySelector('img');
    const aperture = opening.getBoundingClientRect();
    const scene = opening.closest('.astral-portal');
    const unfilled = [];

    // Exercise the artwork at every corner of the viewpoint's full travel.
    for (const x of [-1.5, 1.5]) {
      for (const y of [-1.5, 1.5]) {
        scene.style.setProperty('--view-x', x + '%');
        scene.style.setProperty('--view-y', y + '%');
        const box = sky.getBoundingClientRect();
        const factor = canvas.width / aperture.width;
        context.clearRect(0, 0, canvas.width, canvas.height);
        context.drawImage(sky, (box.x - aperture.x) * factor, (box.y - aperture.y) * factor,
          box.width * factor, box.height * factor);
        const skyPixels = context.getImageData(0, 0, canvas.width, canvas.height).data;
        unfilled.push(aperturePixels.some((alpha, index) =>
          index % 4 === 3 && alpha > 0 && skyPixels[index] < 255));
      }
    }
    scene.style.removeProperty('--view-x');
    scene.style.removeProperty('--view-y');
    return unfilled;
  });
  assert.deepEqual(uncovered, [false, false, false, false], 'Opaque sky covers the visible aperture at the full tilt limits');
  // Match the three visible bright stars to the owner's 507px mock-up.
  for (const [sourceX, sourceY, mockX, mockY] of [[161, 551, 125, 216],
    [390, 305, 195, 141], [1087, 612, 407, 234]]) {
    const x = (neutralSky.x - original.x + neutralSky.width * sourceX / 1254) * 507 / original.width;
    const y = (neutralSky.y - original.y + neutralSky.height * sourceY / 1254) * 507 / original.height;
    assert.ok(Math.hypot(x - mockX, y - mockY) < 1, 'Star registers to the resting mock-up');
  }
  for (const axis of ['x', 'y', 'width', 'height']) {
    assert.ok(Math.abs(neutralCup[axis] - original[axis]) < .05, 'Original alignment and proportions');
  }
  assert.equal(await page.getByRole('img', {name: 'Tin Foil FA Cup crest'}).count(), 1);
  await orient(page, 60, 20);
  assert.equal(await page.evaluate(() => window.motionRequests), 0);
  assert.deepEqual(await rect(page, cup), neutralCup);

  await page.getByRole('button', {name: 'Enable tilt'}).tap();
  assert.equal(await page.evaluate(() => window.motionRequests), 1);
  await freeze(page);
  await orient(page, 45, 0);
  assert.deepEqual(await rect(page, cup), neutralCup);
  await orient(page, 62, 17);
  await page.clock.runFor(144);
  const tiltedCup = await rect(page, cup);
  const tiltedSky = await rect(page, stars);
  assert.ok(tiltedCup.x > neutralCup.x && tiltedCup.y > neutralCup.y);
  assert.ok(tiltedSky.x < neutralSky.x && tiltedSky.y < neutralSky.y);
  const opposedTravel = distance(tiltedSky, neutralSky) / distance(tiltedCup, neutralCup);
  assert.ok(Math.abs(opposedTravel - (45 / 215) / (20.4 / 149.6)) < .04,
    'Both planes follow the same viewpoint at their respective depths');
  assert.ok(Math.abs(tiltedCup.width - neutralCup.width) < .05);
  assert.ok(Math.abs(tiltedSky.width - neutralSky.width) < .05);
  assert.deepEqual(await readBackground(), background);

  const white = await phone('granted', '/beta/floating-cup.html');
  const whiteCup = '.floating-cup-depth img';
  await white.getByRole('button', {name: 'Enable tilt'}).tap();
  await freeze(white);
  await orient(white, 45, 0);
  const whiteStart = await rect(white, whiteCup);
  await orient(white, 62, 17);
  await white.clock.runFor(144);
  const ratio = distance(tiltedCup, neutralCup) / distance(await rect(white, whiteCup), whiteStart);
  assert.ok(ratio >= .22 && ratio <= .28, 'About a quarter of the #751 cup travel, measured ratio ' + ratio);
  await white.close();

  // Cross the old 200 ms boundary, include sensor jitter, and rebase during motion.
  let previous = tiltedCup;
  for (const jitter of [.06, -.06, .03, 0, 0, 0, 0, 0]) {
    await orient(page, 62 + jitter, 17 - jitter);
    for (let frame = 0; frame < 8; frame++) {
      await page.clock.runFor(16);
      const current = await rect(page, cup);
      assert.ok(distance(current, previous) < .05, 'No step while settling');
      assert.ok(current.x >= neutralCup.x - .02 && current.y >= neutralCup.y - .02, 'No rebound');
      previous = current;
    }
  }
  assert.ok(distance(previous, neutralCup) < .08, 'Held pose becomes neutral');
  await page.clock.runFor(5000);
  assert.ok(distance(await rect(page, cup), neutralCup) < .005);
  assert.ok(distance(await rect(page, stars), neutralSky) < .005);
  await page.clock.runFor(1000);
  assert.deepEqual(await readBackground(), background);

  await orient(page, 55, 10);
  await page.clock.runFor(112);
  const beforeRebase = await rect(page, cup);
  assert.ok(distance(beforeRebase, neutralCup) > .1);
  await page.evaluate(() => Object.defineProperty(screen.orientation, 'angle', {value: 90}));
  await orient(page, 110, 7);
  assert.deepEqual(await rect(page, cup), beforeRebase);
  await page.clock.runFor(16);
  assert.ok(distance(await rect(page, cup), beforeRebase) < .05);
  await page.emulateMedia({reducedMotion: 'reduce'});
  await page.getByRole('button', {name: 'Enable tilt'}).waitFor({state: 'hidden'});
  await orient(page, 112, -10);
  assert.deepEqual(await rect(page, cup), neutralCup);
  assert.deepEqual(await rect(page, stars), neutralSky);
  await page.close();

  const denied = await phone('denied');
  await denied.getByRole('button', {name: 'Enable tilt'}).tap();
  await denied.getByRole('button', {name: 'Tilt blocked'}).waitFor();
  await orient(denied, 50, 13);
  assert.deepEqual(await rect(denied, cup), neutralCup);
  assert.deepEqual(await rect(denied, stars), neutralSky);
  await denied.close();

  const fallback = await browser.newPage();
  await fallback.route('**' + skyPath, route => route.abort());
  await fallback.goto(origin + experiment, {waitUntil: 'networkidle'});
  assert.equal(await fallback.locator('.astral-portal').count(), 0);
  assert.equal(await fallback.getByRole('img', {name: 'Tin Foil FA Cup crest'}).count(), 1);
  await fallback.goto(origin + '/');
  assert.equal(await fallback.locator('.astral-portal').count(), 0);
  assert.equal(await fallback.locator('script[src*="astral-portal"]').count(), 0);
} finally {
  await browser.close();
}

console.log('Astral Portal: owner background, mask bleed, fixed reference plane, opposed parallax, 25% travel, smooth settling, permissions and fallbacks passed.');
