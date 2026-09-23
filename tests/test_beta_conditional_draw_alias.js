// Exercise the actual BETA functions, not a rewritten copy of their logic.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const html = fs.readFileSync('beta/clubfinder-beta.html', 'utf8');
function between(start, end) {
  const a = html.indexOf(start), b = html.indexOf(end, a);
  assert(a >= 0 && b > a, 'BETA function not found: ' + start);
  return html.slice(a, b);
}
const fixture = {round:'Third Round Qualifying',
  home:'Hamp & Rich or Crowborough', away:'Weston SM or Wimborne',
  date:'2026-10-03', kickoff:'15:00', conditional:true};
const ctx = {LIVE_COMPETITION_DATA:{fixtures:{
  Hampton:fixture, Weston:fixture,
  Cray:{home:'Cray Wands or Maidstone',away:'Yate Town or Chippenham'},
  Dagenham:{home:'Brentwood Town',away:'Waltham A or Dag & Red'},
  Wingate:{home:'Bedford Town',away:'Hemel H or Win Finch'},
  Gainsborough:{home:"Leamington or G'borough T",away:'Anstey Nomads'}
}}};
vm.createContext(ctx);
vm.runInContext(
  between('function canonicalClubKey(', 'function sameClubIdentity(') +
  between('function drawAlternatives(', 'function resolveConditionalSide('),
  ctx);
assert.equal(ctx.drawIdentityCompatible('Hamp & Rich','Hampton & Richmond Borough FC'), true);
assert.equal(ctx.drawIdentityCompatible('Weston SM','Weston-super-Mare FC'), true);
assert.equal(ctx.drawIdentityCompatible('Crowborough','Hampton & Richmond Borough FC'), false);
for (const [abbrev,full] of [
  ['Cray Wands','Cray Wanderers FC'],
  ['Dag & Red','Dagenham & Redbridge FC'],
  ['Win Finch','Wingate & Finchley FC'],
  ["G'borough T",'Gainsborough Trinity FC']
]) assert.equal(ctx.drawIdentityCompatible(abbrev,full),true,abbrev);
assert.equal(ctx.liveConditionalFixtureForClub('Hampton & Richmond Borough FC').home, fixture.home);
assert.equal(ctx.liveConditionalFixtureForClub('Weston-super-Mare FC').away, fixture.away);
for (const [name,expected] of [
  ['Cray Wanderers FC','Cray Wands or Maidstone'],
  ['Dagenham & Redbridge FC','Brentwood Town'],
  ['Wingate & Finchley FC','Bedford Town'],
  ['Gainsborough Trinity FC',"Leamington or G'borough T"]
]) assert.equal(ctx.liveConditionalFixtureForClub(name).home,expected,name);
assert.equal(ctx.liveConditionalFixtureForClub('An Unrelated Club'), null);
// Validate the real current draw, not just hand-written example fixtures.
ctx.LIVE_COMPETITION_DATA = JSON.parse(fs.readFileSync('competition.json','utf8'));
for (const winner of [
  'Braintree Town','Chippenham Town','Cirencester Town',
  'Cray Wanderers','Crowborough Athletic','Dagenham & Redbridge',
  'Dorking Wanderers','Uxbridge','Gainsborough Trinity',
  'Wingate & Finchley','Truro City','Worksop Town','Wimborne Town'
]) {
  assert(ctx.liveConditionalFixtureForClub(winner),
    'No unique Third Qualifying draw for ' + winner);
}
assert(ctx.liveConditionalFixtureForClub('Hampton & Richmond Borough FC'),
  'Hampton must see conditional draw while replay unresolved');
console.log('BETA conditional draw alias regression: PASS (Hampton, Weston, unrelated club)');

// BETA reconciliation: ported verified-opponent resolution must not destroy
// the existing preserveConditional path for genuinely pending replays.
vm.runInContext(
  between('function canonicalResultWinner(', 'function sameSemanticResult(') +
  between('function resolveConditionalSide(', 'function verifiedConditionalWinner(') +
  between('function verifiedConditionalWinner(', 'function nextRoundInfo('), ctx);
ctx.VERIFIED_MATCH_VENUE_OVERRIDES = {};
ctx.candidateClubByName = () => null;
ctx.groundByClubName = name => /crowborough/i.test(name)
  ? {ground:'Charles Century Community Stadium',postcode:'TN6 3BU'}
  : {};
const replay = {round:'Second Round Qualifying Replay',
  home:'Wimborne Town',away:'Weston-super-Mare',date:'2026-09-22',
  home_score:1,away_score:1,winner:'Wimborne Town',
  decision:'penalties',penalties_home:4,penalties_away:3};
const hampton = {round:'Second Round Qualifying Replay',
  home:'Crowborough Athletic',away:'Hampton & Richmond Borough',
  date:'2026-09-22',home_score:3,away_score:1,winner:'Crowborough Athletic'};
ctx.LIVE_COMPETITION_DATA = {result_history:{},results:{
  Wimborne:replay,Crowborough:hampton}};
const resolved = ctx.resolveLiveFixtureForCarrier(fixture,
  {name:'Crowborough Athletic FC'},false);
assert.equal(resolved.conditional,false);
assert.equal(resolved.home,'Crowborough Athletic FC');
assert.equal(resolved.away,'Wimborne Town');
assert.equal(resolved.venue.postcode,'TN6 3BU');
const pending = ctx.resolveLiveFixtureForCarrier(fixture,
  {name:'Crowborough Athletic FC'},true);
assert.equal(pending.conditional,true);
assert.equal(pending.home,fixture.home);
assert.equal(pending.away,fixture.away);
ctx.LIVE_COMPETITION_DATA = {result_history:{},results:{}};
const unknown = ctx.resolveLiveFixtureForCarrier(fixture,
  {name:'Crowborough Athletic FC'},false);
assert.equal(unknown.conditional,true);
assert.match(unknown.away,/Weston SM or Wimborne/);
ctx.LIVE_COMPETITION_DATA = {result_history:{replays:[replay,hampton]},results:{}};
const fromHistory = ctx.resolveLiveFixtureForCarrier(fixture,
  {name:'Crowborough Athletic FC'},false);
assert.equal(fromHistory.away,'Wimborne Town');
console.log('BETA verified replay opponent regression: PASS (results, history, pending, missing evidence)');
