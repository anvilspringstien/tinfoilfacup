#!/usr/bin/env python3
"""Build an isolated reconciliation candidate from canonical production data.

Only imports scoreless, provenance-backed advancement rows already present in
BETA history. Production fixtures, replays, and all other fields remain intact.
This tool never writes to production input. A candidate is NOT promotion.
"""
import argparse
import copy
import json
import sys
from pathlib import Path

def match(row):
    return tuple(sorted((str(row.get("home","")).strip().lower(),str(row.get("away","")).strip().lower())))

def unique_rows(history):
    seen=set()
    for entries in history.values():
        for row in entries:
            if not isinstance(row,dict) or row.get("decision")!="next-round-fixture": continue
            key=(match(row),str(row.get("round")),str(row.get("date")))
            if key not in seen:
                seen.add(key)
                yield row

def build(prod,beta):
    out=copy.deepcopy(prod)
    errors=[]
    imported=[]
    if prod.get("schema_version")!=1 or beta.get("schema_version")!=1 or prod.get("season")!=beta.get("season"):
        return None,[],["schema/season mismatch"]
    fixtures=list(prod.get("fixtures",{}).values())
    histories=out.setdefault("result_history",{})
    results=out.setdefault("results",{})
    for row in unique_rows(beta.get("result_history",{})):
        key=match(row)
        if any(row.get(x) is not None for x in ("home_score","away_score")):
            errors.append(f"score invented: {key}");continue
        winner=str(row.get("winner") or "").strip()
        if winner.lower() not in key or not row.get("source_url") or not row.get("evidence_fixture"):
            errors.append(f"invalid provenance: {key}");continue
        next_matches=[f for f in fixtures if isinstance(f,dict) and winner.lower() in match(f) and f.get("round")==row.get("evidence_round") and not f.get("conditional") and " or " not in str(f.get("home","")).lower() and " or " not in str(f.get("away","")).lower()]
        if len(next_matches)!=1 or row["evidence_fixture"]!=f'{next_matches[0].get("home")} v {next_matches[0].get("away")}':
            errors.append(f"missing/ambiguous canonical next-round evidence: {key}");continue
        # A newer or authoritative result is never overwritten.
        for club, entries in histories.items():
            if not isinstance(entries,list): errors.append(f"malformed history: {club}");continue
            for old in entries:
                if not isinstance(old,dict) or match(old)!=key: continue
                if str(old.get("round","")).lower().endswith(" replay") and old.get("decision")!="next-round-fixture" and (old.get("winner") or (isinstance(old.get("home_score"),int) and isinstance(old.get("away_score"),int))):
                    errors.append(f"authoritative replay already exists: {key}")
        if errors: continue
        aliases=[club for club,entries in beta.get("result_history",{}).items() if isinstance(entries,list) and row in entries]
        if not aliases: errors.append(f"no aliases: {key}");continue
        for club in aliases:
            existing=histories.setdefault(club,[])
            if row not in existing: existing.append(copy.deepcopy(row))
            current=results.get(club)
            if current and str(current.get("date") or "")>str(row.get("date") or ""):
                continue
            if current and str(current.get("round","")).lower().endswith(" replay") and current.get("decision")!="next-round-fixture" and current.get("winner"):
                continue
            results[club]=copy.deepcopy(row)
        imported.append({"home":row["home"],"away":row["away"],"winner":winner})
    return (None if errors else out),imported,errors

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--production",required=True,type=Path)
    p.add_argument("--evidence",required=True,type=Path)
    p.add_argument("--output",required=True,type=Path)
    args=p.parse_args()
    prod=json.loads(args.production.read_text())
    beta=json.loads(args.evidence.read_text())
    candidate,imported,errors=build(prod,beta)
    print(json.dumps({"status":"BLOCKED" if errors else "CANDIDATE_BUILT","advancements":imported,"issues":errors},indent=2))
    if errors: return 1
    if args.output.resolve()==args.production.resolve() or args.output.resolve()==args.evidence.resolve():
        print("Refusing to overwrite source data",file=sys.stderr);return 1
    args.output.write_text(json.dumps(candidate,indent=2,ensure_ascii=False)+"\n")
    return 0
if __name__=="__main__":
    sys.exit(main())
