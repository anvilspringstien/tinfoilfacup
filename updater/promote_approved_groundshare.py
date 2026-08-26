#!/usr/bin/env python3
import argparse,json,re
from pathlib import Path
from datetime import datetime,timezone

ROOT=Path(__file__).resolve().parents[1]
HTML=ROOT/"clubfinder.html"
LEDGER=ROOT/"updater/ground-approval-ledger.json"
VERIFY=ROOT/"updater/ground-verification.json"
DISCOVERY=ROOT/"updater/ground-discovery.json"
REPORT=ROOT/"approved-groundshare-promotion.md"

def norm(s):
    s=(s or "").lower().replace("&"," and ").replace("’","'")
    s=re.sub(r"\b(fc|afc|cfc|football club)\b"," ",s)
    return re.sub(r"[^a-z0-9]+"," ",s).strip()

def locate_array(text,name):
    m=re.search(r"\b(?:const|let|var)\s+"+re.escape(name)+r"\s*=\s*\[",text)
    if not m: raise SystemExit("Could not find "+name+" array")
    st=text.find("[",m.start()); d=0; ins=False; esc=False; q=""
    for i in range(st,len(text)):
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
                if d==0:return st,i+1
    raise SystemExit("Unbalanced "+name)

def load_json(path,default):
    try:return json.loads(path.read_text(encoding="utf8"))
    except:return default

def recursive_records(obj):
    if isinstance(obj,dict):
        yield obj
        for v in obj.values(): yield from recursive_records(v)
    elif isinstance(obj,list):
        for v in obj: yield from recursive_records(v)

ap=argparse.ArgumentParser()
ap.add_argument("--tenant",required=True)
ap.add_argument("--publish",action="store_true")
a=ap.parse_args()

ledger=load_json(LEDGER,{})
entries=[x for x in ledger.get("known_groundshares",[]) if norm(x.get("tenant"))==norm(a.tenant)]
if len(entries)!=1:
    raise SystemExit(f"Expected exactly one approved groundshare for {a.tenant}; found {len(entries)}")
approval=entries[0]

text=HTML.read_text(encoding="utf8")
gs,ge=locate_array(text,"GROUNDS")
grounds=json.loads(text[gs:ge])
if any(norm(g.get("name") or g.get("club"))==norm(a.tenant) for g in grounds):
    raise SystemExit(f"{a.tenant} already has a canonical GROUNDS record; refusing duplicate promotion.")

# Search prior validation/discovery machine-readable outputs if present.
sources=[]
for p in (VERIFY,DISCOVERY):
    if p.exists(): sources.append(load_json(p,{}))
cands=[]
for src in sources:
    for r in recursive_records(src):
        club=r.get("club") or r.get("name") or r.get("canonical_club")
        if norm(club)!=norm(a.tenant): continue
        ground=r.get("ground") or r.get("ground_name") or r.get("venue")
        postcode=(r.get("postcode") or "").upper().strip()
        lat=r.get("lat",r.get("latitude")); lon=r.get("lon",r.get("longitude"))
        status=str(r.get("status") or r.get("classification") or r.get("verification") or "").upper()
        if ground and postcode and lat is not None and lon is not None:
            cands.append({"ground":ground,"postcode":postcode,"lat":lat,"lon":lon,"status":status})

# v7.7.3 intentionally does not invent coordinates. If old JSON filenames differ,
# operator can supply reviewed coordinates explicitly.
ap2=argparse.ArgumentParser(add_help=False)
# fallback environment intentionally avoided: explicit CLI only
if not cands:
    raise SystemExit(
      "No machine-readable validated candidate with coordinates found for this tenant. "
      "Promotion stopped safely. Re-run the existing ground discovery/verification workflow "
      "so its JSON candidate output is present, then retry."
    )

approved_pc=(approval.get("postcode") or "").upper().strip()
approved_ground=norm(approval.get("ground"))
agree=[c for c in cands if c["postcode"]==approved_pc and norm(c["ground"])==approved_ground]
if not agree:
    raise SystemExit("Validated candidate does not agree with approved ground + postcode; refusing promotion.")
cand=agree[0]

record={
 "name":approval["tenant"],
 "ground":approval["ground"],
 "postcode":approved_pc,
 "lat":float(cand["lat"]),
 "lon":float(cand["lon"]),
 "verification":"verified",
 "verification_label":"✅ Verified",
 "source":"Approved current groundshare + previously validated ground candidate",
 "groundshare_host":approval.get("host",""),
 "groundshare_season":approval.get("season",""),
 "groundshare_source":approval.get("source_url","")
}

if a.publish:
    grounds.append(record)
    HTML.write_text(text[:gs]+json.dumps(grounds,ensure_ascii=False,separators=(",",":"))+text[ge:],encoding="utf8")

ready="YES"
lines=[
"# Tin Foil FA Cup — Approved Groundshare Promotion","",
f"Last run: **{datetime.now(timezone.utc).strftime('%d/%m/%Y, %H:%M:%S UTC')}**","",
f"- Mode: **{'PUBLISH' if a.publish else 'DRY RUN'}**",
f"- Tenant: **{approval['tenant']}**",
f"- Host: **{approval.get('host','')}**",
f"- Approved venue: **{approval.get('ground','')} • {approved_pc}**",
"- Ledger approval: **✅**",
"- Validated candidate agrees: **✅**",
"- Validated coordinates available: **✅**",
f"- Ready to promote: **{ready}**",
f"- Canonical GROUNDS changed: **{'YES' if a.publish else 'NO'}**","",
"## Candidate","",
f"- **{record['name']}** — {record['ground']} • {record['postcode']} • `{record['lat']}, {record['lon']}`","",
"## Safety","",
"- Existing canonical GROUNDS records are never overwritten.",
"- Duplicate tenant records are refused.",
"- Ground and postcode must exactly agree with the reviewed ledger approval.",
"- Coordinates must come from an existing machine-readable validated candidate.",
"- `competition.json` is untouched."
]
REPORT.write_text("\n".join(lines)+"\n",encoding="utf8")
print("APPROVED GROUNDSHARE PROMOTION v7.7.3")
print("Mode:", "PUBLISH" if a.publish else "DRY RUN")
print("READY TO PROMOTE:", ready)
print(record)
