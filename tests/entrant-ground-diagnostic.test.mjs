import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const root = new URL('../', import.meta.url);
const page = readFileSync(new URL('beta/entrant-ground-diagnostic.html', root), 'utf8');
const code = readFileSync(new URL('beta/entrant-ground-diagnostic.mjs', root), 'utf8');
test('standalone BETA-only diagnostic with no route injection', () => {
  assert.match(page, /noindex,nofollow,noarchive/);
  assert.match(page, /Evidence only\. Not a verified location/);
  assert.match(page, /entrant-ground-diagnostic\.mjs/);
  assert.doesNotMatch(page, /phone-frame-shed\.js|clubfinder-beta\.html\?stats/);
});
test('diagnostic does not mutate campaign, storage, locations or mileage', () => {
  assert.match(code, /pendingCustodianGround\(input\.value, evidence\)/);
  assert.match(code, /Pending human review — NOT VERIFIED/);
  assert.match(code, /response\.ok/);
  assert.match(code, /verified_location_badge_authorized !== false/);
  assert.doesNotMatch(code, /localStorage|sessionStorage|indexedDB|postMessage|\.setItem\(|\.pushState\(|geolocat|milesFlown|updateGrounds/);
  assert.doesNotMatch(code, /\bfetch\([^)]*,\s*\{\s*method:\s*['"](?:POST|PUT|PATCH|DELETE)/i);
});
test('request uses staged file without sourcing tie venue', () => {
  assert.match(code, /\.\.\/updater\/entrant-home-ground-evidence-2026\.json/);
  assert.doesNotMatch(code, /competition\.json|venue\s*:/);
});
