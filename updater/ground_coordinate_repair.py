#!/usr/bin/env python3
import json,re,urllib.request,urllib.parse
from datetime import datetime,timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
HTML=ROOT/"clubfinder.html"
REPORT=ROOT/"ground-coordinate-repair.md"
JSON_REPORT=ROOT/"updater/ground-coordinate-repair.json"
APPLY=ROOT/"updater/ground-coordinate-repair.json"

def fetch(pc):
    u="https://api.postcodes.io/postcodes/"+urllib.parse.quote(pc.replace(" ",""))
    req=urllib.request.Request(u,headers={"User-Agent":"TinFoilFACup/7.6.3"})
    with urllib.request.urlopen(req,timeout=20) as r:
        x=json.load(r)
    y=x.get("result") or {}
    return {"postcode":y.get("postcode"),"lat":y.get("latitude"),"lon":y.get("longitude"),"quality":y.get("quality")}

def parse_ground_records(t):
    m=re.search(r"\b(?:const|let|var)\s+GROUNDS\s*=\s*\[",t)
    if not m: raise SystemExit("Could not find GROUNDS array")
    st=t.find("[",m.start()); d=0; ins=False; esc=False; q=""
    for i in range(st,len(t)):
        c=t[i]
        if ins:
            if esc:esc=False
            elif c=="\\":esc=True
            elif c==q:ins=False
        else:
            if c in ("'",'"'):ins=True;q=c
            elif c=="[":d+=1
            elif c=="]":
                d-=1
                if d==0:return json.loads(t[st:i+1])
    raise SystemExit("Unbalanced GROUNDS array")

t=HTML.read_text(encoding="utf8")
grounds=parse_ground_records(t)
targets=[]
for g in grounds:
    if g.get("postcode") and (g.get("lat") is None or g.get("lon") is None):
        targets.append(g)

rows=[]
for g in targets:
    row={"club":g.get("name") or g.get("club"),"ground":g.get("ground"),"postcode":g.get("postcode")}
    try:
        geo=fetch(g["postcode"])
        row.update(geo)
        row["status"]="READY" if geo["lat"] is not None and geo["lon"] is not None else "NO-COORDINATES"
    except Exception as e:
        row["status"]="LOOKUP-FAILED";row["error"]=str(e)
    rows.append(row)

payload={"checked_at":datetime.now(timezone.utc).isoformat(),"source":"postcodes.io","mode":"proposal-only","count":len(rows),"records":rows}
JSON_REPORT.write_text(json.dumps(payload,indent=2)+"\n")
L=["# Tin Foil FA Cup — Ground Coordinate Repair","",
   f"Last checked: **{datetime.now(timezone.utc).strftime('%d/%m/%Y, %H:%M:%S UTC')}**","",
   "This is a **proposal-only** report. No Clubfinder data has been changed.","",
   f"- Missing-coordinate records checked: **{len(rows)}**",
   f"- 🟢 Ready to repair: **{sum(r['status']=='READY' for r in rows)}**",
   f"- 🔴 Lookup failures: **{sum(r['status']!='READY' for r in rows)}**","",
   "## Proposed repairs",""]
for r in rows:
    if r["status"]=="READY":
        L.append(f"- **{r['club']}** — {r['ground']} • {r['postcode']} → `{r['lat']}, {r['lon']}`")
    else:L.append(f"- **{r['club']}** — {r['ground']} • {r['postcode']} → **{r['status']}**")
L+=["","Postcodes.io coordinates are postcode centroids, not guaranteed stadium entrance/rooftop coordinates."]
REPORT.write_text("\n".join(L)+"\n")
print("GROUND COORDINATE REPAIR v7.6.3 — PROPOSAL ONLY")
print("Targets:",len(rows))
print("Ready:",sum(r["status"]=="READY" for r in rows))
for r in rows:print(r["status"],r["club"],r["postcode"],r.get("lat"),r.get("lon"))
print("NO DATA CHANGED.")
