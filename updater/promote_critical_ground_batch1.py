#!/usr/bin/env python3
import json,re
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
HTML=ROOT/"clubfinder.html"; HEALTH=ROOT/"updater/ground-health.json"; OUT=ROOT/"updater/critical-ground-batch1.json"; REPORT=ROOT/"critical-ground-batch1.md"
def norm(s):
 s=(s or "").lower().replace("&"," and ").replace("’","'"); s=re.sub(r"\b(fc|afc|cfc|football club)\b"," ",s); return re.sub(r"[^a-z0-9]+"," ",s).strip()
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
   if c in ("'",'\"'): ins=True;q=c
   elif c=="[": d+=1
   elif c=="]":
    d-=1
    if d==0:return s,i+1
 raise SystemExit("Unbalanced "+name)
if not HTML.exists() or not HEALTH.exists(): raise SystemExit("Missing clubfinder.html or Ground Health")
h=json.loads(HEALTH.read_text()); missing={x[0] for x in h.get("missing_or_incomplete",[])}
TARGETS=[
 {"name":"Handsworth FC","ground":"Express Worktops Stadium @ Olivers Mount","postcode":"S9 4PA","lat":53.38468,"lon":-1.39122,"source":"https://www.pitchero.com/clubs/handsworthfc","ground_source":"Current official Handsworth FC site, 2026/27","coordinate_source":"Geograph subject-location geotag for Olivers Mount football ground (10m precision)"},
 {"name":"Loughborough Students FC","ground":"Loughborough University Stadium","postcode":"LE11 3GR","lat":52.756975,"lon":-1.242555,"source":"https://www.lboro.ac.uk/sport/facilities/stadium/","ground_source":"Current Loughborough University stadium page and venue address","coordinate_source":"FCHD mapped Loughborough University Stadium ground coordinate"},
 {"name":"Moulton FC","ground":"Brunting Road","postcode":"NN3 7QF","lat":52.285353,"lon":-0.85807,"source":"https://fulltime.thefa.com/displayTeam.html?id=863869752","ground_source":"Current FA Full-Time 2026/27 home fixtures at Brunting Road; FCHD current ground/postcode","coordinate_source":"FCHD 2025-26 mapped Brunting Road ground coordinate"},
 {"name":"Northampton Sileby Rangers FC","ground":"O'Riordan Bond Stadium, Fernie Fields","postcode":"NN3 6FR","lat":52.275583,"lon":-0.852269,"source":"https://theucl.co.uk/clubs/northampton-sileby-rangers-fc/","ground_source":"Current 2026/27 United Counties League club directory and official club contact","coordinate_source":"FCHD 2025-26 mapped Fernie Fields ground coordinate"},
]
expected={x["name"] for x in TARGETS}
if not expected.issubset(missing): raise SystemExit("Safety stop: one or more batch clubs are no longer critical missing records; rerun research instead of overwriting")
text=HTML.read_text(); s,e=locate(text,"GROUNDS"); grounds=json.loads(text[s:e]); existing={norm(g.get("name") or g.get("club")) for g in grounds}
new=[]
for t in TARGETS:
 if norm(t["name"]) in existing: raise SystemExit("Safety stop: canonical record appeared for "+t["name"])
 new.append({"name":t["name"],"ground":t["ground"],"postcode":t["postcode"],"lat":t["lat"],"lon":t["lon"],"verification":"verified","verification_label":"✅ Verified","source":"Current 2026/27 venue evidence: "+t["source"],"ground_source":t["ground_source"],"coordinate_source":t["coordinate_source"]})
HTML.write_text(text[:s]+json.dumps(grounds+sorted(new,key=lambda x:x["name"].lower()),ensure_ascii=False,separators=(",",":"))+text[e:])
now=datetime.now(timezone.utc).isoformat(); held={"club":"Prestwich Heys AFC","ground":"Adie Moran Park","postcode":"M45 6NT","reason":"Current venue/postcode verified; held until venue-level coordinate is evidenced to the same standard as this publication batch."}
p={"published_at":now,"version":"7.9.6","canonical_records_added":4,"existing_records_overwritten":0,"records":new,"held_from_batch":held,"competition_json_changed":False}
OUT.write_text(json.dumps(p,indent=2,ensure_ascii=False)+"\n")
L=["# Tin Foil FA Cup — Critical Ground Batch 1","",f"Published: **{datetime.now(timezone.utc).strftime('%d/%m/%Y, %H:%M:%S UTC')}**","","**v7.9.6 SAFE PROMOTION — four current venues independently resolved from the critical missing-record queue.**","","- New canonical verified records: **4**","- Existing canonical records overwritten: **0**","- Held for stronger coordinate evidence: **1**","- `competition.json` changed: **NO**","","## Published",""]
for g in new:L.append(f"- **{g['name']}** — {g['ground']} • {g['postcode']} • `{g['lat']}, {g['lon']}`")
L += ["","## Held from this batch","",f"- **{held['club']}** — {held['ground']} • {held['postcode']} — {held['reason']}","","## Safety","","- Every published club had to still appear in Ground Health as a missing canonical record.","- Any canonical record appearing after research causes a safety stop rather than an overwrite.","- Current 2026/27 venue evidence was required; unsafe historic/fuzzy candidates were not reused.","- `competition.json` is untouched."]
REPORT.write_text("\n".join(L)+"\n")
print("CRITICAL GROUND BATCH 1 v7.9.6")
print("Published verified canonical records: 4")
print("Held for stronger coordinate evidence: Prestwich Heys AFC")
print("competition.json: untouched")
