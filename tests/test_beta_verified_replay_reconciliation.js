// Regression for BETA's verified conditional draw reconciliation.
const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const html=fs.readFileSync('beta/clubfinder-beta.html','utf8');
function between(start,end){
  const a=html.indexOf('function '+start+'('),b=html.indexOf('function '+end+'(',a+1);
  assert(a>=0&&b>a,'missing BETA function: '+start);return html.slice(a,b);
}
const code=between('drawAlternatives','nextRoundInfo')+between('canonicalClubKey','sameSemanticResult');
const replay={round:'Second Round Qualifying Replay',date:'2026-09-22',
  home:'Wimborne Town',away:'Weston-super-Mare',home_score:1,away_score:1,
  winner:'Wimborne Town',decision:'penalties',home_penalties:4,away_penalties:3};
const crow={round:'Second Round Qualifying Replay',date:'2026-09-22',
  home:'Crowborough Athletic',away:'Hampton & Richmond Borough',home_score:3,away_score:1,
  winner:'Crowborough Athletic'};
const fixture={round:'Third Round Qualifying',home:'Hamp & Rich or Crowborough',
  away:'Weston SM or Wimborne',date:'2026-10-03',kickoff:'15:00',conditional:true};
const ctx={LIVE_COMPETITION_DATA:{result_history:{},results:{crow,replay}},
  VERIFIED_MATCH_VENUE_OVERRIDES:{},
  candidateClubByName:()=>null,
  groundByClubName:n=>/crowborough/i.test(n)?{ground:'Charles Century Community Stadium',postcode:'TN6 3BU'}:{},
};
vm.createContext(ctx);vm.runInContext(code,ctx);
const resolve=(preserve=false)=>ctx.resolveLiveFixtureForCarrier(fixture,{name:'Crowborough Athletic'},preserve);
let f=resolve();
assert.equal(f.home,'Crowborough Athletic');assert.equal(f.away,'Wimborne Town');
assert.equal(f.conditional,false);assert.equal(f.venue.postcode,'TN6 3BU');
f=resolve(true);assert.equal(f.conditional,true);assert.match(f.away,/Weston SM or Wimborne/);
ctx.LIVE_COMPETITION_DATA={result_history:{},results:{crow}};
f=resolve();assert.equal(f.home,'Crowborough Athletic');assert.match(f.away,/Weston SM or Wimborne/);
assert.equal(f.conditional,true);assert.equal(f.venue.postcode,'Postcode TBC');
ctx.LIVE_COMPETITION_DATA={result_history:{replays:[crow,replay]},results:{}};
f=resolve();assert.equal(f.away,'Wimborne Town');assert.equal(f.conditional,false);
console.log('PASS: BETA verified results, chronology fallback, conditional preview, fail-closed venue');
