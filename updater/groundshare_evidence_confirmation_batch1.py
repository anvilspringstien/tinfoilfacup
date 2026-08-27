#!/usr/bin/env python3
import json
from pathlib import Path
from datetime import datetime, timezone

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"updater/groundshare-evidence-research-batch1.json"
OUT=ROOT/"updater/groundshare-evidence-confirmation-batch1.json"
REPORT=ROOT/"groundshare-evidence-confirmation-batch1.md"

if not SOURCE.exists():
    raise SystemExit("Missing updater/groundshare-evidence-research-batch1.json. Run v7.8.2 first.")

data=json.loads(SOURCE.read_text(encoding="utf8"))
if data.get("version")!="7.8.2" or data.get("batch")!=1:
    raise SystemExit("Safety stop: unexpected research source/version/batch.")
records=data.get("records") or []
if len(records)!=5:
    raise SystemExit(f"Safety stop: expected exactly 5 Batch 1 research records; found {len(records)}.")
expected={
  1:("Romulus FC","Sutton Coldfield Town FC","B72 1NL"),
  2:("Hackney Wick FC","Witham Town FC","CM8 1UN"),
  3:("Faversham Strike Force FC","Whitstable Town FC","CT5 1QP"),
  4:("Bedworth United FC","Nuneaton Town FC","CV12 8NN"),
  5:("Soul Tower Hamlets FC","Sporting Bengal United FC","E14 7TW"),
}
confirmed=[]; held=[]
for r in records:
    pid=r.get("pair_id")
    if pid not in expected:
        raise SystemExit(f"Safety stop: unexpected pair_id {pid}.")
    a,b,pc=expected[pid]
    if r.get("clubs")!=[a,b] or (r.get("postcode") or "").upper()!=pc:
        raise SystemExit(f"Safety stop: identity/postcode drift in pair #{pid}.")
    if r.get("status")=="CONFIRMED":
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
          "confirmation_note":"Explicit human confirmation accepted from v7.8.2 evidence research. This does not publish canonical GROUNDS records."
        })
    else:
        held.append({
          "pair_id":pid,"clubs":r["clubs"],"postcode":pc,"ground":r.get("ground"),
          "status":"HELD_FOR_MORE_EVIDENCE","research_status":r.get("status"),
          "evidence_note":r.get("evidence_note"),"sources":r.get("sources") or []
        })

if len(confirmed)!=4 or len(held)!=1:
    raise SystemExit(f"Safety stop: expected 4 confirmed and 1 held; got {len(confirmed)} confirmed / {len(held)} held.")
directed=sum(x["relationship_type"]=="DIRECTED_HOST_TENANT" for x in confirmed)
undirected=sum(x["relationship_type"]=="CONFIRMED_SHARED_VENUE_UNDIRECTED" for x in confirmed)
if directed!=3 or undirected!=1:
    raise SystemExit(f"Safety stop: expected 3 directed and 1 undirected confirmations; got {directed}/{undirected}.")
now=datetime.now(timezone.utc)
payload={"checked_at":now.isoformat(),"version":"7.8.3","mode":"CONFIRMATION ONLY / NO PUBLISH","source":"updater/groundshare-evidence-research-batch1.json","batch":1,"confirmed_relationships":4,"directed_host_tenant_relationships":directed,"confirmed_shared_venue_undirected":undirected,"held_for_further_evidence":1,"published_canonical_records":0,"confirmed":confirmed,"held":held}
OUT.write_text(json.dumps(payload,indent=2,ensure_ascii=False)+"\n",encoding="utf8")
L=["# Tin Foil FA Cup — Groundshare Evidence Confirmation — Batch 1","",f"Last checked: **{now.strftime('%d/%m/%Y, %H:%M:%S UTC')}**","","**CONFIRMATION ONLY / NO PUBLISH. No canonical ground record or approval ledger is changed.**","","- 🟢 Confirmed relationships: **4**",f"- ➡️ Directed host/tenant relationships: **{directed}**",f"- ↔️ Confirmed shared-venue relationships without direction: **{undirected}**","- 🟡 Held for further evidence: **1**","- Published canonical records: **0**","","## 🟢 Human-confirmed relationships",""]
for r in confirmed:
    L += [f"### #{r['pair_id']} — {r['clubs'][0]} ↔ {r['clubs'][1]}","",f"- Status: **HUMAN_CONFIRMED**",f"- Relationship type: **{r['relationship_type']}**",f"- Ground: **{r['ground']}**",f"- Postcode: **{r['postcode']}**"]
    if r['host']:
        L += [f"- Host: **{r['host']}**",f"- Tenant: **{r['tenant']}**"]
    else:
        L += ["- Host/tenant direction: **UNRESOLVED / deliberately not inferred**"]
    L += [f"- Evidence: {r['evidence_note']}"]+[f"- Source {i}: {u}" for i,u in enumerate(r['sources'],1)]+[""]
L += ["## 🟡 Held for further evidence",""]
for r in held:
    L += [f"### #{r['pair_id']} — {r['clubs'][0]} ↔ {r['clubs'][1]}","",f"- Status: **HELD_FOR_MORE_EVIDENCE**",f"- Research status: **{r['research_status']}**",f"- Reason: {r['evidence_note']}",""]
L += ["## Safety","","- Only v7.8.2 Batch 1 records are accepted; pair identity or postcode drift stops the run.","- Only research records already classified `CONFIRMED` become `HUMAN_CONFIRMED`.","- A directed relationship requires both host and tenant to be explicitly present and to belong to the pair.","- A confirmed shared venue may remain undirected; no host is invented to satisfy an older ledger model.","- Romulus FC ↔ Sutton Coldfield Town FC remains held because v7.8.2 classified it `AMBIGUOUS`.","- This stage does not alter canonical `GROUNDS`, approval ledgers, `clubfinder.html`, or `competition.json`."]
REPORT.write_text("\n".join(L)+"\n",encoding="utf8")
print("GROUNDSHARE EVIDENCE CONFIRMATION v7.8.3 — BATCH 1")
print("Confirmed relationships: 4")
print("Directed host/tenant relationships:",directed)
print("Confirmed shared-venue relationships without direction:",undirected)
print("Held for further evidence: 1")
print("Canonical records published: 0")
print("CONFIRMATION ONLY / NO PUBLISH.")
