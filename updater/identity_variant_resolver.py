#!/usr/bin/env python3
import json
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "updater/ground-exception-verification.json"
OUT = ROOT / "updater/identity-variant-review.json"
REPORT = ROOT / "ground-identity-variant-review.md"

# Deliberately tiny allow-list. v7.7.8 is proposal-only: these are the three
# remaining records already described by v7.7.4 as mechanical/plausible name
# variants. Nothing else is inferred by fuzzy matching.
CASES = {
    "Bishop's Cleeve FC": {
        "expected_fchd": "Bishops Cleeve",
        "classification": "MECHANICAL_NAME_VARIANT",
        "note": "Apostrophe/name-format variant only; retain for one current-ground confirmation before any promotion.",
    },
    "Horsham YMCA FC": {
        "expected_fchd": "Horsham YM",
        "classification": "PLAUSIBLE_IDENTITY_VARIANT",
        "note": "FCHD short-name variant; explicit human identity confirmation still required before any promotion.",
    },
    "Pershore Town 88 FC": {
        "expected_fchd": "Pershore Town",
        "classification": "PLAUSIBLE_IDENTITY_VARIANT",
        "note": "FCHD historical/short-name variant; explicit human identity confirmation still required before any promotion.",
    },
}

if not SOURCE.exists():
    raise SystemExit("Missing updater/ground-exception-verification.json. Run Ground exception verification first.")

data = json.loads(SOURCE.read_text(encoding="utf8"))
records = data.get("records", [])
by_club = {r.get("club"): r for r in records if isinstance(r, dict)}

review = []
missing = []
mismatch = []
for club, rule in CASES.items():
    r = by_club.get(club)
    if not r:
        missing.append(club)
        continue
    actual = r.get("fchd_match")
    if actual != rule["expected_fchd"]:
        mismatch.append({"club": club, "expected_fchd": rule["expected_fchd"], "actual_fchd": actual})
        continue
    review.append({
        "club": club,
        "fchd_match": actual,
        "ground_candidate": r.get("ground_candidate"),
        "postcode": r.get("postcode"),
        "distance_km": r.get("distance_km"),
        "classification": rule["classification"],
        "decision": "HUMAN_CONFIRMATION_REQUIRED",
        "note": rule["note"],
        "source_state": r.get("state"),
    })

payload = {
    "checked_at": datetime.now(timezone.utc).isoformat(),
    "version": "7.7.8",
    "mode": "PROPOSAL ONLY",
    "source": "updater/ground-exception-verification.json",
    "candidate_count": len(review),
    "missing_count": len(missing),
    "mismatch_count": len(mismatch),
    "records": review,
    "missing": missing,
    "mismatches": mismatch,
}
OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf8")

L = [
    "# Tin Foil FA Cup — Identity Variant Review",
    "",
    f"Last checked: **{datetime.now(timezone.utc).strftime('%d/%m/%Y, %H:%M:%S UTC')}**",
    "",
    "**PROPOSAL ONLY — no canonical ground record, approval ledger, competition data, or Clubfinder data is changed.**",
    "",
    f"- 🟡 Identity/name variants ready for one human confirmation: **{len(review)}**",
    f"- 🔴 Expected records missing: **{len(missing)}**",
    f"- 🔴 FCHD identity mismatches: **{len(mismatch)}**",
    "",
    "## 🟡 One human identity confirmation required",
    "",
]
if review:
    for r in review:
        bits = [f"FCHD: **{r['fchd_match']}**"]
        if r.get("ground_candidate"): bits.append(r["ground_candidate"])
        if r.get("postcode"): bits.append(r["postcode"])
        if r.get("distance_km") is not None: bits.append(f"separation `{r['distance_km']} km`")
        bits.append(r["note"])
        L.append(f"- **{r['club']}** — " + " • ".join(bits))
else:
    L.append("None.")

L += ["", "## 🔴 Safety stops", ""]
if not missing and not mismatch:
    L.append("None.")
for club in missing:
    L.append(f"- **{club}** — expected actionable exception record not found; no inference made.")
for x in mismatch:
    L.append(f"- **{x['club']}** — expected FCHD **{x['expected_fchd']}**, found **{x['actual_fchd']}**; stopped for research.")

L += [
    "",
    "## Rules",
    "",
    "- v7.7.8 does not use open-ended fuzzy matching.",
    "- Only the three explicitly reviewed name-variant cases are considered.",
    "- A name resemblance never publishes a ground record.",
    "- All three remain human decisions until explicitly confirmed.",
    "- `clubfinder.html`, `competition.json`, canonical `GROUNDS`, and the groundshare approval ledger are untouched.",
]
REPORT.write_text("\n".join(L) + "\n", encoding="utf8")

print("IDENTITY VARIANT RESOLVER v7.7.8")
print("Human confirmations:", len(review))
print("Missing expected records:", len(missing))
print("Identity mismatches:", len(mismatch))
print("PROPOSAL ONLY.")
