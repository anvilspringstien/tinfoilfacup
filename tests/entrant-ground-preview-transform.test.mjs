import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {buildEntrantGroundPreview} from '../beta/entrant-ground-preview-transform.mjs';
const html=readFileSync(new URL('../beta/clubfinder-beta.html',import.meta.url),'utf8');
const ledger=JSON.parse(readFileSync(new URL('../updater/entrant-home-ground-evidence-2026.json',import.meta.url),'utf8'));
const competition=JSON.parse(readFileSync(new URL('../competition.json',import.meta.url),'utf8'));
test('runtime review of current BETA never promotes a location or freezes source',()=>{
 const {html:preview,additions,already,skipped}=buildEntrantGroundPreview(html,ledger,competition);
 assert.equal(additions.length+already.length,31);
 assert.equal([...additions,...already].filter(x=>x.verification==='unverified').length,31);
 for(const row of [...additions,...already]){
  assert.equal(row.preview_evidence_only,true);
  assert.equal('lat' in row,false);
  assert.equal('lon' in row,false);
 }
 assert.ok(preview.includes('previewAfcBoundary'));
 assert.ok(preview.includes('function findGround(c){'));
 assert.ok(html.includes('function findGround(c){'));
 assert.ok([...additions,...already].some(x=>x.name==='Leyton Orient FC'&&x.postcode==='E10 5NF'));
 assert.ok([...additions,...already].some(x=>x.name==='Rotherham United FC'&&x.postcode==='S60 1FJ'));
 assert.ok(!additions.some(x=>x.name==='Gillingham FC'),'existing ground must not duplicate');
 assert.equal(skipped.length,ledger.clubs.length-(additions.length+already.length));
 const tampered=structuredClone(ledger);
 tampered.safety.verified_location_badge_authorized=true;
 assert.throws(()=>buildEntrantGroundPreview(html,tampered,competition),/safety policy/);
});
