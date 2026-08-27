#!/usr/bin/env python3
import json
from pathlib import Path
from datetime import datetime, timezone

ROOT=Path(__file__).resolve().parents[1]
QUEUE=ROOT/"updater/groundshare-evidence-queue.json"
OUT=ROOT/"updater/groundshare-evidence-research-batch1.json"
REPORT=ROOT/"groundshare-evidence-research-batch1.md"

if not QUEUE.exists():
    raise SystemExit("Missing updater/groundshare-evidence-queue.json. Run v7.8.1 first.")

q=json.loads(QUEUE.read_text(encoding="utf8"))
if q.get("version")!="7.8.1" or len(q.get("pairs",[]))!=15:
    raise SystemExit("Safety stop: expected the 15-pair v7.8.1 evidence queue.")

expected={
  1:{"clubs":["Romulus FC","Sutton Coldfield Town FC"],"postcode":"B72 1NL"},
  2:{"clubs":["Hackney Wick FC","Witham Town FC"],"postcode":"CM8 1UN"},
  3:{"clubs":["Faversham Strike Force FC","Whitstable Town FC"],"postcode":"CT5 1QP"},
  4:{"clubs":["Bedworth United FC","Nuneaton Town FC"],"postcode":"CV12 8NN"},
  5:{"clubs":["Soul Tower Hamlets FC","Sporting Bengal United FC"],"postcode":"E14 7TW"},
}

# Curated current/public evidence gathered for Batch 1. This stage records research only.
research={
  1:{
    "status":"AMBIGUOUS",
    "host":None,"tenant":None,
    "ground":"Central Ground / Coles Lane",
    "evidence_note":"Current 2026/27 fixture evidence places Romulus home matches at Central Ground, Coles Lane, B72 1NL, but the evidence gathered for this batch does not explicitly establish a current Romulus ↔ Sutton Coldfield Town groundshare or host/tenant direction.",
    "sources":["https://runcorntown.co.uk/news2.php?id=3401"],
  },
  2:{
    "status":"CONFIRMED",
    "host":"Witham Town FC","tenant":"Hackney Wick FC",
    "ground":"Simarco Stadium",
    "evidence_note":"Current 2026/27 Essex Senior League reporting explicitly lists Hackney Wick as groundsharing at Witham Town; independent current league-opponent reporting also describes Hackney Wick as playing at Witham.",
    "sources":["https://www.harwichandparkeston.com/news/shrimpers-staying-in-esl-2979068.html","https://www.claptoncfc.co.uk/2026/05/14/clapton-cfc-mens-first-team-placed-in-the-essex-senior-league-for-2026-27/"],
  },
  3:{
    "status":"CONFIRMED",
    "host":"Whitstable Town FC","tenant":"Faversham Strike Force FC",
    "ground":"The Belmont Stadium / YMS Stadium",
    "evidence_note":"Faversham Strike Force announced in April 2025 that its Men's First Team would groundshare with Whitstable Town for the next two seasons. Whitstable's July 2026 match report still describes Strike Force as sharing its stadium, confirming the arrangement remains current in 2026/27.",
    "sources":["https://www.favershamstrikeforce.co.uk/news/groundshare-with-whitstable-town-fc-for-mens-first-team-next-season","https://www.whitstabletownfc.club/teams/224251/match-centre/0-6515623/report"],
  },
  4:{
    "status":"CONFIRMED",
    "host":"Bedworth United FC","tenant":"Nuneaton Town FC",
    "ground":"The Oval",
    "evidence_note":"Nuneaton Town's current match-day information explicitly says its home games are at The Oval, home of Bedworth United FC, under a pitch-hire agreement, and gives CV12 8NN. This explicitly establishes Bedworth as host and Nuneaton as tenant for the current period.",
    "sources":["https://www.nuneatontownfc.co.uk/match-day-information"],
  },
  5:{
    "status":"CONFIRMED",
    "host":None,"tenant":None,
    "ground":"Mile End Stadium",
    "evidence_note":"Current 2026/27 Essex Senior League reporting explicitly lists SOUL Tower Hamlets and Sporting Bengal United as groundsharing with each other at Mile End Stadium. The evidence supports the shared relationship but not a reliable host/tenant direction, so direction remains unresolved.",
    "sources":["https://www.harwichandparkeston.com/news/shrimpers-staying-in-esl-2979068.html"],
  },
}

pairs_by_id={p.get("pair_id"):p for p in q["pairs"]}
rows=[]
for pid in range(1,6):
    p=pairs_by_id.get(pid)
    if not p:
        raise SystemExit(f"Safety stop: missing expected pair #{pid}.")
    exp=expected[pid]
    if p.get("clubs")!=exp["clubs"] or p.get("postcode")!=exp["postcode"]:
        raise SystemExit(f"Safety stop: v7.8.1 pair #{pid} no longer matches reviewed Batch 1 scope.")
    r=research[pid]
    rows.append({"pair_id":pid,"clubs":p["clubs"],"postcode":p["postcode"],"queue_records":p.get("club_records",[]),**r})

counts={s:sum(1 for r in rows if r["status"]==s) for s in ("CONFIRMED","AMBIGUOUS","NOT_CURRENT")}
now=datetime.now(timezone.utc)
payload={
 "checked_at":now.isoformat(),"version":"7.8.2","mode":"PROPOSAL ONLY / RESEARCH",
 "source":"updater/groundshare-evidence-queue.json","batch":1,"pairs_researched":5,
 "confirmed":counts["CONFIRMED"],"ambiguous":counts["AMBIGUOUS"],"not_current":counts["NOT_CURRENT"],"records":rows
}
OUT.write_text(json.dumps(payload,indent=2,ensure_ascii=False)+"\n",encoding="utf8")

L=["# Tin Foil FA Cup — Groundshare Evidence Research — Batch 1","",f"Last checked: **{now.strftime('%d/%m/%Y, %H:%M:%S UTC')}**","","**PROPOSAL ONLY / RESEARCH. No approval ledger or canonical ground record is changed.**","",f"- 🏟️ Relationships researched: **5**",f"- 🟢 Confirmed from explicit current/public evidence: **{counts['CONFIRMED']}**",f"- 🟡 Ambiguous / more explicit evidence required: **{counts['AMBIGUOUS']}**",f"- 🔴 Not current / rejected: **{counts['NOT_CURRENT']}**","","## Results",""]
for r in rows:
    icon={"CONFIRMED":"🟢","AMBIGUOUS":"🟡","NOT_CURRENT":"🔴"}[r["status"]]
    L += [f"### {icon} #{r['pair_id']} — {r['clubs'][0]} ↔ {r['clubs'][1]}","",f"- Classification: **{r['status']}**",f"- Queue postcode: **{r['postcode']}**",f"- Ground: **{r['ground']}**"]
    if r["host"] and r["tenant"]:
        L.append(f"- Evidence-supported direction: **{r['tenant']} → {r['host']}**")
    else:
        L.append("- Evidence-supported direction: **UNRESOLVED / not inferred**")
    L.append(f"- Evidence: {r['evidence_note']}")
    for i,u in enumerate(r["sources"],1): L.append(f"- Source {i}: {u}")
    L.append("")
L += ["## Safety","","- Only v7.8.1 pairs #1–#5 are in scope; changed club/postcode identities stop the run.","- CONFIRMED means evidence research supports the relationship; it is **not** an approval and does not publish anything.","- Host/tenant direction is recorded only where explicit evidence supports it.","- Ground-name sponsorship variants are preserved in the research note rather than silently normalised.","- `clubfinder.html`, canonical `GROUNDS`, approval ledgers, and `competition.json` are untouched."]
REPORT.write_text("\n".join(L)+"\n",encoding="utf8")

print("GROUNDSHARE EVIDENCE RESEARCH v7.8.2 — BATCH 1")
print("Relationships researched: 5")
print("Confirmed:",counts["CONFIRMED"])
print("Ambiguous:",counts["AMBIGUOUS"])
print("Not current/rejected:",counts["NOT_CURRENT"])
print("PROPOSAL ONLY / RESEARCH.")
