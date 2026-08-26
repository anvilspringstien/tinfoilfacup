#!/usr/bin/env python3
import json,re
from pathlib import Path
from datetime import datetime,timezone
R=Path(__file__).resolve().parents[1]; E=R/"updater/ground-exceptions.json"
if not E.exists(): raise SystemExit("Missing updater/ground-exceptions.json; run v7.6.7 first.")
x=json.loads(E.read_text(encoding="utf8")); cats=x.get("categories",{}); rows=[]
def n(s):
 s=(s or "").lower().replace("&"," and "); s=re.sub(r"\b(fc|afc|cfc|football club)\b"," ",s)
 return re.sub(r"[^a-z0-9]+"," ",s).strip()
def add(a,state,reason):
 for z in cats.get(a,[]): rows.append({**z,"state":state,"reason":reason})
# Groundshare bucket: shared postcode remains human; old host-name-only flag is cleared.
for z in cats.get("GROUNDSHARE / HOST-GROUND REVIEW",[]):
 shared="SHARED_POSTCODE" in z.get("flags",[])
 rows.append({**z,"state":"HUMAN_DECISION" if shared else "APPROVED_CANDIDATE",
 "reason":"Approve shared-ground relationship" if shared else "Old generic host-ground heuristic cleared"})
add("GEOGRAPHY / POSTCODE REVIEW","HUMAN_DECISION","Verify current ground/postcode once (750m–2km centroid difference)")
add("GEOGRAPHY / POSTCODE INVESTIGATION","GROUND_RESEARCH","Postcode failure or >2km disagreement")
for z in cats.get("FUZZY CLUB-NAME MATCH",[]):
 a,b=n(z.get("club")),n(z.get("fchd_match"))
 plausible=(a==b or ("horsham ymca" in a and "horsham ym" in b) or ("pershore town 88" in a and "pershore town" in b))
 rows.append({**z,"state":"HUMAN_DECISION" if plausible else "GROUND_RESEARCH",
 "reason":"Plausible name variant; confirm identity" if plausible else "Unsafe fuzzy match; independent identity research required"})
add("NO FCHD MATCH","GROUND_RESEARCH","No FCHD candidate; another free/public source required")
add("OTHER EXCEPTION","GROUND_RESEARCH","Unclassified exception")
states=["APPROVED_CANDIDATE","HUMAN_DECISION","GROUND_RESEARCH"]
counts={s:sum(z["state"]==s for z in rows) for s in states}
(R/"updater/ground-exception-verification.json").write_text(json.dumps({"checked_at":datetime.now(timezone.utc).isoformat(),"mode":"triage-only","counts":counts,"records":rows},indent=2,ensure_ascii=False)+"\n",encoding="utf8")
L=["# Tin Foil FA Cup — Ground Exception Verification","",f"Last checked: **{datetime.now(timezone.utc).strftime('%d/%m/%Y, %H:%M:%S UTC')}**","","**Verification/triage only. Nothing is published automatically.**","",f"- 🟢 Approved candidates: **{counts['APPROVED_CANDIDATE']}**",f"- 🟡 One human decision required: **{counts['HUMAN_DECISION']}**",f"- 🔴 Genuine ground research required: **{counts['GROUND_RESEARCH']}**","","Generic words such as `Town` or `United` in a ground name are no longer treated as host-club evidence."]
titles={"APPROVED_CANDIDATE":"🟢 Approved candidates","HUMAN_DECISION":"🟡 One human decision required","GROUND_RESEARCH":"🔴 Genuine ground research required"}
for s in states:
 L+=["",f"## {titles[s]}",""]
 for z in sorted((q for q in rows if q["state"]==s),key=lambda q:q.get("club","")):
  bits=[v for v in [z.get("ground_candidate"),z.get("postcode")] if v]
  if z.get("distance_km") is not None: bits.append(f"separation `{z['distance_km']} km`")
  bits.append(z["reason"]); L.append(f"- **{z.get('club')}** — "+" • ".join(bits))
L+=["","## Rules","","- 🟢 clears the exception rule only; it is not auto-published.","- 🟡 requires one explicit human approval/current-ground check.","- 🔴 requires another free/public source.","- Known groundshares should eventually be stored explicitly.","- `clubfinder.html` and `competition.json` are untouched."]
(R/"ground-exception-verification.md").write_text("\n".join(L)+"\n",encoding="utf8")
print("GROUND EXCEPTION VERIFICATION v7.6.8"); print(counts); print("TRIAGE ONLY.")
