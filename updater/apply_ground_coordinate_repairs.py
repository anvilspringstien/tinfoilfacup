#!/usr/bin/env python3
import json,re,sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
HTML=ROOT/"clubfinder.html"
PROPOSAL=ROOT/"updater/ground-coordinate-repair.json"

def norm(s):
    s=(s or "").lower().replace("&"," and ")
    s=re.sub(r"\b(fc|afc|cfc)\b"," ",s)
    return re.sub(r"[^a-z0-9]+"," ",s).strip()

def locate_array(text,name):
    m=re.search(r"\b(?:const|let|var)\s+"+re.escape(name)+r"\s*=\s*\[",text)
    if not m:
        raise SystemExit(f"Could not find {name} array")
    start=text.find("[",m.start())
    depth=0; in_str=False; esc=False; quote=""
    for i in range(start,len(text)):
        ch=text[i]
        if in_str:
            if esc: esc=False
            elif ch=="\\": esc=True
            elif ch==quote: in_str=False
        else:
            if ch in ("'",'"'):
                in_str=True; quote=ch
            elif ch=="[":
                depth+=1
            elif ch=="]":
                depth-=1
                if depth==0:
                    return start,i+1
    raise SystemExit(f"Unbalanced {name} array")

if not HTML.exists():
    raise SystemExit("clubfinder.html not found")
if not PROPOSAL.exists():
    raise SystemExit("updater/ground-coordinate-repair.json not found. Run v7.6.3 probe first.")

proposal=json.loads(PROPOSAL.read_text(encoding="utf-8"))
if proposal.get("source")!="postcodes.io":
    raise SystemExit("Unexpected proposal source")
records=proposal.get("records") or []
ready=[r for r in records if r.get("status")=="READY"]
if not ready:
    raise SystemExit("No READY coordinate repairs found in proposal.")

text=HTML.read_text(encoding="utf-8")
start,end=locate_array(text,"GROUNDS")
grounds=json.loads(text[start:end])

index={}
for i,g in enumerate(grounds):
    club=g.get("name") or g.get("club") or ""
    pc=(g.get("postcode") or "").strip().upper()
    index[(norm(club),pc)]=i

applied=[]; skipped=[]

for r in ready:
    club=r.get("club") or ""
    pc=(r.get("postcode") or "").strip().upper()
    lat=r.get("lat"); lon=r.get("lon")
    if lat is None or lon is None:
        skipped.append({"club":club,"reason":"Proposal has no coordinates"})
        continue

    key=(norm(club),pc)
    if key not in index:
        skipped.append({"club":club,"postcode":pc,"reason":"Canonical record/postcode no longer matches"})
        continue

    g=grounds[index[key]]
    # Safety: never overwrite existing coordinates.
    if g.get("lat") is not None or g.get("lon") is not None:
        skipped.append({"club":club,"postcode":pc,"reason":"Coordinates already present; left unchanged"})
        continue

    g["lat"]=float(lat)
    g["lon"]=float(lon)
    g["coordinate_source"]="Postcodes.io postcode centroid"
    applied.append({"club":club,"postcode":pc,"lat":lat,"lon":lon})

if not applied:
    print("No coordinate repairs applied.")
    for x in skipped: print("SKIP",x)
    sys.exit(0)

new_array=json.dumps(grounds,ensure_ascii=False,separators=(",",":"))
new_text=text[:start]+new_array+text[end:]
HTML.write_text(new_text,encoding="utf-8")

audit={
    "applied":applied,
    "skipped":skipped,
    "proposal_checked_at":proposal.get("checked_at"),
}
(ROOT/"updater/ground-coordinate-apply-result.json").write_text(
    json.dumps(audit,indent=2,ensure_ascii=False)+"\n",encoding="utf-8"
)

print("GROUND COORDINATE APPLY v7.6.3a")
print("Applied:",len(applied))
for x in applied:
    print("APPLIED",x["club"],x["postcode"],x["lat"],x["lon"])
print("Skipped:",len(skipped))
for x in skipped:
    print("SKIP",x)
print("clubfinder.html updated. competition.json untouched.")
