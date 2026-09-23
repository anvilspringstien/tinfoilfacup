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
  const rows=(LIVE_COMPETITION_DATA&&LIVE_COMPETITION_DATA.result_history)||{};
  const results=[];
  const alias={'cray wands':'cray wanderers','hamp and rich':'hampton and richmond borough',
    'weston sm':'weston super mare','dag and red':'dagenham and redbridge',
    'win finch':'wingate and finchley','g borough t':'gainsborough trinity'};
  const identity=x=>alias[canonicalClubKey(x)]||canonicalClubKey(x);
  const matches=(a,b)=>identity(a)===identity(b)||identity(b).startsWith(identity(a)+' ');
  const seen=new Set();
  for(const bucket of Object.values(rows)){
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
elif new_fixture_resolver not in text:
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
if text.count("function verifiedConditionalWinner(")!=1:
    raise SystemExit("ABORT: conditional resolver marker count unexpected")

P.write_text(text, encoding="utf-8")
print("CLUBFINDER REPLAY PROGRESSION PATCH: SUCCESS")
print("Trailing Replay suffix is ignored only when selecting the next round.")
print("Uniquely abbreviated conditional draw alternatives resolve to the custodian.")
print("Competition data: UNTOUCHED")
print("Ground records: UNTOUCHED")
