'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const html=fs.readFileSync('clubfinder.html','utf8');
const competition=JSON.parse(fs.readFileSync('competition.json','utf8'));
const between=(start,end)=>{
  const a=html.indexOf(start),b=html.indexOf(end,a+start.length);
  assert(a>=0&&b>a,'Missing production source boundary: '+start);
  return html.slice(a,b);
};
const ctx={
  LIVE_COMPETITION_DATA:competition,
  VERIFIED_MATCH_VENUE_OVERRIDES:{},
  candidateClubByName:()=>null,
  groundByClubName:()=>({ground:'Test Ground',postcode:'AB1 2CD',verification:'unverified'}),
  ROUND_META:{'Third Round Qualifying':{date:'3 October 2026',drawDate:'TBC'}},
  PRELIM_FIXTURES_BY_CLUB:{},NEXT_FIXTURE_OVERRIDES:{},
  FA_FIXTURES_URL:'https://www.thefa.com/competitions/thefacup/fixtures',
  resultFor:club=>/Thame|Exmouth/i.test(club.name)?{round:'Second Round Qualifying Replay'}:null,
  liveLookup:(section,name)=>{
    // Use the same exact-name and stripped-FC lookup as real Clubfinder.
    // The previous null stub missed the Exmouth source-index shortcut.
    const obj=(ctx.LIVE_COMPETITION_DATA||{})[section]||{};
    const raw=String(name||''),short=raw.replace(/\s+(FC|AFC|CFC)$/,'');
    return obj[raw]||obj[short]||null;
  }
};
vm.createContext(ctx);
vm.runInContext(between('function drawAlternatives(','function sameSemanticResult('),ctx);
assert.equal(typeof ctx.tinFoilVerifiedThameNextFixture,'function');
const fixture=Object.values(competition.fixtures||{}).find(f=>f&&
  f.round==='Third Round Qualifying'&&
  f.home==='Thame Utd or Exmouth Town'&&f.away==='Eastbourne Borough');
assert(fixture,'Actual published Thame conditional draw missing');
const exmouthIndexed=ctx.liveLookup('fixtures','Exmouth Town FC');
assert(exmouthIndexed&&exmouthIndexed.home==='Thame Utd or Exmouth Town',
  'Exmouth direct fixture index missing: negative test would not exercise the defect');
const eastbourne=ctx.nextRoundInfo({name:'Eastbourne Borough FC',entry_round:'Second Round Qualifying'});
assert(eastbourne.knownFixture,'Legitimate Eastbourne opposing fixture must survive the Exmouth guard');
assert.equal(eastbourne.knownFixture.away,'Eastbourne Borough');
assert.equal(eastbourne.knownFixture.home,'Thame United');
assert.equal(eastbourne.knownFixture.conditional,false);

const thame=()=>ctx.nextRoundInfo({name:'Thame United FC',entry_round:'Second Round Qualifying'});
const next=thame();
assert(next.knownFixture,'Production Thame has no verified next fixture');
assert.equal(next.knownFixture.home,'Thame United');
assert.equal(next.knownFixture.away,'Eastbourne Borough');
assert.equal(next.knownFixture.date,'2026-10-03');
assert.equal(next.knownFixture.conditional,false);
assert.equal(ctx.nextRoundInfo({name:'Exmouth Town FC',entry_round:'Second Round Qualifying'}).knownFixture,null,
  'Losing Exmouth was incorrectly advanced');
const finalReplay=r=>r&&r.round==='Second Round Qualifying Replay'&&
  r.home==='Exmouth Town'&&r.away==='Thame United'&&r.date==='2026-09-23'&&
  r.home_score===1&&r.away_score===3;
assert(Object.values(competition.results||{}).some(finalReplay),'Final replay missing');
ctx.LIVE_COMPETITION_DATA={
  ...competition,
  results:Object.fromEntries(Object.entries(competition.results||{}).filter(([,r])=>!finalReplay(r))),
  result_history:Object.fromEntries(Object.entries(competition.result_history||{}).map(([k,rows])=>
    [k,Array.isArray(rows)?rows.filter(r=>!finalReplay(r)):rows]))
};
assert.equal(thame().knownFixture,null,'Unverified replay must not advance Thame');
ctx.LIVE_COMPETITION_DATA=competition;
assert.equal(ctx.tinFoilVerifiedThameNextFixture({name:'Thame United FC'},'Fourth Round Qualifying'),null);
console.log('Production Thame next-fixture and Exmouth fail-closed regression: PASS');
