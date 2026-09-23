// Guarded, source-backed regression: both sides of conditional draws must resolve.
const fs=require('fs'),vm=require('vm'),assert=require('assert');
const html=fs.readFileSync('clubfinder.html','utf8');
const data=JSON.parse(fs.readFileSync('competition.json','utf8'));
function extract(name){
  const start=html.indexOf('function '+name+'(');
  assert(start>=0,'missing '+name);
  const brace=html.indexOf('{',start);
  let depth=0,end=brace;
  for(;end<html.length;end++){
    if(html[end]==='{')depth++;
    if(html[end]==='}'&&!--depth){end++;break;}
  }
  return html.slice(start,end);
}
const names=['canonicalClubKey','sameClubIdentity','canonicalResultWinner','drawAlternatives',
  'resolveConditionalSide','verifiedConditionalWinner','resolveLiveFixtureForCarrier','resultLineFromResult','nextRoundInfo'];
const code=names.map(extract).join('\n');
const context={
  LIVE_COMPETITION_DATA:data,
  ROUND_META:{'Third Round Qualifying':{date:'2026-10-03',drawDate:'2026-09-21'}},
  FA_FIXTURES_URL:'https://www.thefa.com/competitions/thefacup/fixtures',
  resultFor:club=>context.LIVE_COMPETITION_DATA.results?.[club.name]||context.LIVE_COMPETITION_DATA.results?.[club.name.replace(/\s+FC$/,'')]||null,
  liveLookup:(section,name)=>context.LIVE_COMPETITION_DATA[section]?.[name]||context.LIVE_COMPETITION_DATA[section]?.[name.replace(/\s+FC$/,'')]||null,
  VERIFIED_MATCH_VENUE_OVERRIDES:{},
  candidateClubByName:()=>null,
  groundByClubName:n=>({'crowborough athletic':{ground:'Charles Century Community Stadium',postcode:'TN6 3BU'},
    'cray wanderers':{ground:'Flamingo Park',postcode:'BR7 6HL'}}[String(n).toLowerCase().replace(/\s+fc$/,'')]||{}),
  esc:x=>String(x),
};
vm.createContext(context);vm.runInContext(code,context);
const fixtures=Object.values(data.fixtures).filter(x=>x.round==='Third Round Qualifying');
const pick=(a,b)=>fixtures.find(x=>x.home.includes(a)&&x.away.includes(b));
function resolve(f,carrier){return context.resolveLiveFixtureForCarrier(f,{name:carrier});}
const crow=resolve(pick('Crowborough','Wimborne'),'Wimborne Town');
assert.strictEqual(crow.home,'Crowborough Athletic');
assert.strictEqual(crow.away,'Wimborne Town');
assert.strictEqual(crow.venue.postcode,'TN6 3BU');
assert.strictEqual(crow.conditional,false);
const crowSaved=resolve(pick('Crowborough','Wimborne'),'Crowborough Athletic FC');
assert.strictEqual(crowSaved.home,'Crowborough Athletic FC');
assert.strictEqual(crowSaved.away,'Wimborne Town');
assert.strictEqual(crowSaved.conditional,false);
assert.strictEqual(crowSaved.venue.postcode,'TN6 3BU');
// A fresh Hampton campaign must resolve the same opponent even if the
// separately published chronology is missing or has not yet refreshed.
context.LIVE_COMPETITION_DATA={...data,result_history:{}};
const crowFromResults=resolve(pick('Crowborough','Wimborne'),'Crowborough Athletic FC');
assert.strictEqual(crowFromResults.home,'Crowborough Athletic FC');
assert.strictEqual(crowFromResults.away,'Wimborne Town');
assert.strictEqual(crowFromResults.conditional,false);
assert.strictEqual(crowFromResults.venue.postcode,'TN6 3BU');
const crowNext=context.nextRoundInfo({name:'Crowborough Athletic FC',entry_round:'Second Round Qualifying',fixture:{}});
assert.strictEqual(crowNext.name,'Third Round Qualifying');
assert.strictEqual(crowNext.knownFixture.home,'Crowborough Athletic FC');
assert.strictEqual(crowNext.knownFixture.away,'Wimborne Town');
assert.strictEqual(crowNext.knownFixture.conditional,false);
assert.strictEqual(crowNext.knownFixture.venue.postcode,'TN6 3BU');
// No chronology or verified result: retain the conditional draw and TBC ground.
context.LIVE_COMPETITION_DATA={...data,result_history:{},results:{}};
const crowUnknown=resolve(pick('Crowborough','Wimborne'),'Crowborough Athletic FC');
assert.strictEqual(crowUnknown.home,'Crowborough Athletic FC');
assert.strictEqual(crowUnknown.away,'Weston SM or Wimborne');
assert.strictEqual(crowUnknown.conditional,true);
assert.strictEqual(crowUnknown.venue.postcode,'Postcode TBC');
context.LIVE_COMPETITION_DATA=data;
const chip=resolve(pick('Cray Wands','Chippenham'),'Chippenham Town');
assert.strictEqual(chip.home,'Cray Wanderers');
assert.strictEqual(chip.away,'Chippenham Town');
assert.strictEqual(chip.conditional,false);
assert.strictEqual(chip.venue.postcode,'BR7 6HL');
const w=Object.values(data.results).find(r=>r.date==='2026-09-22'&&r.home==='Wimborne Town'&&r.away==='Weston-super-Mare');
assert(w,'missing Wimborne result');
assert(context.resultLineFromResult(w).includes('won on penalties (4–3)'));
const unresolved=resolve({home:'Unknown A or Unknown B',away:'Wimborne Town',round:'Third Round Qualifying'},'Wimborne Town');
assert.strictEqual(unresolved.conditional,true);
assert.strictEqual(unresolved.venue.postcode,'Postcode TBC');

// Saved campaigns must find the uniquely abbreviated fixture key, not lose
// the published draw simply because the campaign has an FC suffix.
const key='Wimborne', saved='Wimborne Town FC';
assert(data.fixtures[key],'missing abbreviated Wimborne fixture');
assert(!data.fixtures[saved],'regression fixture must exercise fallback');
const target=context.canonicalClubKey(saved);
const matches=Object.entries(data.fixtures).filter(([name,f])=>
  f.round==='Third Round Qualifying'&&
  (context.canonicalClubKey(name)===target||target.startsWith(context.canonicalClubKey(name)+' ')));
const unique=[...new Map(matches.map(([,f])=>
  [[f.home,f.away,f.round,f.date].join('|'),f])).values()];
assert.strictEqual(unique.length,1);
const savedFixture=resolve(unique[0],saved);
assert.strictEqual(savedFixture.home,'Crowborough Athletic');
assert(context.sameClubIdentity(savedFixture.away,'Wimborne Town FC'));
assert.strictEqual(savedFixture.venue.postcode,'TN6 3BU');

console.log('Conditional draw, venue, penalty and saved-campaign fixture guards: PASS');
