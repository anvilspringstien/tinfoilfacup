// Regress the real BETA resolver, including its preserveConditional behaviour.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');

const html = fs.readFileSync('beta/clubfinder-beta.html', 'utf8');
const competition = JSON.parse(fs.readFileSync('competition.json', 'utf8'));

function between(start, end) {
  const a = html.indexOf(start), b = html.indexOf(end, a);
  assert(a >= 0 && b > a, 'Missing BETA source boundary: ' + start);
  return html.slice(a, b);
}

const ctx = {
  LIVE_COMPETITION_DATA: null,
  VERIFIED_MATCH_VENUE_OVERRIDES: {},
  candidateClubByName: () => null,
  groundByClubName: name => /crowborough/i.test(name)
    ? {ground: 'Charles Century Community Stadium', postcode: 'TN6 3BU', verification: 'verified'}
    : {ground: 'Test Ground', postcode: 'AB1 2CD', verification: 'unverified'}
};
vm.createContext(ctx);
vm.runInContext(
  between('function canonicalClubKey(', 'function sameClubIdentity(') +
  between('function canonicalResultWinner(', 'function sameSemanticResult(') +
  between('function drawAlternatives(', 'function nextRoundInfo('),
  ctx
);

const fixture = {
  round: 'Third Round Qualifying',
  home: 'Hamp & Rich or Crowborough',
  away: 'Weston SM or Wimborne',
  date: '2026-10-03',
  kickoff: '15:00',
  conditional: true
};
const crowborough = {
  round: 'Second Round Qualifying Replay',
  date: '2026-09-22',
  home: 'Crowborough Athletic',
  away: 'Hampton & Richmond Borough',
  home_score: 3, away_score: 1, winner: 'Crowborough Athletic'
};
const wimborne = {
  round: 'Second Round Qualifying Replay',
  date: '2026-09-22',
  home: 'Wimborne Town',
  away: 'Weston-super-Mare',
  home_score: 1, away_score: 1, decision: 'penalties',
  winner: 'Wimborne Town'
};
function resolve(data, preserveConditional = true, round = fixture.round) {
  ctx.LIVE_COMPETITION_DATA = data;
  return ctx.resolveLiveFixtureForCarrier({...fixture, round},
    {name: 'Hampton & Richmond Borough FC'}, preserveConditional);
}
function check(actual, home, away, conditional) {
  assert.equal(actual.home, home);
  assert.equal(actual.away, away);
  assert.equal(actual.conditional, conditional);
}

// An unplayed replay must not be treated as a known win.
check(resolve({result_history: {}, results: {}}),
  fixture.home, fixture.away, true);
check(resolve({result_history: {}, results: {}}, false),
  fixture.home, fixture.away, true);

// Each side resolves independently: one verified winner leaves the other undecided.
check(resolve({result_history: {Crowborough: [crowborough]}, results: {}}),
  'Crowborough Athletic', fixture.away, true);

// Equal scores with a published penalty winner resolve correctly.
check(resolve({result_history: {
  Crowborough: [crowborough], Wimborne: [wimborne]
}, results: {}}), 'Crowborough Athletic', 'Wimborne Town', false);

// Current published results must resolve the same way as archived chronology.
const published = resolve({result_history: {}, results: {
  crowborough, wimborne
}});
check(published, 'Crowborough Athletic', 'Wimborne Town', false);
assert.equal(published.venue.postcode, 'TN6 3BU');

// One independently published replay must not decide the other side.
check(resolve({result_history: {}, results: {crowborough}}),
  'Crowborough Athletic', fixture.away, true);

// An undecided fixture has no confirmed match venue.
assert.equal(resolve({result_history: {}, results: {}}).venue.postcode, 'Postcode TBC');

// Conflicting winner records must not select either claimant.
check(resolve({result_history: {
  A: [crowborough],
  B: [{...crowborough, date: '2026-09-23',
    home: 'Hampton & Richmond Borough', away: 'Crowborough Athletic',
    home_score: 2, away_score: 0, winner: 'Hampton & Richmond Borough'}]
}, results: {}}), fixture.home, fixture.away, true);

// A win in an earlier, unrelated round cannot settle this draw.
check(resolve({result_history: {
  A: [{...crowborough, round: 'First Round Qualifying'}]
}, results: {}}), fixture.home, fixture.away, true);

// The same resolver must work on this branch's real published competition data.
check(resolve(competition), 'Crowborough Athletic', 'Wimborne Town', false);

// Only apply this parent-round reconciliation to Third Round Qualifying.
check(resolve({result_history: {
  Crowborough: [crowborough], Wimborne: [wimborne]
}, results: {}}, true, 'Fourth Round Qualifying'), fixture.home, fixture.away, true);

// The actual Third Qualifying draw abbreviates Thame United as "Thame Utd".
const thameFixture = {...fixture, home: 'Thame Utd or Exmouth Town', away: 'Eastbourne Borough'};
const thameReplay = {
  round: 'Second Round Qualifying Replay', date: '2026-09-23',
  home: 'Exmouth Town', away: 'Thame United',
  home_score: 1, away_score: 3, winner: 'Thame United', status: 'FT'
};
ctx.LIVE_COMPETITION_DATA = {result_history: {}, results: {}};
let thameResolved = ctx.resolveLiveFixtureForCarrier(thameFixture,
  {name: 'Exmouth Town FC'}, true);
check(thameResolved, thameFixture.home, thameFixture.away, true);
ctx.LIVE_COMPETITION_DATA = {result_history: {Exmouth: [thameReplay]}, results: {}};
thameResolved = ctx.resolveLiveFixtureForCarrier(thameFixture,
  {name: 'Exmouth Town FC'}, true);
check(thameResolved, 'Thame United', 'Eastbourne Borough', false);

assert.match(html, /next:nextRoundInfo\(club,true\)/);
console.log('BETA verified conditional replay regression: PASS (10 cases plus venue checks)');
