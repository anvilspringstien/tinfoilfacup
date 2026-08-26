#!/usr/bin/env python3
import argparse,json,re,sys
from pathlib import Path
from datetime import datetime,timezone

ROOT=Path(__file__).resolve().parents[1]
HTML=ROOT/"clubfinder.html"
LEDGER=ROOT/"updater/ground-approval-ledger.json"
REPORT=ROOT/"groundshare-approval.md"
RUN=ROOT/"updater/groundshare-approval-run.json"

def norm(s):
 s=(s or "").lower().replace("&"," and ").replace("’","'")
 s=re.sub(r"\b(fc|afc|cfc|football club)\b"," ",s)
 return re.sub(r"[^a-z0-9]+"," ",s).strip()

def locate_array(text,name):
 m=re.search(r"\b(?:const|let|var)\s+"+re.escape(name)+r"\s*=\s*\[",text)
 if not m: raise SystemExit(f"Could not find {name} array in clubfinder.html")
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
 raise SystemExit(f"Unbalanced {name} array")

def parse_arr(text,name):
 s,e=locate_array(text,name); return s,e,json.loads(text[s:e])

ap=argparse.ArgumentParser()
ap.add_argument("--mode",choices=["approve","correct"],required=True)
ap.add_argument("--tenant",required=True)
ap.add_argument("--host",default="")
ap.add_argument("--ground",required=True)
ap.add_argument("--postcode",required=True)
ap.add_argument("--season",default="2026-27")
ap.add_argument("--evidence",required=True)
ap.add_argument("--source-url",required=True)
ap.add_argument("--lat",type=float)
ap.add_argument("--lon",type=float)
ap.add_argument("--publish",action="store_true")
a=ap.parse_args()

if not re.match(r"^[A-Z]{1,2}\d[A-Z\d]?\s*\d[A-Z]{2}$",a.postcode.upper().strip()):
 raise SystemExit("Postcode does not look like a UK postcode.")
if not a.source_url.startswith(("http://","https://")): raise SystemExit("Source URL must be http(s).")
if len(a.evidence.strip())<8: raise SystemExit("Evidence note is too short.")

ledger={"version":"7.7.1","updated_at":None,"known_groundshares":[],"approved_exceptions":[],"venue_corrections":[]}
if LEDGER.exists():
 old=json.loads(LEDGER.read_text(encoding="utf8"))
 for k in ("known_groundshares","approved_exceptions","venue_corrections"): ledger[k]=old.get(k,[])
tenant_key=norm(a.tenant)
now=datetime.now(timezone.utc).isoformat()
entry={"tenant":a.tenant.strip(),"host":a.host.strip(),"ground":a.ground.strip(),
       "postcode":a.postcode.upper().strip(),"season":a.season.strip(),
       "evidence":a.evidence.strip(),"source_url":a.source_url.strip(),
       "approved_at":now,"status":"current"}
if a.lat is not None: entry["lat"]=a.lat
if a.lon is not None: entry["lon"]=a.lon

# Replace previous approval for same tenant rather than accumulate contradictory "current" rows.
ledger["known_groundshares"]=[x for x in ledger["known_groundshares"] if norm(x.get("tenant"))!=tenant_key]
if a.mode=="approve":
 ledger["known_groundshares"].append(entry)
else:
 ledger["venue_corrections"].append({**entry,"type":"changed-groundshare"})
 ledger["known_groundshares"].append(entry)
ledger["updated_at"]=now

html_changed=False
candidate=None
if a.mode=="correct":
 if not HTML.exists(): raise SystemExit("clubfinder.html missing")
 text=HTML.read_text(encoding="utf8")
 gs,ge,grounds=parse_arr(text,"GROUNDS")
 matches=[g for g in grounds if norm(g.get("name") or g.get("club"))==tenant_key]
 if len(matches)!=1: raise SystemExit(f"Expected exactly one canonical GROUNDS record for {a.tenant}; found {len(matches)}.")
 oldg=matches[0]
 candidate=dict(oldg)
 candidate["ground"]=a.ground.strip(); candidate["postcode"]=a.postcode.upper().strip()
 candidate["verification"]="verified"; candidate["verification_label"]="✅ Verified"
 candidate["source"]=f"Current groundshare evidence ({a.season}): {a.source_url.strip()}"
 candidate["ground_source"]=a.source_url.strip()
 # Coordinates are mandatory for a changed venue unless postcode is unchanged.
 if candidate.get("postcode") != oldg.get("postcode"):
  if a.lat is None or a.lon is None:
   raise SystemExit("Changed postcode requires --lat and --lon. Refusing to reuse stale coordinates.")
  candidate["lat"]=a.lat; candidate["lon"]=a.lon
 if a.publish:
  grounds=[candidate if g is oldg else g for g in grounds]
  HTML.write_text(text[:gs]+json.dumps(grounds,ensure_ascii=False,separators=(",",":"))+text[ge:],encoding="utf8")
  html_changed=True

LEDGER.write_text(json.dumps(ledger,indent=2,ensure_ascii=False)+"\n",encoding="utf8")
run={"mode":a.mode,"publish":a.publish,"tenant":a.tenant,"host":a.host,"ground":a.ground,
     "postcode":a.postcode.upper(),"season":a.season,"html_changed":html_changed,
     "correction_candidate":candidate}
RUN.write_text(json.dumps(run,indent=2,ensure_ascii=False)+"\n",encoding="utf8")
L=["# Tin Foil FA Cup — Current Groundshare Approval","",
 f"Last run: **{datetime.now(timezone.utc).strftime('%d/%m/%Y, %H:%M:%S UTC')}**","",
 f"- Mode: **{a.mode.upper()}**",f"- Publish: **{'YES' if a.publish else 'NO / DRY RUN'}**",
 f"- Tenant: **{a.tenant}**",f"- Host: **{a.host or 'Not specified'}**",
 f"- Ground: **{a.ground}**",f"- Postcode: **{a.postcode.upper()}**",
 f"- Season/current period: **{a.season}**","",
 "## Evidence","",a.evidence.strip(),"",f"Source: {a.source_url.strip()}","",
 "## Safety","",
 "- An approval is never inferred from a shared postcode.",
 "- Every ledger entry requires an evidence note and source URL.",
 "- A changed postcode cannot reuse old coordinates; new latitude/longitude are required.",
 "- Existing canonical venue data is changed only in CORRECT mode with Publish enabled.",
 "- `competition.json` is untouched."]
REPORT.write_text("\n".join(L)+"\n",encoding="utf8")
print("CURRENT GROUNDSHARE APPROVAL v7.7.1")
print("Mode:",a.mode.upper(),"Publish:",a.publish)
print(a.tenant,"->",a.host or "(host unspecified)","@",a.ground,a.postcode.upper())
print("clubfinder.html changed:",html_changed)
