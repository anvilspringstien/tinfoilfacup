#!/usr/bin/env python3
import argparse,json,re
from pathlib import Path
from datetime import datetime,timezone

ROOT=Path(__file__).resolve().parents[1]
HTML=ROOT/"clubfinder.html"
VAL=ROOT/"updater/geography-coordinate-validation.json"
OUT=ROOT/"updater/geography-candidate-promotion.json"
REPORT=ROOT/"ground-geography-promotion.md"
ALLOWED={"EXISTING_CANDIDATE_VALIDATED","CORRECTED_POSTCODE_VALIDATED"}

def norm(s):
    s=(s or "").lower().replace("&"," and ").replace("’","'").replace("'","")
    s=re.sub(r"\b(fc|afc|cfc|football club)\b"," ",s)
    return re.sub(r"[^a-z0-9]+"," ",s).strip()

def locate_array(text,name):
    m=re.search(r"\b(?:const|let|var)\s+"+re.escape(name)+r"\s*=\s*\[",text)
    if not m: raise SystemExit("Safety stop: could not locate "+name+" in clubfinder.html")
    s=text.find("[",m.start()); depth=0; ins=False; esc=False; q=""
    for i in range(s,len(text)):
        ch=text[i]
        if ins:
            if esc: esc=False
            elif ch=="\\": esc=True
            elif ch==q: ins=False
        else:
            if ch in ("'",'"'): ins=True;q=ch
            elif ch=="[": depth+=1
            elif ch=="]":
                depth-=1
                if depth==0:return s,i+1
    raise SystemExit("Safety stop: unbalanced "+name+" array")

ap=argparse.ArgumentParser()
ap.add_argument("--publish",action="store_true")
a=ap.parse_args()

if not VAL.exists(): raise SystemExit("Missing v7.7.6 validation JSON.")
data=json.loads(VAL.read_text(encoding="utf8"))
rows=data.get("records",[])
if len(rows)!=7: raise SystemExit("Safety stop: expected exactly seven v7.7.6 cases.")

text=HTML.read_text(encoding="utf8")
s,e=locate_array(text,"GROUNDS")
grounds=json.loads(text[s:e])
existing={norm(g.get("name") or g.get("club")) for g in grounds}

ready=[]; held=[]; skipped=[]
for r in rows:
    st=r.get("validation_status")
    club=r.get("club")
    if st not in ALLOWED:
        held.append({"club":club,"status":st,"reason":"Status is not promotion-eligible"})
        continue
    if norm(club) in existing:
        skipped.append({"club":club,"reason":"Canonical GROUNDS record already exists; overwrite prohibited"})
        continue

    if st=="CORRECTED_POSTCODE_VALIDATED":
        lat=r.get("validated_lat"); lon=r.get("validated_lon")
        coord_source="Fresh Postcodes.io coordinates for corrected postcode"
    else:
        # Existing validated candidates retain the FCHD coordinates from the
        # original v7.6.5 queue, carried into v7.7.5 as fchd_lat/fchd_lon if present.
        lat=r.get("fchd_lat"); lon=r.get("fchd_lon")
        if lat is None or lon is None:
            # v7.7.5 evidence/report may not carry them. Recover ONLY from the
            # original machine-readable verification queue by exact club.
            q=ROOT/"updater/ground-verification-queue.json"
            if q.exists():
                qd=json.loads(q.read_text(encoding="utf8"))
                candidates=qd.get("records",qd.get("queue",qd if isinstance(qd,list) else []))
                hit=next((x for x in candidates if norm(x.get("club"))==norm(club)),None)
                if hit: lat,lon=hit.get("fchd_lat"),hit.get("fchd_lon")
        coord_source="Previously validated FCHD coordinates"
    if lat is None or lon is None:
        skipped.append({"club":club,"reason":"Validated coordinates unavailable; promotion stopped safely"})
        continue

    rec={
      "name":club,
      "ground":r.get("current_ground") or r.get("ground_candidate") or r.get("old_ground"),
      "postcode":r.get("current_postcode"),
      "lat":lat,"lon":lon,
      "verification":"verified","verification_label":"✅ Verified",
      "source":"v7.7.5 current-ground review + v7.7.6 independent coordinate validation",
      "coordinate_source":coord_source,
      "geography_validation":"v7.7.6"
    }
    if not rec["ground"] or not rec["postcode"]:
        skipped.append({"club":club,"reason":"Ground/postcode incomplete; promotion stopped safely"})
        continue
    ready.append(rec)

published=False
if a.publish:
    if skipped:
        raise SystemExit("Safety stop: one or more eligible records failed safety checks; nothing published.")
    newgrounds=grounds+ready
    rendered=json.dumps(newgrounds,ensure_ascii=False,separators=(",",":"))
    HTML.write_text(text[:s]+rendered+text[e:],encoding="utf8")
    published=True

payload={
 "checked_at":datetime.now(timezone.utc).isoformat(),"version":"7.7.7",
 "mode":"PUBLISH" if a.publish else "DRY RUN",
 "eligible_geography_candidates":sum(r.get("validation_status") in ALLOWED for r in rows),
 "ready_to_promote":len(ready),"held_rejected":len(held),
 "skipped_safety":len(skipped),"overwrites":0,"published":published,
 "promotion_records":ready,"held":held,"skipped":skipped
}
OUT.write_text(json.dumps(payload,indent=2,ensure_ascii=False)+"\n",encoding="utf8")

L=["# Tin Foil FA Cup — Geography Candidate Promotion","",
f"Last checked: **{datetime.now(timezone.utc).strftime('%d/%m/%Y, %H:%M:%S UTC')}**","",
f"Mode: **{payload['mode']}**","",
f"- Eligible geography candidates: **{payload['eligible_geography_candidates']}**",
f"- Ready to promote: **{len(ready)}**",
f"- Held/rejected: **{len(held)}**",
f"- Skipped by safety checks: **{len(skipped)}**",
"- Existing canonical records overwritten: **0**",
f"- Published: **{'YES' if published else 'NO'}**","",
"## Promotion records",""]
for x in ready:
    L.append(f"- **{x['name']}** — {x['ground']} • {x['postcode']} • `{x['lat']}, {x['lon']}` • {x['coordinate_source']}")
L+=["","## Held / rejected",""]
for x in held:L.append(f"- **{x['club']}** — {x['status']} — {x['reason']}")
if not held:L.append("None.")
L+=["","## Safety","",
"- Only v7.7.6 `EXISTING_CANDIDATE_VALIDATED` and `CORRECTED_POSTCODE_VALIDATED` records are eligible.",
"- Existing canonical `GROUNDS` records are never overwritten.",
"- Corrected postcodes use only fresh v7.7.6 coordinates.",
"- Corby Town and every non-eligible status remain excluded.",
"- `competition.json` is untouched."
]
REPORT.write_text("\n".join(L)+"\n",encoding="utf8")

print("GEOGRAPHY CANDIDATE PROMOTION v7.7.7")
print("Mode:","PUBLISH" if a.publish else "DRY RUN")
print("Eligible geography candidates:",payload["eligible_geography_candidates"])
print("Ready to promote:",len(ready))
print("Held/rejected:",len(held))
print("Skipped by safety checks:",len(skipped))
print("Existing canonical records overwritten: 0")
print("Published:","YES" if published else "NO")
