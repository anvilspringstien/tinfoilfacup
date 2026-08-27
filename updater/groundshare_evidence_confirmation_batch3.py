#!/usr/bin/env python3
import json
from pathlib import Path
from datetime import datetime, timezone

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"updater/groundshare-evidence-research-batch3.json"
OUT=ROOT/"updater/groundshare-evidence-confirmation-batch3.json"
REPORT=ROOT/"groundshare-evidence-confirmation-batch3.md"

if not SOURCE.exists():
    raise SystemExit("Missing updater/groundshare-evidence-research-batch3.json. Run v7.8.8 first.")

data=json.loads(SOURCE.read_text(encoding="utf8"))
if data.get("version")!="7.8.8" or data.get("batch")!=3:
    raise SystemExit("Safety stop: unexpected research source/version/batch.")
records=data.get("records") or []
if len(records)!=5:
    raise SystemExit(f"Safety stop: expected exactly 5 Batch 3 research records; found {len(records)}.")
expected={
  11:("Grays Athletic FC","Tilbury FC","RM18 8NL"),
  12:("Enfield FC","Hertford Town FC","SG13 8EX"),
  13:("Balham FC","Tooting & Mitcham United FC","SM4 6BF"),
  14:("Hayes & Yeading United FC","Southall FC","UB4 0SL"),
  15:("Dudley Town FC","Sporting Khalsa FC","WV13 3BB"),
}
confirmed=[]; rejected=[]
for r in records:
    pid=r.get("pair_id")
    if pid not in expected:
        raise SystemExit(f"Safety stop: unexpected pair_id {pid}.")
    a,b,pc=expected[pid]
    if r.get("clubs")!=[a,b] or (r.get("postcode") or "").upper()!=pc:
        raise SystemExit(f"Safety stop: identity/postcode drift in pair #{pid}.")
    status=r.get("status")
    if status=="CONFIRMED":
        if not r.get("sources") or not r.get("evidence_note") or not r.get("ground"):
            raise SystemExit(f"Safety stop: confirmed pair #{pid} lacks evidence/source/ground.")
        host=r.get("host"); tenant=r.get("tenant")
        if not host or not tenant:
            raise SystemExit(f"Safety stop: confirmed Batch 3 pair #{pid} lacks explicit host/tenant direction.")
        if host not in r["clubs"] or tenant not in r["clubs"] or host==tenant:
            raise SystemExit(f"Safety stop: invalid host/tenant direction in pair #{pid}.")
        confirmed.append({
          "pair_id":pid,"clubs":r["clubs"],"postcode":pc,"ground":r["ground"],
          "status":"HUMAN_CONFIRMED","relationship_type":"DIRECTED_HOST_TENANT",
          "host":host,"tenant":tenant,"evidence_note":r["evidence_note"],"sources":r["sources"],
          "confirmation_note":"Explicit human confirmation accepted from v7.8.8 evidence research. This does not publish canonical GROUNDS records."
        })
    elif status=="NOT_CURRENT":
        if not r.get("sources") or not r.get("evidence_note") or not r.get("ground"):
            raise SystemExit(f"Safety stop: NOT_CURRENT pair #{pid} lacks evidence/source/current-ground information.")
        rejected.append({
          "pair_id":pid,"clubs":r["clubs"],"postcode":pc,"current_ground":r["ground"],
          "status":"HUMAN_REJECTED_NOT_CURRENT","research_status":"NOT_CURRENT",
          "evidence_note":r["evidence_note"],"sources":r["sources"],
          "confirmation_note":"Human confirmation accepts the v7.8.8 finding that this queued relationship is not current. It is excluded from groundshare promotion."
        })
    else:
        raise SystemExit(f"Safety stop: unexpected Batch 3 research status {status!r} in pair #{pid}.")

if len(confirmed)!=4 or len(rejected)!=1:
    raise SystemExit(f"Safety stop: expected 4 confirmed and 1 NOT_CURRENT; got {len(confirmed)} confirmed / {len(rejected)} rejected.")
if {x["pair_id"] for x in confirmed}!={11,12,13,15}:
    raise SystemExit("Safety stop: only pairs #11, #12, #13 and #15 may be confirmed in Batch 3.")
if {x["pair_id"] for x in rejected}!={14}:
    raise SystemExit("Safety stop: only pair #14 may be confirmed NOT_CURRENT in Batch 3.")

now=datetime.now(timezone.utc)
payload={
  "checked_at":now.isoformat(),"version":"7.8.9","mode":"CONFIRMATION ONLY / NO PUBLISH",
  "source":"updater/groundshare-evidence-research-batch3.json","batch":3,
  "confirmed_relationships":4,"directed_host_tenant_relationships":4,
  "confirmed_shared_venue_undirected":0,"rejected_not_current_relationships":1,
  "published_canonical_records":0,"confirmed":confirmed,"rejected_not_current":rejected
}
OUT.write_text(json.dumps(payload,indent=2,ensure_ascii=False)+"\n",encoding="utf8")

L=["# Tin Foil FA Cup — Groundshare Evidence Confirmation — Batch 3","",f"Last checked: **{now.strftime('%d/%m/%Y, %H:%M:%S UTC')}**","","**CONFIRMATION ONLY / NO PUBLISH. No canonical ground record or approval ledger is changed.**","","- 🟢 Confirmed relationships: **4**","- ➡️ Directed host/tenant relationships: **4**","- ↔️ Confirmed shared-venue relationships without direction: **0**","- 🔴 Rejected / not-current relationships: **1**","- Published canonical records: **0**","","## 🟢 Human-confirmed relationships",""]
for r in confirmed:
    L += [f"### #{r['pair_id']} — {r['clubs'][0]} ↔ {r['clubs'][1]}","",f"- Status: **HUMAN_CONFIRMED**",f"- Relationship type: **{r['relationship_type']}**",f"- Ground: **{r['ground']}**",f"- Postcode: **{r['postcode']}**",f"- Host: **{r['host']}**",f"- Tenant: **{r['tenant']}**",f"- Evidence: {r['evidence_note']}"]+[f"- Source {i}: {u}" for i,u in enumerate(r['sources'],1)]+[""]
L += ["## 🔴 Human-confirmed not-current relationships",""]
for r in rejected:
    L += [f"### #{r['pair_id']} — {r['clubs'][0]} ↔ {r['clubs'][1]}","",f"- Status: **HUMAN_REJECTED_NOT_CURRENT**",f"- Queued postcode: **{r['postcode']}**",f"- Current venue identified by research: **{r['current_ground']}**",f"- Decision: **Do not approve or promote this queued groundshare relationship.**",f"- Evidence: {r['evidence_note']}"]+[f"- Source {i}: {u}" for i,u in enumerate(r['sources'],1)]+[""]
L += ["## Safety","","- Only v7.8.8 Batch 3 records are accepted; pair identity or postcode drift stops the run.","- Only research records classified `CONFIRMED` become `HUMAN_CONFIRMED`.","- Only research records classified `NOT_CURRENT` become `HUMAN_REJECTED_NOT_CURRENT`.","- All four confirmed Batch 3 relationships require explicit host and tenant identities; no direction is invented.","- Hayes & Yeading United FC ↔ Southall FC is explicitly excluded from later groundshare promotion.","- Southall FC's current Honeycroft venue is evidence for a separate current-venue correction/research stage; this confirmation does not publish it.","- This stage does not alter canonical `GROUNDS`, approval ledgers, `clubfinder.html`, or `competition.json`."]
REPORT.write_text("\n".join(L)+"\n",encoding="utf8")

print("GROUNDSHARE EVIDENCE CONFIRMATION v7.8.9 — BATCH 3")
print("Confirmed relationships: 4")
print("Directed host/tenant relationships: 4")
print("Confirmed shared-venue relationships without direction: 0")
print("Rejected/not-current relationships: 1")
print("Canonical records published: 0")
print("CONFIRMATION ONLY / NO PUBLISH.")
