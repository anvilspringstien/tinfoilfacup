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
    """Build an opt-in preview, also after reviewed grounds are in normal BETA.

    Generator is idempotent: previously published unverified evidence is
    validated rather than duplicated. Still never writes to the source.
    """
    from updater.apply_reviewed_entrant_grounds_beta import transform
    html=(root/"beta/clubfinder-beta.html").read_text(encoding="utf-8")
    ledger=json.loads((root/"updater/entrant-home-ground-evidence-2026.json").read_text(encoding="utf-8"))
    competition=json.loads((root/"competition.json").read_text(encoding="utf-8"))
    changed, review=transform(html,ledger,competition)
    audit=analyze(root)
    gaps=len(audit["missing_second_round_custodian_locations"]["beta"])
    if gaps!=review["new_pending"]:
        raise ValueError("Ground preview disagrees with canonical entrant gap audit")
    return changed, {
        "second_round_missing":gaps,
        "staged_preview_records":review["new_pending"],
        "already_reviewed_records":review["already_pending"],
        "skipped":[],
        "read_only_preview":True,
        "automatic_verification":False
    }


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
