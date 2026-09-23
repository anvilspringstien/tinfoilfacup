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
  'resolveConditionalSide','verifiedConditionalWinner','resolveLiveFixtureForCarrier','resultLineFromResult'];
const code=names.map(extract).join('\n');
const context={
  LIVE_COMPETITION_DATA:data,
  VERIFIED_MATCH_VENUE_OVERRIDES:{},
  candidateClubByName:()=>null,
  groundByClubName:n=>({'Crowborough Athletic':{ground:'Charles Century Community Stadium',postcode:'TN6 3BU'},
    'Cray Wanderers':{ground:'Flamingo Park',postcode:'BR7 6HL'}}[n]||{}),
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
console.log('Conditional draw, venue, penalty and unresolved-fixture guards: PASS');
