#!/usr/bin/env python3
"""Guarded, one-use iPhone BETA Stats viewport fix, preserving accepted report CSS."""
import argparse
from pathlib import Path
P=Path(__file__).resolve().parents[1]/"beta"/"clubfinder-beta.html"
OLD_HEAD='<meta name="viewport" content="width=device-width,initial-scale=1">'
NEW_HEAD="""<script>document.write(new URLSearchParams(location.search||'').get('stats')==='1'?'<meta name="viewport" content="width=980">':'<meta name="viewport" content="width=device-width,initial-scale=1">');</script>"""
OLD_DOC="""const doc='<!doctype html><html><head><meta charset="utf-8"><title"""
NEW_DOC="""const doc='<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=980"><title"""
def revise(s):
    if s.count(NEW_HEAD)==1 and s.count(NEW_DOC)==1 and s.count(OLD_DOC)==0:
        return s,False
    for label,a,b in [("document head",OLD_HEAD,NEW_HEAD),("generated certificate head",OLD_DOC,NEW_DOC)]:
        if s.count(a)!=1 or s.count(b)!=0:
            raise ValueError(label+" missing, duplicate, or partially patched")
    new=s.replace(OLD_HEAD,NEW_HEAD,1).replace(OLD_DOC,NEW_DOC,1)
    if new.replace(NEW_HEAD,OLD_HEAD,1).replace(NEW_DOC,OLD_DOC,1)!=s:
        raise ValueError("Unrelated source changed")
    if new.count("@media(max-width:650px)")==0 or new.count("campaign-identity-name-row")<2:
        raise ValueError("Previously accepted Stats/pigeon-name styling is missing")
    return new,True
def main():
    arg=argparse.ArgumentParser()
    arg.add_argument("--check",action="store_true")
    flags=arg.parse_args()
    s=P.read_text(encoding="utf-8")
    updated,changed=revise(s)
    if flags.check and changed: raise SystemExit("FAIL: original wide Stats viewport fix not committed")
    if changed and not flags.check:P.write_text(updated,encoding="utf-8")
    print("BETA STATS ORIGINAL PINCH-ZOOM LAYOUT:", "PASS" if not changed else "PATCHED")
    print("Only route-aware viewport and generated certificate viewport changed.")
if __name__=="__main__":main()
