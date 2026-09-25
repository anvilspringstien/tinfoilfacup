#!/usr/bin/env python3
"""One-time fail-closed BETA-only iPhone Stats identity CSS correction.

Only the generated Stats certificate CSS may change: prevent unbroken
Call Sign/Pigeon Name from extending beyond the page, and curb Safari text
autosizing on the identity band without changing the rest of Stats.
"""
import argparse
from pathlib import Path

TARGET=Path(__file__).resolve().parents[1] / "beta/clubfinder-beta.html"
OLD_BAND=".campaign-identity-band{margin:0 0 4px;padding:13px 16px 14px;border-bottom:1px solid #d40000;text-align:left;white-space:nowrap}"
NEW_BAND=".campaign-identity-band{margin:0 0 4px;padding:13px 16px 14px;border-bottom:1px solid #d40000;text-align:left;white-space:normal;overflow-wrap:anywhere;-webkit-text-size-adjust:100%;text-size-adjust:100%}"
MOBILE_RULE="@media screen and (max-width:650px),screen and (max-device-width:650px){.campaign-identity-band{padding:11px 10px;white-space:normal;overflow-wrap:anywhere}.campaign-identity-label{font-size:8pt}.campaign-identity-value{font-size:9pt;letter-spacing:0;overflow-wrap:anywhere}.campaign-identity-band .campaign-identity-label:nth-of-type(3){display:block;margin-top:4px}}"
PRINT_ANCHOR="  '@media print{body{background:#fff;padding:0}"

def patch(source):
    if source.count(NEW_BAND)==1 and source.count(MOBILE_RULE)==1 and OLD_BAND not in source:
        return source,False
    if source.count(OLD_BAND)!=1 or source.count(NEW_BAND)!=0:
        raise ValueError("Stats identity band original CSS drifted")
    if source.count(PRINT_ANCHOR)!=1 or MOBILE_RULE in source:
        raise ValueError("Stats certificate print boundary drifted")
    out=source.replace(OLD_BAND,NEW_BAND,1)
    out=out.replace(PRINT_ANCHOR,"  '"+MOBILE_RULE+"'+\n"+PRINT_ANCHOR,1)
    if out.count(NEW_BAND)!=1 or out.count(MOBILE_RULE)!=1 or OLD_BAND in out:
        raise ValueError("Stats-only replacement did not validate")
    if out.replace(NEW_BAND,OLD_BAND,1).replace("  '"+MOBILE_RULE+"'+\n","",1)!=source:
        raise ValueError("Unrelated BETA source changed")
    return out,True

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--check",action="store_true")
    args=ap.parse_args()
    before=TARGET.read_text(encoding="utf-8")
    after,changed=patch(before)
    if args.check and changed: raise SystemExit("FAIL: iPhone Stats fix not yet applied")
    if changed and not args.check: TARGET.write_text(after,encoding="utf-8")
    print("BETA iPhone Stats identity CSS:", "PASS" if not changed else "PATCHED")
    print("No Stats markup, navigation, campaign data or production code changed")

if __name__=="__main__": main()
