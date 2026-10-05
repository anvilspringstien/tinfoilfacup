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
// After FQR promotion, the resolved Thame–Eastbourne TRQ tie is historical.
assert.equal(typeof ctx.tinFoilBetaVerifiedThameNextFixture,'function',
  'The isolated Thame fixture bridge was not installed');
const archived=(competition.round_fixtures||{})['Third Round Qualifying']||[];
const archivedRows=Array.isArray(archived)?archived:Object.values(archived);
const fixture=archivedRows.find(f=>f&&
  f.round==='Third Round Qualifying'&&
  f.home==='Thame United'&&f.away==='Eastbourne Borough');
assert(fixture,'Archived resolved Thame–Eastbourne draw missing');
assert(!fixture.conditional,'Archived Thame–Eastbourne fixture must not remain conditional');
assert.equal(fixture.date,'2026-10-03');

const finalReplay=r=>r&&r.round==='Second Round Qualifying Replay'&&
  r.home==='Exmouth Town'&&r.away==='Thame United'&&r.date==='2026-09-23'&&
  r.home_score===1&&r.away_score===3;
assert(Object.values(competition.results||{}).some(finalReplay),'Final replay missing');

const thameLoss=r=>r&&r.round==='Third Round Qualifying'&&r.date==='2026-10-03'&&
  r.home==='Thame United'&&r.away==='Eastbourne Borough'&&
  r.home_score===0&&r.away_score===1&&r.winner==='Eastbourne Borough';
const history=Object.values(competition.result_history||{}).flatMap(x=>Array.isArray(x)?x:[]);
assert(history.some(thameLoss),'Canonical Thame 0-1 Eastbourne TRQ result missing');

const active=Object.values(competition.fixtures||{});
const activeFqr=active.filter(f=>f&&f.round==='Fourth Round Qualifying');
const uniqueFqr=new Map(activeFqr.map(f=>[
  [f.round,f.date,f.home,f.away].join('|'),f
]));
assert.equal(uniqueFqr.size,32,'Active FQR draw must remain exactly 32 unique ties');
assert(!active.some(f=>f&&/Thame United|Exmouth Town/.test((f.home||'')+' '+(f.away||''))),
  'Eliminated Thame/Exmouth leaked into active FQR draw');

assert.equal(ctx.tinFoilBetaVerifiedThameNextFixture(
  {name:'Thame United FC'},'Third Round Qualifying'),null,
  'Historical Thame bridge must not resurrect an archived TRQ fixture');
assert.equal(ctx.liveLookup('fixtures','Exmouth Town FC'),null,
  'Losing Exmouth must not retain an active fixture index');
assert.equal(ctx.liveLookup('fixtures','Thame United FC'),null,
  'Losing Thame must not retain an active fixture index');
assert.equal(ctx.tinFoilBetaVerifiedThameNextFixture(
  {name:'Thame United FC'},'Fourth Round Qualifying'),null,
  'The special bridge must not apply to other rounds');
console.log('BETA Thame next-fixture and Exmouth fail-closed regression: PASS');
