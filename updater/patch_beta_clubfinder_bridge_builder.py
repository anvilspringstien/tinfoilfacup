#!/usr/bin/env python3
"""One-time, guarded BETA Clubfinder Stage C pure bridge-builder extraction.

Edit ONLY the verified full BETA Clubfinder file in the isolated Stage C branch.
The full 4.6 MB file is patched inside GitHub Actions; large connector uploads
are unreliable. Fail closed on every unexpected original-source change.
"""
import argparse
import hashlib
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
TARGET=ROOT/"beta/clubfinder-beta.html"
EXPECTED_ORIGINAL_SHA256="aef5737e7a54e66b9754c11c2796ea2586f5f70c2d4239cba9d8767d70dfb858"
START="async function openChallenges(origin){"
END="\nasync function journeyCertificate("
OLD_STATS=" const statsSnapshot=tinFoilChallengeStatsSnapshot(origin,journey,crumbs,saved,Number.isFinite(pm.miles)?pm.miles:0);"
OLD_TRUTH=" const truth={source:'Clubfinder v7.6',originName:origin.name,currentCustodian:(journey.carrier||origin).name,postcode:saved&&saved.postcode||'',selectedAt:saved&&saved.selectedAt||null,searchNumber:saved&&saved.searchNumber||null,callSign:tinFoilSavedCallSign(saved),pigeonName:tinFoilSavedPigeonName(saved),tiesPlayed:crumbs.length,awayTies:away,pigeonMiles:Number.isFinite(pm.miles)?pm.miles:0,campaignRound:ri,ended:!!(saved&&saved.ended),statsSnapshot,updatedAt:new Date().toISOString()};"
NEW_STATS=(" const verifiedMiles=Number.isFinite(pm.miles)?pm.miles:0;\n"
           " const statsSnapshot=tinFoilChallengeStatsSnapshot(origin,journey,crumbs,saved,verifiedMiles);")
NEW_TRUTH=(" const truth=tinFoilBuildChallengeBridgeRecord("
           "origin,journey,crumbs,saved,"
           "{awayTies:away,pigeonMiles:verifiedMiles,campaignRound:ri},"
           "statsSnapshot,new Date().toISOString());")
HELPER="""// Stage C: pure v1 bridge assembly. Keep source-of-truth calculations and
// browser storage/navigation in openChallenges; the timestamp is passed in.
function tinFoilBuildChallengeBridgeRecord(origin,journey,crumbs,saved,progress,statsSnapshot,updatedAt){
 return {
  source:'Clubfinder v7.6',
  originName:origin.name,
  currentCustodian:(journey.carrier||origin).name,
  postcode:saved&&saved.postcode||'',
  selectedAt:saved&&saved.selectedAt||null,
  searchNumber:saved&&saved.searchNumber||null,
  callSign:tinFoilSavedCallSign(saved),
  pigeonName:tinFoilSavedPigeonName(saved),
  tiesPlayed:crumbs.length,
  awayTies:progress.awayTies,
  pigeonMiles:progress.pigeonMiles,
  campaignRound:progress.campaignRound,
  ended:!!(saved&&saved.ended),
  statsSnapshot,
  updatedAt
 };
}

"""

def exactly_once(text,part,label):
    if text.count(part)!=1:
        raise ValueError(f"ABORT: {label}: expected one occurrence, found {text.count(part)}")

def validate_done(text):
    exactly_once(text,"function tinFoilBuildChallengeBridgeRecord(","pure builder")
    exactly_once(text,HELPER,"exact unmodified pure builder")
    exactly_once(text,NEW_STATS,"canonical verified miles reused")
    exactly_once(text,NEW_TRUTH,"pure builder call")
    if OLD_TRUTH in text or OLD_STATS in text:
        raise ValueError("ABORT: obsolete inline bridge record remains")
    a=text.index(START);b=text.index(END,a)
    consumer=text[a:b]
    for token in (
        "function venueForChallenge(r){return completedResultVenue(r);}",
        "tinFoilPigeonMilesForStats(crumbs,saved&&saved.postcode,venueForChallenge)",
        "tinFoilChallengeRoundIndex((cr.result||{}).round)",
        "localStorage.setItem(TIN_FOIL_CHALLENGE_BRIDGE_KEY,JSON.stringify(truth));",
        "tinFoilSaveClubfinderReturnSnapshot();",
        "sessionStorage.setItem('tffc.challengeOrigin','clubfinder-beta')",
        "window.location.href='challenges-beta.html'"
    ):
        if token not in consumer:
            raise ValueError("ABORT: original Clubfinder handover changed: "+token)

def patch(text):
    a=text.index(START)
    b=text.index(END,a)
    exactly_once(text,START,"openChallenges definition")
    exactly_once(text,END,"journeyCertificate boundary")
    original=text[a:b]
    exactly_once(original,OLD_STATS,"original Stats snapshot expression")
    exactly_once(original,OLD_TRUTH,"original bridge literal")
    for token in (
        "function venueForChallenge(r){return completedResultVenue(r);}",
        "localStorage.setItem(TIN_FOIL_CHALLENGE_BRIDGE_KEY,JSON.stringify(truth));",
        "tinFoilSaveClubfinderReturnSnapshot();",
        "sessionStorage.setItem('tffc.challengeOrigin','clubfinder-beta')",
        "window.location.href='challenges-beta.html'"
    ):
        if token not in original:raise ValueError("ABORT: source drift: "+token)
    new_block=original.replace(OLD_STATS,NEW_STATS).replace(OLD_TRUTH,NEW_TRUTH)
    new=text[:a]+HELPER+new_block+text[b:]
    if text[:a]!=new[:a] or text[b:]!=new[a+len(HELPER)+len(new_block):]:
        raise ValueError("ABORT: code outside target bridge block changed")
    validate_done(new)
    return new

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check",action="store_true")
    args=ap.parse_args()
    original=TARGET.read_bytes()
    text=original.decode("utf-8")
    if "function tinFoilBuildChallengeBridgeRecord(" in text:
        validate_done(text)
        print("PASS: Stage C pure bridge-builder source already patched; sha256="+hashlib.sha256(original).hexdigest())
        return
    if args.check:
        raise SystemExit("FAIL: Stage C builder patch not yet applied")
    sha=hashlib.sha256(original).hexdigest()
    if sha!=EXPECTED_ORIGINAL_SHA256:
        raise SystemExit("ABORT: input BETA source SHA changed; expected "+EXPECTED_ORIGINAL_SHA256+", got "+sha)
    changed=patch(text)
    TARGET.write_bytes(changed.encode("utf-8"))
    print("PATCHED: only BETA Clubfinder pure builder; sha256="+hashlib.sha256(changed.encode("utf-8")).hexdigest())

if __name__=="__main__":
    main()
