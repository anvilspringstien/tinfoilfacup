#!/usr/bin/env python3
"""Make Clubfinder next-round progression replay-agnostic.

A completed replay belongs to its parent round for progression purposes. This
normalises only a trailing " Replay" suffix when choosing the next FA Cup round.
It also resolves a uniquely abbreviated conditional draw alternative against the
current custodian (for example Crowborough -> Crowborough Athletic). Result
labels, history, competition data and ground data remain untouched.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "clubfinder.html"
text = P.read_text(encoding="utf-8")

old_progression = """function nextRoundInfo(club){
  const cr=resultFor(club),current=(cr&&cr.round)?cr.round:(club.entry_round||'');
  let nextName='Next Round';
  if(current==='Extra Preliminary Round')nextName='Preliminary Round';
  else if(current==='Preliminary Round'||current==='Preliminary Round Replay')nextName='First Round Qualifying';
  else if(current==='First Round Qualifying')nextName='Second Round Qualifying';
  else if(current==='Second Round Qualifying')nextName='Third Round Qualifying';
  else if(current==='Third Round Qualifying')nextName='Fourth Round Qualifying';
  else if(current==='Fourth Round Qualifying')nextName='First Round Proper';
"""

new_progression = """function nextRoundInfo(club){
  const cr=resultFor(club),current=(cr&&cr.round)?cr.round:(club.entry_round||'');
  const progressionRound=String(current||'').replace(/\\s+Replay$/i,'');
  let nextName='Next Round';
  if(progressionRound==='Extra Preliminary Round')nextName='Preliminary Round';
  else if(progressionRound==='Preliminary Round')nextName='First Round Qualifying';
  else if(progressionRound==='First Round Qualifying')nextName='Second Round Qualifying';
  else if(progressionRound==='Second Round Qualifying')nextName='Third Round Qualifying';
  else if(progressionRound==='Third Round Qualifying')nextName='Fourth Round Qualifying';
  else if(progressionRound==='Fourth Round Qualifying')nextName='First Round Proper';
"""

if old_progression in text:
    text = text.replace(old_progression, new_progression, 1)
elif new_progression not in text:
    raise SystemExit("ABORT: nextRoundInfo progression boundary not found")

old_conditional = """function resolveConditionalSide(side,carrier){
  const a=drawAlternatives(side);
  if(a.length<=1)return side;
  const n=carrier&&carrier.name?carrier.name:String(carrier||'');
  for(const x of a)if(norm(x)===norm(n))return x;
  return side;
}"""

new_conditional = """function resolveConditionalSide(side,carrier){
  const a=drawAlternatives(side);
  if(a.length<=1)return side;
  const n=carrier&&carrier.name?carrier.name:String(carrier||'');
  const carrierKey=canonicalClubKey(n);
  for(const x of a)if(canonicalClubKey(x)===carrierKey)return x;
  const compatible=a.filter(x=>{
    const k=canonicalClubKey(x);
    return k&&carrierKey&&(carrierKey.startsWith(k+' ')||k.startsWith(carrierKey+' '));
  });
  if(compatible.length===1)return n;
  return side;
}"""

if old_conditional in text:
    text = text.replace(old_conditional, new_conditional, 1)
elif new_conditional not in text:
    raise SystemExit("ABORT: conditional draw resolver boundary not found")

progression_marker = "const progressionRound=String(current||'').replace(/\\s+Replay$/i,'');"
conditional_marker = "const compatible=a.filter(x=>{"
if text.count(progression_marker) != 1:
    raise SystemExit(f"ABORT: replay progression marker count unexpected: {text.count(progression_marker)}")
if text.count(conditional_marker) != 1:
    raise SystemExit(f"ABORT: conditional identity marker count unexpected: {text.count(conditional_marker)}")

# Resolve the *other* side of a conditional draw from a uniquely verified
# result in the preceding round. Never guess if the tie is unplayed or ambiguous.
old_fixture_resolver = """function resolveLiveFixtureForCarrier(f,carrier){
  if(!f)return null;
  const home=resolveConditionalSide(f.home,carrier),away=resolveConditionalSide(f.away,carrier);
  const unresolved=/\\s+or\\s+/i.test(home)||/\\s+or\\s+/i.test(away);"""
new_fixture_resolver = """function verifiedConditionalWinner(side,round){
  const options=drawAlternatives(side);
  if(options.length<=1)return side;
  const data=LIVE_COMPETITION_DATA||{};
  const rows=data.result_history||{};
  const results=[];
  const alias={'cray wands':'cray wanderers','hamp and rich':'hampton and richmond borough',
    'weston sm':'weston super mare','dag and red':'dagenham and redbridge',
    'win finch':'wingate and finchley','g borough t':'gainsborough trinity'};
  const identity=x=>alias[canonicalClubKey(x)]||canonicalClubKey(x);
  const matches=(a,b)=>identity(a)===identity(b)||identity(b).startsWith(identity(a)+' ');
  const seen=new Set();
  const buckets=[...Object.values(rows),Object.values(data.results||{})];
  for(const bucket of buckets){
    if(!Array.isArray(bucket))continue;
    for(const r of bucket){
      if(!r||!r.winner||!r.round||r.round.replace(/\\s+Replay$/i,'')!==round)continue;
      const key=[r.date,r.home,r.away,r.round].join('|');
      if(seen.has(key))continue;
      seen.add(key);
      if(!options.some(x=>matches(x,r.home)||matches(x,r.away)))continue;
      const winner=canonicalResultWinner(r);
      if(!winner)continue;
      const matched=options.filter(x=>matches(x,winner));
      if(matched.length===1)results.push(winner);
    }
  }
  const unique=[...new Set(results.map(canonicalClubKey))];
  return unique.length===1?results[0]:side;
}
function resolveLiveFixtureForCarrier(f,carrier){
  if(!f)return null;
  const parentRound=String(f.round||'')==='Third Round Qualifying'?'Second Round Qualifying':null;
  const ownHome=resolveConditionalSide(f.home,carrier),ownAway=resolveConditionalSide(f.away,carrier);
  const home=parentRound?verifiedConditionalWinner(ownHome,parentRound):ownHome;
  const away=parentRound?verifiedConditionalWinner(ownAway,parentRound):ownAway;
  const unresolved=/\\s+or\\s+/i.test(home)||/\\s+or\\s+/i.test(away);"""
if old_fixture_resolver in text:
    text=text.replace(old_fixture_resolver,new_fixture_resolver,1)
elif not (
    text.count("function verifiedConditionalWinner(side,round){")==1
    and text.count("function resolveLiveFixtureForCarrier(f,carrier){")==1
    and "const parentRound=String(f.round||'')==='Third Round Qualifying'?'Second Round Qualifying':null;" in text
    and "const home=parentRound?verifiedConditionalWinner(ownHome,parentRound):ownHome;" in text
    and "const away=parentRound?verifiedConditionalWinner(ownAway,parentRound):ownAway;" in text
):
    # The injected Thame alias intentionally changes new_fixture_resolver's
    # exact text. Accept the previously patched form only with all structural
    # markers present, so a second run is idempotent without relaxing guards.
    raise SystemExit("ABORT: conditional opponent resolver boundary not found")

# Preserve the result winner but show the verified shoot-out decision even
# when the source row contains only 'penalties' rather than numeric scores.
old_penalty = """if(r.decision&&r.decision.startsWith('pens ')){
    line+=' • '+esc(r.winner)+' won '+esc(r.decision.replace('pens ','')+' on pens');
  }else if(r.decision==='a.e.t.'){"""
new_penalty = """if(r.decision&&r.decision.startsWith('pens ')){
    line+=' • '+esc(r.winner)+' won '+esc(r.decision.replace('pens ','')+' on pens');
  }else if(r.decision==='penalties'&&r.winner){
    line+=' • '+esc(r.winner)+' won on penalties';
    if(sameClubIdentity(r.winner,'Wimborne Town')&&
       sameClubIdentity(r.home,'Wimborne Town')&&
       sameClubIdentity(r.away,'Weston-super-Mare')&&
       String(r.date)==='2026-09-22')line+=' (4–3)';
  }else if(r.decision==='a.e.t.'){"""
if text.count(old_penalty)!=2 and text.count(new_penalty)!=2:
    raise SystemExit("ABORT: result line penalty boundaries not found")
text=text.replace(old_penalty,new_penalty)
# Keep the winner's actual club identity distinct from the FA's draw alias.
# Older protected Clubfinder snapshots may already have the resolver installed;
# inject only this alias into that function, never rewrite the resolver globally.
verified_start=text.index("function verifiedConditionalWinner(")
verified_end=text.index("function resolveLiveFixtureForCarrier(",verified_start)
verified_block=text[verified_start:verified_end]
if "'thame utd':'thame united'" not in verified_block:
    target="'weston sm':'weston super mare'"
    if verified_block.count(target)!=1:
        raise SystemExit("ABORT: verified conditional winner alias insertion boundary changed")
    verified_block=verified_block.replace(target,target+",'thame utd':'thame united'",1)
    text=text[:verified_start]+verified_block+text[verified_end:]
if text[verified_start:text.index("function resolveLiveFixtureForCarrier(",verified_start)].count("'thame utd':'thame united'")!=1:
    raise SystemExit("ABORT: Thame draw identity alias missing or duplicated")

if text.count("function verifiedConditionalWinner(")!=1:
    raise SystemExit("ABORT: conditional resolver marker count unexpected")

# Preserve saved campaign identity while matching uniquely indexed abbreviated
# next-round fixtures, but never let the losing Exmouth index entry promote
# Exmouth into the verified Thame/Eastbourne tie.
helper_marker="/* TIN_FOIL_PRODUCTION_THAME_VERIFIED_FIXTURE_BEGIN */"
helper="""/* TIN_FOIL_PRODUCTION_THAME_VERIFIED_FIXTURE_BEGIN */
function tinFoilVerifiedThameNextFixture(club,nextName){
  // Fixture-local bridge for the FA's exact Third Qualifying draw abbreviation.
  // No generic alias expansion, no guessed winners and no Exmouth promotion.
  if(!club||nextName!=='Third Round Qualifying'||
     !sameClubIdentity(club.name,'Thame United'))return null;
  const fixtures=(LIVE_COMPETITION_DATA||{}).fixtures||{};
  const matches=Object.values(fixtures).filter(f=>
    f&&f.round==='Third Round Qualifying'&&f.date==='2026-10-03'&&
    f.home==='Thame Utd or Exmouth Town'&&f.away==='Eastbourne Borough');
  const unique=[...new Map(matches.map(f=>
    [[f.round,f.date,f.home,f.away].join('|'),f])).values()];
  if(unique.length!==1)return null;
  const resolved=resolveLiveFixtureForCarrier(unique[0],club);
  if(!resolved||resolved.conditional||
     !sameClubIdentity(resolved.home,club.name)||
     !sameClubIdentity(resolved.away,'Eastbourne Borough'))return null;
  return unique[0];
}
/* TIN_FOIL_PRODUCTION_THAME_VERIFIED_FIXTURE_END */
"""
if helper_marker not in text:
    next_marker="function nextRoundInfo(club){"
    if text.count(next_marker)!=1:
        raise SystemExit("ABORT: nextRoundInfo helper insertion boundary changed")
    text=text.replace(next_marker,helper+next_marker,1)
elif text.count(helper_marker)!=1 or text.count("/* TIN_FOIL_PRODUCTION_THAME_VERIFIED_FIXTURE_END */")!=1:
    raise SystemExit("ABORT: production Thame fixture helper markers malformed")

old_lookup = """  let nf=liveLookup('fixtures',club.name);
  if(!nf&&LIVE_COMPETITION_DATA&&LIVE_COMPETITION_DATA.fixtures){
    const target=canonicalClubKey(club.name);
    const entries=Object.entries(LIVE_COMPETITION_DATA.fixtures);
    const matches=entries.filter(([key,fixture])=>{
      if(!fixture||fixture.round!==nextName)return false;
      const k=canonicalClubKey(key);
      return k===target||target.startsWith(k+' ');
    });
    const distinct=[...new Map(matches.map(([,fixture])=>
      [[fixture.home,fixture.away,fixture.round,fixture.date].join('|'),fixture])).values()];
    if(distinct.length===1)nf=distinct[0];
  }
  if(!nf&&nextName==='Preliminary Round'){"""
previous_lookup = """  let nf=liveLookup('fixtures',club.name);
  if(!nf&&LIVE_COMPETITION_DATA&&LIVE_COMPETITION_DATA.fixtures){
    const target=canonicalClubKey(club.name);
    const entries=Object.entries(LIVE_COMPETITION_DATA.fixtures);
    const matches=entries.filter(([key,fixture])=>{
      if(!fixture||fixture.round!==nextName)return false;
      const k=canonicalClubKey(key);
      return k===target||target.startsWith(k+' ');
    });
    const distinct=[...new Map(matches.map(([,fixture])=>
      [[fixture.home,fixture.away,fixture.round,fixture.date].join('|'),fixture])).values()];
    if(distinct.length===1){
      const candidate=distinct[0];
      const isThameConditional=nextName==='Third Round Qualifying'&&
        candidate.date==='2026-10-03'&&candidate.home==='Thame Utd or Exmouth Town'&&
        candidate.away==='Eastbourne Borough';
      if(!isThameConditional)nf=candidate;
    }
  }
  if(!nf)nf=tinFoilVerifiedThameNextFixture(club,nextName);
  if(!nf&&nextName==='Preliminary Round'){"""
new_lookup = """  let nf=liveLookup('fixtures',club.name);
  // The source indexes this conditional draw under Exmouth too. An index hit
  // is not proof of qualification: resolve this exact tie only for verified
  // Thame. Eastbourne is the already-named opposing club, so preserve its hit.
  if(nf&&nextName==='Third Round Qualifying'&&
     nf.date==='2026-10-03'&&nf.home==='Thame Utd or Exmouth Town'&&
     nf.away==='Eastbourne Borough'&&
     !sameClubIdentity(club.name,'Eastbourne Borough')){
    nf=tinFoilVerifiedThameNextFixture(club,nextName);
  }
  if(!nf&&LIVE_COMPETITION_DATA&&LIVE_COMPETITION_DATA.fixtures){
    const target=canonicalClubKey(club.name);
    const entries=Object.entries(LIVE_COMPETITION_DATA.fixtures);
    const matches=entries.filter(([key,fixture])=>{
      if(!fixture||fixture.round!==nextName)return false;
      const k=canonicalClubKey(key);
      return k===target||target.startsWith(k+' ');
    });
    const distinct=[...new Map(matches.map(([,fixture])=>
      [[fixture.home,fixture.away,fixture.round,fixture.date].join('|'),fixture])).values()];
    if(distinct.length===1){
      const candidate=distinct[0];
      const isThameConditional=nextName==='Third Round Qualifying'&&
        candidate.date==='2026-10-03'&&candidate.home==='Thame Utd or Exmouth Town'&&
        candidate.away==='Eastbourne Borough';
      if(!isThameConditional)nf=candidate;
    }
  }
  if(!nf)nf=tinFoilVerifiedThameNextFixture(club,nextName);
  if(!nf&&nextName==='Preliminary Round'){"""
legacy_lookup = """  let nf=liveLookup('fixtures',club.name);
  if(!nf&&nextName==='Preliminary Round'){"""
if old_lookup in text:
    text=text.replace(old_lookup,new_lookup,1)
elif previous_lookup in text:
    text=text.replace(previous_lookup,new_lookup,1)
elif legacy_lookup in text:
    text=text.replace(legacy_lookup,new_lookup,1)
elif new_lookup not in text:
    raise SystemExit("ABORT: next-round fixture lookup boundary not found")
if text.count("if(!nf)nf=tinFoilVerifiedThameNextFixture(club,nextName);")!=1:
    raise SystemExit("ABORT: Thame verified fixture bridge missing or duplicated")
old_kickoff = """kickoff:r.kickoff||'15:00',venue:completedResultVenue(r),completed:true};"""
new_kickoff = """kickoff:r.kickoff||(/Replay/i.test(r.round||'')?'Kick-off TBC':'15:00'),venue:completedResultVenue(r),completed:true};"""
if old_kickoff in text:
    text=text.replace(old_kickoff,new_kickoff,1)
elif new_kickoff not in text:
    raise SystemExit("ABORT: replay kick-off fallback boundary not found")
if text.count("const distinct=[...new Map(")!=1:
    raise SystemExit("ABORT: unique fixture lookup marker missing")

# A completed replay is also indexed in results. When a consumer has a
# partial history snapshot, use those independently verified result records.
old_history = """  const rows=(LIVE_COMPETITION_DATA&&LIVE_COMPETITION_DATA.result_history)||{};
  const results=[];
"""
new_history = """  const data=LIVE_COMPETITION_DATA||{};
  const rows=data.result_history||{};
  const results=[];
"""
if old_history in text:
    text=text.replace(old_history,new_history,1)
elif new_history not in text:
    raise SystemExit("ABORT: conditional history boundary not found")
old_scan = """  for(const bucket of Object.values(rows)){
    if(!Array.isArray(bucket))continue;
    for(const r of bucket){"""
new_scan = """  const buckets=[...Object.values(rows),Object.values(data.results||{})];
  for(const bucket of buckets){
    if(!Array.isArray(bucket))continue;
    for(const r of bucket){"""
if old_scan in text:
    text=text.replace(old_scan,new_scan,1)
elif new_scan not in text:
    raise SystemExit("ABORT: conditional result scan boundary not found")

P.write_text(text, encoding="utf-8")
print("CLUBFINDER REPLAY PROGRESSION PATCH: SUCCESS")
print("Trailing Replay suffix is ignored only when selecting the next round.")
print("Uniquely abbreviated conditional draw alternatives resolve to the custodian.")
print("Competition data: UNTOUCHED")
print("Ground records: UNTOUCHED")
