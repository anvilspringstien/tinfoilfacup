import test from 'node:test';
import assert from 'node:assert/strict';
import { handleRequest, BarryPostOffice, MAILBOX, validate } from '../post-office-worker/worker.mjs';

const id = '7adf428f-bfbc-4191-ace1-729d3dfe2614';
function payload(overrides = {}) { return { id, kind: 'feedback', name: 'Supporter', email: 'supporter@example.org', message: 'The pies were excellent.', website: '', token: 'test-token', ...overrides }; }
function request(value = payload(), origin = 'https://tinfoilfacup.com') { return new Request('https://worker.example/messages', { method: 'POST', headers: { origin, 'content-type': 'application/json', 'CF-Connecting-IP': '192.0.2.1' }, body: JSON.stringify(value) }); }
function memory() {
 const data = new Map(); let writesFail = false;
 return { data, set writesFail(x) { writesFail = x; },
  async get(k) { return structuredClone(data.get(k)); },
  async put(k, v) { if (writesFail) throw Error('storage'); if (typeof k === 'object') { for (const [a,b] of Object.entries(k)) data.set(a, structuredClone(b)); } else data.set(k, structuredClone(v)); },
  async list({ prefix, limit = Infinity }) { return new Map([...data].filter(([k]) => k.startsWith(prefix)).slice(0, limit)); },
  async delete(k) { data.delete(k); }, async setAlarm() {},
 };
}
function setup(send = async () => ({ messageId: 'provider-test' })) {
 const storage = memory(), sent = [];
 const service = new BarryPostOffice({ storage }, { POST_MAIL: { async send(message) { sent.push(message); return send(message); } } });
 const env = { ENABLED: 'true', TURNSTILE_SECRET: 'private-test-secret', ALLOWED_ORIGINS: 'https://tinfoilfacup.com', RATE_LIMITER: { async limit() { return { success: true }; } }, POST_OFFICE: { idFromName: x => x, get: () => service } };
 let verifications = 0;
 const transport = async (_url, opts) => { verifications++; assert.equal(JSON.parse(opts.body).idempotency_key, id); return Response.json({ success: true, hostname: 'tinfoilfacup.com', action: 'post-office' }); };
 return { env, storage, sent, service, transport, get verifications() { return verifications; } };
}
function internal(value) { return new Request('https://post-office.internal/deliver', { method: 'POST', body: JSON.stringify(value) }); }

test('accepts a bounded supporter message; rejects header injection, empty content and honeypot', () => {
 assert.ok(validate(payload()));
 for (const change of [{ email: 'a@example.org\r\nBcc: stolen@example.org' }, { name: 'name\nBcc: x' }, { message: '  ' }, { message: 'a'.repeat(5001) }, { website: 'spam' }, { kind: 'custom-subject' }, { id: 'not-a-uuid' }, { token: '' }]) assert.equal(validate(payload(change)), null);
});
test('requires an exact allowed origin and explicitly enabled service', async () => {
 const s = setup();
 assert.equal((await handleRequest(request(payload(), 'https://tinfoilfacup.com.evil.test'), s.env, s.transport)).status, 403);
 assert.equal((await handleRequest(request(), { ...s.env, ENABLED: 'false' }, s.transport)).status, 503);
 assert.equal(s.verifications, 0); assert.equal(s.sent.length, 0);
});
test('rejects oversized streamed bodies without trusting Content-Length', async () => {
 const s = setup(); const req = request(payload({ message: 'a'.repeat(25000) }));
 assert.equal((await handleRequest(req, s.env, s.transport)).status, 413); assert.equal(s.sent.length, 0);
});
test('rate limit fails closed before challenge verification or delivery', async () => {
 const s = setup(); s.env.RATE_LIMITER.limit = async () => ({ success: false });
 assert.equal((await handleRequest(request(), s.env, s.transport)).status, 429); assert.equal(s.verifications, 0); assert.equal(s.sent.length, 0);
});
test('requires Turnstile success, correct hostname and correct action', async () => {
 for (const check of [{ success: false }, { success: true, hostname: 'evil.test', action: 'post-office' }, { success: true, hostname: 'tinfoilfacup.com', action: 'other' }]) {
  const s = setup(); assert.equal((await handleRequest(request(), s.env, async () => Response.json(check))).status, 400); assert.equal(s.sent.length, 0);
 }
});
test('confirmed acceptance uses fixed mailbox and validated Reply-To; receipt stores no PII', async () => {
 const s = setup(); const response = await handleRequest(request(), s.env, s.transport);
 assert.equal(response.status, 200); assert.deepEqual(await response.json(), { ok: true, id });
 assert.equal(response.headers.get('access-control-allow-origin'), 'https://tinfoilfacup.com');
 assert.equal(s.sent.length, 1); assert.equal(s.sent[0].to, MAILBOX); assert.equal(s.sent[0].replyTo, payload().email);
 const stored = JSON.stringify([...s.storage.data]);
 assert.ok(!stored.includes(payload().email)); assert.ok(!stored.includes(payload().message)); assert.ok(!stored.includes('192.0.2.1'));
});
test('concurrent duplicate submission calls provider once and returns same receipt', async () => {
 const s = setup(); const [a,b] = await Promise.all([handleRequest(request(), s.env, s.transport), handleRequest(request(), s.env, s.transport)]);
 assert.equal(a.status, 200); assert.equal(b.status, 200); assert.equal(s.sent.length, 1);
});
test('provider failure is uncertain and same ID is never sent again', async () => {
 const s = setup(async () => { throw Error('ambiguous upstream connection'); });
 const a = await handleRequest(request(), s.env, s.transport), b = await handleRequest(request(), s.env, s.transport);
 assert.equal((await a.json()).error, 'uncertain'); assert.equal((await b.json()).error, 'uncertain'); assert.equal(s.sent.length, 1);
});
test('reused ID with changed message is rejected', async () => {
 const s = setup(); await s.service.fetch(internal(payload()));
 const b = await s.service.fetch(internal(payload({ message: 'A different message' })));
 assert.equal(b.status, 409); assert.equal(s.sent.length, 1);
});
test('crash after provider acceptance retains sending receipt, never duplicates', async () => {
 let s; s = setup(async () => { s.storage.writesFail = true; });
 assert.equal((await handleRequest(request(), s.env, s.transport)).status, 503);
 s.storage.writesFail = false;
 assert.equal((await handleRequest(request(), s.env, s.transport)).status, 503); assert.equal(s.sent.length, 1);
});
test('global daily cap rejects new submissions before provider call', async () => {
 const s = setup(); await s.storage.put('daily', { day: new Date().toISOString().slice(0,10), count: 100 });
 assert.equal((await handleRequest(request(), s.env, s.transport)).status, 429); assert.equal(s.sent.length, 0);
});
test('receipt cleanup retains recent records and removes those seven days old', async () => {
 const s = setup(); await s.storage.put('receipt:old', { created: Date.now() - 8 * 86400000 }); await s.storage.put('receipt:new', { created: Date.now() });
 await s.service.alarm(); assert.equal(await s.storage.get('receipt:old'), undefined); assert.ok(await s.storage.get('receipt:new'));
});
