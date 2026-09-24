#!/usr/bin/env python3
"""Guarded BETA-only fixture-local lookup for verified Thame United replay custody.

Run ONLY against beta/clubfinder-beta.html. Never changes production or canonical
competition data. An unknown source shape fails closed rather than silently editing.
"""
from pathlib import Path
R=Path(__file__).resolve().parents[1]
path=R/"beta/clubfinder-beta.html"
s=path.read_text(encoding="utf-8")
BEGIN="/* TIN_FOIL_BETA_THAME_VERIFIED_FIXTURE_BEGIN */"
END="/* TIN_FOIL_BETA_THAME_VERIFIED_FIXTURE_END */"
helper="""/* TIN_FOIL_BETA_THAME_VERIFIED_FIXTURE_BEGIN */
function tinFoilBetaVerifiedThameNextFixture(club,nextName){
  // Fixture-local bridge for the FA's exact Third Qualifying draw abbreviation.
  // No generic alias expansion, no guessed winners and no Exmouth promotion.
  if(!club||nextName!=='Third Round Qualifying'||
     !sameClubIdentity(club.name,'Thame United'))return null;
  const fixtures=(LIVE_COMPETITION_DATA||{}).fixtures||{};
  const matches=Object.values(fixtures).filter(f=>
    f&&f.round==='Third Round Qualifying'&&f.date==='2026-10-03'&&
    f.home==='Thame Utd or Exmouth Town'&&f.away==='Eastbourne Borough');
  // Three index keys may point to the same published draw; require one
  // unique matching fixture, not one matching index entry.
  const unique=[...new Map(matches.map(f=>
    [[f.round,f.date,f.home,f.away].join('|'),f])).values()];
  if(unique.length!==1)return null;
  const resolved=resolveLiveFixtureForCarrier(unique[0],club,true);
  if(!resolved||resolved.conditional||
     !sameClubIdentity(resolved.home,club.name)||
     !sameClubIdentity(resolved.away,'Eastbourne Borough'))return null;
  return unique[0];
}
/* TIN_FOIL_BETA_THAME_VERIFIED_FIXTURE_END */
"""
anchor="function nextRoundInfo(club,preserveConditional){"
fallback="  if(!nf)nf=liveConditionalFixtureForClub(club.name);"
new_fallback=fallback+"\n  if(!nf)nf=tinFoilBetaVerifiedThameNextFixture(club,nextName);"
if BEGIN in s or END in s:
    if s.count(BEGIN)==s.count(END)==1 and new_fallback in s and s.count("function tinFoilBetaVerifiedThameNextFixture(")==1:
        print("BETA THAME VERIFIED FIXTURE PATCH: PASS (idempotent)")
        raise SystemExit(0)
    raise SystemExit("ABORT: existing BETA Thame patch is incomplete or duplicated")
if s.count(anchor)!=1 or s.count(fallback)!=1 or s.count(new_fallback)!=0:
    raise SystemExit("ABORT: BETA source anchors changed; do not patch blindly")
s=s.replace(anchor,helper+anchor,1).replace(fallback,new_fallback,1)
if s.count(BEGIN)!=1 or s.count(END)!=1 or s.count(new_fallback)!=1:
    raise SystemExit("ABORT: postpatch integrity check failed")
path.write_text(s,encoding="utf-8")
print("BETA THAME VERIFIED FIXTURE PATCH: PASS")
print("Changed beta/clubfinder-beta.html only; production and competition untouched")
