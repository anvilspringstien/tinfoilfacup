#!/usr/bin/env python3
"""Guard Clubfinder journey integrity and next-round presentation.

Responsibilities:
1. Always fetch the live competition snapshot with cache-busting/no-store semantics.
2. Return Previous Rounds breadcrumbs only for the actual Tin Foil FA Cup custody chain.
3. Never present the just-played/current-round fixture as the known fixture for the next round.
"""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / 'clubfinder.html'
text = P.read_text(encoding='utf-8')

old_fetch = "const u=LIVE_COMPETITION_DATA_URL+(force?(LIVE_COMPETITION_DATA_URL.includes('?')?'&':'?')+'t='+Date.now():'');\n    const r=await fetch(u,{cache:force?'no-store':'default'});"
new_fetch = "const u=LIVE_COMPETITION_DATA_URL+(LIVE_COMPETITION_DATA_URL.includes('?')?'&':'?')+'t='+Date.now();\n    const r=await fetch(u,{cache:'no-store'});"
if old_fetch in text:
    text = text.replace(old_fetch, new_fetch, 1)
elif new_fetch not in text:
    raise SystemExit('ABORT: live competition fetch boundary not found')

new_build = r'''function buildJourney(origin){
  let carrier=origin;
  const candidates=[];
  function clubObjectForWinner(name,prior){
    return clubByDisplayName(name)||candidateClubByName(name)||{name:name,entry_round:(prior&&prior.entry_round)||'',fixture:{}};
  }
  function appendHistory(club){
    const history=historicalResultsForClub(club);
    for(const item of history){
      if(!candidates.some(x=>sameSemanticResult(x.result,item.result)))candidates.push(item);
    }
  }
  function resolveChain(){
    let c=origin;
    const chain=[];
    const ordered=[...candidates].sort((a,b)=>resultSortValue(a.result)-resultSortValue(b.result));
    for(const item of ordered){
      const r=item.result||{};
      const participant=sameClubIdentity(r.home,c.name)||sameClubIdentity(r.away,c.name);
      if(!participant)continue;
      chain.push(item);
      const winner=canonicalResultWinner(r);
      if(winner&&!resultNeedsReplay(r))c=clubObjectForWinner(winner,c);
    }
    return {carrier:c,breadcrumbs:chain};
  }
  const expanded=new Set();
  for(let hop=0;hop<20;hop++){
    const key=canonicalClubKey(carrier.name);
    if(expanded.has(key))break;
    expanded.add(key);
    appendHistory(carrier);
    const resolved=resolveChain();
    const next=resolved.carrier;
    if(canonicalClubKey(next.name)===key){carrier=next;break;}
    carrier=next;
  }
  appendHistory(carrier);
  const resolved=resolveChain();
  return {origin,carrier:resolved.carrier,breadcrumbs:resolved.breadcrumbs};
}'''
journey_pat = re.compile(r'function buildJourney\(origin\)\{.*?\}\s*function previousRoundsHtml', re.S)
text, n = journey_pat.subn(lambda m: new_build + ' function previousRoundsHtml', text, count=1)
if n != 1:
    raise SystemExit(f'ABORT: expected one buildJourney function, replaced {n}')

next_guard = r'''
/* TIN_FOIL_NEXT_ROUND_INTEGRITY_BEGIN */
const tinFoilBaseNextRoundInfo=nextRoundInfo;
nextRoundInfo=function(club){
  const info=tinFoilBaseNextRoundInfo(club);
  if(!info||!info.knownFixture)return info;
  const fixture=info.knownFixture||{};
  const target=String(info.name||'').trim().toLowerCase();
  const actual=String(fixture.round||'').trim().toLowerCase();
  if(target&&actual&&target!==actual){
    return {...info,knownFixture:null};
  }
  return info;
};
/* TIN_FOIL_NEXT_ROUND_INTEGRITY_END */
'''.strip()
# Place this AFTER buildJourney. The upstream competition patcher deliberately
# replaces buildJourney on every health run, so it will remove this block first;
# this patch then reinstalls it. That keeps both patchers safely idempotent.
marker = 'function previousRoundsHtml'
pos = text.find(marker)
if pos < 0:
    raise SystemExit('ABORT: previousRoundsHtml insertion boundary not found')
text = text[:pos] + next_guard + '\n' + text[pos:]

required = (
    "fetch(u,{cache:'no-store'})",
    "+'t='+Date.now()",
    'const candidates=[];',
    'function resolveChain(){',
    'if(!participant)continue;',
    'breadcrumbs:resolved.breadcrumbs',
    'const tinFoilBaseNextRoundInfo=nextRoundInfo;',
    'return {...info,knownFixture:null};',
)
for required_marker in required:
    if required_marker not in text:
        raise SystemExit(f'ABORT: required journey-integrity marker missing: {required_marker}')

if "cache:force?'no-store':'default'" in text:
    raise SystemExit('ABORT: stale default-cache live competition fetch remains')

P.write_text(text, encoding='utf-8')
print('CLUBFINDER JOURNEY INTEGRITY PATCH: SUCCESS')
print('Live competition fetch: cache-busted + no-store')
print('Previous Rounds: filtered to actual custody chain')
print('Next Round: stale current-round fixture suppressed')
print('Competition data itself: UNTOUCHED')
print('Ground records: UNTOUCHED')
