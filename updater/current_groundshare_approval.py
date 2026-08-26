#!/usr/bin/env python3
import argparse,json,re,sys
from pathlib import Path
from datetime import datetime,timezone
from urllib.parse import urlsplit,urlunsplit,parse_qsl,urlencode
ROOT=Path(__file__).resolve().parents[1]
HTML=ROOT/"clubfinder.html"; LEDGER=ROOT/"updater/ground-approval-ledger.json"
REPORT=ROOT/"groundshare-approval.md"; RUN=ROOT/"updater/groundshare-approval-run.json"
def norm(s):
 s=(s or "").lower().replace("&"," and ").replace("’","'"); s=re.sub(r"\b(fc|afc|cfc|football club)\b"," ",s); return re.sub(r"[^a-z0-9]+"," ",s).strip()
def clean_url(u):
 p=urlsplit(u.strip()); q=[(k,v) for k,v in parse_qsl(p.query,keep_blank_values=True) if not k.lower().startswith("utm_")]; return urlunsplit((p.scheme,p.netloc,p.path,urlencode(q),p.fragment))
def locate(text,name):
 m=re.search(r"\b(?:const|let|var)\s+"+re.escape(name)+r"\s*=\s*\[",text)
 if not m: raise SystemExit("Could not find "+name)
 s=text.find("[",m.start()); d=0; ins=False; esc=False; q=""
 for i in range(s,len(text)):
  c=text[i]
  if ins:
   if esc: esc=False
   elif c=="\\": esc=True
   elif c==q: ins=False
  else:
   if c in ("'",'"'): ins=True;q=c
   elif c=="[": d+=1
   elif c=="]":
    d-=1
    if d==0:return s,i+1
 raise SystemExit("Unbalanced "+name)
ap=argparse.ArgumentParser()
ap.add_argument("--mode",choices=["approve","correct"],required=True); ap.add_argument("--tenant",required=True); ap.add_argument("--host",default="")
ap.add_argument("--ground",required=True); ap.add_argument("--postcode",required=True); ap.add_argument("--season",default="2026-27")
ap.add_argument("--evidence",required=True); ap.add_argument("--source-url",required=True); ap.add_argument("--lat",type=float); ap.add_argument("--lon",type=float); ap.add_argument("--publish-correction",action="store_true")
a=ap.parse_args()
if not re.match(r"^[A-Z]{1,2}\d[A-Z\d]?\s*\d[A-Z]{2}$",a.postcode.upper().strip()): raise SystemExit("Bad UK postcode")
src=clean_url(a.source_url); now=datetime.now(timezone.utc).isoformat()
ledger={"version":"7.7.2","updated_at":now,"known_groundshares":[],"approved_exceptions":[],"venue_corrections":[]}
if LEDGER.exists():
 old=json.loads(LEDGER.read_text()); 
 for k in ("known_groundshares","approved_exceptions","venue_corrections"): ledger[k]=old.get(k,[])
entry={"tenant":a.tenant.strip(),"host":a.host.strip(),"ground":a.ground.strip(),"postcode":a.postcode.upper().strip(),"season":a.season.strip(),"evidence":a.evidence.strip(),"source_url":src,"approved_at":now,"status":"current"}
ledger["known_groundshares"]=[x for x in ledger["known_groundshares"] if norm(x.get("tenant"))!=norm(a.tenant)] + [entry]
html_changed=False
if a.mode=="correct":
 ledger["venue_corrections"].append({**entry,"type":"changed-groundshare"})
 text=HTML.read_text(); s,e=locate(text,"GROUNDS"); grounds=json.loads(text[s:e]); matches=[g for g in grounds if norm(g.get("name") or g.get("club"))==norm(a.tenant)]
 if len(matches)!=1: raise SystemExit("Expected exactly one canonical ground record")
 g=matches[0]; oldpc=(g.get("postcode") or "").upper(); newpc=a.postcode.upper().strip()
 g["ground"]=a.ground.strip(); g["postcode"]=newpc; g["verification"]="verified"; g["verification_label"]="✅ Verified"; g["source"]="Current groundshare evidence: "+src
 if newpc!=oldpc:
  if a.lat is None or a.lon is None: raise SystemExit("Changed postcode requires latitude and longitude")
  g["lat"]=a.lat; g["lon"]=a.lon
 if a.publish_correction:
  HTML.write_text(text[:s]+json.dumps(grounds,ensure_ascii=False,separators=(",",":"))+text[e:]); html_changed=True
LEDGER.write_text(json.dumps(ledger,indent=2,ensure_ascii=False)+"\n")
RUN.write_text(json.dumps({"mode":a.mode,"relationship_recorded":True,"canonical_correction_published":a.publish_correction,"html_changed":html_changed},indent=2)+"\n")
REPORT.write_text(f"# Tin Foil FA Cup — Current Groundshare Approval\n\n- Mode: **{a.mode.upper()}**\n- Relationship recorded in approval ledger: **YES**\n- Canonical venue correction published: **{'YES' if a.publish_correction else 'NO'}**\n- Tenant: **{a.tenant}**\n- Host: **{a.host or 'Not specified'}**\n- Ground: **{a.ground}**\n- Postcode: **{a.postcode.upper()}**\n- Season/current period: **{a.season}**\n\n## Evidence\n\n{a.evidence}\n\nSource: {src}\n\n`competition.json` is untouched.\n")
print("v7.7.2 approval recorded; canonical correction published:",a.publish_correction)
