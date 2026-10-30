import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {clubDetails} from '../beta/club-details-model.mjs';
const queue=JSON.parse(readFileSync('updater/club_website_audit_queue.json'));
const competition=JSON.parse(readFileSync('competition.json'));
const current=queue.rows.filter(r=>r.current_competition);
assert.equal(current.length,80);
for(const row of current){const d=clubDetails(row.club,queue,competition);assert.equal(d.club,row.club);assert.ok(d.fixture,'Published fixture for '+row.club);assert.ok(d.website?.startsWith('https://'));}
const york=clubDetails('York City',queue,competition);
assert.equal(york.fixture.venue.postcode,'YO32 9AF');assert.equal(york.fixture.home,'York City');assert.equal(york.fixture.away,'Northampton Town');
const reading=clubDetails('Reading',queue,competition);assert.equal(reading.fixture.home,'Peterborough United');assert.equal(reading.fixture.venue.postcode,'PE2 8AL','away-club review must show actual match postcode');
assert.throws(()=>clubDetails('<img src=x onerror=alert(1)>',queue,competition),/unique published listing/);
assert.throws(()=>clubDetails('',queue,competition),/link in your email/);
assert.throws(()=>clubDetails('York City',{rows:[...queue.rows,current.find(r=>r.club==='York City')]},competition),/unique/);
assert.equal(clubDetails('York City',queue,{fixtures:{}}).fixture,null);
assert.equal(clubDetails('York City',{rows:[{club:'York City',website:'javascript:alert(1)'}]},competition).website,null);
console.log('PASS: all 80 current clubs resolve; York and away-match venues; missing/ambiguous clubs and unsafe URLs rejected.');
