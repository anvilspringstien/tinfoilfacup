#!/usr/bin/env python3
"""Generate an *unpublished* BETA-only review copy with sourced, unverified grounds.

Do NOT write to beta/clubfinder-beta.html or clubfinder.html. Only an explicitly
specified output under a temporary directory is permitted. This is a visual
acceptance candidate, not a guarded location promotion or map/miles repair.
"""
import argparse
import json
import re
from pathlib import Path
from updater.audit_active_custodian_locations import analyze, display_key, identity_key

ROOT=Path(__file__).resolve().parents[1]
ARRAY=re.compile(r"((?:let|const|var)\s+GROUNDS\s*=\s*)(\[[\s\S]*?\])(\s*;)")


def build(root=ROOT):
    html=(root/"beta/clubfinder-beta.html").read_text(encoding="utf-8")
    ledger=json.loads((root/"updater/entrant-home-ground-evidence-2026.json").read_text(encoding="utf-8"))
    if ledger.get("season")!="2026-27" or ledger["safety"]["automated_ground_promotion"] is not False or ledger["safety"]["verified_location_badge_authorized"] is not False:
        raise ValueError("Promotion guards missing")
    found=list(ARRAY.finditer(html))
    if len(found)!=1:
        raise ValueError(f"Expected one GROUNDS declaration, got {len(found)}")
    match=found[0]
    grounds=json.loads(match.group(2))
    existing={}
    for row in grounds:
        existing.setdefault(display_key(row["name"]),set()).add(identity_key(row["name"]))
    from updater.audit_active_custodian_locations import array_from_html
    for row in array_from_html(html,"LAW2_ORIGIN_LOCATIONS"):
        existing.setdefault(display_key(row["name"]),set()).add(identity_key(row["name"]))
    audit=analyze(root)
    gaps={identity_key(x["club"]) for x in audit["missing_second_round_custodian_locations"]["beta"]}
    staged={}
    for row in ledger["clubs"]:
        key=identity_key(row["official_identity"])
        if key in staged:
            raise ValueError("Ambiguous evidence identity")
        staged[key]=row
    blocked={identity_key(x["official_identity"]) for x in ledger.get("unresolved_conflicts",[])}
    additions=[]
    skipped=[]
    for key in sorted(gaps):
        row=staged.get(key)
        if not row or key in blocked:
            skipped.append([key,"no unblocked evidence"])
            continue
        n=display_key(row["official_identity"])
        if n in existing:
            skipped.append([row["official_identity"],"existing loose-key collision"])
            continue
        if not row.get("ground") or not row.get("postcode") or row.get("source_review")!="official-ground-and-postcode-confirmed":
            skipped.append([row["official_identity"],"incomplete official evidence"])
            continue
        record={
          "name":row["official_identity"],
          "ground":row["ground"],
          "postcode":row["postcode"],
          "verification":"unverified",
          "source":row["official_home_ground_source"],
          "ground_source":"Official club source — pending independent coordinate verification",
          "preview_evidence_only":True,
        }
        assert all(k not in record for k in ("lat","lon","latitude","longitude","distance"))
        additions.append(record)
        existing[n]={key}
    # Preserve the original array rows and every other byte outside the array.
    updated=grounds+additions
    changed=html[:match.start(2)]+json.dumps(updated,ensure_ascii=False,separators=(",",":"))+html[match.end(2):]
    # The existing display-key normaliser erases leading AFC, so "Liverpool FC"
    # could otherwise inherit AFC Liverpool's ground. In this isolated preview
    # guard the existing lookup without changing the protected BETA master.
    start_marker = "function findGround(c){"
    end_marker = "}function verification(c,g){"
    if changed.count(start_marker)!=1 or changed.count(end_marker)!=1:
        raise ValueError("BETA ground lookup anchors have drifted")
    before, tail = changed.split(start_marker, 1)
    lookup, after = tail.split(end_marker, 1)
    if lookup.count("if(g)return g;")!=1 or lookup.count("if(s)return s;")!=1:
        raise ValueError("BETA lookup return structure has drifted")
    # Only prohibit cross-identity borrowing involving a *leading* AFC prefix.
    # Existing alias rules for unrelated clubs are preserved.
    boundary = (r"  const previewAfcBoundary=(requested,record)=>"
                r"/^\s*afc\b/i.test(requested||'')==="
                r"/^\s*afc\b/i.test(record||'');" + "\n")
    lookup = boundary + lookup.replace("if(g)return g;",
                "if(g&&previewAfcBoundary(c.name,g.name))return g;").replace(
                "if(s)return s;",
                "if(s&&previewAfcBoundary(c.name,s.name))return s;")
    changed = before + start_marker + lookup + end_marker + after
    if len(additions)+len(skipped)!=len(gaps):
        raise AssertionError("Preview coverage mismatch")
    if not all(x["verification"]=="unverified" for x in additions):
        raise AssertionError("Preview accidentally verified")
    return changed, {"second_round_missing":len(gaps),"staged_preview_records":len(additions),"skipped":skipped,"read_only_preview":True,"automatic_verification":False}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    destination=args.output.resolve()
    protected=[(ROOT/"beta/clubfinder-beta.html").resolve(),(ROOT/"clubfinder.html").resolve()]
    if destination in protected or ROOT.resolve() in destination.parents:
        raise SystemExit("Output MUST be outside repository; never mutate production or main BETA")
    source,report=build()
    destination.parent.mkdir(parents=True,exist_ok=True)
    destination.write_text(source,encoding="utf-8")
    print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=="__main__":
    main()
