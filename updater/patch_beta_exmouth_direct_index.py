#!/usr/bin/env python3
"""BETA-only, fixture-local Exmouth index guard; protected production untouched."""
from pathlib import Path

root = Path(__file__).resolve().parents[1]
path = root / "beta/clubfinder-beta.html"
text = path.read_text(encoding="utf-8")
old = """  let nf=liveLookup('fixtures',club.name);
  if(!nf)nf=liveConditionalFixtureForClub(club.name);
  if(!nf)nf=tinFoilBetaVerifiedThameNextFixture(club,nextName);"""
new = """  let nf=liveLookup('fixtures',club.name);
  if(!nf)nf=liveConditionalFixtureForClub(club.name);
  // The FA indexes this draw under the eventual loser too. Index presence
  // does not establish progress. Preserve alternatives only before a result.
  if(nf&&nextName==='Third Round Qualifying'&&
     nf.date==='2026-10-03'&&nf.home==='Thame Utd or Exmouth Town'&&
     nf.away==='Eastbourne Borough'&&
     !sameClubIdentity(club.name,'Eastbourne Borough')){
    const verified=verifiedConditionalWinner(nf.home,'Second Round Qualifying');
    if(!/\\s+or\\s+/i.test(verified)){
      nf=sameClubIdentity(verified,'Thame United')&&
         sameClubIdentity(club.name,verified)
        ?tinFoilBetaVerifiedThameNextFixture(club,nextName):null;
    }else if(!preserveConditional){
      nf=null;
    }
  }
  if(!nf)nf=tinFoilBetaVerifiedThameNextFixture(club,nextName);"""
if text.count(old) == 1:
    text = text.replace(old, new, 1)
    path.write_text(text, encoding="utf-8")
elif text.count(new) != 1:
    raise SystemExit("ABORT: BETA direct nextRoundInfo index boundary changed")
if text.count("const verified=verifiedConditionalWinner(nf.home,'Second Round Qualifying');") != 1:
    raise SystemExit("ABORT: BETA verified draw guard missing or duplicated")
print("BETA DIRECT EXMOUTH INDEX GUARD: PASS")
print("Production and canonical competition data: UNTOUCHED")
