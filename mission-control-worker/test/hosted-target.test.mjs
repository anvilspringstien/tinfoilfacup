import assert from 'node:assert/strict';
import { createHash, createHmac } from 'node:crypto';
import { readFile } from 'node:fs/promises';
import { test } from 'node:test';
import { hostedSource, testOrigin } from '../build-radar-test.mjs';
import { browser, inlineScripts } from './dashboard-harness.mjs';

const baseSource = await readFile(new URL('../worker.mjs', import.meta.url), 'utf8');
const generated = await hostedSource(baseSource);
const { default: worker } = await import('data:text/javascript;base64,' + Buffer.from(generated).toString('base64'));
const liveOrigin = 'https://tffac-mission-control.anvilspringstien.workers.dev';
const env = {
  GOOGLE_CLIENT_ID: 'synthetic-test-client',
  GOOGLE_CLIENT_SECRET: 'synthetic-unused-client-secret',
  SESSION_SECRET: Buffer.alloc(32, 43).toString('base64'),
};

function session(aud = testOrigin, { offset = 0, sub = 'synthetic-subject' } = {}) {
  const iat = Math.floor(Date.now() / 1000) + offset;
  const data = Buffer.from(JSON.stringify({
    iat, exp: iat + 3600, aud, kind: 'session', sub, email: 'tinfoilfacup@gmail.com',
  })).toString('base64url');
  return '__Host-tffac_session=' + data + '.' +
    createHmac('sha256', Buffer.from(env.SESSION_SECRET, 'base64')).update(data).digest('base64url');
}

const grantName = '__Host-tffac_gmail';
function grantCookie(response) {
  return response.headers.getSetCookie().find(value => value.startsWith(grantName + '='));
}
function call(path, { method = 'GET', cookies = [], headers = {}, body, bindings = env } = {}) {
  return worker.fetch(new Request(new URL(path, testOrigin), {
    method, headers: { cookie: cookies.join('; '), ...headers }, body,
  }), bindings);
}
function connect(scenario, options = {}) {
  return call('/gmail/connect', { method: 'POST', cookies: [session()], headers: { Origin: testOrigin },
    body: new URLSearchParams({ scenario }), ...options });
}
async function connectCookie(scenario) {
  const r = await connect(scenario);
  assert.equal(r.status, 303);
  assert.equal(r.headers.get('Location'), testOrigin + '/');
  assert.match(grantCookie(r), /^__Host-tffac_gmail=v1\..+; Path=\/; Max-Age=\d+; Secure; HttpOnly; SameSite=Lax$/);
  return grantCookie(r).split(';')[0];
}
function scan(kind, grant, page = '') {
  return call('/api/gmail/outreach?kind=' + kind + '&page=' + page, { cookies: [session(), grant] });
}

test('derives a deterministic, explicit Radar TEST target with no live Gmail transport', async () => {
  assert.equal(generated, await hostedSource(baseSource));
  await assert.rejects(hostedSource(baseSource.replace('return gmailConnect(env,key,session);', '')), /integration point/);
  const config = await readFile(new URL('../wrangler.radar-test.toml', import.meta.url), 'utf8');
  const settings = config.split(/\r?\n/).map(line => line.trim())
    .filter(line => line && !line.startsWith('#'));
  // Allow comments and whitespace. An extra setting, binding or section needs explicit review.
  assert.deepEqual(settings, [
    'name = "tffac-mission-control-radar-test"',
    'main = ".radar-test-build/worker.mjs"',
    'compatibility_date = "2026-11-21"',
    'compatibility_flags = []',
    'workers_dev = true',
    'preview_urls = false',
    'keep_vars = true',
    'no_bundle = true',
    'find_additional_modules = false',
    '[cache]',
    'enabled = false',
    '[observability]',
    'enabled = true',
    '[observability.logs]',
    'enabled = true',
    '[build]',
    'command = "node build-radar-test.mjs"',
    '[[services]]',
    'binding = "OMBUDSMAN_SERVICE"',
    'service = "tffc-ombudsman"',
    'environment = "production"',
    'entrypoint = "default"',
  ]);
  await assert.rejects(hostedSource(baseSource.replace('https://x.com/', 'https://mail.google.com/mail/u/0/#inbox')),
    /live mailbox destinations/);
  assert.doesNotMatch(generated, /async function gmail(?:Connect|Callback)\(/);
  for (const host of [liveOrigin, 'https://preview.example.test', testOrigin.replace('https:', 'http:')]) {
    assert.equal((await call(host + '/login')).status, 403);
  }
  assert.equal((await call('/', { cookies: [session(liveOrigin)] })).status, 403);
  assert.equal((await call('/api/gmail/status', { cookies: [session(testOrigin, { offset: -3601 })] })).status, 401);
  const login = await call('/login');
  const redirect = new URL(login.headers.get('Location'));
  assert.equal(redirect.origin, 'https://accounts.google.com');
  assert.equal(redirect.searchParams.get('scope'), 'openid email');
  assert.equal(redirect.searchParams.get('redirect_uri'), testOrigin + '/oauth/callback');
  assert.equal(redirect.searchParams.get('client_id'), env.GOOGLE_CLIENT_ID);
  const dashboard = await call('/', { cookies: [session()] });
  const html = await dashboard.text();
  assert.match(html, /<title>TFFAC Mission Control TEST<\/title>/);
  assert.match(html, /MISSION CONTROL TEST · Synthetic Gmail only/);
  for (const [, script] of html.matchAll(/<script>([\s\S]*?)<\/script>/g)) {
    assert.ok(dashboard.headers.get('Content-Security-Policy').includes(createHash('sha256').update(script).digest('base64')));
  }
});

test('requires the same authenticated test origin to set a synthetic grant and reports Ombudsman honestly', async () => {
  assert.equal((await call('/gmail/connect')).status, 403);
  assert.equal((await connect('complete', { cookies: [] })).status, 403);
  assert.equal((await connect('complete', { headers: { Origin: liveOrigin } })).status, 403);
  assert.equal((await connect('complete', { headers: { Origin: 'null' } })).status, 403);
  assert.equal((await connect('invalid')).status, 403);
  const page = await call('/gmail/connect', { cookies: [session()] });
  assert.equal(page.status, 200);
  assert.equal(page.headers.get('Referrer-Policy'), 'same-origin');
  assert.match(await page.text(), /Connect synthetic Gmail/);
  const grant = await connectCookie('complete');
  const differentSession = session(testOrigin, { sub: 'other-subject' });
  assert.deepEqual(await (await call('/api/gmail/status', { cookies: [differentSession, grant] })).json(), {
    connected: false, reason: 'gmail_grant_expired',
  });
  const report = await call('/api/ombudsman', { cookies: [session()], bindings: {
    ...env, OMBUDSMAN_SERVICE: { fetch() { assert.fail('No token means no fetch'); } },
  } });
  assert.equal(report.status, 503);
  assert.equal((await report.json()).reason, 'binding_or_token_not_configured');
});

test('uses synthetic provider data through actual pagination, parsing and error classification', async t => {
  const outbound = t.mock.method(globalThis, 'fetch', () => { assert.fail('No external request for a synthetic mailbox'); });
  const grant = await connectCookie('complete');
  const classic = await (await scan('classic', grant)).json();
  assert.deepEqual(classic.rows.map(row => row.club), ['Synthetic Oak FC']);
  assert.equal(classic.audit.repliesSkipped, 1);
  const current = await (await scan('current', grant)).json();
  assert.deepEqual(current.rows.map(row => row.club), ['Synthetic Oak FC']);
  assert.equal(current.next, 'fixture_current_2');
  assert.deepEqual((await (await scan('current', grant, current.next)).json()).rows.map(row => row.club), ['Synthetic Elm FC']);
  const unresolved = await (await scan('current', await connectCookie('unresolved'), current.next)).json();
  assert.equal(unresolved.audit.unparseable, 1);
  for (const kind of ['classic', 'current']) {
    const page = await (await scan(kind, await connectCookie('empty'))).json();
    assert.deepEqual(page.rows, []);
    assert.equal(page.next, null);
    assert.equal(page.audit.listed, 0);
  }
  assert.deepEqual(await (await call('/api/gmail/drafts', { cookies: [session(), await connectCookie('partialDrafts')] })).json(),
    { count: 1, complete: false });
  for (const [scenario, status, error] of [
    ['quota', 429, 'gmail_quota'], ['network', 502, 'gmail_network'],
    ['permission', 403, 'gmail_permission'], ['rejected', 401, 'gmail_grant_rejected'],
  ]) {
    const result = await scan('classic', await connectCookie(scenario));
    assert.equal(result.status, status);
    assert.deepEqual(await result.json(), { error });
    assert.equal(grantCookie(result), undefined);
  }
  assert.equal(outbound.mock.callCount(), 0);
});

test('separate tab requests share grant changes when the browser applies Set-Cookie', async () => {
  let grant = await connectCookie('complete');
  const tab = async (path, options = {}) => {
    const response = await call(path, { cookies: [session(), grant], ...options });
    const cookie = grantCookie(response);
    if (cookie) grant = cookie.split(';')[0];
    return response;
  };
  assert.deepEqual(await (await tab('/api/gmail/status')).json(), { connected: true });
  const disconnected = await tab('/gmail/disconnect', { method: 'POST',
    headers: { Origin: testOrigin, 'X-TFFAC-Action': 'disconnect' } });
  assert.deepEqual(await disconnected.json(), { disconnected: true });
  assert.doesNotMatch(disconnected.headers.getSetCookie().join('\n'), /__Host-tffac_session/);
  assert.deepEqual(await (await tab('/api/gmail/status')).json(), { connected: false });
  grant = await connectCookie('empty');
  assert.deepEqual(await (await tab('/api/gmail/status')).json(), { connected: true });
  assert.equal((await tab('/api/gmail/outreach?kind=classic')).status, 200);
});

test('a late provider 401 cannot delete the new grant established in another tab', async t => {
  t.mock.timers.enable({ apis: ['setTimeout'] });
  const oldGrant = await connectCookie('delayedRejected');
  const firstTabScan = scan('classic', oldGrant);
  const newGrant = await connectCookie('complete');
  assert.notEqual(newGrant, oldGrant);
  assert.deepEqual(await (await call('/api/gmail/status', { cookies: [session(), newGrant] })).json(), { connected: true });
  t.mock.timers.tick(5000);
  const late = await firstTabScan;
  assert.equal(late.status, 401);
  assert.deepEqual(late.headers.getSetCookie(), []);
  const connected = await call('/api/gmail/status', { cookies: [session(), newGrant] });
  assert.deepEqual(await connected.json(), { connected: true });
  const newId = connected.headers.get('X-TFFAC-Gmail-Grant');
  const oldId = (await call('/api/gmail/status', { cookies: [session(), oldGrant] })).headers.get('X-TFFAC-Gmail-Grant');
  assert.match(newId, /^[a-zA-Z0-9_-]{43}$/);
  assert.notEqual(newId, oldId);
  const stale = await call('/gmail/disconnect', { method: 'POST', cookies: [session(), newGrant],
    headers: { Origin: testOrigin, 'X-TFFAC-Action': 'disconnect', 'X-TFFAC-Gmail-Grant': oldId } });
  assert.equal(stale.status, 409);
  assert.deepEqual(stale.headers.getSetCookie(), []);
});

const mailboxLink = /(?:href|action|src)\s*=\s*["'](?:mailto:|(?:https?:)?\/\/(?:mail\.google\.com|gmail\.(?:com|googleapis\.com|google\.com)|inbox\.google\.com)\b)/i;

function assertMailboxIsolation(html) {
  assert.doesNotMatch(html, mailboxLink);
  assert.doesNotMatch(html, /Open Gmail drafts|External Gmail workflow|(?:Connect|Reconnect) Gmail read-only/i);
}

async function renderHostedDashboard(t, { storage } = {}) {
  const outbound = t.mock.method(globalThis, 'fetch', () => { assert.fail('No external request for the hosted UI test'); });
  let sessionCookie = session();
  let grant;
  const response = await call('/', { cookies: [sessionCookie] });
  const html = await response.text();
  const app = browser(testOrigin, inlineScripts(html), storage, async (url, options) => {
    if (url.origin !== testOrigin) return new Response(null, { status: 503 });
    const result = await call(url.pathname + url.search, {
      ...options, headers: { ...options.headers, Origin: testOrigin },
      cookies: [sessionCookie, grant].filter(Boolean),
    });
    if (grantCookie(result)?.includes('Max-Age=0')) grant = undefined;
    return result;
  });
  await app.idle();
  const content = () => app.element('content').innerHTML;
  return { html, app, outbound, content,
    async selectFixture(scenario) {
      const action = /href="(\/gmail\/connect)"/.exec(content());
      assert.ok(action, 'Fixture link must remain on the TEST Worker');
      const fixturePage = await call(action[1], { cookies: [sessionCookie] });
      assert.equal(fixturePage.status, 200);
      const form = await fixturePage.text();
      assert.match(form, /Connect synthetic Gmail/);
      assert.match(form, /<form method="post" action="\/gmail\/connect">/);
      assertMailboxIsolation(form);
      grant = await connectCookie(scenario);
      await app.action('refresh-all');
      await app.idle();
    },
    expireSession() { sessionCookie = session(testOrigin, { offset: -3601 }); },
  };
}

test('rendered TEST views and workspace links cannot open the live mailbox', async t => {
  const { html, app, content, outbound } = await renderHostedDashboard(t);
  assertMailboxIsolation(html);
  const sections = new Set(Array.from(html.matchAll(/data-nav="([a-z]+)"/g), ([, name]) => name));
  assert.ok(sections.has('overview') && sections.has('outreach') && sections.has('links'));
  for (const section of sections) {
    app.navigate(section);
    assert.ok(content().length > 0);
    assertMailboxIsolation(content());
  }
  app.navigate('links');
  assert.match(content(), /GitHub repository/);
  assert.doesNotMatch(content(), /Gmail inbox|Gmail drafts|Gmail sent/);

  app.navigate('outreach');
  app.action('log-incoming-reply');
  const overlay = app.element('overlay').innerHTML;
  assert.match(overlay, /Fixture message ID/);
  assertMailboxIsolation(overlay);
  for (const url of [
    'https://mail.google.com/mail/u/0/#drafts', 'https://GMAIL.com./',
    'https://www.google.com/gmail/', 'https://gmail.googleapis.com/gmail/v1/users/me',
    'mailto:synthetic@example.test',
  ]) {
    assert.doesNotMatch(app.evaluate('urlLink(' + JSON.stringify(url) + ', "Evidence")'), /<a\b/);
  }
  assert.match(app.evaluate('urlLink("https://club.example.test/", "Evidence")'), /href="https:\/\/club\.example\.test\//);
  assert.equal(outbound.mock.callCount(), 0);
});

test('synthetic labels and safe controls survive scan, disconnect, reconnection and both kinds of expiry', async t => {
  const { app, content, outbound, selectFixture, expireSession } = await renderHostedDashboard(t);
  const assertPanel = (...patterns) => {
    for (const pattern of patterns) assert.match(content(), pattern);
    assertMailboxIsolation(content());
  };
  assertPanel(/Connect synthetic Gmail/, /Synthetic clubs contacted: Unknown/);
  app.navigate('outreach');
  assertPanel(/Connect synthetic Gmail/, /Synthetic Gmail drafts/);

  await selectFixture('complete');
  assertPanel(/Synthetic Gmail connected/, /Synthetic clubs contacted: 2/, /Refresh synthetic Gmail counts/,
    /Disconnect synthetic Gmail/, /Switch synthetic Gmail fixture/);
  await app.action('gmail-disconnect');
  assertPanel(/Synthetic Gmail disconnected/, /Connect synthetic Gmail/, /Stale data/);

  await selectFixture('expiring');
  const afterGrantExpiry = Date.now() + 21_000;
  const clock = t.mock.method(Date, 'now', () => afterGrantExpiry);
  await app.action('refresh-all');
  assertPanel(/Synthetic Gmail fixture expired/, /Reconnect synthetic Gmail/, /Synthetic clubs contacted: 2/, /Stale data/);
  clock.mock.restore();

  await selectFixture('empty');
  assertPanel(/Synthetic Gmail connected/, /Synthetic clubs contacted: 0/);
  app.navigate('overview');
  assertPanel(/0 synthetic clubs contacted/, /Synthetic clubs contacted: 0/);
  expireSession();
  await app.action('refresh-all');
  assertPanel(/Mission Control session expired/, /href="\/login">Sign in to Mission Control/, /Stale data/);
  assert.doesNotMatch(content(), /href="\/gmail\/connect"/);
  assert.equal(outbound.mock.callCount(), 0);
});
