// Dedicated contact service. Never shares Ombudsman secrets, quotas or storage.
export const MAILBOX = 'tinfoilfacup@gmail.com';
const SENDER = 'barry@post.tinfoilfacup.com';
const MAX_BYTES = 24576;
const DAY = 86400000;

function reply(data, status = 200, origin) {
  return new Response(JSON.stringify(data), { status, headers: {
    'content-type': 'application/json; charset=utf-8', 'cache-control': 'no-store',
    ...(origin ? { 'access-control-allow-origin': origin, vary: 'Origin' } : {}),
  }});
}
function origins(env) {
  return String(env.ALLOWED_ORIGINS || '').split(',').map(x => x.trim()).filter(Boolean);
}
export function validate(value) {
  if (!value || typeof value !== 'object' || Array.isArray(value)) return null;
  const { id, kind, name = '', email, message, website = '', token } = value;
  if (!/^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i.test(id || '')) return null;
  if (!['feedback', 'issue'].includes(kind)) return null;
  if (typeof name !== 'string' || name.length > 80 || /[\x00-\x1f\x7f]/.test(name)) return null;
  if (typeof email !== 'string' || email.length > 254 || !/^[a-z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?\.[a-z]{2,}$/i.test(email)) return null;
  if (typeof message !== 'string' || !message.trim() || message.length > 5000 || /[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]/.test(message)) return null;
  if (typeof website !== 'string' || website !== '') return null;
  if (typeof token !== 'string' || !token || token.length > 2048) return null;
  return { id: id.toLowerCase(), kind, name: name.trim(), email, message: message.trim(), token };
}
async function boundedJson(request) {
  if (!request.body) throw new Error('empty');
  const reader = request.body.getReader(); let size = 0; const chunks = [];
  try {
    while (true) {
      const { done, value } = await reader.read(); if (done) break;
      size += value.byteLength;
      if (size > MAX_BYTES) { await reader.cancel(); throw new Error('too-large'); }
      chunks.push(value);
    }
  } finally { reader.releaseLock(); }
  const bytes = new Uint8Array(size); let offset = 0;
  for (const chunk of chunks) { bytes.set(chunk, offset); offset += chunk.byteLength; }
  return JSON.parse(new TextDecoder('utf-8', { fatal: true }).decode(bytes));
}
export async function handleRequest(request, env, transport = fetch) {
  const path = new URL(request.url).pathname;
  if (path === '/health' && request.method === 'GET') return reply({ service: 'barrys-post-office', ready: env.ENABLED === 'true' && !!env.TURNSTILE_SECRET && !!env.POST_OFFICE && !!env.RATE_LIMITER });
  const origin = request.headers.get('origin');
  if (!origin || !origins(env).includes(origin)) return reply({ error: 'origin' }, 403);
  if (path !== '/messages') return reply({ error: 'not-found' }, 404, origin);
  if (request.method === 'OPTIONS') return new Response(null, { status: 204, headers: {
    'access-control-allow-origin': origin, 'access-control-allow-methods': 'POST, OPTIONS',
    'access-control-allow-headers': 'content-type', 'access-control-max-age': '3600', vary: 'Origin',
  }});
  if (request.method !== 'POST') return reply({ error: 'method' }, 405, origin);
  if (env.ENABLED !== 'true' || !env.TURNSTILE_SECRET || !env.POST_OFFICE || !env.RATE_LIMITER) return reply({ error: 'closed' }, 503, origin);
  if ((request.headers.get('content-type') || '').split(';')[0].trim().toLowerCase() !== 'application/json') return reply({ error: 'content-type' }, 415, origin);
  if (Number(request.headers.get('content-length')) > MAX_BYTES) return reply({ error: 'too-large' }, 413, origin);
  const ip = request.headers.get('CF-Connecting-IP');
  if (!ip) return reply({ error: 'unavailable' }, 503, origin);
  try {
    if (!(await env.RATE_LIMITER.limit({ key: ip })).success) return reply({ error: 'rate-limit' }, 429, origin);
  } catch { return reply({ error: 'unavailable' }, 503, origin); }
  let message;
  try { message = validate(await boundedJson(request)); }
  catch (error) { return reply({ error: error.message === 'too-large' ? 'too-large' : 'invalid' }, error.message === 'too-large' ? 413 : 400, origin); }
  if (!message) return reply({ error: 'invalid' }, 400, origin);
  try {
    const verification = await transport('https://challenges.cloudflare.com/turnstile/v0/siteverify', {
      method: 'POST', headers: { 'content-type': 'application/json' }, signal: AbortSignal.timeout(8000),
      body: JSON.stringify({ secret: env.TURNSTILE_SECRET, response: message.token, remoteip: ip, idempotency_key: message.id }),
    });
    if (!verification.ok) return reply({ error: 'verification-unavailable' }, 503, origin);
    const check = await verification.json();
    if (check.success !== true || check.action !== 'post-office' || check.hostname !== new URL(origin).hostname) return reply({ error: 'verification' }, 400, origin);
  } catch { return reply({ error: 'verification-unavailable' }, 503, origin); }
  // Only validated fields go to the mailbox; never cookies, location or Campaign data.
  delete message.token;
  try {
    const stub = env.POST_OFFICE.get(env.POST_OFFICE.idFromName('barry-mail-counter'));
    const result = await stub.fetch(new Request('https://post-office.internal/deliver', { method: 'POST', body: JSON.stringify(message) }));
    return reply(await result.json(), result.status, origin);
  } catch { return reply({ error: 'uncertain', id: message.id }, 503, origin); }
}
export default { fetch(request, env) { return handleRequest(request, env); } };

// Serialises delivery and persists receipts before calling the mail provider.
// A crash or ambiguous provider error is held for review, never sent again.
export class BarryPostOffice {
  constructor(ctx, env) { this.ctx = ctx; this.env = env; this.tail = Promise.resolve(); }
  fetch(request) {
    const task = this.tail.then(() => this.deliver(request));
    this.tail = task.catch(() => {}); return task;
  }
  async deliver(request) {
    if (new URL(request.url).pathname !== '/deliver' || request.method !== 'POST') return reply({ error: 'not-found' }, 404);
    const data = await request.json();
    const valid = validate({ ...data, token: 'internal' });
    if (!valid) return reply({ error: 'invalid' }, 400);
    const { id, kind, name, email, message } = valid;
    const digest = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(JSON.stringify([kind, name, email, message])));
    const fingerprint = Array.from(new Uint8Array(digest), x => x.toString(16).padStart(2, '0')).join('');
    const key = 'receipt:' + id, storage = this.ctx.storage, previous = await storage.get(key);
    if (previous) {
      if (previous.fingerprint !== fingerprint) return reply({ error: 'id-conflict' }, 409);
      return previous.status === 'sent' ? reply({ ok: true, id }) : reply({ error: 'uncertain', id }, 503);
    }
    if (!this.env.POST_MAIL?.send) return reply({ error: 'closed' }, 503);
    const now = Date.now(), day = new Date(now).toISOString().slice(0, 10);
    const counts = await storage.get('daily') || { day, count: 0 };
    if (counts.day !== day) { counts.day = day; counts.count = 0; }
    if (counts.count >= 100) return reply({ error: 'rate-limit' }, 429);
    // Retain no email address, message or IP in durable storage.
    counts.count++;
    await storage.put({ daily: counts, [key]: { fingerprint, status: 'sending', created: now } });
    await storage.setAlarm(now + DAY);
    const subject = 'Tin Foil FA Cup — ' + (kind === 'issue' ? 'Issue Report' : 'Feedback') + ' — Barry’s Post Office';
    const text = 'Barry’s Post Office\n\n' + (kind === 'issue' ? 'Report an Issue' : 'Feedback') +
      '\nFrom: ' + (name || 'A Tin Foil FA Cup supporter') + '\nReply email: ' + email +
      '\nDelivery reference: ' + id + '\n\n' + message;
    try {
      await this.env.POST_MAIL.send({ to: MAILBOX, from: { email: SENDER, name: 'Barry’s Post Office | Tin Foil FA Cup' }, replyTo: email, subject, text });
    } catch {
      await storage.put(key, { fingerprint, status: 'uncertain', created: now });
      return reply({ error: 'uncertain', id }, 503);
    }
    await storage.put(key, { fingerprint, status: 'sent', created: now });
    return reply({ ok: true, id });
  }
  async alarm() {
    const entries = await this.ctx.storage.list({ prefix: 'receipt:' });
    for (const [key, receipt] of entries) if (Date.now() - receipt.created >= 7 * DAY) await this.ctx.storage.delete(key);
    if ((await this.ctx.storage.list({ prefix: 'receipt:', limit: 1 })).size) await this.ctx.storage.setAlarm(Date.now() + DAY);
  }
}
