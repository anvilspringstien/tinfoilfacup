#!/usr/bin/env python3
"""Guard Clubfinder journey integrity and next-round presentation.

Responsibilities:
1. Always fetch the live competition snapshot with cache-busting/no-store semantics.
2. Return Previous Rounds breadcrumbs only for the actual Tin Foil FA Cup custody chain.
3. Re-resolve the displayed custodian from the resolved breadcrumb chronology at the render boundary.
4. Do not render the first Campaign card until the live competition refresh attempt has finished.
5. Never present the just-played/current-round fixture as the known fixture for the next round.
6. Present next-round dates in a human-friendly British format.
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

render_helper = r'''function tinFoilJourneyForRender(origin){
  const journey=buildJourney(origin);
  let carrier=origin;
  const ordered=[...(journey.breadcrumbs||[])].sort((a,b)=>resultSortValue(a.result)-resultSortValue(b.result));
  for(const item of ordered){
    const r=item.result||{};
    const participant=sameClubIdentity(r.home,carrier.name)||sameClubIdentity(r.away,carrier.name);
    if(!participant)continue;
    const winner=canonicalResultWinner(r);
    if(winner&&!resultNeedsReplay(r)){
      carrier=clubByDisplayName(winner)||candidateClubByName(winner)||{name:winner,entry_round:carrier.entry_round||'',fixture:{}};
    }
  }
  return {...journey,carrier};
}
'''
if 'function tinFoilJourneyForRender(origin)' not in text:
    marker = 'function previousRoundsHtml'
    pos = text.find(marker)
    if pos < 0:
        raise SystemExit('ABORT: previousRoundsHtml render-helper boundary not found')
    text = text[:pos] + render_helper + text[pos:]

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
marker = 'function previousRoundsHtml'
pos = text.find(marker)
if pos < 0:
    raise SystemExit('ABORT: previousRoundsHtml insertion boundary not found')
text = text[:pos] + next_guard + '\n' + text[pos:]

old_render_journey = 'j=buildJourney(origin),c=j.carrier||origin'
new_render_journey = 'j=tinFoilJourneyForRender(origin),c=j.carrier||origin'
if old_render_journey in text:
    text = text.replace(old_render_journey, new_render_journey, 1)
elif new_render_journey not in text:
    raise SystemExit('ABORT: Campaign card journey-selection boundary not found')

old_go = "async function go(){\n const input=document.getElementById('postcode')"
new_go = "async function go(){\n await tinFoilCompetitionReady;\n const input=document.getElementById('postcode')"
identity_old_go = "async function go(userInitiated=false){\n const input=document.getElementById('postcode')"
identity_new_go = "async function go(userInitiated=false){\n await tinFoilCompetitionReady;\n const input=document.getElementById('postcode')"
if old_go in text:
    text = text.replace(old_go, new_go, 1)
elif identity_old_go in text:
    text = text.replace(identity_old_go, identity_new_go, 1)
elif new_go not in text and identity_new_go not in text:
    raise SystemExit('ABORT: Campaign go() readiness boundary not found')

old_boot = '\nrefreshCompetitionData(false);\n</script>'
new_boot = '\nconst tinFoilCompetitionReady=refreshCompetitionData(false);\n</script>'
if old_boot in text:
    text = text.replace(old_boot, new_boot, 1)
elif new_boot not in text:
    raise SystemExit('ABORT: competition refresh bootstrap boundary not found')

# Human-facing next-round dates should never leak the canonical ISO storage form.
old_date = "'<br>'+esc(next.date)+"
new_date = "'<br>'+esc(tinFoilDisplayDate(next.date))+"
if old_date in text:
    text = text.replace(old_date, new_date, 1)
elif new_date not in text:
    raise SystemExit('ABORT: next-round date renderer boundary not found')

helper = r'''function tinFoilDisplayDate(value){
  if(!value)return 'Date TBC';
  const raw=String(value).trim();
  const d=new Date(raw+'T12:00:00');
  if(Number.isNaN(d.getTime()))return raw;
  return d.toLocaleDateString('en-GB',{weekday:'long',day:'numeric',month:'long',year:'numeric'});
}
'''
if 'function tinFoilDisplayDate(value)' not in text:
    state_marker = 'function stateHtml(club)'
    state_pos = text.find(state_marker)
    if state_pos < 0:
        raise SystemExit('ABORT: stateHtml insertion boundary not found')
    text = text[:state_pos] + helper + text[state_pos:]

required = (
    "fetch(u,{cache:'no-store'})",
    "+'t='+Date.now()",
    'const candidates=[];',
    'function resolveChain(){',
    'if(!participant)continue;',
    'breadcrumbs:resolved.breadcrumbs',
    'function tinFoilJourneyForRender(origin)',
    'j=tinFoilJourneyForRender(origin),c=j.carrier||origin',
    'await tinFoilCompetitionReady;',
    'const tinFoilCompetitionReady=refreshCompetitionData(false);',
    'const tinFoilBaseNextRoundInfo=nextRoundInfo;',
    'return {...info,knownFixture:null};',
    'function tinFoilDisplayDate(value)',
    "weekday:'long',day:'numeric',month:'long',year:'numeric'",
    "'<br>'+esc(tinFoilDisplayDate(next.date))+",
)
for required_marker in required:
    if required_marker not in text:
        raise SystemExit(f'ABORT: required journey-integrity marker missing: {required_marker}')

if "cache:force?'no-store':'default'" in text:
    raise SystemExit('ABORT: stale default-cache live competition fetch remains')
if '\nrefreshCompetitionData(false);\n</script>' in text:
    raise SystemExit('ABORT: untracked competition refresh bootstrap remains')

P.write_text(text, encoding='utf-8')
print('CLUBFINDER JOURNEY INTEGRITY PATCH: SUCCESS')
print('Live competition fetch: cache-busted + no-store')
print('First Campaign render waits for live competition refresh attempt')
print('Campaign card custodian: re-resolved from decisive breadcrumb chronology')
print('Previous Rounds: filtered to actual custody chain')
print('Next Round: stale current-round fixture suppressed')
print('Next Round date: long-form en-GB display')
print('Competition data itself: UNTOUCHED')
print('Ground records: UNTOUCHED')
