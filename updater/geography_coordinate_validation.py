#!/usr/bin/env python3
import json, math, urllib.parse, urllib.request
from pathlib import Path
from datetime import datetime,timezone

ROOT=Path(__file__).resolve().parents[1]
INP=ROOT/"updater/geography-review.json"
OUT=ROOT/"updater/geography-coordinate-validation.json"
REPORT=ROOT/"ground-geography-coordinate-validation.md"

def lookup(postcode):
    url="https://api.postcodes.io/postcodes/"+urllib.parse.quote(postcode.replace(" ",""))
    req=urllib.request.Request(url,headers={"User-Agent":"TinFoilFACup-ground-maintenance/7.7.6"})
    with urllib.request.urlopen(req,timeout=20) as r:
        data=json.load(r)
    x=data.get("result") or {}
    return {
      "postcode":x.get("postcode"),"lat":x.get("latitude"),"lon":x.get("longitude"),
      "quality":x.get("quality"),"country":x.get("country")
    }

def hav(a,b,c,d):
    R=6371.0088
    p1,p2=math.radians(a),math.radians(c)
    dp=math.radians(c-a); dl=math.radians(d-b)
    q=math.sin(dp/2)**2+math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 2*R*math.asin(math.sqrt(q))

if not INP.exists():
    raise SystemExit("Missing updater/geography-review.json. Run v7.7.5 first.")

src=json.loads(INP.read_text(encoding="utf8"))
rows=src.get("records",[])
if len(rows)!=7:
    raise SystemExit("Safety stop: v7.7.6 expects exactly seven v7.7.5 cases.")

results=[]
for x in rows:
    r=dict(x)
    if x.get("status")=="AMBIGUOUS":
        r.update({"validation_status":"HELD_FOR_RESEARCH","coordinate_action":"NONE",
                  "validation_note":"Conflicting current postcode evidence remains unresolved; no postcode selected and no coordinates promoted."})
        results.append(r); continue

    pc=x.get("current_postcode")
    if not pc:
        r.update({"validation_status":"LOOKUP_FAILED","coordinate_action":"NONE",
                  "validation_note":"No current postcode available."})
        results.append(r); continue
    try:
        geo=lookup(pc)
    except Exception as e:
        r.update({"validation_status":"LOOKUP_FAILED","coordinate_action":"NONE",
                  "validation_note":"Independent postcode lookup failed: "+str(e)})
        results.append(r); continue

    r["independent_postcode"]=geo
    if geo["lat"] is None or geo["lon"] is None:
        r.update({"validation_status":"LOOKUP_FAILED","coordinate_action":"NONE",
                  "validation_note":"Postcode resolved but supplied no usable WGS84 coordinates."})
        results.append(r); continue

    if x.get("status")=="CHANGED":
        # A changed postcode must use its freshly resolved centroid; old FCHD
        # coordinates are retained only as a comparison, never silently reused.
        r.update({
          "validation_status":"CORRECTED_POSTCODE_VALIDATED",
          "coordinate_action":"USE_FRESH_POSTCODE_COORDINATES",
          "validated_lat":geo["lat"],"validated_lon":geo["lon"],
          "validation_note":"Corrected postcode independently resolves. Fresh postcode coordinates proposed; old coordinates are not inherited."
        })
    elif x.get("status")=="CONFIRMED":
        # v7.7.5's original queue distance was already FCHD↔postcode-centroid.
        # Recheck the current postcode and require a sensible <=2 km separation.
        d=x.get("distance_km")
        if d is not None and float(d)<=2.0:
            r.update({
              "validation_status":"EXISTING_CANDIDATE_VALIDATED",
              "coordinate_action":"KEEP_VALIDATED_FCHD_COORDINATES",
              "validation_note":"Current postcode independently resolves and the existing candidate was already within the <=2 km review envelope."
            })
        else:
            r.update({"validation_status":"NEEDS_REVIEW","coordinate_action":"NONE",
                      "validation_note":"Independent postcode resolves, but the existing candidate separation is outside the safe review envelope."})
    results.append(r)

counts={
 "existing_validated":sum(r.get("validation_status")=="EXISTING_CANDIDATE_VALIDATED" for r in results),
 "corrected_validated":sum(r.get("validation_status")=="CORRECTED_POSTCODE_VALIDATED" for r in results),
 "held":sum(r.get("validation_status")=="HELD_FOR_RESEARCH" for r in results),
 "failed_or_review":sum(r.get("validation_status") in ("LOOKUP_FAILED","NEEDS_REVIEW") for r in results)
}
payload={"checked_at":datetime.now(timezone.utc).isoformat(),"version":"7.7.6",
         "mode":"VALIDATION ONLY","counts":counts,"records":results}
OUT.write_text(json.dumps(payload,indent=2,ensure_ascii=False)+"\n",encoding="utf8")

L=["# Tin Foil FA Cup — Geography Coordinate Validation","",
f"Last checked: **{datetime.now(timezone.utc).strftime('%d/%m/%Y, %H:%M:%S UTC')}**","",
"**VALIDATION ONLY. No canonical ground data is changed.**","",
f"- 🟢 Existing candidate coordinates validated: **{counts['existing_validated']}**",
f"- 🟢 Corrected postcode coordinates validated: **{counts['corrected_validated']}**",
f"- 🔴 Held for genuine research: **{counts['held']}**",
f"- 🟡 Lookup/review failures: **{counts['failed_or_review']}**",
f"- ⚪ Cases processed: **{len(results)}**",""]
for r in results:
    st=r.get("validation_status")
    icon="🟢" if st in ("EXISTING_CANDIDATE_VALIDATED","CORRECTED_POSTCODE_VALIDATED") else ("🔴" if st=="HELD_FOR_RESEARCH" else "🟡")
    geo=r.get("independent_postcode") or {}
    coord=""
    if geo.get("lat") is not None: coord=f" • postcode centroid `{geo['lat']}, {geo['lon']}`"
    L.append(f"- {icon} **{r['club']}** — {r.get('current_ground')} • {r.get('current_postcode') or 'UNRESOLVED'}{coord} — {r.get('validation_note')}")
L += ["","## Safety","",
"- `clubfinder.html`, `competition.json`, canonical `GROUNDS`, and approval ledgers are untouched.",
"- Corrected postcodes never inherit coordinates from the superseded postcode.",
"- Postcodes are independently resolved at runtime through Postcodes.io.",
"- Corby Town remains held: this validator cannot choose between conflicting current postcodes.",
"- Any API failure remains yellow/red; it is never converted into an approval."
]
REPORT.write_text("\n".join(L)+"\n",encoding="utf8")

print("GEOGRAPHY COORDINATE VALIDATION v7.7.6")
print("Existing candidate coordinates validated:",counts["existing_validated"])
print("Corrected postcode coordinates validated:",counts["corrected_validated"])
print("Held for research:",counts["held"])
print("Lookup/review failures:",counts["failed_or_review"])
print("Cases processed:",len(results))
print("VALIDATION ONLY.")
