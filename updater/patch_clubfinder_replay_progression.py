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

P.write_text(text, encoding="utf-8")
print("CLUBFINDER REPLAY PROGRESSION PATCH: SUCCESS")
print("Trailing Replay suffix is ignored only when selecting the next round.")
print("Uniquely abbreviated conditional draw alternatives resolve to the custodian.")
print("Competition data: UNTOUCHED")
print("Ground records: UNTOUCHED")
