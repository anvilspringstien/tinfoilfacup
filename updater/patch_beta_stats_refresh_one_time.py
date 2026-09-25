#!/usr/bin/env python3
"""One-time, fail-closed patch: open BETA Stats via its existing reloadable URL.

Never alters protected production, competition data, or Stats presentation.
"""
import argparse
from pathlib import Path

TARGET=Path(__file__).resolve().parents[1]/"beta"/"clubfinder-beta.html"

OLD_ENTRY='async function journeyCertificate(origin, suppliedWindow=null, returnMode="clubfinder"){\n  const w=suppliedWindow || window.open("","_blank");'
NEW_ENTRY='async function journeyCertificate(origin, suppliedWindow=null, returnMode="clubfinder"){\n  // Open the existing reloadable Stats route while still in the user click.\n  if(!suppliedWindow){\n    window.open("clubfinder-beta.html?stats=1","_blank");\n    return;\n  }\n  const w=suppliedWindow || window.open("","_blank");'
OLD_ROUTE="  if(q.get('stats')!=='1')return;\n  const saved=loadSavedJourney();"
NEW_ROUTE="  if(q.get('stats')!=='1')return;\n  await tinFoilCompetitionReady;\n  const saved=loadSavedJourney();"

def patch(text):
    if all(text.count(after)==1 and text.count(before)==0 for before,after in ((OLD_ENTRY,NEW_ENTRY),(OLD_ROUTE,NEW_ROUTE))):
        return text,False
    for label,before,after in (("Stats entry",OLD_ENTRY,NEW_ENTRY),("Stats on-load route",OLD_ROUTE,NEW_ROUTE)):
        if text.count(before)!=1 or text.count(after)!=0:
            raise ValueError(label+" source drift / partial patch — ABORT")
    out=text.replace(OLD_ENTRY,NEW_ENTRY,1).replace(OLD_ROUTE,NEW_ROUTE,1)
    if out.replace(NEW_ENTRY,OLD_ENTRY,1).replace(NEW_ROUTE,OLD_ROUTE,1)!=text:
        raise ValueError("Unrelated BETA source modified — ABORT")
    return out,True

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--check",action="store_true")
    args=ap.parse_args()
    original=TARGET.read_text(encoding="utf-8")
    revised,changed=patch(original)
    if args.check and changed:
        raise SystemExit("FAIL: BETA Stats reloadable entry patch missing")
    if changed:
        TARGET.write_text(revised,encoding="utf-8")
    print("BETA STATS RELOADABLE ROUTE:", "PATCHED" if changed else "PASS")
    print("No BETA Stats formatting, production, canonical data, or Deck edits.")

if __name__=="__main__": main()
