#!/usr/bin/env python3
"""Guarded, idempotent 2026–27 Holmesdale merger repair. BETA HTML only."""
from pathlib import Path
import argparse

BETA=Path("beta/clubfinder-beta.html")
BEGIN="/* TIN_FOIL_BETA_HOLMESDALE_2026_BEGIN */"
END="/* TIN_FOIL_BETA_HOLMESDALE_2026_END */"
OLD_SAME="function sameClubIdentity(a,b){return canonicalClubKey(a)===canonicalClubKey(b);}"
NEW_SAME="function sameClubIdentity(a,b){return tinFoilBetaCompetitionClubKey(a)===tinFoilBetaCompetitionClubKey(b);}"
HELPER="""/* TIN_FOIL_BETA_HOLMESDALE_2026_BEGIN */
// Only activate the retired Holmesdale name for the actual 2026–27 merger
// when canonical competition history proves the 8 August Petts Wood tie.
// Do NOT change canonicalClubKey: postcode selection and ground history are
// independent of competition identity.
function tinFoilBetaHolmesdale2026Ready(){
  const d=LIVE_COMPETITION_DATA||{};
  const rows=(d.result_history||{})['Petts Wood & Holmesdale'];
  return Array.isArray(rows)&&rows.some(r=>r&&
    r.round==='Extra Preliminary Round'&&r.date==='2026-08-08'&&
    canonicalClubKey(r.home)==='petts wood and holmesdale'&&
    canonicalClubKey(r.away)==='tooting and mitcham united');
}
function tinFoilBetaCompetitionClubKey(name){
  const key=canonicalClubKey(name);
  return key==='holmesdale'&&tinFoilBetaHolmesdale2026Ready()
    ?'petts wood and holmesdale':key;
}
/* TIN_FOIL_BETA_HOLMESDALE_2026_END */
"""
OLD_LOOKUP="""  const target=canonicalClubKey(raw);
  if(!target)return null;
  for(const [key,value] of Object.entries(obj)){
    if(canonicalClubKey(key)===target)return value;
  }"""
NEW_LOOKUP="""  // Explicit 2026–27 merger identity only; never rewrite surveyed ground keys.
  const target=tinFoilBetaCompetitionClubKey(raw);
  if(!target)return null;
  for(const [key,value] of Object.entries(obj)){
    if(tinFoilBetaCompetitionClubKey(key)===target)return value;
  }"""
OLD_VENUE="""  const rv=result.venue||{};
  const homeClub=candidateClubByName(result.home);"""
NEW_VENUE="""  const rv=result.venue||{};
  // The 8 August merged-club home tie predates the explicit per-match venue
  // now available for 5 September. Supply a postcode-only fallback using the
  // independently surveyed former Holmesdale home location, not a guessed
  // 2026 sponsor name. Per-match verified venue names remain authoritative.
  if(result.date==='2026-08-08'&&
     canonicalClubKey(result.home)==='petts wood and holmesdale'&&
     !rv.postcode&&!rv.ground&&tinFoilBetaHolmesdale2026Ready()){
    const home=groundByClubName('Holmesdale FC');
    if(String(home.postcode||'').toUpperCase().replace(/\s+/g,'')==='BR28HQ')
      return {ground:'Ground name unconfirmed',postcode:home.postcode,
        lat:home.lat,lon:home.lon,verification:'unverified'};
  }
  const homeClub=candidateClubByName(result.home);"""

def exactly_one(src,needle,label):
    n=src.count(needle)
    if n!=1:raise RuntimeError(f"{label}: expected exactly one marker, found {n}")
def replace_idempotent(src,old,new,label):
    if old in src:
        exactly_one(src,old,label+" old")
        if new in src:raise RuntimeError(label+": old and new variants both present")
        return src.replace(old,new,1)
    exactly_one(src,new,label+" applied")
    return src
def patch(src):
    if src.count(BEGIN)==0 and src.count(END)==0:
        exactly_one(src,OLD_SAME,"sameClubIdentity insertion boundary")
        src=src.replace(OLD_SAME,HELPER+NEW_SAME,1)
    else:
        exactly_one(src,BEGIN,"merger begin")
        exactly_one(src,END,"merger end")
        exactly_one(src,NEW_SAME,"merged identity")
    src=replace_idempotent(src,OLD_LOOKUP,NEW_LOOKUP,"live lookup")
    src=replace_idempotent(src,OLD_VENUE,NEW_VENUE,"historical venue fallback")
    if src.count(BEGIN)!=1 or src.count(END)!=1:
        raise RuntimeError("merger marker corruption")
    return src
def main():
    arg=argparse.ArgumentParser()
    arg.add_argument("--check",action="store_true")
    opts=arg.parse_args()
    before=BETA.read_text(encoding="utf-8")
    after=patch(before)
    if opts.check:
        if before!=after:raise SystemExit("BETA Holmesdale identity patch missing or stale")
        print("BETA Holmesdale patch idempotency: PASS")
    elif before!=after:
        BETA.write_text(after,encoding="utf-8")
        print("Patched BETA-only explicit Holmesdale 2026 merger; production untouched")
    else:
        print("BETA Holmesdale patch already applied; idempotent")
if __name__=="__main__":main()
