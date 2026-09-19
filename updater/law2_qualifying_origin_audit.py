#!/usr/bin/env python3
"""Audit Tin Foil FA Cup Law 2 origin eligibility.

Law 2 scope: every club whose 2026-27 Emirates FA Cup campaign begins in a
qualifying round is eligible to be a Clubfinder journey origin. Proper-round
entrants remain outside the Tin Foil FA Cup starting population.

This audit is READ ONLY. It does not modify clubfinder.html, competition.json,
GROUNDS or journey logic.
"""
from pathlib import Path
from collections import Counter
import json
import re

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "clubfinder.html"
REGISTRY = ROOT / "journey-club-registry.json"
OUT = ROOT / "updater" / "law2-qualifying-origin-audit.json"

LATER_QUALIFYING = {
    "First Round Qualifying",
    "Second Round Qualifying",
    "Third Round Qualifying",
    "Fourth Round Qualifying",
}
EXPECTED_LATER = {
    "First Round Qualifying": 88,
    "Second Round Qualifying": 48,
    "Third Round Qualifying": 0,
    "Fourth Round Qualifying": 24,
}
EXPECTED_CURRENT_ORIGINS = 491
EXPECTED_LAW2_ORIGINS = 651
EXPECTED_PROPER_ONLY = 92


def arr(text, name):
    m = re.search(rf"(?:const|let|var)\s+{re.escape(name)}\s*=\s*(\[.*?\])\s*;", text, re.S)
    if not m:
        raise SystemExit(f"ABORT: {name} missing from clubfinder.html")
    return json.loads(m.group(1))


def key(name):
    s = str(name or "").lower().replace("&", " and ")
    s = re.sub(r"\b(association football club|football club)\b", " ", s)
    s = re.sub(r"\b(fc|cfc)\b", " ", s)
    s = re.sub(r"\bafc$", " ", s)
    s = re.sub(r"[^a-z0-9]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


html = HTML.read_text(encoding="utf-8")
eligible = arr(html, "ELIGIBLE")
registry = json.loads(REGISTRY.read_text(encoding="utf-8"))

if len(eligible) != EXPECTED_CURRENT_ORIGINS:
    raise SystemExit(f"ABORT: expected {EXPECTED_CURRENT_ORIGINS} current origins, found {len(eligible)}")
if registry.get("scope", {}).get("official_accepted_clubs") != 743:
    raise SystemExit("ABORT: Journey Club Registry is not the canonical 743-club 2026-27 registry")
if len(registry.get("clubs", [])) != 252:
    raise SystemExit("ABORT: expected 252 companion Journey Club Registry clubs")

current_keys = {key(x.get("name") or x.get("club")) for x in eligible}
supplement = [x for x in registry["clubs"] if x.get("entry_round") in LATER_QUALIFYING]
proper_only = [x for x in registry["clubs"] if x.get("entry_round") not in LATER_QUALIFYING]
round_counts = Counter(x.get("entry_round") for x in supplement)

for round_name, expected in EXPECTED_LATER.items():
    if round_counts.get(round_name, 0) != expected:
        raise SystemExit(
            f"ABORT: expected {expected} {round_name} entrants, got {round_counts.get(round_name, 0)}"
        )

if len(supplement) != 160:
    raise SystemExit(f"ABORT: expected 160 later qualifying entrants, got {len(supplement)}")
if len(proper_only) != EXPECTED_PROPER_ONLY:
    raise SystemExit(f"ABORT: expected {EXPECTED_PROPER_ONLY} proper-round-only entrants, got {len(proper_only)}")

overlap = sorted(x["club"] for x in supplement if key(x["club"]) in current_keys)
if overlap:
    raise SystemExit(f"ABORT: later-qualifying supplement overlaps current origins: {overlap}")

prospective = len(eligible) + len(supplement)
if prospective != EXPECTED_LAW2_ORIGINS:
    raise SystemExit(f"ABORT: expected Law 2 population {EXPECTED_LAW2_ORIGINS}, got {prospective}")

leatherhead = [x for x in supplement if key(x.get("club")) == key("Leatherhead FC")]
if len(leatherhead) != 1:
    raise SystemExit(f"ABORT: expected exactly one Leatherhead FC record, got {len(leatherhead)}")
if leatherhead[0].get("entry_round") != "First Round Qualifying":
    raise SystemExit(f"ABORT: Leatherhead entry round is {leatherhead[0].get('entry_round')!r}")

with_guarded_ground = sum(bool(x.get("existing_guarded_ground_record")) for x in supplement)
with_supporting_ground = sum(bool(x.get("supporting_ground_evidence")) for x in supplement)
without_any_ground_evidence = [
    x["club"] for x in supplement
    if not x.get("existing_guarded_ground_record") and not x.get("supporting_ground_evidence")
]

report = {
    "season": "2026-27",
    "law2_rule": "Every club whose Emirates FA Cup campaign begins in a qualifying round is eligible as a Tin Foil FA Cup journey origin.",
    "read_only": True,
    "current_origin_population": len(eligible),
    "later_qualifying_origins_missing_from_current_population": len(supplement),
    "law2_origin_population": prospective,
    "proper_round_only_entrants_excluded": len(proper_only),
    "later_qualifying_entry_round_counts": dict(sorted(round_counts.items())),
    "ground_evidence": {
        "existing_guarded_ground_records": with_guarded_ground,
        "supporting_ground_evidence": with_supporting_ground,
        "without_any_ground_evidence": without_any_ground_evidence,
    },
    "constitutional_canary": {
        "club": leatherhead[0]["club"],
        "entry_round": leatherhead[0]["entry_round"],
        "registry_state": leatherhead[0].get("registry_state"),
        "promotion_readiness": leatherhead[0].get("promotion_readiness"),
        "existing_guarded_ground_record": leatherhead[0].get("existing_guarded_ground_record"),
        "supporting_ground_evidence": leatherhead[0].get("supporting_ground_evidence"),
    },
    "missing_qualifying_origins": [
        {
            "club": x["club"],
            "entry_round": x.get("entry_round"),
            "registry_state": x.get("registry_state"),
            "promotion_readiness": x.get("promotion_readiness"),
            "existing_guarded_ground_record": x.get("existing_guarded_ground_record"),
            "supporting_ground_evidence": x.get("supporting_ground_evidence"),
        }
        for x in sorted(supplement, key=lambda y: (y.get("entry_round", ""), y["club"].casefold()))
    ],
}
OUT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

print("LAW 2 QUALIFYING ORIGIN AUDIT: SUCCESS")
print("Current origins:", len(eligible))
print("Missing later qualifying origins:", len(supplement))
for r in ("First Round Qualifying", "Second Round Qualifying", "Third Round Qualifying", "Fourth Round Qualifying"):
    print(f"{r}: {round_counts.get(r, 0)}")
print("Law 2 origin population:", prospective)
print("Proper-round-only entrants excluded:", len(proper_only))
print("Supplement with existing guarded ground:", with_guarded_ground)
print("Supplement with supporting ground evidence:", with_supporting_ground)
print("Supplement with no ground evidence:", len(without_any_ground_evidence))
print("Constitutional canary: Leatherhead FC — First Round Qualifying")
print("READ ONLY: production Clubfinder untouched")
