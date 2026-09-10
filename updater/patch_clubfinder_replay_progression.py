#!/usr/bin/env python3
"""Make Clubfinder next-round progression replay-agnostic.

A completed replay belongs to its parent round for progression purposes. This
normalises only a trailing " Replay" suffix when choosing the next FA Cup round;
result labels, history, competition data and ground data remain untouched.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "clubfinder.html"
text = P.read_text(encoding="utf-8")

old = """function nextRoundInfo(club){
  const cr=resultFor(club),current=(cr&&cr.round)?cr.round:(club.entry_round||'');
  let nextName='Next Round';
  if(current==='Extra Preliminary Round')nextName='Preliminary Round';
  else if(current==='Preliminary Round'||current==='Preliminary Round Replay')nextName='First Round Qualifying';
  else if(current==='First Round Qualifying')nextName='Second Round Qualifying';
  else if(current==='Second Round Qualifying')nextName='Third Round Qualifying';
  else if(current==='Third Round Qualifying')nextName='Fourth Round Qualifying';
  else if(current==='Fourth Round Qualifying')nextName='First Round Proper';
"""

new = """function nextRoundInfo(club){
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

if old in text:
    text = text.replace(old, new, 1)
elif new not in text:
    raise SystemExit("ABORT: nextRoundInfo progression boundary not found")

marker = "const progressionRound=String(current||'').replace(/\\s+Replay$/i,'');"
if text.count(marker) != 1:
    raise SystemExit(f"ABORT: replay progression marker count unexpected: {text.count(marker)}")

P.write_text(text, encoding="utf-8")
print("CLUBFINDER REPLAY PROGRESSION PATCH: SUCCESS")
print("Trailing Replay suffix is ignored only when selecting the next round.")
print("All qualifying-round replays therefore advance through the normal round map.")
print("Competition data: UNTOUCHED")
print("Ground records: UNTOUCHED")
