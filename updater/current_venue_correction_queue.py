#!/usr/bin/env python3
import json
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
B2 = ROOT / "updater/groundshare-evidence-confirmation-batch2.json"
B3 = ROOT / "updater/groundshare-evidence-confirmation-batch3.json"
OUT = ROOT / "updater/current-venue-correction-queue.json"
REPORT = ROOT / "current-venue-correction-queue.md"

for p in (B2, B3):
    if not p.exists():
        raise SystemExit(f"Missing {p.relative_to(ROOT)}.")

b2 = json.loads(B2.read_text(encoding="utf8"))
b3 = json.loads(B3.read_text(encoding="utf8"))
if b2.get("version") != "7.8.6" or b2.get("batch") != 2:
    raise SystemExit("Safety stop: unexpected Batch 2 confirmation source/version.")
if b3.get("version") != "7.8.9" or b3.get("batch") != 3:
    raise SystemExit("Safety stop: unexpected Batch 3 confirmation source/version.")

rejected = {r["pair_id"]: r for r in (b2.get("rejected_not_current") or []) + (b3.get("rejected_not_current") or [])}
if set(rejected) != {8, 10, 14}:
    raise SystemExit(f"Safety stop: expected rejected pairs #8, #10 and #14 only; found {sorted(rejected)}.")

expected = {
    8: (["Cobham FC", "Epsom & Ewell FC"], "KT11 1AA", "Epsom & Ewell FC", "Chalky Lane, Chessington", "Cobham FC"),
    10: (["Belper United FC", "Eastwood Community FC"], "NG16 3HB", "Belper United FC", "Don Amott Arena, Mickleover", "Eastwood Community FC"),
    14: (["Hayes & Yeading United FC", "Southall FC"], "UB4 0SL", "Southall FC", "Honeycroft, Uxbridge", "Hayes & Yeading United FC"),
}

items = []
for pid, (clubs, stale_pc, moved_club, current_ground, counterpart) in expected.items():
    r = rejected[pid]
    if r.get("status") != "HUMAN_REJECTED_NOT_CURRENT" or r.get("clubs") != clubs or (r.get("postcode") or "").upper() != stale_pc:
        raise SystemExit(f"Safety stop: identity/status/postcode drift in rejected pair #{pid}.")
    if r.get("current_ground") != current_ground or not r.get("sources") or not r.get("evidence_note"):
        raise SystemExit(f"Safety stop: rejected pair #{pid} lacks the expected evidenced current venue.")
    items.append({
        "club": moved_club,
        "action": "CURRENT_VENUE_CORRECTION_RESEARCH",
        "evidenced_current_venue": current_ground,
        "stale_groundshare_postcode": stale_pc,
        "source_pair_id": pid,
        "evidence_note": r["evidence_note"],
        "sources": r["sources"],
        "publish_eligible": False,
    })
    items.append({
        "club": counterpart,
        "action": "COUNTERPART_CURRENT_GROUND_CHECK",
        "stale_groundshare_postcode": stale_pc,
        "source_pair_id": pid,
        "reason": "Former counterpart remains a separate current-ground verification unit; do not infer its current venue from the rejected relationship.",
        "publish_eligible": False,
    })

items.append({
    "club": "Corby Town FC",
    "action": "CURRENT_GROUND_POSTCODE_CHECK",
    "candidate_ground": "Steel Park",
    "candidate_postcode": "NN17 2AE",
    "candidate_separation_km": 0.908,
    "reason": "Verify current ground/postcode once (750m–2km centroid difference).",
    "publish_eligible": False,
})

held = [{
    "clubs": ["Romulus FC", "Sutton Coldfield Town FC"],
    "postcode": "B72 1NL",
    "status": "HELD_FOR_MORE_EVIDENCE",
    "reason": "Existing evidence places Romulus home matches at Coles Lane/B72 1NL but does not explicitly establish the current Romulus ↔ Sutton Coldfield Town relationship. Keep outside the correction queue.",
}]

if len(items) != 7:
    raise SystemExit("Safety stop: correction queue must contain exactly 7 club-level research/check units.")

now = datetime.now(timezone.utc)
payload = {
    "checked_at": now.isoformat(),
    "version": "7.9.1",
    "mode": "PROPOSAL ONLY / CURRENT-VENUE CORRECTION QUEUE",
    "sources": [str(B2.relative_to(ROOT)), str(B3.relative_to(ROOT))],
    "queue_items": len(items),
    "evidenced_moved_clubs": 3,
    "counterpart_checks": 3,
    "centroid_current_ground_checks": 1,
    "held_outside_queue": 2,
    "published_canonical_records": 0,
    "items": items,
    "held": held,
}
OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf8")

L = [
    "# Tin Foil FA Cup — Current Venue Correction Queue",
    "",
    f"Last checked: **{now.strftime('%d/%m/%Y, %H:%M:%S UTC')}**",
    "",
    "**PROPOSAL ONLY / RESEARCH QUEUE. No canonical ground record, groundshare ledger, `clubfinder.html`, or `competition.json` is changed.**",
    "",
    "- 🧭 Current-venue correction/check units: **7**",
    "- 🔁 Clubs with replacement venues already evidenced: **3**",
    "- 🏟️ Former counterpart current-ground checks: **3**",
    "- 📍 Centroid/current-ground checks: **1**",
    "- 🟡 Held outside this queue pending better groundshare evidence: **2 club warnings / 1 relationship**",
    "- Published canonical records: **0**",
    "",
    "## 🔁 Evidenced replacement venues requiring correction research",
    "",
]
for x in [i for i in items if i["action"] == "CURRENT_VENUE_CORRECTION_RESEARCH"]:
    L += [f"### {x['club']}", "", f"- Evidenced current venue: **{x['evidenced_current_venue']}**", f"- Stale groundshare postcode: **{x['stale_groundshare_postcode']}**", f"- Source rejected pair: **#{x['source_pair_id']}**", f"- Evidence: {x['evidence_note']}"] + [f"- Source {n}: {u}" for n, u in enumerate(x["sources"], 1)] + ["- Decision required: **Research/validate the current venue sufficiently for a separate canonical correction; do not revive the rejected groundshare.**", ""]
L += ["## 🏟️ Former counterpart current-ground checks", ""]
for x in [i for i in items if i["action"] == "COUNTERPART_CURRENT_GROUND_CHECK"]:
    L += [f"- **{x['club']}** — former pair **#{x['source_pair_id']}** • stale shared postcode **{x['stale_groundshare_postcode']}** • verify independently; no venue is inferred from the rejected relationship."]
L += ["", "## 📍 Standalone current-ground check", "", "- **Corby Town FC** — Steel Park • NN17 2AE • separation `0.908 km` • verify current ground/postcode once; this is not a groundshare decision.", "", "## 🟡 Held outside this correction queue", "", "- **Romulus FC ↔ Sutton Coldfield Town FC** — B72 1NL — remains `HELD_FOR_MORE_EVIDENCE`; do not approve, reject, correct, or publish from the current evidence.", "", "## Safety", "", "- Only v7.8.6 rejected pairs #8/#10 and v7.8.9 rejected pair #14 are accepted as stale-groundshare inputs.", "- The three replacement venues are carried forward only because the human-confirmed rejection records explicitly identify them; they are not automatically canonical.", "- Cobham FC, Eastwood Community FC and Hayes & Yeading United FC are independent verification units; their current venues are not inferred from their former partners.", "- Corby Town FC is included only as the existing 750m–2km centroid/current-ground check.", "- Romulus FC ↔ Sutton Coldfield Town FC remains outside scope until stronger explicit current evidence exists.", "- This stage publishes nothing and does not alter canonical `GROUNDS`, approval ledgers, `clubfinder.html`, or `competition.json`."]
REPORT.write_text("\n".join(L) + "\n", encoding="utf8")

print("CURRENT VENUE CORRECTION QUEUE v7.9.1")
print("Current-venue correction/check units: 7")
print("Evidenced moved clubs: 3")
print("Former counterpart checks: 3")
print("Centroid/current-ground checks: 1")
print("Held outside queue: 2 club warnings / 1 relationship")
print("Published canonical records: 0")
print("PROPOSAL ONLY / RESEARCH QUEUE.")
