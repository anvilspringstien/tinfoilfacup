#!/usr/bin/env python3
"""Guarded BETA-only public-identity repair for the 2026 Holmesdale merger."""
from pathlib import Path
import argparse

BETA=Path("beta/clubfinder-beta.html")
OLD="Holmesdale FC"
NEW="Petts Wood & Holmesdale FC"

def one(src, old, new, label):
    n=src.count(old)
    if n==1:
        return src.replace(old,new,1)
    if n==0 and src.count(new)>=1:
        return src
    raise RuntimeError(f"{label}: expected one old marker, found {n}")

def replace_all_required(src, old, new, label):
    n=src.count(old)
    if n:
        return src.replace(old,new)
    if new in src:
        return src
    raise RuntimeError(f"{label}: neither old nor applied form found")

def patch(src):
    src=one(src,
        '{"name":"Holmesdale FC","entry_round":"Extra Preliminary Round"',
        '{"name":"Petts Wood & Holmesdale FC","entry_round":"Extra Preliminary Round"',
        "eligible current club identity")
    src=one(src,
        '{"name":"Holmesdale FC","ground":"RTL Group Stadium","postcode":"BR2 8HQ"',
        '{"name":"Petts Wood & Holmesdale FC","ground":"RTL Group Stadium","postcode":"BR2 8HQ"',
        "ground current club identity")
    src=one(src,
        "const home=groundByClubName('Holmesdale FC');",
        "const home=groundByClubName('Petts Wood & Holmesdale FC');",
        "8 August surveyed-ground fallback")
    src=one(src,
        "function savedOrigin(rows,s){return s?rows.find(r=>norm(r.name)===norm(s.originName))||null:null}",
        "function savedOrigin(rows,s){return s?rows.find(r=>sameClubIdentity(r.name,s.originName))||null:null}",
        "saved campaign semantic origin lookup")
    src=replace_all_required(src,
        "norm(existing.originName)===norm(origin.name)",
        "sameClubIdentity(existing.originName,origin.name)",
        "saved identity preservation")
    src=replace_all_required(src,
        "norm(saved.originName)===norm(origin.name)",
        "sameClubIdentity(saved.originName,origin.name)",
        "visible saved campaign matching")
    src=replace_all_required(src,
        "norm(e.originName)!==norm(o.name)",
        "!sameClubIdentity(e.originName,o.name)",
        "replacement campaign comparison")
    # Preserve pending/backup campaign identity across the retired->current name.
    src=src.replace(
        "norm(saved.originName)!==norm(candidate.originName)",
        "!sameClubIdentity(saved.originName,candidate.originName)")
    src=src.replace(
        "norm(saved.originName)!==norm(pending.originName)",
        "!sameClubIdentity(saved.originName,pending.originName)")
    # Keep the historic alias only where it is intentionally evidence/compatibility data.
    if src.count('{"name":"Holmesdale FC","entry_round') or src.count('{"name":"Holmesdale FC","ground":"RTL Group Stadium"'):
        raise RuntimeError("retired Holmesdale public club record still present")
    return src

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--check",action="store_true")
    args=ap.parse_args()
    before=BETA.read_text(encoding="utf-8")
    after=patch(before)
    if args.check:
        if before!=after:
            raise SystemExit("BETA Petts Wood public identity patch missing or stale")
        print("BETA Petts Wood public identity patch: PASS")
    elif before!=after:
        BETA.write_text(after,encoding="utf-8")
        print("Patched BETA current public identity to Petts Wood & Holmesdale FC; production untouched")
    else:
        print("BETA Petts Wood public identity already applied")

if __name__=="__main__":
    main()
