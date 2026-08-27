#!/usr/bin/env python3
import json
from pathlib import Path
from datetime import datetime, timezone

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"updater/groundshare-evidence-research-batch2.json"
OUT=ROOT/"updater/groundshare-evidence-confirmation-batch2.json"
REPORT=ROOT/"groundshare-evidence-confirmation-batch2.md"

if not SOURCE.exists():
    raise SystemExit("Missing updater/groundshare-evidence-research-batch2.json. Run v7.8.5 first.")

data=json.loads(SOURCE.read_text(encoding="utf8"))
if data.get("version")!="7.8.5" or data.get("batch")!=2:
    raise SystemExit("Safety stop: unexpected research source/version/batch.")
records=data.get("records") or []
if len(records)!=5:
    raise SystemExit(f"Safety stop: expected exactly 5 Batch 2 research records; found {len(records)}.")
expected={
  6:("Walthamstow FC","West Essex FC","E17 4JP"),
  7:("Broadfields United FC","Rayners Lane FC","HA2 0XH"),
  8:("Cobham FC","Epsom & Ewell FC","KT11 1AA"),
  9:("Barwell FC","Hinckley AFC","LE9 8FQ"),
  10:("Belper United FC","Eastwood Community FC","NG16 3HB"),
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
        if bool(host) != bool(tenant):
            raise SystemExit(f"Safety stop: pair #{pid} has incomplete host/tenant direction.")
        if host and tenant:
            if host not in r["clubs"] or tenant not in r["clubs"] or host==tenant:
                raise SystemExit(f"Safety stop: invalid host/tenant direction in pair #{pid}.")
            relationship_type="DIRECTED_HOST_TENANT"
        else:
            relationship_type="CONFIRMED_SHARED_VENUE_UNDIRECTED"
        confirmed.append({
          "pair_id":pid,"clubs":r["clubs"],"postcode":pc,"ground":r["ground"],
          "status":"HUMAN_CONFIRMED","relationship_type":relationship_type,
          "host":host,"tenant":tenant,"evidence_note":r["evidence_note"],"sources":r["sources"],
          "confirmation_note":"Explicit human confirmation accepted from v7.8.5 evidence research. This does not publish canonical GROUNDS records."
        })
    elif status=="NOT_CURRENT":
        if not r.get("sources") or not r.get("evidence_note") or not r.get("ground"):
            raise SystemExit(f"Safety stop: NOT_CURRENT pair #{pid} lacks evidence/source/current-ground information.")
        rejected.append({
          "pair_id":pid,"clubs":r["clubs"],"postcode":pc,"current_ground":r["ground"],
          "status":"HUMAN_REJECTED_NOT_CURRENT","research_status":"NOT_CURRENT",
          "evidence_note":r["evidence_note"],"sources":r["sources"],
          "confirmation_note":"Human confirmation accepts the v7.8.5 finding that this queued relationship is not current. It is excluded from groundshare promotion."
        })
    else:
        raise SystemExit(f"Safety stop: unexpected Batch 2 research status {status!r} in pair #{pid}.")

if len(confirmed)!=3 or len(rejected)!=2:
    raise SystemExit(f"Safety stop: expected 3 confirmed and 2 NOT_CURRENT; got {len(confirmed)} confirmed / {len(rejected)} rejected.")
directed=sum(x["relationship_type"]=="DIRECTED_HOST_TENANT" for x in confirmed)
undirected=sum(x["relationship_type"]=="CONFIRMED_SHARED_VENUE_UNDIRECTED" for x in confirmed)
if directed!=2 or undirected!=1:
    raise SystemExit(f"Safety stop: expected 2 directed and 1 undirected confirmations; got {directed}/{undirected}.")
if {x["pair_id"] for x in rejected}!={8,10}:
    raise SystemExit("Safety stop: only pairs #8 and #10 may be confirmed NOT_CURRENT in Batch 2.")

now=datetime.now(timezone.utc)
payload={
  "checked_at":now.isoformat(),"version":"7.8.6","mode":"CONFIRMATION ONLY / NO PUBLISH",
  "source":"updater/groundshare-evidence-research-batch2.json","batch":2,
  "confirmed_relationships":3,"directed_host_tenant_relationships":directed,
  "confirmed_shared_venue_undirected":undirected,"rejected_not_current_relationships":2,
  "published_canonical_records":0,"confirmed":confirmed,"rejected_not_current":rejected
}
OUT.write_text(json.dumps(payload,indent=2,ensure_ascii=False)+"\n",encoding="utf8")

L=["# Tin Foil FA Cup — Groundshare Evidence Confirmation — Batch 2","",f"Last checked: **{now.strftime('%d/%m/%Y, %H:%M:%S UTC')}**","","**CONFIRMATION ONLY / NO PUBLISH. No canonical ground record or approval ledger is changed.**","","- 🟢 Confirmed relationships: **3**",f"- ➡️ Directed host/tenant relationships: **{directed}**",f"- ↔️ Confirmed shared-venue relationships without direction: **{undirected}**","- 🔴 Rejected / not-current relationships: **2**","- Published canonical records: **0**","","## 🟢 Human-confirmed relationships",""]
for r in confirmed:
    L += [f"### #{r['pair_id']} — {r['clubs'][0]} ↔ {r['clubs'][1]}","",f"- Status: **HUMAN_CONFIRMED**",f"- Relationship type: **{r['relationship_type']}**",f"- Ground: **{r['ground']}**",f"- Postcode: **{r['postcode']}**"]
    if r['host']:
        L += [f"- Host: **{r['host']}**",f"- Tenant: **{r['tenant']}**"]
    else:
        L += ["- Host/tenant direction: **UNRESOLVED / deliberately not inferred**"]
    L += [f"- Evidence: {r['evidence_note']}"]+[f"- Source {i}: {u}" for i,u in enumerate(r['sources'],1)]+[""]
L += ["## 🔴 Human-confirmed not-current relationships",""]
for r in rejected:
    L += [f"### #{r['pair_id']} — {r['clubs'][0]} ↔ {r['clubs'][1]}","",f"- Status: **HUMAN_REJECTED_NOT_CURRENT**",f"- Queued postcode: **{r['postcode']}**",f"- Current venue identified by research: **{r['current_ground']}**",f"- Decision: **Do not approve or promote this queued groundshare relationship.**",f"- Evidence: {r['evidence_note']}"]+[f"- Source {i}: {u}" for i,u in enumerate(r['sources'],1)]+[""]
L += ["## Safety","","- Only v7.8.5 Batch 2 records are accepted; pair identity or postcode drift stops the run.","- Only research records classified `CONFIRMED` become `HUMAN_CONFIRMED`.","- Only research records classified `NOT_CURRENT` become `HUMAN_REJECTED_NOT_CURRENT`.","- A directed relationship requires both host and tenant to be explicitly present and to belong to the pair.","- A confirmed shared venue may remain undirected; no host is invented.","- Cobham FC ↔ Epsom & Ewell FC and Belper United FC ↔ Eastwood Community FC are explicitly excluded from later groundshare promotion.","- The replacement/current venues identified for Epsom & Ewell FC and Belper United FC are evidence for a separate current-venue correction/research stage; this confirmation does not publish them.","- This stage does not alter canonical `GROUNDS`, approval ledgers, `clubfinder.html`, or `competition.json`."]
REPORT.write_text("\n".join(L)+"\n",encoding="utf8")

print("GROUNDSHARE EVIDENCE CONFIRMATION v7.8.6 — BATCH 2")
print("Confirmed relationships: 3")
print("Directed host/tenant relationships:",directed)
print("Confirmed shared-venue relationships without direction:",undirected)
print("Rejected/not-current relationships: 2")
print("Canonical records published: 0")
print("CONFIRMATION ONLY / NO PUBLISH.")
