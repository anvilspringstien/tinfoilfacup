import assert from 'node:assert/strict';
import {chromium, devices} from 'playwright';

const browser = await chromium.launch();
const shed = 'http://127.0.0.1:8765/beta/';
const art = '.astral-art';
const still = '.shed-astral-crest';
const settings = page => page.getByRole('button', {name: 'Crest motion settings'});
const allow = page => page.getByRole('button', {name: 'Enable crest motion'});
const campaign = page => page.locator('.splash-start');

async function mobile(permission, reducedMotion = 'no-preference') {
  const page = await browser.newPage({...devices['iPhone 14'], reducedMotion});
  await page.addInitScript(permission => {
    window.requests = 0;
    if (permission === 'unsupported') {
      window.DeviceOrientationEvent = undefined;
      return;
    }
    DeviceOrientationEvent.requestPermission = async () => {
      if (!navigator.userActivation.isActive) throw new Error('Motion request without interaction');
      window.requests++;
      return permission;
    };
  }, permission);
  return page;
}

const orient = (page, beta, gamma) => page.evaluate(([beta, gamma]) =>
  window.dispatchEvent(new DeviceOrientationEvent('deviceorientation', {beta, gamma})), [beta, gamma]);
const stillVisible = page => page.locator(still).evaluate(el =>
  el.complete && el.naturalWidth === 507 && getComputedStyle(el).opacity === '1');
const requests = page => page.evaluate(() => window.requests);

try {
  for (const configuration of [
    {viewport: {width: 1440, height: 900}},
    devices['iPhone 14'],
    {...devices['iPhone 14'], viewport: {width: 844, height: 390}},
    devices['iPad Pro 11'],
    devices['iPad Pro 11 landscape'],
  ]) {
    const page = await browser.newPage({...configuration, reducedMotion: 'reduce'});
    await page.goto(shed + 'shed-splash.html');
    const measure = () => page.evaluate(() => [
      '.crest-compartment', '.crest', '.room', '.splash-intro', '.splash-message',
      '.splash-start', '.splash-grassroots',
    ].map(selector => document.querySelector(selector).getBoundingClientRect().toJSON()));
    const integrated = await measure();
    assert.ok(await stillVisible(page));
    await page.goto(shed + 'floating-cup.html');
    assert.deepEqual(await measure(), integrated, 'Shed geometry matches the unchanged visual reference');
    await page.close();
  }

  const granted = await mobile('granted');
  const heldRequests = [];
  await granted.route('**/assets/astral-portal/full-sky.webp', route => {
    heldRequests.push(route);
  });
  await granted.goto(shed);
  const grantedSplash = await granted.locator('#phoneApp').elementHandle().then(el => el.contentFrame());
  await grantedSplash.waitForURL('**/beta/shed-splash.html');
  assert.match(await granted.locator('#phoneApp').getAttribute('allow'), /accelerometer 'self'; gyroscope 'self'/);
  assert.ok(await grantedSplash.evaluate(() => !document.featurePolicy ||
    ['accelerometer', 'gyroscope'].every(feature => document.featurePolicy.allowsFeature(feature))));
  assert.ok(await stillVisible(grantedSplash));
  assert.equal(heldRequests.length, 0, 'The sky layers are idle at rest');
  assert.equal(await requests(grantedSplash), 0);
  assert.equal(await allow(grantedSplash).count(), 0);
  assert.equal(await campaign(grantedSplash).textContent(), 'Start Campaign');
  const originalBox = await grantedSplash.locator(still).boundingBox();
  const campaignBox = await campaign(grantedSplash).boundingBox();
  await settings(grantedSplash).tap();
  assert.equal(await requests(grantedSplash), 0, 'Opening settings does not cause a browser prompt');
  await grantedSplash.getByRole('button', {name: 'Keep still'}).tap();
  assert.equal(await requests(grantedSplash), 0);
  await settings(grantedSplash).tap();
  await allow(grantedSplash).tap();
  assert.equal(await requests(grantedSplash), 1);
  await orient(grantedSplash, 45, 0);
  await orient(grantedSplash, 55, 9);
  await grantedSplash.waitForFunction(() => document.querySelector('.astral-portal').style.getPropertyValue('--view-x'));
  assert.ok(await stillVisible(grantedSplash), 'Accepted static crest remains visible while layers are slow');
  assert.deepEqual(await grantedSplash.locator(still).boundingBox(), originalBox);
  assert.deepEqual(await campaign(grantedSplash).boundingBox(), campaignBox);
  assert.equal(heldRequests.length, 1);
  await heldRequests.pop().continue();
  await grantedSplash.locator(art).waitFor();
  assert.equal(await stillVisible(grantedSplash), false);
  assert.deepEqual(await grantedSplash.locator(still).boundingBox(), originalBox);
  await settings(grantedSplash).tap();
  await grantedSplash.getByRole('button', {name: 'Turn off crest motion'}).tap();
  assert.ok(await stillVisible(grantedSplash));
  await granted.reload();
  const reloaded = await granted.locator('#phoneApp').elementHandle().then(el => el.contentFrame());
  await reloaded.waitForURL('**/beta/shed-splash.html');
  await reloaded.locator(still).waitFor();
  assert.ok(await stillVisible(reloaded));
  assert.equal(await requests(reloaded), 0, 'Reload never re-requests permission automatically');
  assert.equal(await allow(reloaded).count(), 0);
  await granted.close();

  const denied = await mobile('denied');
  await denied.goto(shed);
  const deniedSplash = await denied.locator('#phoneApp').elementHandle().then(el => el.contentFrame());
  await deniedSplash.waitForURL('**/beta/shed-splash.html');
  await settings(deniedSplash).tap();
  await allow(deniedSplash).tap();
  await deniedSplash.getByRole('status').getByText('Motion permission was declined.', {exact: false}).waitFor();
  assert.equal(await requests(deniedSplash), 1);
  assert.ok(await stillVisible(deniedSplash));
  assert.equal(await campaign(deniedSplash).getAttribute('href'), 'clubfinder-journey.html');
  await denied.close();

  for (const [permission, reduced] of [['unsupported', 'no-preference'], ['granted', 'reduce']]) {
    const page = await mobile(permission, reduced);
    await page.goto(shed + 'shed-splash.html');
    assert.ok(await stillVisible(page));
    assert.equal(await settings(page).isVisible(), false);
    assert.equal(await requests(page), 0);
    await page.close();
  }

  const unresponsive = await mobile('granted');
  await unresponsive.goto(shed);
  const unresponsiveSplash = await unresponsive.locator('#phoneApp').elementHandle().then(el => el.contentFrame());
  await unresponsiveSplash.waitForURL('**/beta/shed-splash.html');
  await settings(unresponsiveSplash).tap();
  const start = new Date('2026-11-27T14:00:00Z');
  await unresponsive.clock.install({time: start});
  await allow(unresponsiveSplash).tap();
  await orient(unresponsiveSplash, null, null);
  await unresponsive.clock.runFor(2600);
  assert.ok(await stillVisible(unresponsiveSplash));
  assert.equal(await unresponsiveSplash.locator(art).count(), 0);
  await unresponsive.close();

  const desktop = await browser.newPage();
  await desktop.goto(shed + 'shed-splash.html');
  assert.equal(await settings(desktop).count(), 0);
  assert.equal(await desktop.locator(art).count(), 0);
  const box = await desktop.locator(still).boundingBox();
  await desktop.mouse.move(box.x + box.width * .8, box.y + box.height * .8);
  await desktop.locator(art).waitFor();
  assert.equal(await stillVisible(desktop), false);
  await desktop.close();

  for (const extension of ['js', 'css']) {
    const slow = await mobile('granted');
    await slow.route(`**/astral-portal.${extension}?v=shed-paint-20261128`, route => route.abort());
    await slow.goto(shed + 'shed-splash.html', {waitUntil: 'domcontentloaded'});
    await slow.waitForFunction(() => document.querySelector('.shed-astral-crest')?.naturalWidth === 507);
    assert.ok(await stillVisible(slow));
    assert.equal(await slow.locator('.astral-portal').count(), 0);
    assert.equal(await campaign(slow).getAttribute('href'), 'clubfinder-journey.html');
    await slow.close();
  }
} finally {
  await browser.close();
}

console.log('Shed Astral Portal: locked geometry, static first render, motion consent, reload and slow-layer fallbacks passed.');
