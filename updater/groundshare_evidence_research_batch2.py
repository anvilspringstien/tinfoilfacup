#!/usr/bin/env python3
import json
from pathlib import Path
from datetime import datetime, timezone

ROOT=Path(__file__).resolve().parents[1]
QUEUE=ROOT/"updater/groundshare-evidence-queue.json"
OUT=ROOT/"updater/groundshare-evidence-research-batch2.json"
REPORT=ROOT/"groundshare-evidence-research-batch2.md"

if not QUEUE.exists():
    raise SystemExit("Missing updater/groundshare-evidence-queue.json. Run v7.8.1 first.")

q=json.loads(QUEUE.read_text(encoding="utf8"))
if q.get("version")!="7.8.1" or len(q.get("pairs",[]))!=15:
    raise SystemExit("Safety stop: expected the 15-pair v7.8.1 evidence queue.")

expected={
  6:{"clubs":["Walthamstow FC","West Essex FC"],"postcode":"E17 4JP"},
  7:{"clubs":["Broadfields United FC","Rayners Lane FC"],"postcode":"HA2 0XH"},
  8:{"clubs":["Cobham FC","Epsom & Ewell FC"],"postcode":"KT11 1AA"},
  9:{"clubs":["Barwell FC","Hinckley AFC"],"postcode":"LE9 8FQ"},
  10:{"clubs":["Belper United FC","Eastwood Community FC"],"postcode":"NG16 3HB"},
}

# Curated current/public evidence gathered for Batch 2. Research only: no approval or publish.
research={
  6:{
    "status":"CONFIRMED",
    "host":None,"tenant":None,
    "ground":"Wadham Lodge Stadium / Wadham Lodge Sports Ground (Match Day Centres)",
    "evidence_note":"Current Essex Senior League club information says West Essex's Senior 1st XI groundshare at Wadham Lodge Stadium, while current FA county directory information places both Walthamstow and West Essex at Wadham Lodge, E17 4JP. West Essex's own ground announcement explicitly described sharing the stadium with Walthamstow. The shared venue is therefore supported, but because the venue is operated separately and the current evidence does not safely establish a landlord/tenant direction between the two clubs, direction remains unresolved.",
    "sources":[
      "https://www.essexseniorleague.co.uk/en_US/archive15032-club-info/92007845",
      "https://www.thefa.com/-/media/cfa/essexfa/files/handbook/2025-26/section-3---club-and-competition-directory---men---senior-status.ashx",
      "https://westessexfc.org.uk/news/club-statement-re--ground-announcement"
    ],
  },
  7:{
    "status":"CONFIRMED",
    "host":"Rayners Lane FC","tenant":"Broadfields United FC",
    "ground":"Tithe Farm Sports & Social Club",
    "evidence_note":"Rayners Lane's current 2026/27 official site states that Broadfields United groundshare at Tithe Farm, and Broadfields United's own club history records the move into a groundshare agreement with Rayners Lane at Tithe Farm. Current venue information also lists both clubs there. This supports Rayners Lane as the host club and Broadfields United as tenant.",
    "sources":[
      "https://raynerslanefc.co.uk/",
      "https://www.broadfieldsunitedfc.co.uk/a/club-history-64122.html",
      "https://www.tithefarmclub.com/whats-on/"
    ],
  },
  8:{
    "status":"NOT_CURRENT",
    "host":None,"tenant":None,
    "ground":"Chalky Lane, Chessington",
    "evidence_note":"The queued Cobham relationship is no longer current. Epsom & Ewell's own history says the club returned to Cobham for 2025/26 but moved again in October 2025 to Chessington & Hook United. Its August 2026 FA Cup match preview identifies Chalky Lane as its 2026/27 home venue. Cobham ↔ Epsom & Ewell must therefore not be approved from the stale shared-postcode candidate.",
    "sources":[
      "https://epsomandewellfc.co.uk/club/history/",
      "https://epsomandewellfc.co.uk/2026/08/match-preview-epsom-ewell-vs-chipstead-emirates-f-a-cup-extra-preliminary-round/"
    ],
  },
  9:{
    "status":"CONFIRMED",
    "host":"Barwell FC","tenant":"Hinckley AFC",
    "ground":"Kirkby Road",
    "evidence_note":"Hinckley AFC's current official ground information says the club plays its home matches at Barwell FC, Kirkby Road, LE9 8FQ. A July 2026 FA Cup announcement explicitly calls Barwell the landlords when explaining a fixture move caused by Barwell also being at home. This establishes Barwell as host and Hinckley AFC as tenant for 2026/27.",
    "sources":[
      "https://hinckleyafc.co.uk/first-team/where-are-we/",
      "https://hinckleyafc.co.uk/2026/07/19/friday-night-fa-cup-football-at-kirkby-road/"
    ],
  },
  10:{
    "status":"NOT_CURRENT",
    "host":None,"tenant":None,
    "ground":"Don Amott Arena, Mickleover",
    "evidence_note":"The queued Eastwood relationship is no longer current. Belper United announced in March 2026 that it would leave Eastwood CFC at the end of the 2025/26 season, ending a three-year groundshare. Belper United's current official site now gives the Don Amott Arena, home of Mickleover FC, as its ground. Eastwood's current site continues to identify Coronation Park as Eastwood's home. Belper United ↔ Eastwood Community must therefore not be approved for 2026/27.",
    "sources":[
      "https://belperunited.co.uk/",
      "https://www.eastwoodcfc.co.uk/"
    ],
  },
}

pairs_by_id={p.get("pair_id"):p for p in q["pairs"]}
rows=[]
for pid in range(6,11):
    p=pairs_by_id.get(pid)
    if not p:
        raise SystemExit(f"Safety stop: missing expected pair #{pid}.")
    exp=expected[pid]
    if p.get("clubs")!=exp["clubs"] or p.get("postcode")!=exp["postcode"]:
        raise SystemExit(f"Safety stop: v7.8.1 pair #{pid} no longer matches reviewed Batch 2 scope.")
    r=research[pid]
    rows.append({"pair_id":pid,"clubs":p["clubs"],"postcode":p["postcode"],"queue_records":p.get("club_records",[]),**r})

counts={s:sum(1 for r in rows if r["status"]==s) for s in ("CONFIRMED","AMBIGUOUS","NOT_CURRENT")}
now=datetime.now(timezone.utc)
payload={
 "checked_at":now.isoformat(),"version":"7.8.5","mode":"PROPOSAL ONLY / RESEARCH",
 "source":"updater/groundshare-evidence-queue.json","batch":2,"pairs_researched":5,
 "confirmed":counts["CONFIRMED"],"ambiguous":counts["AMBIGUOUS"],"not_current":counts["NOT_CURRENT"],"records":rows
}
OUT.write_text(json.dumps(payload,indent=2,ensure_ascii=False)+"\n",encoding="utf8")

L=["# Tin Foil FA Cup — Groundshare Evidence Research — Batch 2","",f"Last checked: **{now.strftime('%d/%m/%Y, %H:%M:%S UTC')}**","","**PROPOSAL ONLY / RESEARCH. No approval ledger or canonical ground record is changed.**","",f"- 🏟️ Relationships researched: **5**",f"- 🟢 Confirmed from explicit current/public evidence: **{counts['CONFIRMED']}**",f"- 🟡 Ambiguous / more explicit evidence required: **{counts['AMBIGUOUS']}**",f"- 🔴 Not current / rejected: **{counts['NOT_CURRENT']}**","","## Results",""]
for r in rows:
    icon={"CONFIRMED":"🟢","AMBIGUOUS":"🟡","NOT_CURRENT":"🔴"}[r["status"]]
    L += [f"### {icon} #{r['pair_id']} — {r['clubs'][0]} ↔ {r['clubs'][1]}","",f"- Classification: **{r['status']}**",f"- Queue postcode: **{r['postcode']}**",f"- Ground/current venue: **{r['ground']}**"]
    if r["host"] and r["tenant"]:
        L.append(f"- Evidence-supported direction: **{r['tenant']} → {r['host']}**")
    else:
        L.append("- Evidence-supported direction: **UNRESOLVED / not inferred**")
    L.append(f"- Evidence: {r['evidence_note']}")
    for i,u in enumerate(r["sources"],1): L.append(f"- Source {i}: {u}")
    L.append("")
L += ["## Safety","","- Only v7.8.1 pairs #6–#10 are in scope; changed club/postcode identities stop the run.","- CONFIRMED means evidence research supports the relationship; it is **not** an approval and does not publish anything.","- NOT_CURRENT records are explicitly rejected from any later groundshare approval/promotion stage.","- Host/tenant direction is recorded only where explicit evidence supports it.","- A current shared venue may remain undirected; no host is invented merely to fit the ledger model.","- Ground-name sponsorship/current-venue changes are preserved rather than silently normalised.","- `clubfinder.html`, canonical `GROUNDS`, approval ledgers, and `competition.json` are untouched."]
REPORT.write_text("\n".join(L)+"\n",encoding="utf8")

print("GROUNDSHARE EVIDENCE RESEARCH v7.8.5 — BATCH 2")
print("Relationships researched: 5")
print("Confirmed:",counts["CONFIRMED"])
print("Ambiguous:",counts["AMBIGUOUS"])
print("Not current/rejected:",counts["NOT_CURRENT"])
print("PROPOSAL ONLY / RESEARCH.")
