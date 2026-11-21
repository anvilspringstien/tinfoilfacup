import {chromium} from 'playwright';
import assert from 'node:assert/strict';
import {mkdirSync} from 'node:fs';

const BASE = process.env.TFFC_DIAGNOSTIC_URL || 'http://127.0.0.1:8765/beta/entrant-ground-diagnostic.html';
const contexts = [
  {name: 'big-boy', width: 1365, height: 860, isMobile: false},
  {name: 'iphone', width: 390, height: 844, isMobile: true},
  {name: 'ipad-portrait', width: 820, height: 1180, isMobile: true}
];
const expected = [
  {query: 'Leyton Orient FC', ground: 'BetWright Stadium', postcode: 'E10 5NF'},
  {query: 'Gillingham FC', ground: 'MEMS Priestfield Stadium', postcode: 'ME7 2PE'},
  {query: 'Rotherham United FC', ground: 'AESSEAL New York Stadium', postcode: 'S60 1FJ'}
];
mkdirSync('/tmp/tffc-ground-diagnostic', {recursive:true});
const browser = await chromium.launch({headless:true});
try {
  for (const viewport of contexts) {
    const context = await browser.newContext({
      viewport:{width:viewport.width,height:viewport.height},
      isMobile:viewport.isMobile,
      hasTouch:viewport.isMobile
    });
    const page = await context.newPage();
    const badRequests = [];
    page.on('response', r => { if (r.status() >= 400) badRequests.push(r.url()); });
    await page.goto(BASE, {waitUntil:'networkidle'});
    await page.getByText('Evidence loaded. Enter an exact club name to inspect its pending record.').waitFor();
    const button = page.getByRole('button', {name: 'Inspect pending evidence'});
    assert.equal(await button.isDisabled(), false);
    const initialStorage = await page.evaluate(() => ({
      local: {...localStorage}, session: {...sessionStorage}
    }));
    for (const row of expected) {
      await page.locator('#club').fill(row.query);
      await button.click();
      const result = await page.locator('#result').innerText();
      assert.ok(result.includes(row.ground), row.query + ' ground mismatch');
      assert.ok(result.includes(row.postcode), row.query + ' postcode mismatch');
      assert.ok(result.includes('NOT VERIFIED'), 'must not imply location verification');
      assert.ok(!result.includes('Miles Flown'), 'must not expose computed mileage');
    }
    await page.locator('#club').fill('AFC Liverpool');
    await button.click();
    assert.match(await page.locator('#result').innerText(), /No unambiguous pending ground evidence/);
    await page.locator('#club').fill('Liverpool FC');
    await button.click();
    assert.match(await page.locator('#result').innerText(), /No unambiguous pending ground evidence/);
    await page.locator('#club').fill('Leyton Orient FC');
    await button.click();
    assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1), true,
      viewport.name + ' must not overflow horizontally');
    const finalStorage = await page.evaluate(() => ({
      local: {...localStorage}, session: {...sessionStorage}
    }));
    assert.deepEqual(finalStorage, initialStorage, 'diagnostic must not modify stored Campaign state');
    assert.deepEqual(badRequests, [], viewport.name + ' had failed requests');
    await page.screenshot({path:'/tmp/tffc-ground-diagnostic/' + viewport.name + '.png', fullPage:true});
    console.log('PASS', viewport.name, '- Leyton Orient, Gillingham, Rotherham, AFC identity, no storage writes');
    await context.close();
  }
} finally {
  await browser.close();
}
