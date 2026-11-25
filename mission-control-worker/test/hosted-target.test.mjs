import assert from 'node:assert/strict';
import { createHash, createHmac } from 'node:crypto';
import { readFile } from 'node:fs/promises';
import { test } from 'node:test';
import { hostedSource, testOrigin } from '../build-radar-test.mjs';

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
  assert.match(config, /^name = "tffac-mission-control-radar-test"$/m);
  assert.match(config, /^compatibility_date = "2026-11-21"$/m);
  assert.match(config, /^keep_vars = true$/m);
  assert.doesNotMatch(config, /^\[vars\]|^\[env\.|^routes?\s*=|OMBUDSMAN_STATUS_TOKEN/m);
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
    assert.equal(Boolean(grantCookie(result)), scenario === 'rejected');
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

test('a late provider 401 still sends a deletion after another tab reconnects', async t => {
  // Characterise the existing shared-cookie race for the hosted acceptance gate.
  t.mock.timers.enable({ apis: ['setTimeout'] });
  const oldGrant = await connectCookie('delayedRejected');
  const firstTabScan = scan('classic', oldGrant);
  const newGrant = await connectCookie('complete');
  assert.notEqual(newGrant, oldGrant);
  assert.deepEqual(await (await call('/api/gmail/status', { cookies: [session(), newGrant] })).json(), { connected: true });
  t.mock.timers.tick(5000);
  const late = await firstTabScan;
  assert.equal(late.status, 401);
  assert.match(grantCookie(late), /^__Host-tffac_gmail=; Path=\/; Max-Age=0;/);
});
