import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {entrantIdentityKey, pendingCustodianGround} from '../beta/entrant-ground-evidence.mjs';

const evidence = JSON.parse(readFileSync(new URL('../updater/entrant-home-ground-evidence-2026.json', import.meta.url), 'utf8'));

test('second-round evidence stays explicitly unverified', () => {
  const ro = pendingCustodianGround('Leyton Orient', evidence);
  assert.equal(ro.postcode, 'E10 5NF');
  assert.equal(ro.verified, false);
  assert.equal(ro.coordinates, null);
  assert.equal(ro.locationStatus, 'pending-human-review');
  assert.equal(pendingCustodianGround('Port Vale', evidence).postcode, 'ST6 1AW');
  assert.notEqual(ro.postcode, pendingCustodianGround('Port Vale', evidence).postcode);
});
test('resolved supporter satnav postcodes remain separate from old candidates', () => {
  assert.equal(pendingCustodianGround('Gillingham FC', evidence).postcode, 'ME7 2PE');
  assert.equal(pendingCustodianGround('Rotherham United FC', evidence).postcode, 'S60 1FJ');
});
test('AFC is part of identity, never borrowed from a different club', () => {
  assert.notEqual(entrantIdentityKey('AFC Liverpool'), entrantIdentityKey('Liverpool FC'));
  assert.notEqual(entrantIdentityKey('AFC Bournemouth'), entrantIdentityKey('Bournemouth FC'));
  const isolated = structuredClone(evidence);
  isolated.clubs = [{...isolated.clubs[0], official_identity: 'Liverpool FC'}];
  assert.equal(pendingCustodianGround('AFC Liverpool', isolated), null);
});
test('fail closed on blocked or duplicated identities', () => {
  const isolated = structuredClone(evidence);
  isolated.unresolved_conflicts = [{official_identity:'Leyton Orient FC'}];
  assert.equal(pendingCustodianGround('Leyton Orient', isolated), null);
  isolated.unresolved_conflicts = [];
  isolated.clubs.push({...isolated.clubs.find(x=>x.official_identity==='Leyton Orient FC')});
  assert.equal(pendingCustodianGround('Leyton Orient', isolated), null);
});
test('reject altered safety gates and invalid evidence, never create miles', () => {
  const isolated = structuredClone(evidence);
  isolated.safety.verified_location_badge_authorized = true;
  assert.equal(pendingCustodianGround('Leyton Orient', isolated), null);
  const w = pendingCustodianGround('AFC Wimbledon', evidence);
  assert.equal(w.coordinates, null); // even source-provided coords need separate human approval
  assert.equal('miles' in w, false);
  assert.equal('venue' in w, false);
});
