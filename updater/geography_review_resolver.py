#!/usr/bin/env python3
import json
from pathlib import Path
from datetime import datetime,timezone

ROOT=Path(__file__).resolve().parents[1]
EVID=ROOT/"updater/geography-review-evidence.json"
OUT=ROOT/"updater/geography-review.json"
REPORT=ROOT/"ground-geography-review.md"

data=json.loads(EVID.read_text(encoding="utf8"))
rows=data["evidence"]
allowed={"CONFIRMED","CHANGED","AMBIGUOUS"}
if len(rows)!=7: raise SystemExit("Safety stop: expected exactly seven geography-review cases.")
if any(r["status"] not in allowed for r in rows): raise SystemExit("Safety stop: unknown classification.")

counts={k:sum(r["status"]==k for r in rows) for k in allowed}
payload={
 "checked_at":datetime.now(timezone.utc).isoformat(),
 "version":"7.7.5",
 "mode":"PROPOSAL ONLY",
 "counts":counts,
 "records":rows
}
OUT.write_text(json.dumps(payload,indent=2,ensure_ascii=False)+"\n",encoding="utf8")

icons={"CONFIRMED":"🟢","CHANGED":"🟡","AMBIGUOUS":"🔴"}
L=[
"# Tin Foil FA Cup — Geography Review Resolver","",
f"Last checked: **{datetime.now(timezone.utc).strftime('%d/%m/%Y, %H:%M:%S UTC')}**","",
"**PROPOSAL ONLY — no canonical ground record is changed by this workflow.**","",
f"- 🟢 Current ground/postcode confirmed: **{counts['CONFIRMED']}**",
f"- 🟡 Current source indicates postcode correction: **{counts['CHANGED']}**",
f"- 🔴 Conflicting current evidence / manual research: **{counts['AMBIGUOUS']}**",
f"- ⚪ Geography-review cases checked: **{len(rows)}**",""
]
for status,title in [
 ("CONFIRMED","🟢 Confirmed current ground/postcode"),
 ("CHANGED","🟡 Correction proposed — do not publish automatically"),
 ("AMBIGUOUS","🔴 Conflicting evidence — stop and investigate")]:
    L += [f"## {title}",""]
    xs=[r for r in rows if r["status"]==status]
    if not xs: L.append("None.")
    for r in xs:
        newpc=r.get("current_postcode") or "UNRESOLVED"
        L.append(f"- **{r['club']}** — queued: {r['old_ground']} • {r['old_postcode']} → current: {r['current_ground']} • {newpc} — {r['note']}")
        for u in r["sources"]:
            L.append(f"  - Evidence: {u}")
    L.append("")

L += ["## Safety","",
"- This workflow writes only its JSON/report outputs.",
"- It does not modify `clubfinder.html`, `competition.json`, canonical `GROUNDS`, or the approval ledger.",
"- A changed postcode is never allowed to inherit old coordinates automatically.",
"- Any proposed postcode correction must be independently geocoded/validated before later promotion.",
"- Conflicting evidence remains red rather than being guessed."
]
REPORT.write_text("\n".join(L)+"\n",encoding="utf8")
print("GEOGRAPHY REVIEW RESOLVER v7.7.5")
print("Confirmed:",counts["CONFIRMED"])
print("Postcode corrections proposed:",counts["CHANGED"])
print("Ambiguous:",counts["AMBIGUOUS"])
print("Cases checked:",len(rows))
print("PROPOSAL ONLY.")
