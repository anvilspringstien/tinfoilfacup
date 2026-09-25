#!/usr/bin/env python3
"""Guarded one-use, BETA-only Stats name-row patch; leaves production unchanged."""
import argparse
from pathlib import Path

TARGET=Path(__file__).resolve().parents[1]/"beta"/"clubfinder-beta.html"
OLD_CSS="@media screen and (max-width:650px),screen and (max-device-width:650px){.campaign-identity-band{padding:11px 10px;white-space:normal;overflow-wrap:anywhere}.campaign-identity-label{font-size:8pt}.campaign-identity-value{font-size:9pt;letter-spacing:0;overflow-wrap:anywhere}.campaign-identity-band .campaign-identity-label:nth-of-type(3){display:block;margin-top:4px}}"
NEW_CSS="@media screen and (max-width:650px),screen and (max-device-width:650px){.campaign-identity-band{padding:11px 10px;white-space:normal;overflow-wrap:anywhere}.campaign-identity-label{font-size:8pt}.campaign-identity-value{font-size:9pt;letter-spacing:0;overflow-wrap:anywhere}.campaign-identity-name-row{display:flex;align-items:baseline;flex-wrap:nowrap;gap:0 5px;margin-top:4px;min-width:0}.campaign-identity-name-row .campaign-identity-separator{display:none}.campaign-identity-name-row .campaign-identity-label{flex:0 0 auto;white-space:nowrap}.campaign-identity-name-row .campaign-identity-value{flex:1 1 auto;min-width:0;white-space:normal;overflow-wrap:anywhere}}"
OLD_MARKUP="' <span class=\"campaign-identity-label\">· PIGEON NAME:</span> <span class=\"campaign-identity-value\">'+certEsc(campaignPigeonName)+'</span>'"
NEW_MARKUP="' <span class=\"campaign-identity-name-row\"><span class=\"campaign-identity-label\"><span class=\"campaign-identity-separator\" aria-hidden=\"true\">· </span>PIGEON NAME:</span> <span class=\"campaign-identity-value\">'+certEsc(campaignPigeonName)+'</span></span>'"

def patch(source):
    if source.count(NEW_CSS)==1 and source.count(NEW_MARKUP)==1 and OLD_CSS not in source and OLD_MARKUP not in source:
        return source,False
    for label,before,after in [("CSS",OLD_CSS,NEW_CSS),("markup",OLD_MARKUP,NEW_MARKUP)]:
        if source.count(before)!=1 or source.count(after)!=0:
            raise ValueError(label+" exact certificate source drift")
    out=source.replace(OLD_CSS,NEW_CSS,1).replace(OLD_MARKUP,NEW_MARKUP,1)
    if out.replace(NEW_CSS,OLD_CSS,1).replace(NEW_MARKUP,OLD_MARKUP,1)!=source:
        raise ValueError("unrelated BETA bytes unexpectedly changed")
    return out,True

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--check",action="store_true")
    args=parser.parse_args()
    before=TARGET.read_text(encoding="utf-8")
    after,changed=patch(before)
    if changed and args.check: raise SystemExit("FAIL: iPhone Stats two-line correction missing")
    if changed: TARGET.write_text(after,encoding="utf-8")
    print("BETA iPhone Stats two-line identity:", "PATCHED" if changed else "PASS")
    print("Verified only the mobile certificate CSS and Pigeon Name grouping changed.")

if __name__=="__main__":main()
