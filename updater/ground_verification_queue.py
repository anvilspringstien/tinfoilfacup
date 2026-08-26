#!/usr/bin/env python3
import json,math,re,urllib.parse,urllib.request
from datetime import datetime,timezone
from pathlib import Path
from collections import defaultdict

ROOT=Path(__file__).resolve().parents[1]
QUEUE=ROOT/"updater/ground-discovery-queue.json"
REPORT=ROOT/"ground-verification-queue.md"
JSON_REPORT=ROOT/"updater/ground-verification-queue.json"

def fetch_postcode(pc):
    url="https://api.postcodes.io/postcodes/"+urllib.parse.quote((pc or "").replace(" ",""))
    req=urllib.request.Request(url,headers={"User-Agent":"TinFoilFACupGroundVerification/7.6.5"})
    try:
        with urllib.request.urlopen(req,timeout=20) as r:
            x=json.load(r)
        y=x.get("result") or {}
        return {"valid":bool(y),"postcode":y.get("postcode"),
                "lat":y.get("latitude"),"lon":y.get("longitude"),
                "quality":y.get("quality")}
    except Exception as e:
        return {"valid":False,"error":str(e)}

def hav(lat1,lon1,lat2,lon2):
    R=6371.0088
    p1,p2=math.radians(lat1),math.radians(lat2)
    dp=math.radians(lat2-lat1);dl=math.radians(lon2-lon1)
    a=math.sin(dp/2)**2+math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return R*2*math.atan2(math.sqrt(a),math.sqrt(1-a))

if not QUEUE.exists():
    raise SystemExit("ground-discovery-queue.json missing. Run v7.6.4 first.")
q=json.loads(QUEUE.read_text(encoding="utf8"))
items=[x for x in q.get("queue",[]) if x.get("confidence")=="HIGH"]
if not items: raise SystemExit("No HIGH candidates found.")

# One postcode lookup can validate multiple groundshare candidates.
pcs=sorted({(x.get("postcode") or "").strip().upper() for x in items if x.get("postcode")})
lookups={pc:fetch_postcode(pc) for pc in pcs}
pc_clubs=defaultdict(list)
for x in items:
    if x.get("postcode"):pc_clubs[x["postcode"].strip().upper()].append(x["eligible_club"])

rows=[]
for x in items:
    pc=(x.get("postcode") or "").strip().upper()
    p=lookups.get(pc,{"valid":False,"error":"No postcode"})
    f_lat=x.get("lat");f_lon=x.get("lon")
    dist=None
    if p.get("valid") and None not in (p.get("lat"),p.get("lon"),f_lat,f_lon):
        dist=hav(float(f_lat),float(f_lon),float(p["lat"]),float(p["lon"]))

    flags=[]
    if not p.get("valid"): flags.append("POSTCODE_LOOKUP_FAILED")
    if f_lat is None or f_lon is None: flags.append("FCHD_COORDINATES_MISSING")
    if len(pc_clubs.get(pc,[]))>1: flags.append("SHARED_POSTCODE")
    # Postcode centroid can differ from a pitch location, so use generous review bands.
    if dist is not None and dist>2.0: flags.append("LOCATION_DISAGREEMENT_GT_2KM")
    elif dist is not None and dist>0.75: flags.append("LOCATION_DIFFERENCE_GT_750M")

    # Ground-name heuristics: these don't reject; they just force human review.
    ground=x.get("ground_candidate") or ""
    if re.search(r"\b(FC|AFC|CFC|United|Town|City|Rovers|Athletic)\b",ground,re.I):
        flags.append("GROUND_NAME_MAY_BE_HOST_CLUB")

    if not p.get("valid") or "FCHD_COORDINATES_MISSING" in flags or "LOCATION_DISAGREEMENT_GT_2KM" in flags:
        status="INVESTIGATE"
    elif flags:
        status="REVIEW"
    else:
        status="VALIDATED_CANDIDATE"

    rows.append({
        "queue_id":x.get("queue_id"),"club":x.get("eligible_club"),
        "ground_candidate":ground,"postcode":pc,
        "fchd_lat":f_lat,"fchd_lon":f_lon,
        "postcode_lat":p.get("lat"),"postcode_lon":p.get("lon"),
        "distance_km":round(dist,3) if dist is not None else None,
        "postcode_quality":p.get("quality"),
        "shared_with":[c for c in pc_clubs.get(pc,[]) if c!=x.get("eligible_club")],
        "flags":flags,"status":status,
        "source":x.get("source")
    })

rank={"INVESTIGATE":0,"REVIEW":1,"VALIDATED_CANDIDATE":2}
rows.sort(key=lambda x:(rank[x["status"]],x["club"].lower()))
counts={
 "high_candidates_checked":len(rows),
 "validated_candidates":sum(x["status"]=="VALIDATED_CANDIDATE" for x in rows),
 "review":sum(x["status"]=="REVIEW" for x in rows),
 "investigate":sum(x["status"]=="INVESTIGATE" for x in rows),
 "unique_postcodes_checked":len(pcs)
}
payload={"checked_at":datetime.now(timezone.utc).isoformat(),
 "mode":"validation-only","source_discovery":"FCHD 2025-26 Gazetteer",
 "independent_geocoder":"Postcodes.io","rules":{
   "validated":"valid postcode, FCHD coordinates present, <=750m from postcode centroid, no review flags",
   "review":"valid core data but shared postcode, possible host-club ground label, or 0.75-2km coordinate difference",
   "investigate":"postcode lookup failure, missing FCHD coordinates, or >2km coordinate disagreement"
 },"counts":counts,"records":rows}
JSON_REPORT.write_text(json.dumps(payload,indent=2,ensure_ascii=False)+"\n",encoding="utf8")

L=["# Tin Foil FA Cup — Ground Verification Queue","",
 f"Last checked: **{datetime.now(timezone.utc).strftime('%d/%m/%Y, %H:%M:%S UTC')}**","",
 "This is **validation-only**. No Clubfinder ground data has been changed.","",
 "Discovery source: **FCHD 2025–26 English Football Gazetteer**  ",
 "Independent postcode/location check: **Postcodes.io**","",
 f"- 🟢 Validated candidates: **{counts['validated_candidates']}**",
 f"- 🟡 Human review: **{counts['review']}**",
 f"- 🔴 Investigate: **{counts['investigate']}**",
 f"- ⚪ HIGH discovery candidates checked: **{counts['high_candidates_checked']}**","",
 "## 🔴 Investigate",""]
bad=[x for x in rows if x["status"]=="INVESTIGATE"]
if bad:
 for x in bad:
  L.append(f"- **{x['club']}** — {x['ground_candidate']} • {x['postcode']} — "+", ".join(x["flags"]))
else:L.append("No candidates require investigation.")

L+=["","## 🟡 Human review",""]
rev=[x for x in rows if x["status"]=="REVIEW"]
if rev:
 for x in rev:
  d="?" if x["distance_km"] is None else f"{x['distance_km']} km"
  L.append(f"- **{x['club']}** — {x['ground_candidate']} • {x['postcode']} — separation `{d}` — "+", ".join(x["flags"]))
else:L.append("No candidates require human review.")

L+=["","## 🟢 First 25 validated candidates",""]
good=[x for x in rows if x["status"]=="VALIDATED_CANDIDATE"]
for x in good[:25]:
 L.append(f"- **{x['club']}** — {x['ground_candidate']} • {x['postcode']} — FCHD ↔ postcode centroid `{x['distance_km']} km`")

L+=["","## Validation rules","",
 "- `VALIDATED_CANDIDATE` does **not** mean automatically published.",
 "- Postcode must resolve independently through Postcodes.io.",
 "- FCHD must supply coordinates.",
 "- FCHD coordinates must be within 750 m of the independent postcode centroid for a clean validation.",
 "- 750 m–2 km differences are reviewed because large/rural postcodes can legitimately span distance.",
 "- Differences above 2 km are investigated.",
 "- Shared postcodes and possible host-club/groundshare labels are always reviewed.",
 "- FCHD remains a 2025–26 source; current 2026–27 venue changes can still supersede it.",
 "- `clubfinder.html` and `competition.json` are untouched."]
REPORT.write_text("\n".join(L)+"\n",encoding="utf8")

print("GROUND VERIFICATION QUEUE v7.6.5")
for k,v in counts.items():print(k+":",v)
print("VALIDATION ONLY: no Clubfinder or competition data changed.")
