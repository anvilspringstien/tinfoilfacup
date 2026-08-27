#!/usr/bin/env python3
import json
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "updater/identity-variant-review.json"
OUT = ROOT / "updater/identity-variant-confirmation.json"
REPORT = ROOT / "ground-identity-variant-confirmation.md"

# Explicit human-reviewed/current-source decisions only. This is deliberately
# not a fuzzy matcher and it does not publish canonical GROUNDS records.
CONFIRMATIONS = {
    "Bishop's Cleeve FC": {
        "expected_fchd": "Bishops Cleeve",
        "expected_postcode": "GL52 3PD",
        "current_ground": "Everyone's Energy Stadium",
        "decision": "IDENTITY_CONFIRMED",
        "evidence_note": "Current club contact material identifies Bishops Cleeve Football Club at Everyone's Energy Stadium, GL52 3PD; apostrophe difference is a name-format variant.",
        "evidence_url": "https://bishopscleevefc.ktckts.com/contactus",
    },
    "Horsham YMCA FC": {
        "expected_fchd": "Horsham YM",
        "expected_postcode": "RH13 5BP",
        "current_ground": "Gorings Mead",
        "decision": "IDENTITY_CONFIRMED",
        "evidence_note": "Current club material identifies Horsham YM Football Club as formerly Horsham YMCA FC and gives Gorings Mead, RH13 5BP.",
        "evidence_url": "https://www.horshamymfc.co.uk/contact/1021",
    },
    "Pershore Town 88 FC": {
        "expected_fchd": "Pershore Town",
        "expected_postcode": "WR10 1QU",
        "current_ground": "That Carpet Place Community Stadium",
        "decision": "IDENTITY_CONFIRMED",
        "evidence_note": "Current Pershore Town material and club history support Pershore Town / Pershore Town 88 as the same club at WR10 1QU. Current venue branding supersedes the older FCHD sponsor name Recruit 12 Community Stadium.",
        "evidence_url": "https://www.pershoretownfc.co.uk/contact",
        "venue_name_note": "Use current venue name at promotion time; do not silently retain the older FCHD sponsored ground name.",
    },
}

if not SOURCE.exists():
    raise SystemExit("Missing updater/identity-variant-review.json. Run v7.7.8 first.")

data = json.loads(SOURCE.read_text(encoding="utf8"))
if data.get("version") != "7.7.8":
    raise SystemExit("Identity review source is not v7.7.8. Confirmation stopped safely.")

records = data.get("records", [])
by_club = {r.get("club"): r for r in records if isinstance(r, dict)}
confirmed, held = [], []

for club, rule in CONFIRMATIONS.items():
    r = by_club.get(club)
    if not r:
        held.append({"club": club, "reason": "V7_7_8_RECORD_MISSING"})
        continue
    if r.get("decision") != "HUMAN_CONFIRMATION_REQUIRED":
        held.append({"club": club, "reason": "SOURCE_NOT_AWAITING_HUMAN_CONFIRMATION"})
        continue
    if r.get("fchd_match") != rule["expected_fchd"]:
        held.append({"club": club, "reason": "FCHD_IDENTITY_CHANGED", "actual": r.get("fchd_match")})
        continue
    if r.get("postcode") != rule["expected_postcode"]:
        held.append({"club": club, "reason": "POSTCODE_CHANGED", "actual": r.get("postcode")})
        continue
    confirmed.append({
        "club": club,
        "fchd_match": r.get("fchd_match"),
        "fchd_ground_candidate": r.get("ground_candidate"),
        "current_ground": rule["current_ground"],
        "postcode": r.get("postcode"),
        "classification": r.get("classification"),
        "decision": rule["decision"],
        "evidence_note": rule["evidence_note"],
        "evidence_url": rule["evidence_url"],
        "venue_name_note": rule.get("venue_name_note"),
        "promotion_state": "PROMOTION_CANDIDATE_NOT_PUBLISHED",
    })

now = datetime.now(timezone.utc)
payload = {
    "checked_at": now.isoformat(),
    "version": "7.7.9",
    "mode": "CONFIRMATION ONLY / NO PUBLISH",
    "source": "updater/identity-variant-review.json",
    "confirmed_count": len(confirmed),
    "held_count": len(held),
    "records": confirmed,
    "held": held,
}
OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf8")

L = [
    "# Tin Foil FA Cup — Identity Variant Confirmation",
    "",
    f"Last checked: **{now.strftime('%d/%m/%Y, %H:%M:%S UTC')}**",
    "",
    "**CONFIRMATION ONLY / NO PUBLISH — no canonical ground record, competition data, or Clubfinder data is changed.**",
    "",
    f"- 🟢 Confirmed identities: **{len(confirmed)}**",
    f"- 🔴 Held by safety checks: **{len(held)}**",
    "",
    "## 🟢 Confirmed identities",
    "",
]
if confirmed:
    for r in confirmed:
        L.append(f"- **{r['club']}** ↔ FCHD **{r['fchd_match']}** — {r['current_ground']} • {r['postcode']} — `{r['decision']}`")
        L.append(f"  - Evidence: {r['evidence_note']}")
        L.append(f"  - Source: {r['evidence_url']}")
        if r.get("venue_name_note"):
            L.append(f"  - Venue-name note: {r['venue_name_note']}")
else:
    L.append("None.")

L += ["", "## 🔴 Held / safety stops", ""]
if held:
    for r in held:
        L.append(f"- **{r['club']}** — {r['reason']}")
else:
    L.append("None.")

L += [
    "",
    "## Safety",
    "",
    "- Only the three explicit v7.7.8 human-decision records can be confirmed.",
    "- FCHD identity and postcode must still match the reviewed v7.7.8 record exactly.",
    "- A changed identity or postcode is held rather than inferred.",
    "- Pershore's current venue name is recorded explicitly instead of silently copying the older FCHD sponsor name.",
    "- This step does not write canonical `GROUNDS` records.",
    "- `clubfinder.html` and `competition.json` are untouched.",
]
REPORT.write_text("\n".join(L) + "\n", encoding="utf8")

print("IDENTITY VARIANT CONFIRMATION v7.7.9")
print("Confirmed identities:", len(confirmed))
print("Held by safety checks:", len(held))
print("Published canonical records: 0")
print("CONFIRMATION ONLY / NO PUBLISH.")
