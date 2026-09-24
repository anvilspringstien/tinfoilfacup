// BETA-only regression: the published FA draw is keyed "Thame Utd", but
// the verified custodian is "Thame United FC". Exercise nextRoundInfo itself.
'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const html=fs.readFileSync('beta/clubfinder-beta.html','utf8');
const competition=JSON.parse(fs.readFileSync('competition.json','utf8'));
const between=(start,end)=>{
  const a=html.indexOf(start),b=html.indexOf(end,a+start.length);
  assert(a>=0&&b>a,'Missing real BETA source boundary: '+start);
  return html.slice(a,b);
};
const ctx={
  LIVE_COMPETITION_DATA:competition,
  VERIFIED_MATCH_VENUE_OVERRIDES:{},
  candidateClubByName:()=>null,
  groundByClubName:()=>({ground:'Test Ground',postcode:'AB1 2CD',verification:'unverified'}),
  ROUND_META:{'Third Round Qualifying':{date:'2026-10-03',drawDate:'2026-09-21'}},
  PRELIM_FIXTURES_BY_CLUB:{}, NEXT_FIXTURE_OVERRIDES:{},
  FA_FIXTURES_URL:'https://www.thefa.com/competitions/thefacup/fixtures',
  resultFor:club=>/Thame|Exmouth|Eastbourne/i.test(club.name)?
    {round:'Second Round Qualifying Replay'}:null,
  liveLookup:(section,name)=>{
    // Reproduce Clubfinder's real exact/stripped-FC index path.
    const obj=(ctx.LIVE_COMPETITION_DATA||{})[section]||{};
    const raw=String(name||''),short=raw.replace(/\s+(FC|AFC|CFC)$/,'');
    return obj[raw]||obj[short]||null;
  }
};
vm.createContext(ctx);
vm.runInContext(
  between('function canonicalClubKey(','function sameSemanticResult(')+
  between('function drawAlternatives(','\nfunction canonicalClubKey('),ctx
);
// Exercise the real direct and conditional indexes; stubbing them masked Exmouth.
assert.equal(typeof ctx.tinFoilBetaVerifiedThameNextFixture,'function',
  'The isolated Thame fixture bridge was not installed');
const fixture=Object.values(competition.fixtures||{}).find(f=>f&&
  f.round==='Third Round Qualifying'&&
  f.home==='Thame Utd or Exmouth Town'&&f.away==='Eastbourne Borough');
assert(fixture,'Actual published Third Qualifying draw not found');
const exmouthIndex=ctx.liveLookup('fixtures','Exmouth Town FC');
assert(exmouthIndex&&exmouthIndex.home===fixture.home,
  'Exmouth direct index unavailable: regression would miss original defect');
const exmouthConditional=ctx.liveConditionalFixtureForClub('Exmouth Town FC');
assert(exmouthConditional&&exmouthConditional.home===fixture.home,
  'Exmouth conditional index unavailable: regression would miss fallback defect');
const eastbourne=ctx.nextRoundInfo(
  {name:'Eastbourne Borough FC',entry_round:'Second Round Qualifying'},true);
assert(eastbourne.knownFixture,'Legitimate Eastbourne opponent lost its fixture');
assert.equal(eastbourne.knownFixture.home,'Thame United');
assert.equal(eastbourne.knownFixture.away,'Eastbourne Borough');
assert.equal(eastbourne.knownFixture.conditional,false);
const thame=()=>ctx.nextRoundInfo({name:'Thame United FC',entry_round:'Second Round Qualifying'},true);
const next=thame();
assert.equal(next.name,'Third Round Qualifying');
assert(next.knownFixture,'Verified Thame custodian has no next fixture');
assert.equal(next.knownFixture.home,'Thame United');
assert.equal(next.knownFixture.away,'Eastbourne Borough');
assert.equal(next.knownFixture.date,'2026-10-03');
assert.equal(next.knownFixture.conditional,false);
const duplicateEntries=Object.values(competition.fixtures||{}).filter(f=>f&&
  f.round===fixture.round&&f.home===fixture.home&&f.away===fixture.away);
assert(duplicateEntries.length>=2,'Expected multiple index keys for one real FA tie');
assert.equal(ctx.tinFoilBetaVerifiedThameNextFixture(
  {name:'Thame United FC'},'Third Round Qualifying').home,fixture.home);
// The losing club must not inherit the fixture through this bridge.
assert.equal(ctx.nextRoundInfo(
  {name:'Exmouth Town FC',entry_round:'Second Round Qualifying'},true
).knownFixture,null,'Losing Exmouth was incorrectly advanced');
const finalReplay=r=>r&&r.round==='Second Round Qualifying Replay'&&
  r.home==='Exmouth Town'&&r.away==='Thame United'&&
  r.date==='2026-09-23'&&r.home_score===1&&r.away_score===3;
assert(Object.values(competition.results||{}).some(finalReplay),
  'Final replay missing from canonical published results');
ctx.LIVE_COMPETITION_DATA={
  ...competition,
  results:Object.fromEntries(Object.entries(competition.results||{})
    .filter(([,r])=>!finalReplay(r))),
  result_history:Object.fromEntries(Object.entries(competition.result_history||{})
    .map(([key,rows])=>[key,Array.isArray(rows)?rows.filter(r=>!finalReplay(r)):rows]))
};
assert.equal(thame().knownFixture,null,
  'Unverified result cannot advance Thame into a confirmed fixture');
const unresolved=ctx.nextRoundInfo(
  {name:'Exmouth Town FC',entry_round:'Second Round Qualifying'},true);
assert(unresolved.knownFixture&&unresolved.knownFixture.conditional,
  'BETA must preserve the possible next fixture while replay is unresolved');
assert.match(unresolved.knownFixture.home,/Thame Utd or Exmouth Town/);
ctx.LIVE_COMPETITION_DATA=competition;
assert.equal(ctx.tinFoilBetaVerifiedThameNextFixture(
  {name:'Thame United FC'},'Fourth Round Qualifying'),null,
  'The special bridge must not apply to other rounds');
console.log('BETA Thame next-fixture and Exmouth fail-closed regression: PASS');
