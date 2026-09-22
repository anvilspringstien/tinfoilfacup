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
console.log('BETA conditional draw alias regression: PASS (Hampton, Weston, unrelated club)');
