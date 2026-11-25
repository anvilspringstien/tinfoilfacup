// Test-only: the Worker uses mocked upstreams and the browser uses a fresh Map.
import { readFile } from 'node:fs/promises';

const recoveredOrigin = 'https://tffac-mission-control.anvilspringstien.workers.dev';
const targets = Object.freeze({
  baseline: recoveredOrigin,
  isolated: 'https://mission-control.test',
});
const target = process.env.TFFAC_MC_TEST_TARGET ?? 'baseline';
if (!Object.hasOwn(targets, target)) throw new Error('Unsupported Mission Control test target');
export const origin = targets[target];
export const env = Object.freeze({
  GOOGLE_CLIENT_ID: 'synthetic-client',
  GOOGLE_CLIENT_SECRET: 'synthetic-secret',
  SESSION_SECRET: Buffer.alloc(32, 17).toString('base64'),
  GITHUB_RADAR_TOKEN: 'synthetic-actions-read-token',
  OMBUDSMAN_STATUS_TOKEN: 'synthetic-health-token',
});

// Install the fallback before importing application code. Individual tests
// replace it with an explicit per-route mock and restore it afterwards.
globalThis.fetch = async () => { throw new Error('Unmocked fetch is disabled in Mission Control tests'); };

const workerURL = new URL('../worker.mjs', import.meta.url);
async function loadWorker() {
  if (target === 'baseline') return (await import(workerURL)).default;
  const source = await readFile(workerURL, 'utf8');
  const original = `const BASE = '${recoveredOrigin}';`;
  const parts = source.split(original);
  if (parts.length !== 2) throw new Error('Expected one exact Mission Control origin declaration');
  // Only this in-memory test module gets the reserved .test origin. No
  // deployable copy, local server, real OAuth registration or shared storage.
  const isolated = parts.join(`const BASE = '${origin}';`);
  return (await import('data:text/javascript;base64,' + Buffer.from(isolated).toString('base64'))).default;
}
export const worker = await loadWorker();
