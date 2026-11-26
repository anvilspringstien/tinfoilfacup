import assert from 'node:assert/strict';
import { createHash, generateKeyPairSync, sign } from 'node:crypto';
import { readFile } from 'node:fs/promises';
import { afterEach, beforeEach, test } from 'node:test';
import vm from 'node:vm';
import { crc32, deflateRawSync } from 'node:zlib';
import { env, origin, worker } from './test/isolated-runtime.mjs';
import { browser as dashboardBrowser, inlineScripts } from './test/dashboard-harness.mjs';

const browser = (...args) => dashboardBrowser(origin, ...args);

const allowedMailbox = 'tinfoilfacup@gmail.com'; // Already published project contact.
const gmailScope = 'https://www.googleapis.com/auth/gmail.readonly';
const sessionName = '__Host-tffac_session';
const grantName = '__Host-tffac_gmail';
const { publicKey, privateKey } = generateKeyPairSync('rsa', { modulusLength: 2048 });
const syntheticKey = { ...publicKey.export({ format: 'jwk' }), kid: 'mock-google-key', use: 'sig' };
const mailboxToken = 'synthetic-read-only-mailbox-grant';
const tokenEndpoint = 'https://oauth2.googleapis.com/token';
const certEndpoint = 'https://www.googleapis.com/oauth2/v3/certs';
const github = 'https://api.github.com/repos/anvilspringstien/tinfoilfacup';
let mocks, unexpected;

beforeEach(t => {
  mocks = new Map();
  unexpected = [];
  t.mock.method(globalThis, 'fetch', async (input, options = {}) => {
    const url = new URL(input);
    const method = options.method ?? 'GET';
    const route = method + ' ' + url.origin + url.pathname;
    if (!mocks.has(route)) {
      unexpected.push(route);
      throw new Error('Unexpected upstream request');
    }
    return mocks.get(route)(url, options);
  });
});
afterEach(() => assert.deepEqual(unexpected, []));

function call(path, { method = 'GET', cookies = [], headers = {}, bindings = env } = {}) {
  return worker.fetch(new Request(new URL(path, origin), {
    method, headers: { ...headers, cookie: cookies.join('; ') },
  }), bindings);
}

function cookie(response, name, age) {
  const raw = response.headers.getSetCookie().find(item => item.startsWith(name + '='));
  assert.ok(raw, 'missing ' + name);
  assert.match(raw, /; Path=\/; Max-Age=\d+; Secure; HttpOnly; SameSite=Lax$/);
  if (age !== undefined) assert.match(raw, new RegExp('; Max-Age=' + age + ';'));
  return raw.split(';')[0];
}

function mockGoogle(authURL, { gmail = false, email = allowedMailbox } = {}) {
  const now = Math.floor(Date.now() / 1000);
  const parts = [
    { alg: 'RS256', kid: syntheticKey.kid },
    { iss: 'https://accounts.google.com', aud: env.GOOGLE_CLIENT_ID, iat: now, exp: now + 300,
      nonce: authURL.searchParams.get('nonce'), email, email_verified: true, sub: 'synthetic-account-id' },
  ].map(value => Buffer.from(JSON.stringify(value)).toString('base64url'));
  const unsigned = parts.join('.');
  const idToken = unsigned + '.' + sign('sha256', Buffer.from(unsigned), privateKey).toString('base64url');
  mocks.set('GET ' + certEndpoint, (_url, options) => {
    assert.equal(options.redirect, 'manual');
    return Response.json({ keys: [syntheticKey] });
  });
  mocks.set('POST ' + tokenEndpoint, (_url, options) => {
    assert.equal(options.redirect, 'manual');
    const body = new URLSearchParams(options.body);
    assert.equal(body.get('code'), 'mock-authorization-code');
    assert.equal(body.get('client_secret'), env.GOOGLE_CLIENT_SECRET);
    assert.equal(body.get('redirect_uri'), origin + '/oauth/callback');
    assert.equal(createHash('sha256').update(body.get('code_verifier')).digest('base64url'),
                 authURL.searchParams.get('code_challenge'));
    return Response.json({ id_token: idToken, access_token: mailboxToken,
      scope: gmail ? 'openid email ' + gmailScope : 'openid email', expires_in: 600 });
  });
}

async function authorize({ session, email } = {}) {
  const start = await call(session ? '/gmail/connect' : '/login', { cookies: session ? [session] : [] });
  assert.equal(start.status, 302);
  const url = new URL(start.headers.get('Location'));
  assert.equal(url.origin, 'https://accounts.google.com');
  assert.equal(url.searchParams.get('scope'), session ? 'openid email ' + gmailScope : 'openid email');
  assert.equal(url.searchParams.get('code_challenge_method'), 'S256');
  const flow = cookie(start, session ? '__Host-tffac_gmail_flow' : '__Host-tffac_oauth', 600);
  mockGoogle(url, { gmail: Boolean(session), email });
  const query = new URLSearchParams({ code: 'mock-authorization-code', state: url.searchParams.get('state') });
  return call('/oauth/callback?' + query, { cookies: session ? [flow, session] : [flow] });
}

async function signIn() {
  const response = await authorize();
  assert.equal(response.status, 303);
  assert.equal(response.headers.get('Location'), origin + '/');
  return cookie(response, sessionName, 3600);
}

test('matches the SHA-256 manifest for the current Worker bytes', async () => {
  const original = await readFile(new URL('./worker.mjs', import.meta.url));
  const manifest = await readFile(new URL('./SHA256SUMS', import.meta.url), 'utf8');
  assert.equal(manifest, createHash('sha256').update(original).digest('hex') + '  worker.mjs\n');
});

test('requires the exact host, an authenticated account and a valid session', async () => {
  for (const path of ['/', '/gmail/connect', '/api/radar/latest', '/api/ombudsman',
                      'https://preview.example.test/login',
                      'https://tffac-mission-control-radar-test.anvilspringstien.workers.dev/login']) {
    assert.equal((await call(path)).status, 403, path);
  }
  const otherOrigin = origin === 'https://mission-control.test'
    ? 'https://tffac-mission-control.anvilspringstien.workers.dev'
    : 'https://mission-control.test';
  assert.equal((await call(otherOrigin + '/login')).status, 403);
  assert.equal((await call('/api/gmail/status')).status, 401);
  assert.equal((await call('/', { bindings: {} })).status, 503);
  assert.equal((await call('/', { cookies: [sessionName + '=invalid-session'] })).status, 403);
  assert.equal((await call('/oauth/callback?code=mock-authorization-code&state=wrong')).status, 403);
  assert.equal((await authorize({ email: 'unapproved@example.test' })).status, 403);
  const session = await signIn();
  const dashboard = await call('/', { cookies: [session] });
  assert.equal(dashboard.status, 200);
  assert.match(dashboard.headers.get('Cache-Control'), /no-store/);
  assert.equal(dashboard.headers.get('Vary'), 'Cookie');
  const html = await dashboard.text();
  const scripts = inlineScripts(html);
  assert.equal(scripts.length, 2);
  const csp = dashboard.headers.get('Content-Security-Policy');
  for (const script of scripts) {
    assert.ok(csp.includes("'sha256-" + createHash('sha256').update(script).digest('base64') + "'"));
  }
  assert.ok(!html.includes(mailboxToken));
});

test('denies service writes and retains same-origin session controls', async () => {
  const session = await signIn();
  for (const [method, path] of [
    ['POST', '/api/gmail/send'], ['POST', '/api/gmail/drafts'], ['DELETE', '/api/gmail/drafts'],
    ['POST', '/api/radar/latest'], ['PUT', '/api/ombudsman'], ['POST', '/api/github/merge'],
    ['OPTIONS', '/api/ombudsman'], ['GET', '/deploy'],
  ]) {
    assert.equal((await call(path, { method, cookies: [session] })).status, 403, method + ' ' + path);
  }
  assert.equal((await call('/logout', { method: 'POST', cookies: [session],
    headers: { Origin: 'https://example.test' } })).status, 403);
  const logout = await call('/logout', { method: 'POST', cookies: [session], headers: { Origin: origin } });
  assert.equal(logout.status, 303);
  cookie(logout, sessionName, 0);
  cookie(logout, grantName, 0);
});

test('Gmail reads only with separate consent and returns minimal outreach and draft data', async t => {
  // Gmail's pacing is separate from the response contract under test.
  t.mock.method(globalThis, 'setTimeout', callback => queueMicrotask(callback));
  const session = await signIn();
  assert.deepEqual(await (await call('/api/gmail/status', { cookies: [session] })).json(), { connected: false });
  assert.equal((await call('/api/gmail/drafts', { cookies: [session] })).status, 401);
  const granted = await authorize({ session });
  assert.equal(granted.status, 303);
  const grant = cookie(granted, grantName);
  assert.match(grant, /=v1\./);
  assert.ok(!grant.includes(mailboxToken));
  const cookies = [session, grant];
  assert.deepEqual(await (await call('/api/gmail/status', { cookies })).json(), { connected: true });

  const api = 'GET https://gmail.googleapis.com/gmail/v1/users/me/';
  function gmailRoute(path, result) {
    mocks.set(api + path, (url, options) => {
      assert.equal(options.headers.Authorization, 'Bearer ' + mailboxToken);
      assert.equal(options.redirect, 'manual');
      return result(url);
    });
  }
  gmailRoute('messages', url => {
    assert.match(url.searchParams.get('q'), /^in:sent /);
    assert.equal(url.searchParams.get('maxResults'), '20');
    return Response.json({ messages: [{ id: 'abc123' }, { id: 'abc456' }, { id: 'abc789' }, { id: 'unusable' }],
      nextPageToken: 'next-page' });
  });
  for (const [id, subject] of [['abc123', 'Keeping your club details up to date'], ['abc456', 'Re: Keeping your club details up to date']]) {
    gmailRoute('messages/' + id, url => {
      assert.equal(url.searchParams.get('format'), 'full');
      return Response.json({ internalDate: '1789556400000', payload: {
        mimeType: 'multipart/alternative', headers: [{ name: 'Subject', value: subject }],
        parts: [{ mimeType: 'text/plain', body: {
          data: Buffer.from('Your current listing:\nClub Example Athletic FC\nMock private body').toString('base64url'),
        } }],
      } });
    });
  }
  gmailRoute('messages/abc789', () => Response.json({ payload: {
    headers: [{ name: 'Subject', value: 'Keeping your club details up to date' }],
    mimeType: 'text/plain',
  } }));
  const outreach = await call('/api/gmail/outreach?kind=current', { cookies });
  assert.equal(outreach.status, 200);
  const count = await outreach.json();
  assert.equal(count.next, 'next-page');
  assert.equal(count.audit.repliesSkipped, 1);
  assert.equal(count.audit.unparseable, 1);
  assert.equal(count.audit.bodiesMissing, 1);
  assert.equal(count.audit.idRejected, 1);
  assert.deepEqual(count.rows.map(row => row.club), ['Example Athletic FC']);
  assert.deepEqual(Object.keys(count.rows[0]).sort(), ['club', 'day']);

  gmailRoute('drafts', () => Response.json({ drafts: [{ id: 'synthetic-draft' }], nextPageToken: 'more' }));
  assert.deepEqual(await (await call('/api/gmail/drafts', { cookies })).json(), { count: 1, complete: false });
  gmailRoute('drafts', () => Response.json({ detail: 'Mock provider body' }, { status: 401 }));
  const failed = await call('/api/gmail/drafts', { cookies });
  assert.equal(failed.status, 401);
  assert.deepEqual(await failed.json(), { error: 'gmail_grant_rejected' });
  assert.deepEqual(failed.headers.getSetCookie(), []);
  assert.ok(!failed.headers.getSetCookie().some(item => item.startsWith(sessionName + '=')));

  assert.equal((await call('/gmail/disconnect', { method: 'POST', cookies, headers: { Origin: origin } })).status, 403);
  assert.equal((await call('/gmail/disconnect', { method: 'POST', cookies,
    headers: { Origin: 'null', 'X-TFFAC-Action': 'disconnect' } })).status, 403);
  const disconnect = await call('/gmail/disconnect', { method: 'POST', cookies,
    headers: { Origin: origin, 'X-TFFAC-Action': 'disconnect' } });
  assert.equal(disconnect.status, 200);
  cookie(disconnect, grantName, 0);
});

test('distinguishes local Gmail grant expiry and Mission Control session expiry', async t => {
  let now = Date.now();
  t.mock.method(Date, 'now', () => now);
  const session = await signIn();
  const grant = cookie(await authorize({ session }), grantName);
  const cookies = [session, grant];
  now += 600_000;
  const status = await call('/api/gmail/status', { cookies });
  assert.deepEqual(await status.json(), { connected: false, reason: 'gmail_grant_expired' });
  assert.deepEqual(status.headers.getSetCookie(), []);
  assert.deepEqual(await (await call('/api/gmail/outreach?kind=current', { cookies })).json(),
    { error: 'gmail_grant_expired' });
  assert.equal((await call('/', { cookies: [session] })).status, 200);

  now += 3_001_000;
  const expired = await call('/api/gmail/status', { cookies });
  assert.equal(expired.status, 401);
  assert.deepEqual(await expired.json(), { error: 'sign_in_required' });
  const disconnect = await call('/gmail/disconnect', { method: 'POST', cookies,
    headers: { Origin: origin, 'X-TFFAC-Action': 'disconnect' } });
  assert.equal(disconnect.status, 401);
  assert.deepEqual(await disconnect.json(), { error: 'sign_in_required' });
  assert.deepEqual(disconnect.headers.getSetCookie(), []);
});

test('classifies provider, permission, quota, network and malformed results without leaking details', async () => {
  const session = await signIn();
  const grant = cookie(await authorize({ session }), grantName);
  const cookies = [session, grant];
  const list = 'GET https://gmail.googleapis.com/gmail/v1/users/me/messages';
  for (const [code, expectedStatus, reply] of [
    ['gmail_permission', 403, () => Response.json({ error: { errors: [{ reason: 'insufficientPermissions' }], message: 'private' } }, { status: 403 })],
    ['gmail_quota', 429, () => Response.json({ error: { errors: [{ reason: 'userRateLimitExceeded' }] } }, { status: 403 })],
    ['gmail_quota', 429, () => new Response(null, { status: 429 })],
    ['gmail_network', 502, () => { throw new TypeError('private network detail'); }],
    ['gmail_upstream', 502, () => new Response('private upstream detail', { status: 503 })],
    ['gmail_upstream', 502, () => Response.json({})],
    ['gmail_upstream', 502, () => Response.json({ messages: [], resultSizeEstimate: 1 })],
    ['gmail_upstream', 502, () => Response.json({ messages: [], nextPageToken: 'unexpected-page' })],
  ]) {
    mocks.set(list, reply);
    const response = await call('/api/gmail/outreach?kind=classic', { cookies });
    assert.equal(response.status, expectedStatus);
    assert.deepEqual(await response.json(), { error: code });
    assert.deepEqual(response.headers.getSetCookie(), []);
  }
  mocks.set(list, () => new Response(null, { status: 401 }));
  const rejected = await call('/api/gmail/outreach?kind=classic', { cookies });
  assert.equal(rejected.status, 401);
  assert.deepEqual(await rejected.json(), { error: 'gmail_grant_rejected' });
  assert.deepEqual(rejected.headers.getSetCookie(), []);

  mocks.set(list, () => Response.json({ resultSizeEstimate: 0 }));
  const zero = await call('/api/gmail/outreach?kind=classic', { cookies });
  assert.equal(zero.status, 200);
  assert.deepEqual(await zero.json(), outreachPage());
});

function radarArchive(report) {
  const data = Buffer.from(JSON.stringify(report));
  const compressed = deflateRawSync(data);
  const name = Buffer.from('club-entry-radar.json');
  const local = Buffer.alloc(30), directory = Buffer.alloc(46), end = Buffer.alloc(22);
  local.writeUInt32LE(0x04034b50); directory.writeUInt32LE(0x02014b50); end.writeUInt32LE(0x06054b50);
  local.writeUInt16LE(20, 4); directory.writeUInt16LE(20, 4); directory.writeUInt16LE(20, 6);
  for (const [buffer, position] of [[local, 8], [directory, 10]]) {
    buffer.writeUInt16LE(8, position);
    buffer.writeUInt32LE(crc32(data), position + 6);
    buffer.writeUInt32LE(compressed.length, position + 10);
    buffer.writeUInt32LE(data.length, position + 14);
    buffer.writeUInt16LE(name.length, position + 18);
  }
  end.writeUInt16LE(1, 8); end.writeUInt16LE(1, 10);
  end.writeUInt32LE(directory.length + name.length, 12);
  end.writeUInt32LE(local.length + name.length + compressed.length, 16);
  return Buffer.concat([local, name, compressed, directory, name, end]);
}

test('Radar reads the eligible main dispatch and keeps the GitHub token off the archive host', async () => {
  const session = await signIn();
  const cookies = [session];
  const off = await call('/api/radar/latest', { cookies, bindings: { ...env, GITHUB_RADAR_TOKEN: undefined } });
  assert.equal(off.status, 503);
  const run = { id: 14, head_branch: 'main', conclusion: 'success', status: 'completed', event: 'workflow_dispatch' };
  const authorized = (_url, options) => {
    assert.equal(options.headers.Authorization, 'Bearer ' + env.GITHUB_RADAR_TOKEN);
    assert.equal(options.redirect, 'manual');
  };
  mocks.set('GET ' + github + '/actions/workflows/club-entry-radar.yml/runs', (url, options) => {
    authorized(url, options);
    assert.equal(url.searchParams.get('branch'), 'main');
    return Response.json({ workflow_runs: [{ ...run, id: 15, event: 'pull_request' }, run] });
  });
  mocks.set('GET ' + github + '/actions/runs/14/artifacts', (url, options) => {
    authorized(url, options);
    return Response.json({ artifacts: [{ id: 71, name: 'club-entry-radar-readonly', expired: false, workflow_run: { id: 14 } }] });
  });
  const report = { schema_version: 1, read_only: true, automatic_ground_promotion: false,
    fixture_venues_used_as_home_grounds: false, canonical_source: 'competition.json', rounds: [] };
  const download = 'https://mock-archive.blob.core.windows.net/radar.zip';
  mocks.set('GET ' + github + '/actions/artifacts/71/zip', (url, options) => {
    assert.equal(options.headers.Authorization, 'Bearer ' + env.GITHUB_RADAR_TOKEN);
    assert.equal(options.redirect, 'manual');
    return Response.redirect(download, 302);
  });
  mocks.set('GET ' + download, (_url, options) => {
    assert.equal(options.headers, undefined);
    assert.equal(options.redirect, 'manual');
    return new Response(radarArchive(report));
  });
  const response = await call('/api/radar/latest', { cookies });
  assert.equal(response.status, 200);
  const value = await response.json();
  assert.deepEqual(value.report, report);
  assert.equal(value.provenance.run_id, 14);
  assert.equal(value.provenance.artifact_id, 71);
  mocks.set('GET ' + download, () => new Response(radarArchive({ ...report, read_only: false })));
  const invalid = await call('/api/radar/latest', { cookies });
  assert.equal(invalid.status, 502);
  assert.deepEqual(await invalid.json(), { error: 'radar_source_unavailable' });
});

test('Ombudsman relies on the existing read-only binding and preserves stale status', async () => {
  const session = await signIn();
  const cookies = [session];
  const absent = await call('/api/ombudsman', { cookies });
  assert.equal(absent.status, 503);
  assert.equal((await absent.json()).state, 'unknown');
  let checkedAt = new Date(Date.now() - 60_000).toISOString();
  const binding = {
    async fetch(request) {
      assert.equal(request.method, 'GET');
      assert.equal(request.url, 'https://ombudsman.internal/health');
      assert.equal(request.headers.get('Authorization'), 'Bearer ' + env.OMBUDSMAN_STATUS_TOKEN);
      return Response.json({ state: 'healthy', checked_at: checkedAt, ignored: 'mock internal detail',
        checks: { results: { state: 'healthy', run_id: 42, ignored: 'mock internal result' } } });
    },
  };
  const options = { cookies, bindings: { ...env, OMBUDSMAN_SERVICE: binding } };
  const response = await call('/api/ombudsman', options);
  assert.equal(response.status, 200);
  const health = await response.json();
  assert.equal(health.fresh, true);
  assert.equal(health.source, 'tffc-ombudsman');
  assert.deepEqual(health.checks.results, { state: 'healthy', reason: 'not_reported', run_id: 42 });
  assert.ok(!('ignored' in health));
  checkedAt = new Date(Date.now() - 91 * 60_000).toISOString();
  assert.equal((await (await call('/api/ombudsman', options)).json()).fresh, false);
});

test('the dashboard navigates locally and restores a browser-local workspace', async () => {
  const session = await signIn();
  const html = await (await call('/', { cookies: [session] })).text();
  const scripts = inlineScripts(html);
  const storage = new Map();
  const app = browser(scripts, storage);
  for (const [section, label] of [
    ['overview', 'MISSION CONTROL'], ['clubfinder', 'CLUBFINDER AUDIT'], ['radar', 'CLUB ENTRY RADAR'],
    ['outreach', 'OUTREACH DESK'], ['ombudsman', 'OMBUDSMAN'], ['pullrequests', 'GITHUB PR QUEUE'],
    ['approvals', 'REVIEW LEDGER'], ['sources', 'SOURCES & SAFETY'], ['links', 'LINKS DESK'],
    ['ideas', 'IDEAS BOARD'],
  ]) {
    assert.match(html, new RegExp('data-nav="' + section + '"'));
    app.navigate(section);
    assert.equal(app.element('crumb').textContent, label);
    assert.ok(app.element('content').innerHTML.length > 0);
    if (section === 'links') assert.match(app.element('content').innerHTML, /target="_blank" rel="noopener noreferrer"/);
  }
  const backup = { kind: 'TFFAC_ADMIN_WORKSPACE', version: 1, outreach: [], proposals: [],
    history: [{ id: 'mock-entry', label: 'Synthetic review note' }] };
  app.sandbox.fileInput = { files: [{ size: 128, text: async () => JSON.stringify(backup) }] };
  await vm.runInContext("doImport(fileInput, 'workspace')", app.sandbox);
  assert.deepEqual(JSON.parse(storage.get('tffac-admin-control-v1')).history, backup.history);
  assert.equal(app.element('crumb').textContent, 'SOURCES & SAFETY');

  const reopened = browser(scripts, storage);
  assert.equal(vm.runInContext('workspace.history[0].label', reopened.sandbox), 'Synthetic review note');
  await new Promise(setImmediate);
  const allowed = new Set([origin, 'https://api.github.com', 'https://raw.githubusercontent.com']);
  assert.ok(app.requests.length > 0);
  assert.ok([...app.requests, ...reopened.requests].every(req => req.method === 'GET' && allowed.has(req.url.origin)));
});

const countKey = 'tffac-mission-control-gmail-count-v1';
const mockDrafts = { count: 2, complete: true };

function outreachPage(clubs = [], { next = null, repliesSkipped = 0, unparseable = 0, idRejected = 0 } = {}) {
  const fetched = clubs.length + repliesSkipped + unparseable;
  return {
    next,
    rows: clubs.map(club => ({ club, day: null })),
    audit: { listed: fetched + idRejected, fetched, accepted: clubs.length, repliesSkipped, subjectSkipped: 0,
      unparseable, bodiesMissing: unparseable, idRejected },
  };
}

async function dashboardScripts(session = null) {
  const sessionCookie = session ?? await signIn();
  return inlineScripts(await (await call('/', { cookies: [sessionCookie] })).text());
}

function dashboardFixture(scripts, storage = new Map(), { connected = true, classic, current, drafts, locks } = {}) {
  const fixture = {
    status: () => Response.json({ connected }),
    scan: url => Response.json((url.searchParams.get('kind') === 'classic' ? classic : current) ?? outreachPage()),
    drafts: () => Response.json(drafts ?? mockDrafts),
    disconnect: () => Response.json({ disconnected: true }),
    grant: 'g'.repeat(43),
  };
  const app = browser(scripts, storage, (url, options) => {
    if (url.origin !== origin) return new Response(null, { status: 503 });
    if (url.pathname === '/api/gmail/status') {
      const response = fixture.status();
      response.headers.set('X-TFFAC-Gmail-Grant', fixture.grant);
      return response;
    }
    if (url.pathname === '/api/gmail/outreach') return fixture.scan(url, options);
    if (url.pathname === '/api/gmail/drafts') return fixture.drafts();
    if (url.pathname === '/gmail/disconnect') return fixture.disconnect(options);
    return new Response(null, { status: 503 });
  }, locks);
  return { app, fixture, storage };
}

function panel(app) {
  app.navigate('outreach');
  return app.element('content').innerHTML;
}

test('the delegated Disconnect click clears the Worker grant with exact-origin headers and confirms status', async () => {
  const session = await signIn();
  const grant = cookie(await authorize({ session }), grantName);
  const scripts = await dashboardScripts(session);
  const jar = new Map([[sessionName, session], [grantName, grant]]);
  const app = browser(scripts, new Map(), async (url, options) => {
    if (url.origin !== origin) return new Response(null, { status: 503 });
    if (url.pathname === '/api/gmail/outreach') return Response.json(outreachPage(['Example Town FC']));
    if (url.pathname === '/api/gmail/drafts') return Response.json(mockDrafts);
    if (!['/gmail/disconnect', '/api/gmail/status'].includes(url.pathname)) return new Response(null, { status: 503 });
    assert.equal(options.credentials, 'same-origin');
    let headers;
    if (url.pathname === '/gmail/disconnect') {
      assert.equal(options.method, 'POST');
      assert.equal(options.mode, 'same-origin');
      assert.equal(options.redirect, 'error');
      assert.equal(options.referrerPolicy, 'same-origin');
      // Model the user agent's automatic Origin header. Node fetch does not add it.
      headers = { ...options.headers, Origin: origin };
    }
    const response = await call(url.href, { method: options.method, cookies: [...jar.values()], headers });
    for (const header of response.headers.getSetCookie()) {
      if (/; Max-Age=0;/.test(header)) jar.delete(header.split('=')[0]);
    }
    return response;
  });
  await app.idle();
  assert.match(panel(app), /Clubs contacted: 1/);
  const requestIndex = app.requests.length;
  await app.action('gmail-disconnect');
  assert.deepEqual(app.requests.slice(requestIndex).map(r => [r.method, r.url.pathname]),
    [['POST', '/gmail/disconnect'], ['GET', '/api/gmail/status']]);
  assert.equal(jar.has(grantName), false);
  assert.equal(jar.get(sessionName), session);
  assert.match(panel(app), /Disconnected\./);
  assert.match(panel(app), /Stale data/);
  assert.equal((await call('/', { cookies: [...jar.values()] })).status, 200);
});

test('the delegated Disconnect click requires both acknowledgement and an absent grant', async () => {
  const scripts = await dashboardScripts();
  const { app, fixture } = dashboardFixture(scripts);
  await app.idle();
  fixture.disconnect = () => Response.json({ disconnected: false });
  await app.action('gmail-disconnect');
  assert.match(panel(app), /Disconnect could not be confirmed/);
  assert.doesNotMatch(panel(app), /Disconnected\./);

  fixture.disconnect = () => Response.json({ disconnected: true });
  await app.action('gmail-disconnect');
  assert.match(panel(app), /Disconnect could not be confirmed/);
  assert.doesNotMatch(panel(app), /Disconnected\./);

  fixture.disconnect = () => Response.json({ error: 'sign_in_required' }, { status: 401 });
  await app.action('gmail-disconnect');
  assert.match(panel(app), /Mission Control session expired/);
  assert.match(panel(app), /href="\/login">Sign in to Mission Control/);
});

test('expiry and read failures give distinct dashboard instructions', async () => {
  const scripts = await dashboardScripts();
  const { app, fixture } = dashboardFixture(scripts);
  await app.idle();
  for (const [code, status, message] of [
    ['gmail_permission', 403, /Gmail denied read access/],
    ['gmail_quota', 429, /Gmail rate or quota limit/],
    ['gmail_network', 502, /could not reach Mission Control/],
    ['gmail_upstream', 502, /returned an unusable response/],
    ['gmail_grant_rejected', 401, /Gmail rejected the saved permission/],
  ]) {
    fixture.scan = () => Response.json({ error: code }, { status });
    await app.action('gmail-refresh');
    assert.match(panel(app), message);
    assert.match(panel(app), /Stale data/);
  }
  assert.match(panel(app), /Reconnect Gmail read-only/);

  const expiredGrant = dashboardFixture(scripts, new Map(), { connected: false });
  await expiredGrant.app.idle();
  expiredGrant.fixture.status = () => Response.json({ connected: false, reason: 'gmail_grant_expired' });
  await expiredGrant.app.evaluate('missionGmailStatus()');
  assert.match(panel(expiredGrant.app), /Gmail permission expired/);
  assert.match(panel(expiredGrant.app), /href="\/gmail\/connect">Reconnect Gmail read-only/);

  const expiredSession = dashboardFixture(scripts, new Map(), { connected: false });
  await expiredSession.app.idle();
  expiredSession.fixture.status = () => Response.json({ error: 'sign_in_required' }, { status: 401 });
  await expiredSession.app.evaluate('missionGmailStatus()');
  assert.match(panel(expiredSession.app), /Mission Control session expired/);
  assert.doesNotMatch(panel(expiredSession.app), /href="\/gmail\/connect"/);
});

test('complete zero, incomplete first scans and draft listings retain their distinct meanings', async () => {
  const scripts = await dashboardScripts();
  const zero = dashboardFixture(scripts, new Map(), { drafts: { count: 500, complete: false } });
  await zero.app.idle();
  assert.equal(JSON.parse(zero.storage.get(countKey)).count, 0);
  assert.match(panel(zero.app), /Clubs contacted: 0/);
  assert.match(panel(zero.app), /CURRENT/);
  assert.match(panel(zero.app), /Partial listing checked/);
  assert.doesNotMatch(panel(zero.app), /metric-val">500/);

  for (const page of [
    outreachPage([], { idRejected: 1 }),
    outreachPage([], { unparseable: 1 }),
    { ...outreachPage(), audit: { ...outreachPage().audit, listed: 1 } },
    outreachPage(['Example FC'], { next: 'repeated-token' }),
  ]) {
    const first = dashboardFixture(scripts, new Map(), { current: page });
    await first.app.idle();
    assert.equal(first.storage.has(countKey), false);
    assert.match(panel(first.app), /Clubs contacted: Unknown/);
    assert.match(panel(first.app), /Scan incomplete/);
    assert.match(panel(first.app), /metric-val">2/); // Drafts succeed independently.
  }
});

test('only a reconciled two-family scan replaces the saved count and timestamp', async () => {
  const scripts = await dashboardScripts();
  const { app, fixture, storage } = dashboardFixture(scripts);
  fixture.scan = url => {
    const [kind, page] = [url.searchParams.get('kind'), url.searchParams.get('page')];
    if (kind === 'classic' && !page) return Response.json(outreachPage(['Example Town FC'], { next: 'page-two' }));
    if (kind === 'classic' && page === 'page-two') return Response.json(outreachPage(['United FC'], { repliesSkipped: 1 }));
    assert.equal(kind, 'current');
    return Response.json(outreachPage(['Example Town', 'Town Athletic FC']));
  };
  await app.idle();
  const saved = storage.get(countKey);
  const snapshot = JSON.parse(saved);
  assert.equal(snapshot.count, 3);
  assert.deepEqual(Object.keys(snapshot).sort(), ['checkedAt', 'count', 'version']);
  assert.equal(new Date(snapshot.checkedAt).toISOString(), snapshot.checkedAt);
  assert.match(panel(app), /Combined: 3 unique · 1 repeated keys/);
  assert.ok(app.requests.some(r => r.url.searchParams.get('page') === 'page-two'));

  fixture.scan = url => url.searchParams.get('kind') === 'classic'
    ? Response.json(outreachPage(['Partial Record FC']))
    : Response.json({ error: 'gmail_network' }, { status: 502 });
  await app.action('gmail-refresh');
  assert.equal(storage.get(countKey), saved);
  assert.match(panel(app), /Clubs contacted: 3/);
  assert.match(panel(app), /Stale data/);
  assert.ok(panel(app).includes(snapshot.checkedAt));

  const reloaded = dashboardFixture(scripts, storage, { connected: false });
  await reloaded.app.idle();
  assert.match(panel(reloaded.app), /Clubs contacted: 3/);
  assert.match(panel(reloaded.app), /Stale data/);
  assert.ok(panel(reloaded.app).includes(snapshot.checkedAt));

  const reconnected = dashboardFixture(scripts, storage, {
    classic: outreachPage(['New Club FC']), current: outreachPage(),
  });
  await reconnected.app.idle();
  assert.match(panel(reconnected.app), /Clubs contacted: 1/);
  assert.match(panel(reconnected.app), /CURRENT/);
  reconnected.app.action('reset-local');
  reconnected.app.element('reset-confirm').value = 'RESET LOCAL';
  await reconnected.app.action('confirm-reset');
  assert.equal(storage.has(countKey), false);
  assert.match(panel(reconnected.app), /Clubs contacted: Unknown/);
});

test('disconnect and clear-data invalidate pending refreshes even if a reply arrives after abort', async () => {
  const scripts = await dashboardScripts();
  const { app, fixture, storage } = dashboardFixture(scripts, new Map(), { classic: outreachPage(['Saved FC']) });
  await app.idle();
  const saved = storage.get(countKey);

  async function pauseRefresh() {
    let resume;
    fixture.scan = () => new Promise(resolve => { resume = resolve; });
    const pending = app.action('gmail-refresh');
    await new Promise(setImmediate);
    const scanRequest = app.requests.at(-1);
    assert.match(panel(app), /REFRESHING/);
    return { pending, scanRequest, complete: () => resume(Response.json(outreachPage(['Obsolete FC', 'Another FC']))) };
  }

  const duringDisconnect = await pauseRefresh();
  fixture.status = () => Response.json({ connected: false });
  await app.action('gmail-disconnect');
  assert.equal(duringDisconnect.scanRequest.options.signal.aborted, true);
  assert.equal(storage.get(countKey), saved);
  assert.match(panel(app), /Disconnected\./);

  fixture.status = () => Response.json({ connected: true });
  await app.evaluate('missionGmailStatus()');
  fixture.scan = () => Response.json(outreachPage(['New Connection FC']));
  await app.action('gmail-refresh');
  const reconnected = storage.get(countKey);
  assert.match(panel(app), /CURRENT/);
  duringDisconnect.complete();
  await duringDisconnect.pending;
  assert.equal(storage.get(countKey), reconnected);
  assert.match(panel(app), /Clubs contacted: 1/);

  const duringClear = await pauseRefresh();
  app.element('reset-confirm').value = 'RESET LOCAL';
  await app.action('confirm-reset');
  assert.equal(duringClear.scanRequest.options.signal.aborted, true);
  duringClear.complete();
  await duringClear.pending;
  assert.equal(storage.has(countKey), false);
  assert.match(panel(app), /Clubs contacted: Unknown/);
});

test('shared scan, Disconnect and Clear Data boundaries fence obsolete results even before storage events', async () => {
  const scripts = await dashboardScripts();
  const storage = new Map();
  let tail = Promise.resolve();
  const locks = {
    request(_name, task) {
      const result = tail.then(task);
      tail = result.catch(() => {});
      return result;
    },
  };
  const a = dashboardFixture(scripts, storage, { classic: outreachPage(['Saved FC']), locks });
  await a.app.idle();
  const b = dashboardFixture(scripts, storage, { classic: outreachPage(['Recent FC']), locks });
  await b.app.idle();
  const sync = 'tffac-mission-control-gmail-sync-v1';
  a.app.storageEvent(sync);
  await a.app.idle();

  async function holdScan() {
    let release;
    a.fixture.scan = () => new Promise(resolve => { release = resolve; });
    a.app.storageEvent(sync);
    await a.app.idle();
    const pending = a.app.action('gmail-refresh');
    await new Promise(setImmediate);
    assert.ok(release, 'scan did not reach the provider');
    return async (response = Response.json(outreachPage(['Old One FC', 'Old Two FC']))) => {
      release(response);
      await pending;
    };
  }

  const newer = await holdScan();
  b.app.storageEvent(sync);
  await b.app.idle();
  b.fixture.scan = () => Response.json(outreachPage(['Recent FC', 'Other FC', 'Third FC']));
  await b.app.action('gmail-refresh');
  const saved = storage.get(countKey);
  assert.equal(JSON.parse(saved).count, 3);
  await newer();
  assert.equal(storage.get(countKey), saved);
  a.app.storageEvent(sync);
  await a.app.idle();
  assert.match(panel(a.app), /Clubs contacted: 3/);
  assert.match(panel(a.app), /Stale data/);

  const oldGrant = await holdScan();
  b.fixture.grant = a.fixture.grant = 'n'.repeat(43);
  b.app.storageEvent(sync);
  await b.app.idle();
  await oldGrant(Response.json({ error: 'gmail_grant_rejected' }, { status: 401 }));
  assert.equal(storage.get(countKey), saved);
  assert.equal(JSON.parse(storage.get(sync)).rejected, false);
  assert.match(panel(b.app), /Mailbox connected/);

  const disconnect = await holdScan();
  b.fixture.status = a.fixture.status = () => Response.json({ connected: false });
  await b.app.action('gmail-disconnect');
  await disconnect();
  assert.equal(storage.get(countKey), saved);
  a.app.storageEvent(sync);
  await a.app.idle();
  assert.match(panel(a.app), /Reconnect Gmail/);

  a.fixture.status = b.fixture.status = () => Response.json({ connected: true });
  await a.app.evaluate('missionGmailStatus()');
  const clear = await holdScan();
  b.app.element('reset-confirm').value = 'RESET LOCAL';
  await b.app.action('confirm-reset');
  await clear();
  a.app.storageEvent(sync);
  await a.app.idle();
  assert.equal(storage.has(countKey), false);
  assert.match(panel(a.app), /Clubs contacted: Unknown/);
});
