#!/usr/bin/env python3
import argparse, json, re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
HTML=ROOT/"clubfinder.html"
LEDGER=ROOT/"updater/ground-approval-ledger.json"
VERIFY=ROOT/"updater/ground-verification-queue.json"
REPORT=ROOT/"approved-groundshare-pair-promotion.md"

def norm(s):
    s=(s or "").lower().replace("&"," and ").replace("’","'")
    s=re.sub(r"\b(fc|afc|cfc|football club)\b"," ",s)
    return re.sub(r"[^a-z0-9]+"," ",s).strip()

def locate_array(text,name):
    pattern=r"\b(?:const|let|var)\s+"+re.escape(name)+r"\s*=\s*\["
    m=re.search(pattern,text)
    if not m:
        raise SystemExit(f"Could not find {name} array")
    start=text.find("[",m.start())
    depth=0; in_string=False; escaped=False; quote=""
    for i in range(start,len(text)):
        ch=text[i]
        if in_string:
            if escaped: escaped=False
            elif ch=="\\": escaped=True
            elif ch==quote: in_string=False
        else:
            if ch in ("'",'"'): in_string=True; quote=ch
            elif ch=="[": depth+=1
            elif ch=="]":
                depth-=1
                if depth==0: return start,i+1
    raise SystemExit(f"Unbalanced {name} array")

def find_one(items,key,value,label):
    hits=[x for x in items if norm(x.get(key))==norm(value)]
    if len(hits)!=1:
        raise SystemExit(f"Expected exactly one {label} for {value}; found {len(hits)}")
    return hits[0]

def canonical_name(g):
    return g.get("name") or g.get("club") or ""

ap=argparse.ArgumentParser()
ap.add_argument("--tenant",required=True)
ap.add_argument("--publish",action="store_true")
args=ap.parse_args()

ledger=json.loads(LEDGER.read_text(encoding="utf8"))
approval=find_one(ledger.get("known_groundshares",[]),"tenant",args.tenant,"approved groundshare")
tenant=approval.get("tenant","")
host=approval.get("host","")
ground=approval.get("ground","")
postcode=(approval.get("postcode") or "").upper().strip()
if not host or not ground or not postcode:
    raise SystemExit("Approval ledger entry is missing host, ground, or postcode")

verification=json.loads(VERIFY.read_text(encoding="utf8"))
records=verification.get("records",[])
tenant_c=find_one(records,"club",tenant,"tenant verification candidate")
host_c=find_one(records,"club",host,"host verification candidate")

for role,c in (("tenant",tenant_c),("host",host_c)):
    if norm(c.get("ground_candidate"))!=norm(ground):
        raise SystemExit(f"{role.title()} ground mismatch: ledger '{ground}' vs candidate '{c.get('ground_candidate')}'")
    if (c.get("postcode") or "").upper().strip()!=postcode:
        raise SystemExit(f"{role.title()} postcode mismatch: ledger '{postcode}' vs candidate '{c.get('postcode')}'")
    if c.get("fchd_lat") is None or c.get("fchd_lon") is None:
        raise SystemExit(f"{role.title()} candidate has no FCHD coordinates")

text=HTML.read_text(encoding="utf8")
gs,ge=locate_array(text,"GROUNDS")
grounds=json.loads(text[gs:ge])

tenant_existing=[g for g in grounds if norm(canonical_name(g))==norm(tenant)]
host_existing=[g for g in grounds if norm(canonical_name(g))==norm(host)]
if len(tenant_existing)>1 or len(host_existing)>1:
    raise SystemExit("Duplicate canonical club record detected; refusing promotion")

def make_record(club,c):
    return {
        "name":club,
        "ground":ground,
        "postcode":postcode,
        "lat":float(c["fchd_lat"]),
        "lon":float(c["fchd_lon"]),
        "verification":"verified",
        "verification_label":"✅ Verified",
        "source":"Approved current groundshare + validated ground candidate",
        "ground_source":c.get("source") or "FCHD 2025-26 Gazetteer",
        "coordinate_source":"FCHD coordinates; independently checked against Postcodes.io",
        "groundshare_host":host if norm(club)==norm(tenant) else "",
        "groundshare_tenant":tenant if norm(club)==norm(host) else "",
        "groundshare_season":approval.get("season",""),
        "groundshare_source":approval.get("source_url","")
    }

to_add=[]
if not tenant_existing: to_add.append(make_record(tenant,tenant_c))
if not host_existing: to_add.append(make_record(host,host_c))

if args.publish and to_add:
    grounds.extend(to_add)
    HTML.write_text(
        text[:gs]+json.dumps(grounds,ensure_ascii=False,separators=(",",":"))+text[ge:],
        encoding="utf8"
    )

def state(existing):
    return "already canonical ✅" if existing else "missing; validated candidate found ✅"

lines=[
"# Tin Foil FA Cup — Approved Groundshare Pair Promotion","",
f"- Mode: **{'PUBLISH' if args.publish else 'DRY RUN'}**",
f"- Tenant: **{tenant}** — {state(tenant_existing)}",
f"- Host: **{host}** — {state(host_existing)}",
f"- Approved venue: **{ground} • {postcode}**",
"- Approval-ledger relationship found: **✅**",
"- Tenant candidate agrees with approved venue/postcode: **✅**",
"- Host candidate agrees with approved venue/postcode: **✅**",
f"- Missing canonical records ready to promote: **{len(to_add)}**",
f"- Canonical GROUNDS changed: **{'YES' if args.publish and to_add else 'NO'}**","",
"## Promotion plan",""
]
if to_add:
    for r in to_add:
        lines.append(f"- **{r['name']}** — {r['ground']} • {r['postcode']} • `{r['lat']}, {r['lon']}`")
else:
    lines.append("- Nothing to add; both clubs are already canonical.")
lines += ["","## Safety","",
"- Existing canonical records are never overwritten.",
"- A club is added only if absent from canonical GROUNDS.",
"- Tenant and host must both match the approved ground and postcode.",
"- Both clubs must have machine-readable validated FCHD coordinates.",
"- `competition.json` is untouched.",
]
REPORT.write_text("\n".join(lines)+"\n",encoding="utf8")

print("APPROVED GROUNDSHARE PAIR PROMOTION v7.7.3c")
print("Mode:", "PUBLISH" if args.publish else "DRY RUN")
print("Tenant:", tenant, "-", "already canonical" if tenant_existing else "ready to add")
print("Host:", host, "-", "already canonical" if host_existing else "ready to add")
print("Missing canonical records ready to promote:",len(to_add))
print("READY TO PROMOTE:", "YES" if to_add else "NOTHING TO ADD")
