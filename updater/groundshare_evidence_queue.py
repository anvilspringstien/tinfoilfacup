#!/usr/bin/env python3
import json
from collections import defaultdict
from pathlib import Path
from datetime import datetime, timezone

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"updater/ground-exception-verification.json"
OUT=ROOT/"updater/groundshare-evidence-queue.json"
REPORT=ROOT/"groundshare-evidence-queue.md"

if not SOURCE.exists():
    raise SystemExit("Missing updater/ground-exception-verification.json. Run resolution-aware verification first.")

data=json.loads(SOURCE.read_text(encoding="utf8"))
records=data.get("records",[])

shared=[]
for r in records:
    if r.get("state")!="HUMAN_DECISION":
        continue
    flags=set(r.get("flags") or [])
    if "SHARED_POSTCODE" not in flags:
        continue
    if r.get("reason")!="Approve shared-ground relationship":
        continue
    shared.append(r)

# Current post-v7.8.0 state should contain 30 club-level warnings which collapse
# to 15 two-club relationships. Stop rather than silently changing scope.
if len(shared)!=30:
    raise SystemExit(f"Safety stop: expected exactly 30 shared-ground human-decision records; found {len(shared)}.")

by_postcode=defaultdict(list)
for r in shared:
    pc=(r.get("postcode") or "").strip().upper()
    if not pc:
        raise SystemExit("Safety stop: shared-ground record without postcode.")
    by_postcode[pc].append(r)

pairs=[]
problems=[]
for pc,rs in sorted(by_postcode.items()):
    if len(rs)!=2:
        problems.append({"postcode":pc,"club_count":len(rs),"clubs":[x.get("club") for x in rs]})
        continue
    clubs=sorted(rs,key=lambda x:x.get("club") or "")
    a,b=clubs
    pairs.append({
        "pair_id":len(pairs)+1,
        "postcode":pc,
        "clubs":[a.get("club"),b.get("club")],
        "club_records":[
            {
                "club":x.get("club"),
                "fchd_match":x.get("fchd_match"),
                "ground_candidate":x.get("ground_candidate"),
                "postcode":x.get("postcode"),
                "distance_km":x.get("distance_km"),
                "flags":x.get("flags") or [],
                "raw_lines":x.get("raw_lines") or [],
            } for x in clubs
        ],
        "relationship_status":"CURRENT_SOURCE_CONFIRMATION_REQUIRED",
        "host_tenant_direction":"UNRESOLVED",
        "decision_note":"Shared postcode/FCHD evidence groups these clubs for review only. It does not prove a groundshare or determine host/tenant direction.",
    })

if problems:
    raise SystemExit("Safety stop: one or more shared postcodes did not resolve to exactly two actionable clubs: "+json.dumps(problems,ensure_ascii=False))
if len(pairs)!=15:
    raise SystemExit(f"Safety stop: expected exactly 15 unique pairs; found {len(pairs)}.")

now=datetime.now(timezone.utc)
payload={
    "checked_at":now.isoformat(),
    "version":"7.8.1",
    "mode":"PROPOSAL ONLY",
    "source":"updater/ground-exception-verification.json",
    "club_level_shared_warnings":len(shared),
    "unique_relationships":len(pairs),
    "research_required":len(pairs),
    "approved_relationships":0,
    "pairs":pairs,
}
OUT.write_text(json.dumps(payload,indent=2,ensure_ascii=False)+"\n",encoding="utf8")

L=[
"# Tin Foil FA Cup — Groundshare Evidence Queue","",
f"Last checked: **{now.strftime('%d/%m/%Y, %H:%M:%S UTC')}**","",
"**PROPOSAL ONLY. No groundshare is approved and no canonical ground record is published.**","",
f"- 🏟️ Club-level shared-ground warnings grouped: **{len(shared)}**",
f"- 📦 Unique candidate relationships: **{len(pairs)}**",
f"- 🟡 Current-source confirmations required: **{len(pairs)}**",
"- 🟢 Approved by this stage: **0**","",
"Each row is a research unit only. A shared postcode does **not** establish a groundshare and this stage does **not** infer which club is host or tenant.","",
"## 🟡 Groundshare relationships requiring confirmation",""
]
for p in pairs:
    a,b=p["club_records"]
    L.append(f"### #{p['pair_id']} — {p['clubs'][0]} ↔ {p['clubs'][1]}")
    L.append("")
    L.append(f"- Postcode: **{p['postcode']}**")
    L.append(f"- **{a['club']}** — {a.get('ground_candidate') or 'Ground candidate unavailable'} • separation `{a.get('distance_km')} km`")
    L.append(f"- **{b['club']}** — {b.get('ground_candidate') or 'Ground candidate unavailable'} • separation `{b.get('distance_km')} km`")
    L.append("- Decision required: **Confirm current relationship from an explicit current/public source; identify host/tenant only if the source supports it.**")
    L.append("")

L += [
"## Safety","",
"- Input is restricted to current `HUMAN_DECISION` records explicitly flagged `SHARED_POSTCODE` with reason `Approve shared-ground relationship`.",
"- v7.8.1 expects exactly 30 club-level records and exactly 15 two-club relationships; any scope change stops the run.",
"- Ground-name differences are preserved rather than normalised away because sponsorship/host naming can legitimately differ.",
"- No relationship is approved merely because two records share a postcode.",
"- No host/tenant direction is inferred automatically.",
"- `clubfinder.html`, canonical `GROUNDS`, approval ledgers, and `competition.json` are untouched."
]
REPORT.write_text("\n".join(L)+"\n",encoding="utf8")

print("GROUNDSHARE EVIDENCE QUEUE v7.8.1")
print("Club-level shared warnings:",len(shared))
print("Unique candidate relationships:",len(pairs))
print("Current-source confirmations required:",len(pairs))
print("Approved relationships: 0")
print("PROPOSAL ONLY.")
