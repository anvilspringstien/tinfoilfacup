import assert from 'node:assert/strict';
import { createHash, generateKeyPairSync, sign } from 'node:crypto';
import { readFile } from 'node:fs/promises';
import { afterEach, beforeEach, test } from 'node:test';
import vm from 'node:vm';
import { crc32, deflateRawSync } from 'node:zlib';
import { env, origin, worker } from './test/isolated-runtime.mjs';

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
    return Response.json({ messages: [{ id: 'abc123' }, { id: 'abc456' }], nextPageToken: 'next-page' });
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
  const outreach = await call('/api/gmail/outreach?kind=current', { cookies });
  assert.equal(outreach.status, 200);
  const count = await outreach.json();
  assert.equal(count.next, 'next-page');
  assert.equal(count.audit.repliesSkipped, 1);
  assert.deepEqual(count.rows.map(row => row.club), ['Example Athletic FC']);
  assert.deepEqual(Object.keys(count.rows[0]).sort(), ['club', 'day']);

  gmailRoute('drafts', () => Response.json({ drafts: [{ id: 'synthetic-draft' }], nextPageToken: 'more' }));
  assert.deepEqual(await (await call('/api/gmail/drafts', { cookies })).json(), { count: 1, complete: false });
  gmailRoute('drafts', () => Response.json({ detail: 'Mock provider body' }, { status: 401 }));
  const failed = await call('/api/gmail/drafts', { cookies });
  assert.equal(failed.status, 502);
  assert.deepEqual(await failed.json(), { error: 'draft_list_unavailable' });

  assert.equal((await call('/gmail/disconnect', { method: 'POST', cookies, headers: { Origin: origin } })).status, 403);
  const disconnect = await call('/gmail/disconnect', { method: 'POST', cookies,
    headers: { Origin: origin, 'X-TFFAC-Action': 'disconnect' } });
  assert.equal(disconnect.status, 200);
  cookie(disconnect, grantName, 0);
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

function inlineScripts(html) {
  return Array.from(html.matchAll(/<script(?:\s[^>]*)?>([\s\S]*?)<\/script>/g), match => match[1]);
}

function browser(scripts, storage = new Map()) {
  const listeners = new Map();
  const elements = new Map();
  const requests = [];
  const node = () => ({ innerHTML: '', textContent: '', style: {}, append() {} });
  const getElementById = id => {
    if (!elements.has(id)) elements.set(id, node());
    return elements.get(id);
  };
  const sandbox = vm.createContext({
    document: { body: node(), getElementById, querySelectorAll: () => [], createElement: node,
      addEventListener: (event, handler) => listeners.set(event, handler) },
    localStorage: { getItem: key => storage.get(key) ?? null, setItem: (key, value) => storage.set(key, value) },
    window: { scrollTo() {} }, URL, AbortController, crypto,
    fetch: async (input, options = {}) => {
      requests.push({ url: new URL(input, origin), method: options.method ?? 'GET' });
      return new Response(null, { status: 503 });
    },
    setTimeout: () => 1, clearTimeout() {},
  });
  for (const script of scripts) vm.runInContext(script, sandbox);
  return { requests, sandbox, element: getElementById, navigate: target => {
    listeners.get('click')({ target: { closest: selector => selector === '[data-nav]' ? { dataset: { nav: target } } : null } });
  }};
}

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
