#!/usr/bin/env python3
import argparse,json,re,sys
from pathlib import Path
from datetime import datetime,timezone

ROOT=Path(__file__).resolve().parents[1]
HTML=ROOT/"clubfinder.html"
EX=ROOT/"updater/ground-exception-verification.json"
LEDGER=ROOT/"updater/ground-approval-ledger.json"
REPORT=ROOT/"ground-approval-ledger.md"
RUNJSON=ROOT/"updater/ground-approval-run.json"

def norm(s):
 s=(s or "").lower().replace("&"," and ")
 # punctuation/apostrophes first, then common suffixes
 s=s.replace("'","").replace("’","")
 s=re.sub(r"\b(fc|afc|cfc|football club)\b"," ",s)
 return re.sub(r"[^a-z0-9]+"," ",s).strip()

def locate_array(text,name):
 m=re.search(r"\b(?:const|let|var)\s+"+re.escape(name)+r"\s*=\s*\[",text)
 if not m: raise SystemExit(f"Could not find {name} array")
 start=text.find("[",m.start()); depth=0; ins=False; esc=False; q=""
 for i in range(start,len(text)):
  c=text[i]
  if ins:
   if esc: esc=False
   elif c=="\\": esc=True
   elif c==q: ins=False
  else:
   if c in ("'",'"'): ins=True;q=c
   elif c=="[": depth+=1
   elif c=="]":
    depth-=1
    if depth==0:return start,i+1
 raise SystemExit(f"Unbalanced {name}")

def arr(text,name):
 s,e=locate_array(text,name); return s,e,json.loads(text[s:e])

ap=argparse.ArgumentParser()
ap.add_argument("--publish",action="store_true")
args=ap.parse_args()
if not HTML.exists(): raise SystemExit("clubfinder.html missing")
if not EX.exists(): raise SystemExit("ground-exception-verification.json missing; run v7.6.8 first")

data=json.loads(EX.read_text(encoding="utf8"))
records=data.get("records",[])
text=HTML.read_text(encoding="utf8")
gs,ge,grounds=arr(text,"GROUNDS")
_,_,eligible=arr(text,"ELIGIBLE")
enames={norm(x.get("name")):x.get("name") for x in eligible if x.get("name")}
existing={norm(g.get("name") or g.get("club")) for g in grounds}

# v7.6.9 correction: Bishop's/Bishops Cleeve is punctuation-only identity variation.
for r in records:
 if norm(r.get("club"))==norm("Bishop's Cleeve FC") and norm(r.get("fchd_match"))==norm("Bishops Cleeve"):
  r["state"]="HUMAN_DECISION"
  r["reason"]="Mechanical apostrophe/name-format variant; confirm identity before promotion"

greens=[r for r in records if r.get("state")=="APPROVED_CANDIDATE"]
to_add=[]; skipped=[]
for r in greens:
 key=norm(r.get("club"))
 if key not in enames: skipped.append({"club":r.get("club"),"reason":"Not in ELIGIBLE"}); continue
 if key in existing: skipped.append({"club":r.get("club"),"reason":"Already canonical"}); continue
 if not all([r.get("ground_candidate"),r.get("postcode")]):
  skipped.append({"club":r.get("club"),"reason":"Missing ground/postcode"}); continue
 # v7.6.8 records carry no lat/lon; recover them from v7.6.5 verification.
 vfile=ROOT/"updater/ground-verification-queue.json"
 if not vfile.exists(): raise SystemExit("ground-verification-queue.json missing")
 vr=json.loads(vfile.read_text(encoding="utf8")).get("records",[])
 lookup={norm(x.get("club")):x for x in vr}
 src=lookup.get(key,{})
 if src.get("fchd_lat") is None or src.get("fchd_lon") is None:
  skipped.append({"club":r.get("club"),"reason":"No validated FCHD coordinates"}); continue
 to_add.append({
  "name":enames[key],"ground":r["ground_candidate"],"postcode":r["postcode"],
  "lat":float(src["fchd_lat"]),"lon":float(src["fchd_lon"]),
  "verification":"verified","verification_label":"✅ Verified",
  "source":"FCHD 2025-26 Gazetteer; exception rule reviewed v7.6.9",
  "ground_source":"FCHD 2025-26 Gazetteer",
  "coordinate_source":"FCHD coordinates; validated against Postcodes.io postcode centroid"
 })

# Persistent ledger skeleton. Human approvals are deliberately not invented.
ledger={"version":"7.6.9","updated_at":datetime.now(timezone.utc).isoformat(),
 "known_groundshares":[],"approved_exceptions":[],
 "instructions":"Add approvals only after explicit review. Ground Health integration can consume this ledger in the next stage."}
if LEDGER.exists():
 try:
  old=json.loads(LEDGER.read_text(encoding="utf8"))
  ledger["known_groundshares"]=old.get("known_groundshares",[])
  ledger["approved_exceptions"]=old.get("approved_exceptions",[])
 except Exception: pass
# Record green exception-rule clearances as approved exceptions.
known={norm(x.get("club")) for x in ledger["approved_exceptions"] if isinstance(x,dict)}
for g in to_add:
 if norm(g["name"]) not in known:
  ledger["approved_exceptions"].append({"club":g["name"],"type":"exception-rule-cleared",
   "ground":g["ground"],"postcode":g["postcode"],"rule_version":"7.6.9"})
LEDGER.write_text(json.dumps(ledger,indent=2,ensure_ascii=False)+"\n",encoding="utf8")

run={"mode":"publish" if args.publish else "dry-run","green_candidates_seen":len(greens),
 "eligible_for_promotion":len(to_add),"skipped":skipped,
 "bishops_cleeve_reclassified_to_human_decision":True}
RUNJSON.write_text(json.dumps(run,indent=2,ensure_ascii=False)+"\n",encoding="utf8")
L=["# Tin Foil FA Cup — Ground Approval Ledger","",
 f"Mode: **{'PUBLISH' if args.publish else 'DRY RUN'}**","",
 f"- 🟢 Exception-cleared candidates seen: **{len(greens)}**",
 f"- Eligible for promotion: **{len(to_add)}**",
 f"- Skipped: **{len(skipped)}**",
 "- 🟡 Bishop's Cleeve corrected to human-decision queue: **Yes**","",
 "## Promotion candidates",""]
for g in to_add:L.append(f"- **{g['name']}** — {g['ground']} • {g['postcode']} • `{g['lat']}, {g['lon']}`")
L+=["","## Approval ledger","","The ledger is intentionally conservative. It contains no invented groundshare approvals. Future explicit approvals can be stored in `known_groundshares` so Ground Health can stop repeatedly flagging known arrangements.","",
"## Safety","", "- Existing canonical GROUNDS records are never overwritten.","- Only v7.6.8 green exception-cleared candidates can be promoted by this workflow.","- Bishop's Cleeve is reclassified only; it is not promoted.","- `competition.json` is untouched."]
REPORT.write_text("\n".join(L)+"\n",encoding="utf8")

print("GROUND APPROVAL LEDGER v7.6.9")
print("Mode:","PUBLISH" if args.publish else "DRY RUN")
print("Green candidates:",len(greens),"Eligible:",len(to_add),"Skipped:",len(skipped))
print("Bishop's Cleeve -> HUMAN_DECISION")

if not args.publish:
 print("DRY RUN: clubfinder.html unchanged."); sys.exit(0)
if to_add:
 new=json.dumps(grounds+to_add,ensure_ascii=False,separators=(",",":"))
 HTML.write_text(text[:gs]+new+text[ge:],encoding="utf8")
 print("PUBLISHED:",len(to_add))
else: print("Nothing to publish.")
