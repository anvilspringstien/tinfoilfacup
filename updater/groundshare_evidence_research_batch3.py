#!/usr/bin/env python3
import json
from pathlib import Path
from datetime import datetime, timezone

ROOT=Path(__file__).resolve().parents[1]
QUEUE=ROOT/"updater/groundshare-evidence-queue.json"
OUT=ROOT/"updater/groundshare-evidence-research-batch3.json"
REPORT=ROOT/"groundshare-evidence-research-batch3.md"

if not QUEUE.exists():
    raise SystemExit("Missing updater/groundshare-evidence-queue.json. Run v7.8.1 first.")
q=json.loads(QUEUE.read_text(encoding="utf8"))
if q.get("version")!="7.8.1" or len(q.get("pairs",[]))!=15:
    raise SystemExit("Safety stop: expected the 15-pair v7.8.1 evidence queue.")

expected={
  11:{"clubs":["Grays Athletic FC","Tilbury FC"],"postcode":"RM18 8NL"},
  12:{"clubs":["Enfield FC","Hertford Town FC"],"postcode":"SG13 8EX"},
  13:{"clubs":["Balham FC","Tooting & Mitcham United FC"],"postcode":"SM4 6BF"},
  14:{"clubs":["Hayes & Yeading United FC","Southall FC"],"postcode":"UB4 0SL"},
  15:{"clubs":["Dudley Town FC","Sporting Khalsa FC"],"postcode":"WV13 3BB"},
}

research={
  11:{
    "status":"CONFIRMED","host":"Tilbury FC","tenant":"Grays Athletic FC","ground":"The EMR Stadium",
    "evidence_note":"Grays Athletic's current 2026/27 visitor and membership information says its home matches are played at Tilbury Football Club's EMR Stadium, Saint Chads Road, RM18 8NL. This supports Tilbury as host and Grays Athletic as tenant for the current period.",
    "sources":["https://www.graysathletic.co.uk/a/for-visitors-20933.html?page=1","https://www.graysathletic.co.uk/a/202526-grays-athletic-club-member-ground-pass-67766.html"]
  },
  12:{
    "status":"CONFIRMED","host":"Hertford Town FC","tenant":"Enfield FC","ground":"Hertingfordbury Park",
    "evidence_note":"Current 2026/27 fixture information places Enfield home matches at Hertingfordbury Park, while current club-directory information identifies Hertingfordbury Park as Hertford Town's ground and Enfield as a club sharing it. The relationship has been in place since 2024 and remains supported by current venue evidence.",
    "sources":["https://www.southern-football-league.co.uk/match/6a5dfaf378ef96268d68aee9","https://www.footballgroundmap.com/ground/hertingfordbury-park/hertford-town"]
  },
  13:{
    "status":"CONFIRMED","host":"Tooting & Mitcham United FC","tenant":"Balham FC","ground":"Imperial Fields",
    "evidence_note":"Balham's own club information states that it groundshares at Imperial Fields with Tooting & Mitcham United, and current August 2026 FA Cup opposition reporting independently confirms Balham's home groundshare there. This supports Tooting & Mitcham United as host and Balham as tenant.",
    "sources":["https://www.balhamfc.com/teams/mens-first-team","https://www.pitchero.com/clubs/metropolitanpolicefc/news/fa-cup-preview--balham-2991272.html"]
  },
  14:{
    "status":"NOT_CURRENT","host":None,"tenant":None,"ground":"Honeycroft, Uxbridge",
    "evidence_note":"The queued Hayes & Yeading United relationship is no longer current. Southall announced in March 2026 that its SkyEx groundshare had ended and that it would groundshare at Uxbridge FC's Honeycroft for 2026/27. Uxbridge independently announced Southall as its groundshare tenant. Hayes & Yeading United ↔ Southall must therefore not be approved from the stale UB4 0SL candidate.",
    "sources":["https://www.southallfc.com/news/club-statement-new-groundshare-agreement-20262027-2971024.html","https://www.uxbridgefc.com/post/groundshare-agreement-26-27-season"]
  },
  15:{
    "status":"CONFIRMED","host":"Sporting Khalsa FC","tenant":"Dudley Town FC","ground":"Guardian Warehousing Arena",
    "evidence_note":"Dudley Town's current 2026/27 ticketing information identifies the Guardian Warehousing Arena as its home venue, while Dudley's own historical club statement explicitly describes its groundshare facilities at Sporting Khalsa. Current 2026 fixture evidence continues to place both clubs at the same Willenhall venue. This supports Sporting Khalsa as host and Dudley Town as tenant.",
    "sources":["https://dudleytownfootballclub.co.uk/news/ticketing-details-ahead-of-the-202627-season","https://www.dudleytownfootballclub.co.uk/news/chairman-chats"]
  },
}

pairs_by_id={p.get("pair_id"):p for p in q["pairs"]}
rows=[]
for pid in range(11,16):
    p=pairs_by_id.get(pid)
    if not p: raise SystemExit(f"Safety stop: missing expected pair #{pid}.")
    exp=expected[pid]
    if p.get("clubs")!=exp["clubs"] or p.get("postcode")!=exp["postcode"]:
        raise SystemExit(f"Safety stop: v7.8.1 pair #{pid} no longer matches reviewed Batch 3 scope.")
    rows.append({"pair_id":pid,"clubs":p["clubs"],"postcode":p["postcode"],"queue_records":p.get("club_records",[]),**research[pid]})

counts={s:sum(1 for r in rows if r["status"]==s) for s in ("CONFIRMED","AMBIGUOUS","NOT_CURRENT")}
now=datetime.now(timezone.utc)
payload={"checked_at":now.isoformat(),"version":"7.8.8","mode":"PROPOSAL ONLY / RESEARCH","source":"updater/groundshare-evidence-queue.json","batch":3,"pairs_researched":5,"confirmed":counts["CONFIRMED"],"ambiguous":counts["AMBIGUOUS"],"not_current":counts["NOT_CURRENT"],"records":rows}
OUT.write_text(json.dumps(payload,indent=2,ensure_ascii=False)+"\n",encoding="utf8")

L=["# Tin Foil FA Cup — Groundshare Evidence Research — Batch 3","",f"Last checked: **{now.strftime('%d/%m/%Y, %H:%M:%S UTC')}**","","**PROPOSAL ONLY / RESEARCH. No approval ledger or canonical ground record is changed.**","",f"- 🏟️ Relationships researched: **5**",f"- 🟢 Confirmed from explicit current/public evidence: **{counts['CONFIRMED']}**",f"- 🟡 Ambiguous / more explicit evidence required: **{counts['AMBIGUOUS']}**",f"- 🔴 Not current / rejected: **{counts['NOT_CURRENT']}**","","## Results",""]
for r in rows:
    icon={"CONFIRMED":"🟢","AMBIGUOUS":"🟡","NOT_CURRENT":"🔴"}[r["status"]]
    L += [f"### {icon} #{r['pair_id']} — {r['clubs'][0]} ↔ {r['clubs'][1]}","",f"- Classification: **{r['status']}**",f"- Queue postcode: **{r['postcode']}**",f"- Ground/current venue: **{r['ground']}**"]
    if r["host"] and r["tenant"]: L.append(f"- Evidence-supported direction: **{r['tenant']} → {r['host']}**")
    else: L.append("- Evidence-supported direction: **UNRESOLVED / not inferred**")
    L.append(f"- Evidence: {r['evidence_note']}")
    for i,u in enumerate(r["sources"],1): L.append(f"- Source {i}: {u}")
    L.append("")
L += ["## Safety","","- Only v7.8.1 pairs #11–#15 are in scope; changed club/postcode identities stop the run.","- CONFIRMED means evidence research supports the relationship; it is **not** an approval and does not publish anything.","- NOT_CURRENT records are explicitly rejected from any later groundshare approval/promotion stage.","- Host/tenant direction is recorded only where explicit/current evidence supports it.","- Ground-name sponsorship/current-venue changes are preserved rather than silently normalised.","- `clubfinder.html`, canonical `GROUNDS`, approval ledgers, and `competition.json` are untouched."]
REPORT.write_text("\n".join(L)+"\n",encoding="utf8")

print("GROUNDSHARE EVIDENCE RESEARCH v7.8.8 — BATCH 3")
print("Relationships researched: 5")
print("Confirmed:",counts["CONFIRMED"])
print("Ambiguous:",counts["AMBIGUOUS"])
print("Not current/rejected:",counts["NOT_CURRENT"])
print("PROPOSAL ONLY / RESEARCH.")
