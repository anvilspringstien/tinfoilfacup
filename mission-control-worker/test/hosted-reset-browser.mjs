import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import { createHmac } from 'node:crypto';
import { once } from 'node:events';
import { mkdtempSync, readFileSync, rmSync } from 'node:fs';
import { createServer } from 'node:https';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { test } from 'node:test';
import { chromium } from 'playwright';
import { testOrigin } from '../build-radar-test.mjs';
import worker from '../.radar-test-build/worker.mjs';

const host = '127.0.0.1';
const countKey = 'tffac-mission-control-gmail-count-v1';
const workspaceKey = 'tffac-admin-control-v1';
const credentials = {
  GOOGLE_CLIENT_ID: 'browser-test-client',
  GOOGLE_CLIENT_SECRET: 'unused-test-secret',
  SESSION_SECRET: Buffer.alloc(32, 23).toString('base64'),
};

function sessionCookie() {
  const iat = Math.floor(Date.now() / 1000);
  const payload = Buffer.from(JSON.stringify({
    aud: testOrigin, kind: 'session', sub: 'browser-test', email: 'tinfoilfacup@gmail.com', iat, exp: iat + 3600,
  })).toString('base64url');
  const signature = createHmac('sha256', Buffer.from(credentials.SESSION_SECRET, 'base64'))
    .update(payload).digest('base64url');
  return { name: '__Host-tffac_session', value: payload + '.' + signature, secure: true, httpOnly: true };
}

test('an open workspace reset retains exact confirmation across tabs and fences a late scan', { timeout: 60_000 }, async t => {
  const outbound = t.mock.method(globalThis, 'fetch', () => assert.fail('Worker attempted an external request'));
  const errors = [];
  const arrived = Promise.withResolvers();
  const release = Promise.withResolvers();
  const answered = Promise.withResolvers();
  let holdScan = false;
  let origin;
  const tls = mkdtempSync(join(tmpdir(), 'radar-test-tls-'));
  t.after(() => rmSync(tls, { recursive: true, force: true }));
  const key = join(tls, 'key.pem');
  const cert = join(tls, 'cert.pem');
  execFileSync('openssl', ['req', '-x509', '-newkey', 'rsa:2048', '-nodes', '-days', '1',
    '-subj', '/CN=localhost', '-keyout', key, '-out', cert], { stdio: 'ignore' });
  const server = createServer({ key: readFileSync(key), cert: readFileSync(cert) }, async (request, response) => {
    const held = holdScan && request.url === '/api/gmail/outreach?kind=classic';
    if (held) {
      holdScan = false;
      arrived.resolve();
    }
    try {
      const headers = new Headers(request.headers);
      if (headers.get('origin') === origin) headers.set('origin', testOrigin);
      const chunks = [];
      if (request.method === 'POST') for await (const chunk of request) chunks.push(chunk);
      const result = await worker.fetch(new Request(new URL(request.url, testOrigin), {
        method: request.method, headers, body: chunks.length ? Buffer.concat(chunks) : undefined,
      }), credentials);
      const output = Object.fromEntries(result.headers);
      const cookies = result.headers.getSetCookie();
      if (cookies.length) output['set-cookie'] = cookies;
      if (output.location === testOrigin + '/') output.location = origin + '/';
      const body = Buffer.from(await result.arrayBuffer());
      if (held) await release.promise;
      response.writeHead(result.status, output).end(body);
      if (held) answered.resolve(result.status);
    } catch (error) {
      errors.push(error.message);
      response.writeHead(500).end();
      if (held) answered.resolve(500);
    }
  });
  server.listen(0, host);
  await once(server, 'listening');
  origin = 'https://' + host + ':' + server.address().port;
  t.after(() => { release.resolve(); server.close(); });

  const browser = await chromium.launch({ executablePath: process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH || undefined });
  t.after(() => browser.close());
  const context = await browser.newContext({ serviceWorkers: 'block', ignoreHTTPSErrors: true });
  await context.route('**/*', route => {
    const destination = new URL(route.request().url());
    if (destination.origin === origin) return route.continue();
    if (/gmail|mail\.google\.com/i.test(destination.hostname)) errors.push('Browser attempted access to Gmail');
    return route.fulfill({ status: 503, body: '' });
  });
  await context.addCookies([{ ...sessionCookie(), url: origin }]);

  const scan = page => page.getByRole('button', { name: 'Refresh synthetic Gmail counts' });
  const overview = page => page.locator('.nav[data-nav="overview"]');
  const count = page => page.evaluate(key => JSON.parse(localStorage.getItem(key))?.count ?? null, countKey);
  const tabA = await context.newPage();
  const tabB = await context.newPage();
  for (const tab of [tabA, tabB]) tab.on('pageerror', error => errors.push(error.message));
  await tabA.goto(origin);
  await tabA.locator('.nav[data-nav="ideas"]').click();
  await tabA.getByRole('button', { name: 'A new What If' }).click();
  await tabA.locator('#mission-idea-form input[name="title"]').fill('Existing synthetic idea');
  await tabA.getByRole('button', { name: 'Save in this browser' }).click();
  await tabA.getByRole('heading', { name: 'Existing synthetic idea' }).waitFor();
  await overview(tabA).click();
  await tabA.getByRole('link', { name: 'Connect synthetic Gmail' }).click();
  await tabA.getByRole('combobox', { name: 'Fixture' }).selectOption('delayed');
  await tabA.getByRole('button', { name: 'Use fixture' }).click();
  await tabA.getByRole('heading', { name: 'Synthetic clubs contacted: 2' }).waitFor();
  assert.equal(await count(tabA), 2);

  await tabB.goto(origin);
  await tabB.getByRole('heading', { name: 'Synthetic clubs contacted: 2' }).waitFor();
  // Wait for startup's automatic scan so the manually started scan owns the next fence.
  await tabB.waitForFunction(() => {
    const button = document.querySelector('[data-action="gmail-refresh"]');
    return button && !button.disabled;
  });

  await tabB.locator('.nav[data-nav="sources"]').click();
  await tabB.getByRole('button', { name: 'Reset local workspace' }).click();
  const modal = tabB.getByRole('dialog', { name: 'Reset local workspace' });
  const confirm = modal.locator('#reset-confirm');
  const clear = modal.getByRole('button', { name: 'Clear browser data' });
  await confirm.fill('RESET LOCAL ');
  await clear.click();
  await tabB.getByText('Type RESET LOCAL exactly.').waitFor();
  assert.equal(await count(tabB), 2);
  assert.equal(await tabB.evaluate(key => JSON.parse(localStorage.getItem(key)).ideas.length, workspaceKey), 1);

  await confirm.fill('RESET LOCAL');
  const originalField = await confirm.elementHandle();
  await confirm.evaluate(field => field.setSelectionRange(2, 7));
  await tabA.bringToFront();
  holdScan = true;
  const updatedB = tabB.waitForResponse(response => new URL(response.url()).pathname === '/api/gmail/status');
  await scan(tabA).click();
  await Promise.all([arrived.promise, updatedB]);
  await tabB.bringToFront();
  assert.equal(await confirm.inputValue(), 'RESET LOCAL');
  assert.equal(await confirm.evaluate((field, original) => field === original, originalField), true);
  assert.deepEqual(await confirm.evaluate(field => [field.selectionStart, field.selectionEnd]), [2, 7]);

  const scanAborted = tabA.waitForEvent('requestfailed', {
    predicate: request => new URL(request.url()).pathname === '/api/gmail/outreach',
  });
  await clear.click();
  await modal.waitFor({ state: 'detached' });
  assert.equal(await count(tabB), null);
  assert.equal(await tabB.evaluate(key => JSON.parse(localStorage.getItem(key)).ideas.length, workspaceKey), 0);
  await scanAborted;
  release.resolve();
  assert.equal(await answered.promise, 200, errors.join('\n'));
  await tabA.getByRole('heading', { name: 'Synthetic clubs contacted: Unknown' }).waitFor();
  await overview(tabB).click();
  await tabB.getByRole('heading', { name: 'Synthetic clubs contacted: Unknown' }).waitFor();
  await scan(tabA).waitFor();
  assert.equal(await count(tabA), null);
  assert.equal(await count(tabB), null);

  await tabB.locator('.nav[data-nav="sources"]').click();
  await tabB.getByRole('button', { name: 'Reset local workspace' }).click();
  assert.equal(await confirm.inputValue(), '');
  await confirm.press('Escape');
  await modal.waitFor({ state: 'detached' });

  await tabB.locator('.nav[data-nav="ideas"]').click();
  await tabB.getByRole('button', { name: 'A new What If' }).click();
  const idea = tabB.getByRole('dialog', { name: 'Ideas board editor' });
  await idea.locator('input[name="title"]').fill('Unsaved browser test title');
  await idea.locator('textarea').fill('Unsaved browser test notes');
  await idea.locator('select').selectOption('parked');
  const disconnectedB = tabB.waitForResponse(async response =>
    new URL(response.url()).pathname === '/api/gmail/status' && (await response.json()).connected === false);
  await tabA.getByRole('button', { name: 'Disconnect synthetic Gmail' }).click();
  await disconnectedB;
  assert.equal(await idea.locator('input[name="title"]').inputValue(), 'Unsaved browser test title');
  assert.equal(await idea.locator('textarea').inputValue(), 'Unsaved browser test notes');
  assert.equal(await idea.locator('select').inputValue(), 'parked');
  assert.equal(await tabA.getByRole('link', { name: 'Sign in to Mission Control' }).count(), 0);
  assert.equal(outbound.mock.callCount(), 0);
  assert.deepEqual(errors, []);
});
