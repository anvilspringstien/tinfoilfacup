// Included only to the generated Radar TEST Worker. This transport has no network fallback.
const HOSTED_GMAIL_SCENARIOS = Object.freeze({
  complete: 'Complete scan with two unique clubs and one draft',
  empty: 'Complete zero',
  unresolved: 'Unresolved introduction on the second page',
  partialDrafts: 'Complete contacted count with partial drafts',
  rejected: 'Provider rejects the synthetic grant (401)',
  delayedRejected: 'Slow rejected grant (401) for cross-tab checks',
  quota: 'Provider rate limit (429)',
  permission: 'Provider permission error (403)',
  network: 'Simulated network failure',
  delayed: 'Slow successful scan for tab and Disconnect checks',
  expiring: 'Synthetic grant expires after 20 seconds',
});
const HOSTED_MESSAGE_PREFIX = '/gmail/v1/users/me/';
const HOSTED_MESSAGES = Object.freeze({
  'a0001': ['Synthetic Oak FC on Tin Foil FA Cup — club details check', ''],
  'a0002': ['Re: Synthetic Oak FC on Tin Foil FA Cup — club details check', ''],
  'a0003': ['Keeping your club details up to date', 'Your current listing:\nClub Synthetic Oak FC'],
  'a0004': ['Keeping your club details up to date', 'Your current listing:\nClub Synthetic Elm FC'],
  'a0005': ['Keeping your club details up to date', 'Synthetic introduction with no usable club identity.'],
});

async function hostedGmailConnect(request, env, session) {
  if (request.method === 'GET') {
    const options = Object.entries(HOSTED_GMAIL_SCENARIOS)
      .map(([key, label]) => '<option value="' + key + '">' + escapeHtml(label) + '</option>').join('');
    return page('Connect synthetic Gmail', '<p>TEST data only. This uses your dashboard session and never contacts Gmail.</p>' +
      '<form method="post" action="/gmail/connect"><label>Fixture <select name="scenario">' + options +
      '</select></label> <button type="submit">Use fixture</button></form><p><a href="/">Return to dashboard</a></p>',
      200, { 'Referrer-Policy': 'same-origin' });
  }
  if (request.headers.get('Origin') !== BASE) return denied();
  const scenario = (await request.formData()).get('scenario');
  if (typeof scenario !== 'string' || !Object.hasOwn(HOSTED_GMAIL_SCENARIOS, scenario)) return denied();
  const seconds = Math.min(scenario === 'expiring' ? 20 : 600, session.exp - time());
  if (seconds <= 5) return denied('Sign in to Mission Control again.');
  const token = await gmailSeal({ kind: 'gmail', aud: BASE, sub: session.sub, exp: time() + seconds, token: scenario }, env);
  const headers = new Headers({ ...HEADERS, Location: BASE + '/' });
  headers.append('Set-Cookie', clearCookie(GMAIL_FLOW_COOKIE));
  headers.append('Set-Cookie', setCookie(GMAIL_COOKIE, token, seconds));
  return new Response(null, { status: 303, headers });
}

async function hostedMailboxFetch(url, { headers }) {
  const scenario = headers.Authorization.slice('Bearer '.length);
  if (url.origin !== 'https://gmail.googleapis.com' || !url.pathname.startsWith(HOSTED_MESSAGE_PREFIX) ||
      !Object.hasOwn(HOSTED_GMAIL_SCENARIOS, scenario)) return new Response(null, { status: 403 });
  if (scenario === 'delayedRejected') await gmailPace(5000);
  if (scenario === 'rejected' || scenario === 'delayedRejected') return new Response(null, { status: 401 });
  if (scenario === 'quota') return new Response(null, { status: 429 });
  if (scenario === 'permission') return new Response(null, { status: 403 });
  if (scenario === 'network') throw new Error('Synthetic network failure');
  if (scenario === 'delayed' && url.searchParams.get('q')?.includes('on Tin Foil FA Cup')) await gmailPace(5000);
  const path = url.pathname.slice(HOSTED_MESSAGE_PREFIX.length);
  const page = url.searchParams.get('pageToken');
  if (scenario === 'empty') return Response.json({ resultSizeEstimate: 0 });
  if (path === 'drafts') return Response.json({
    drafts: [{ id: 'd0001' }],
    ...(scenario === 'partialDrafts' ? { nextPageToken: 'fixture_drafts_2' } : {}),
  });
  if (path === 'messages') {
    const classic = url.searchParams.get('q')?.includes('on Tin Foil FA Cup');
    const ids = classic ? ['a0001', 'a0002']
      : page === 'fixture_current_2' ? [scenario === 'unresolved' ? 'a0005' : 'a0004'] : ['a0003'];
    return Response.json({
      messages: ids.map(id => ({ id })),
      ...(!classic && !page ? { nextPageToken: 'fixture_current_2' } : {}),
    });
  }
  const id = path.split('/')[1];
  if (path === 'messages/' + id && Object.hasOwn(HOSTED_MESSAGES, id)) {
    const [subject, body] = HOSTED_MESSAGES[id];
    return Response.json({
      internalDate: '1795564800000',
      payload: { headers: [{ name: 'Subject', value: subject }], mimeType: 'text/plain',
        body: { data: bytesToB64u(new TextEncoder().encode(body)) } },
    });
  }
  return new Response(null, { status: 404 });
}
