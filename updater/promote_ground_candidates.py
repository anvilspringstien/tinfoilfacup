#!/usr/bin/env python3
import argparse,json,re,sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
HTML=ROOT/"clubfinder.html"
QUEUE=ROOT/"updater/ground-verification-queue.json"
DRY_REPORT=ROOT/"ground-candidate-promotion.md"
APPLY_REPORT=ROOT/"updater/ground-candidate-promotion.json"

def norm(s):
    s=(s or "").lower().replace("&"," and ")
    s=re.sub(r"\b(fc|afc|cfc|football club)\b"," ",s)
    return re.sub(r"[^a-z0-9]+"," ",s).strip()

def locate_array(text,name):
    m=re.search(r"\b(?:const|let|var)\s+"+re.escape(name)+r"\s*=\s*\[",text)
    if not m:
        raise SystemExit(f"Could not find {name} array")
    start=text.find("[",m.start())
    depth=0;ins=False;esc=False;q=""
    for i in range(start,len(text)):
        c=text[i]
        if ins:
            if esc: esc=False
            elif c=="\\": esc=True
            elif c==q: ins=False
        else:
            if c in ("'",'"'):
                ins=True;q=c
            elif c=="[":
                depth+=1
            elif c=="]":
                depth-=1
                if depth==0:
                    return start,i+1
    raise SystemExit(f"Unbalanced {name} array")

def extract_array(text,name):
    s,e=locate_array(text,name)
    return s,e,json.loads(text[s:e])

def safe_float(v):
    try:return float(v)
    except:return None

ap=argparse.ArgumentParser()
ap.add_argument("--publish",action="store_true")
args=ap.parse_args()

if not HTML.exists():
    raise SystemExit("clubfinder.html not found.")
if not QUEUE.exists():
    raise SystemExit("updater/ground-verification-queue.json missing. Run v7.6.5 first.")

verification=json.loads(QUEUE.read_text(encoding="utf-8"))
records=[x for x in verification.get("records",[]) if x.get("status")=="VALIDATED_CANDIDATE"]
if not records:
    raise SystemExit("No VALIDATED_CANDIDATE records found.")

text=HTML.read_text(encoding="utf-8")
gs,ge,grounds=extract_array(text,"GROUNDS")
_,_,eligible=extract_array(text,"ELIGIBLE")

eligible_names={norm(x.get("name")):x.get("name") for x in eligible if x.get("name")}
existing={}
for i,g in enumerate(grounds):
    key=norm(g.get("name") or g.get("club") or "")
    if key: existing.setdefault(key,[]).append(i)

to_add=[]
skipped=[]
for r in records:
    club=r.get("club") or ""
    key=norm(club)
    if key not in eligible_names:
        skipped.append({"club":club,"reason":"Club no longer exists in ELIGIBLE"})
        continue
    if key in existing:
        skipped.append({"club":club,"reason":"Canonical GROUNDS record already exists"})
        continue
    pc=(r.get("postcode") or "").strip().upper()
    ground=(r.get("ground_candidate") or "").strip()
    lat=safe_float(r.get("fchd_lat"));lon=safe_float(r.get("fchd_lon"))
    if not pc or not ground or lat is None or lon is None:
        skipped.append({"club":club,"reason":"Candidate missing ground/postcode/FCHD coordinates"})
        continue
    # Preserve the exact eligible display name where possible.
    display=eligible_names[key]
    to_add.append({
        "name":display,
        "ground":ground,
        "postcode":pc,
        "lat":lat,
        "lon":lon,
        "verification":"verified",
        "verification_label":"✅ Verified",
        "source":"FCHD 2025-26 Gazetteer; independently postcode/location validated via Postcodes.io",
        "ground_source":"FCHD 2025-26 Gazetteer",
        "coordinate_source":"FCHD coordinates; validated against Postcodes.io postcode centroid"
    })

# Deterministic ordering prevents noisy diffs.
to_add.sort(key=lambda x:x["name"].lower())

summary={
    "mode":"publish" if args.publish else "dry-run",
    "validated_candidates_seen":len(records),
    "eligible_for_promotion":len(to_add),
    "skipped":len(skipped),
    "records_to_add":to_add,
    "skipped_records":skipped
}
APPLY_REPORT.write_text(json.dumps(summary,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")

L=[
    "# Tin Foil FA Cup — Ground Candidate Promotion",
    "",
    f"Mode: **{'PUBLISH' if args.publish else 'DRY RUN'}**",
    "",
    f"- v7.6.5 validated candidates seen: **{len(records)}**",
    f"- Eligible for promotion now: **{len(to_add)}**",
    f"- Skipped by safety checks: **{len(skipped)}**",
    "",
    "Only `VALIDATED_CANDIDATE` records are eligible. Existing canonical GROUNDS entries are never overwritten.",
    "",
    "## First 30 eligible promotions",
    ""
]
for g in to_add[:30]:
    L.append(f"- **{g['name']}** — {g['ground']} • {g['postcode']} • `{g['lat']}, {g['lon']}`")
if skipped:
    L += ["","## Skipped",""]
    for s in skipped[:100]:
        L.append(f"- **{s['club']}** — {s['reason']}")
DRY_REPORT.write_text("\n".join(L)+"\n",encoding="utf-8")

print("GROUND CANDIDATE PROMOTION v7.6.6")
print("Mode:","PUBLISH" if args.publish else "DRY RUN")
print("Validated candidates:",len(records))
print("Eligible for promotion:",len(to_add))
print("Skipped:",len(skipped))

if not args.publish:
    print("DRY RUN: clubfinder.html unchanged.")
    sys.exit(0)

if not to_add:
    print("Nothing to publish.")
    sys.exit(0)

new_grounds=grounds+to_add
new_array=json.dumps(new_grounds,ensure_ascii=False,separators=(",",":"))
new_text=text[:gs]+new_array+text[ge:]
HTML.write_text(new_text,encoding="utf-8")

print("PUBLISHED:",len(to_add),"new canonical ground records.")
print("clubfinder.html updated. competition.json untouched.")
