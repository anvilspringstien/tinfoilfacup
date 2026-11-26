import { createHash } from 'node:crypto';
import { mkdir, readFile, rename, rm, writeFile } from 'node:fs/promises';
import { pathToFileURL } from 'node:url';

export const testOrigin = 'https://tffac-mission-control-radar-test.anvilspringstien.workers.dev';
const sourceURL = new URL('./worker.mjs', import.meta.url);
const fixtureURL = new URL('./test/hosted-gmail-fixture.mjs', import.meta.url);

function replaceOnce(source, before, after) {
  const parts = source.split(before);
  if (parts.length !== 2) throw new Error('Review hosted candidate integration point: ' + before);
  return parts.join(after);
}

function removeSection(source, start, end) {
  const first = source.indexOf(start);
  const last = source.indexOf(end, first + start.length);
  if (first < 0 || last < 0) throw new Error('Review hosted candidate section: ' + start);
  return replaceOnce(source, source.slice(first, last), '');
}

// The canonical browser script is stored as JSON-escaped string fragments.
const dashboardFragment = value => JSON.stringify(value).slice(1, -1).replaceAll('·', '\\u00b7');

function isolateMailboxUI(source) {
  const drafts = 'https://mail.google.com/mail/u/?authuser=tinfoilfacup%40gmail.com#drafts';
  const edits = [
    [`<a class="btn small" href="${drafts}" rel="noopener noreferrer" target="_blank">Open Gmail drafts</a>`, ''],
    [`<a href="${drafts}" target="_blank" rel="noopener noreferrer">Gmail drafts \${icon('external')}</a>`, ''],
    ["g.connection==='disconnected'?'disconnected':'reconnect'",
      "(g.connection==='disconnected'||(!data.reason&&!g.last))?'disconnected':'reconnect'"],
    ['Mission Control session expired. Sign in again, then reconnect Gmail read-only.',
      'Mission Control session expired. Sign in again, then reconnect synthetic Gmail.'],
    ['Connect Gmail read-only', 'Connect synthetic Gmail'],
    ['Reconnect Gmail read-only', 'Reconnect synthetic Gmail'],
    ['Refresh Gmail counts', 'Refresh synthetic Gmail counts'],
    ['Disconnect Gmail</button>', 'Disconnect synthetic Gmail</button><a class="btn small" href="/gmail/connect">Switch synthetic Gmail fixture</a>'],
    ['GMAIL · READ-ONLY', 'SYNTHETIC GMAIL · TEST FIXTURE'],
    ['<h2>Clubs contacted:', '<h2>Synthetic clubs contacted:'],
    ['Clubs contacted: Unknown', 'Synthetic clubs contacted: Unknown'],
    ['${g.last.count} clubs contacted', '${g.last.count} synthetic clubs contacted'],
    ["metric('Gmail drafts',draftText", "metric('Synthetic Gmail drafts',draftText"],
    ['Mailbox connected. Refresh to check Sent.', 'Synthetic Gmail connected. Refresh to scan test data.'],
    ['Disconnected. Connect synthetic Gmail to check Sent.', 'Synthetic Gmail disconnected. Connect synthetic Gmail to select a fixture.'],
    ['Connect synthetic Gmail to check Sent.', 'Connect synthetic Gmail to select a fixture.'],
    ['Refreshing Gmail Sent history', 'Refreshing synthetic Gmail history'],
    ['Confirming Gmail disconnect', 'Confirming synthetic Gmail disconnect'],
    ['Checking Gmail connection', 'Checking synthetic Gmail connection'],
    ['Checking Gmail Sent history', 'Checking synthetic Gmail history'],
    ['Complete Gmail scan', 'Complete synthetic Gmail scan'],
    ['A complete Gmail scan is needed.', 'A complete synthetic scan is needed.'],
    ['Gmail is disconnected.', 'Synthetic Gmail is disconnected.'],
    ['Gmail permission expired.', 'Synthetic Gmail fixture expired.'],
    ['Gmail rejected the saved permission.', 'The synthetic Gmail provider rejected the test connection.'],
    ['Gmail denied read access. Disconnect and reconnect Gmail. If it persists, check the mailbox policy.',
      'The synthetic Gmail fixture simulated a permission error. Reconnect synthetic Gmail to choose a different fixture.'],
    ['Gmail rate or quota limit reached. Wait before refreshing.', 'The synthetic Gmail fixture simulated a quota limit. Choose a different fixture to retry.'],
    ['Gmail request could not reach Mission Control or Gmail. Check the connection and retry.',
      'The synthetic Gmail request failed. Check the TEST dashboard connection or choose a different fixture.'],
    ['Gmail or Mission Control returned an unusable response.', 'The synthetic Gmail scan returned an unusable response.'],
    ['Gmail connection changed in another tab.', 'Synthetic Gmail connection changed in another tab.'],
    ['refresh, disconnect or clear Gmail data.', 'refresh, disconnect or clear synthetic Gmail data.'],
    ['Check Gmail status and retry.', 'Check the synthetic Gmail status and retry.'],
    ['Gmail access is read-only. Completed counts and timestamps are saved in this browser.',
      'Synthetic mailbox data only. Completed fixture counts and timestamps are saved in this browser.'],
    ['Local approved slots; Gmail must be checked independently.', 'Local TEST workspace approvals only.'],
    ['A Gmail draft is not fetched automatically here. The Gmail connection is separate from this comparison.',
      'Use synthetic copy in this comparison. The test mailbox fixture is separate.'],
    ['External Gmail workflow', 'Local TEST outreach rehearsal'],
    ['Send via approved mailbox', 'Simulate sending in your test notes'],
    ['Email sending is deliberately disabled. After external sending, verify the message in SENT and record the message reference before calling it sent.',
      'Use synthetic draft and reply details. Record a test message reference to rehearse SENT verification.'],
    ['This authorises your prepared copy for external sending. Only a verified SENT reference proves it left the inbox.',
      'This records a local TEST approval. Use fixture references when rehearsing SENT verification.'],
    ['Draft approved. Send externally only after your usual checks; record SENT proof afterward.',
      'TEST draft approved locally. Use a fixture reference to rehearse SENT verification.'],
    ['Record proof that the externally sent message exists.', 'Record a synthetic SENT reference for the rehearsal.'],
    ['Gmail SENT message ID / link', 'Synthetic SENT message ID'],
    ['Message ID or Gmail link', 'Fixture message ID'],
    ['Original Gmail / message reference', 'Original fixture message reference'],
    ['Gmail thread or message reference', 'Fixture thread or message reference'],
    ["return /^https?:$/.test(x.protocol)?x.href:null",
      "return /^https?:$/.test(x.protocol)&&!/(^|\\.)(gmail\\.com|mail\\.google\\.com|gmail\\.googleapis\\.com|gmail\\.google\\.com|inbox\\.google\\.com)\\.?$/i.test(x.hostname)&&!(/(^|\\.)google\\.com\\.?$/i.test(x.hostname)&&/^\\/(mail|gmail)(\\/|$)/i.test(x.pathname))?x.href:null"],
  ];
  source = removeSection(source, '  " {title:\'Outreach & replies\'',
    '  " {title:\'Code, cloud & monitoring\'');
  for (const [before, after] of edits) {
    // Several render branches intentionally reuse the same copy.
    const parts = source.split(dashboardFragment(before));
    if (parts.length < 2) throw new Error('Review hosted mailbox UI: ' + before);
    source = parts.join(dashboardFragment(after));
  }
  if (/(?:https?:)?\/\/(?:mail\.google\.com|gmail\.com|gmail\.google\.com|inbox\.google\.com)\b|mailto:/i.test(source)) {
    throw new Error('Review live mailbox destinations in the hosted dashboard');
  }
  return source;
}

function updateDashboardScriptHashes(source) {
  const fragments = source.match(/const DASHBOARD_HTML = \[([\s\S]*?)\]\.join\(''\);/)?.[1];
  const policy = source.match(/const DASHBOARD_CSP = "[^"\r\n]*?(script-src (?:'sha256-[^']+' ?)+);/)?.[1];
  if (!fragments || !policy) throw new Error('Review hosted dashboard CSP integration');
  const html = JSON.parse('[' + fragments.trim().replace(/,$/, '') + ']').join('');
  const hashes = Array.from(html.matchAll(/<script>([\s\S]*?)<\/script>/g),
    ([, script]) => "'sha256-" + createHash('sha256').update(script).digest('base64') + "'");
  if (hashes.length !== 2) throw new Error('Review the two hosted dashboard scripts');
  return replaceOnce(source, policy, 'script-src ' + hashes.join(' '));
}

export async function hostedSource(source) {
  const fixture = await readFile(fixtureURL, 'utf8');
  const edits = [
    ["const BASE = 'https://tffac-mission-control.anvilspringstien.workers.dev';", "const BASE = " + JSON.stringify(testOrigin) + ";"],
    ['<title>TFFAC Mission Control \\u2014 Private HQ</title>', '<title>TFFAC Mission Control TEST</title>'],
    ['<title>TFFAC Mission Control</title>', '<title>TFFAC Mission Control TEST</title>'],
    ['TIN FOIL FA CUP · HQ', 'TIN FOIL FA CUP · MISSION CONTROL TEST'],
    ['return new Response(DASHBOARD_HTML,', "return new Response(DASHBOARD_HTML.replace('<body>', '<body><div style=\"padding:.55rem 1rem;background:#ffdf89;color:#252014;font-weight:700;text-align:center\">MISSION CONTROL TEST · Synthetic Gmail only</div>'),"],
    ["if (request.method === 'GET' && url.pathname === '/gmail/connect') {", "if (['GET','POST'].includes(request.method) && url.pathname === '/gmail/connect') {"],
    ['return gmailConnect(env,key,session);', 'return hostedGmailConnect(request,env,session);'],
    ["response=await fetch(url,{headers:{Authorization:'Bearer '+token,Accept:'application/json'},redirect:'manual'});",
      "response=await hostedMailboxFetch(url,{headers:{Authorization:'Bearer '+token}});"],
    ["if(!grant){\r\n          const expired=", "if(!grant||!Object.hasOwn(HOSTED_GMAIL_SCENARIOS,grant.token)){\r\n          const expired="],
  ];
  source = removeSection(source, 'async function gmailConnect(', 'class GmailReadError');
  source = removeSection(source, '        const flow=await checked(cookieValue(request,GMAIL_FLOW_COOKIE)',
    '        return callback(request, env, key);');
  for (const [before, after] of edits) source = replaceOnce(source, before, after);
  return '// Generated by build-radar-test.mjs. Review worker.mjs and the hosted fixture.\r\n' + fixture + '\r\n' + updateDashboardScriptHashes(isolateMailboxUI(source));
}

if (process.argv[1] && pathToFileURL(process.argv[1]).href === import.meta.url) {
  const outputDir = new URL('./.radar-test-build/', import.meta.url);
  const candidate = new URL('./worker.mjs', outputDir);
  const temporary = new URL('./worker.tmp', outputDir);
  await mkdir(outputDir, { recursive: true });
  await rm(candidate, { force: true });
  const source = await readFile(sourceURL);
  const manifest = await readFile(new URL('./SHA256SUMS', import.meta.url), 'utf8');
  const expected = createHash('sha256').update(source).digest('hex') + '  worker.mjs\n';
  if (manifest !== expected) throw new Error('Mission Control Worker checksum mismatch');
  await writeFile(temporary, await hostedSource(source.toString('utf8')));
  await rename(temporary, candidate);
}
