import assert from 'node:assert/strict';
import fs from 'node:fs';
import {clubCampaigns} from '../beta/club-details-campaigns.mjs';
import {campaignEngine} from '../beta/club-details-engine.mjs';
const c=JSON.parse(fs.readFileSync(new URL('../competition.json',import.meta.url)));
const engine=campaignEngine(c);
// Compare the reverse shortlist against a full authoritative-engine traversal.
const all=engine.origins.map(o=>engine.buildJourney(o));
for(const club of ['York City','AFC Fylde','Harrogate Town','Guiseley AFC']){
 const expected=all.filter(j=>engine.sameClubIdentity(j.carrier.name,club));
 const actual=clubCampaigns(club,c);
 if(expected.length){assert.equal(actual.category,'custodian');assert.deepEqual(actual.journeys.map(j=>j.origin),expected.map(j=>j.origin.name));}
 else if(club==='York City'){assert.equal(actual.category,'example');assert.equal(actual.count,0);assert.equal(actual.journeys[0].origin,'Newton Aycliffe FC');}
}
const projected=structuredClone(c);
const names=['York City','Northampton Town','AFC Fylde','Harrogate Town'];
for(const [key,f] of Object.entries(projected.fixtures))if(names.some(n=>engine.sameClubIdentity(f.home,n)||engine.sameClubIdentity(f.away,n)))delete projected.fixtures[key];
// Future-round test data: this is an explicit hypothetical, never published competition data.
const f={round:'Second Round Proper',home:'York City',away:'AFC Fylde',date:'2026-12-05',kickoff:'15:00'};
projected.fixtures['York City']=f;projected.fixtures['AFC Fylde']=f;
const before=clubCampaigns('York City',projected);assert.equal(before.category,'next');assert.ok(before.count>0);
const originalCarrier=before.journeys[0].carrier;
const r={...f,home_score:2,away_score:1,winner:'York City',status:'LIVE',source_url:'https://example.test/verified-test-result'};
projected.results['York City']=r;projected.results['AFC Fylde']=r;
assert.equal(clubCampaigns('York City',projected).category,'next','live scores cannot transfer custody');
r.status='FT';r.home_score=1;r.away_score=1;r.winner='';r.decision='draw-replay';
assert.equal(clubCampaigns('York City',projected).category,'next','unresolved draw cannot transfer custody');
r.home_score=2;r.away_score=1;r.winner='York City';r.decision='';
const after=clubCampaigns('York City',projected);assert.equal(after.category,'custodian');assert.equal(after.count,before.count);assert.equal(after.journeys[0].carrier,'York City');
assert.ok(after.journeys[0].history.some(h=>h.round==='Second Round Proper'&&h.custodian==='York City'));
assert.equal(originalCarrier,before.journeys[0].carrier);assert.notDeepEqual(projected,c);
console.log('PASS: origins match full authoritative traversal; real example, future draw, live score, replay and later-round custody transfer.');
