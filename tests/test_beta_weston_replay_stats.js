#!/usr/bin/env node
// Exercise the committed BETA resolver and Stats counting code, not a rewritten copy.
const fs=require('node:fs');
const vm=require('node:vm');
const assert=require('node:assert/strict');
const html=fs.readFileSync('beta/clubfinder-beta.html','utf8');
const competition=JSON.parse(fs.readFileSync('competition.json','utf8'));
function extract(start,end) {
  const a=html.indexOf(start),b=html.indexOf(end,a);
  assert(a>=0&&b>a,'BETA source boundary absent: '+start);
  return html.slice(a,b);
}
const weston={
  round:'Second Round Qualifying',date:'2026-09-19',
  home:'Weston-super-Mare',away:'Wimborne Town',
  home_score:1,away_score:1,decision:'draw-replay'
};
const wimborne=Object.values(competition.results||{}).find(r=>
 r&&r.round==='Second Round Qualifying Replay'&&
 r.date==='2026-09-22'&&r.home==='Wimborne Town'&&
 r.away==='Weston-super-Mare'&&r.decision==='penalties'&&r.winner==='Wimborne Town');
assert(wimborne,'Canonical verified Wimborne replay is absent');
let result=wimborne, replay=null;
const norm=s=>String(s||'').toLowerCase().replace(/\b(fc|afc)\b/g,'').replace(/[^a-z0-9]+/g,' ').trim();
const ctx={
 norm,
 sameClubIdentity:(a,b)=>norm(a)===norm(b),
 esc:s=>String(s??''),
 resultFor:()=>result,
 replayFixtureFor:()=>replay,
 replayVenue:()=>({ground:'The Wyatt Homes Stadium',postcode:'BH21 2FU'}),
 completedResultVenue:()=>({ground:'The Wyatt Homes Stadium',postcode:'BH21 2FU'}),
 completedResultDateLabel:r=>r.date,
 canonicalResultWinner:r=>r.winner||'',
 fixture:()=>({}),
 displayedRound:()=>'',formatDateGB:s=>s,
 nextRoundInfo:()=>null
};
vm.createContext(ctx);
vm.runInContext(
 extract('function tinFoilBetaVerifiedWimborneReplay(','function currentDisplayFixture(')+
 extract('function resultTeamLine(','function sameMatchResult(')+
 extract('function currentDisplayFixture(','function fixtureVenue(')+
 extract('function resultLinePlain(','/* TIN_FOIL_PIGEON_MILES_STATS_BEGIN */')+
 extract('function tinFoilCertificateWinner(','function tinFoilStatsDisplayClubKey('),
 ctx
);
const club={name:'Weston Super Mare FC',entry_round:'Second Round Qualifying'};
assert.equal(ctx.tinFoilBetaCompletedKickoff(wimborne,null),'19:45');
assert.equal(ctx.tinFoilBetaCompletedKickoff(wimborne,{kickoff:'15:00'}),'19:45',
 'Legacy 15:00 replay data must not override verified kick-off');
assert.equal(ctx.currentDisplayFixture(club).kickoff,'19:45');
replay={round:'Second Round Qualifying Replay',date:'2026-09-22',kickoff:'15:00'};
assert.equal(ctx.currentDisplayFixture(club).kickoff,'19:45');
const other={...wimborne,home:'Another FC',away:'Opponent FC',winner:'Another FC'};
assert.equal(ctx.tinFoilBetaCompletedKickoff(other,null),'Kick-off TBC',
 'An unrelated replay without a verified time must not inherit 15:00');
assert.match(ctx.resultTeamLine(club),/Wimborne Town won 4–3 on penalties/);
assert.match(ctx.resultLineFromResult(wimborne),/Wimborne Town won 4–3 on penalties/);
assert.match(ctx.resultLinePlain(wimborne),/Wimborne Town won 4–3 on penalties/);
assert.match(ctx.resultLineFromResult(other),/Another FC won on penalties/);
assert.equal(ctx.tinFoilCertificateWinner(wimborne),'Wimborne Town');
assert.equal(ctx.tinFoilCertificateWinner(weston),'');
assert.equal(ctx.tinFoilCertificateWinner({...wimborne,decision:'draw-replay',winner:''}),'');
assert.equal(ctx.tinFoilCertificateWinner({
 home:'Exmouth Town',away:'Thame United',home_score:1,away_score:3
}),'Thame United');
const loop=extract(
  '  let goals=0, homeGames=0, awayGames=0, custodianWins=0, draws=0, custodianDefeats=0, penaltyWins=0, penaltyLosses=0;',
  '  // A replay completes the same competition round'
);
ctx.crumbs=[{result:weston},{result:wimborne}];
ctx.origin={name:'Weston-super-Mare'};
ctx.venueForResult=r=>r.date==='2026-09-19'?
 {ground:'Optima Stadium',postcode:'BS24 9AA'}:
 {ground:'The Wyatt Homes Stadium',postcode:'BH21 2FU'};
const stats=vm.runInContext(
  '(function(){'+loop+'return {goals,homeGames,awayGames,custodianWins,draws,custodianDefeats,penaltyWins,penaltyLosses,grounds:venueKeys.size};})()',
  ctx
);
assert.equal(JSON.stringify(stats),JSON.stringify({
 goals:4,homeGames:1,awayGames:1,custodianWins:0,draws:2,
 custodianDefeats:0,penaltyWins:0,penaltyLosses:1,grounds:2
}));
assert.match(html,/• Shootouts Won: '\+penaltyWins/);
assert.match(html,/• Shootouts Lost: '\+penaltyLosses/);
assert.match(html,/jr-winner[^;]*tinFoilBetaPenaltyResultNote\(r\)/s);
assert.match(html,/const EMBEDDED_COMPETITION_DATA=/);
console.log('BETA WESTON REPLAY/STATS REGRESSION: PASS');
console.log('19:45 replay / shootout display / canonical custody / 2 draws and separate shootout loss: PASS');
