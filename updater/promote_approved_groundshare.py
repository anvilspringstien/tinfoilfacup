#!/usr/bin/env python3
import argparse,json,re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
HTML=ROOT/"clubfinder.html"
LEDGER=ROOT/"updater/ground-approval-ledger.json"
VERIFY=ROOT/"updater/ground-verification-queue.json"
REPORT=ROOT/"approved-groundshare-promotion.md"

def norm(s):
    s=(s or "").lower().replace("&"," and ").replace("’","'")
    s=re.sub(r"\b(fc|afc|cfc|football club)\b"," ",s)
    return re.sub(r"[^a-z0-9]+"," ",s).strip()

def locate_array(text,name):
    # IMPORTANT: normal raw-regex string; no double escaping.
    pattern = r"\b(?:const|let|var)\s+" + re.escape(name) + r"\s*=\s*\["
    m=re.search(pattern,text)
    if not m:
        raise SystemExit(f"Could not find {name} array")
    start=text.find("[",m.start())
    depth=0; in_string=False; escaped=False; quote=""
    for i in range(start,len(text)):
        ch=text[i]
        if in_string:
            if escaped:
                escaped=False
            elif ch=="\\":
                escaped=True
            elif ch==quote:
                in_string=False
        else:
            if ch in ("'",'"'):
                in_string=True; quote=ch
            elif ch=="[":
                depth+=1
            elif ch=="]":
                depth-=1
                if depth==0:
                    return start,i+1
    raise SystemExit(f"Unbalanced {name} array")

ap=argparse.ArgumentParser()
ap.add_argument("--tenant",required=True)
ap.add_argument("--publish",action="store_true")
a=ap.parse_args()

ledger=json.loads(LEDGER.read_text(encoding="utf8"))
approvals=[x for x in ledger.get("known_groundshares",[]) if norm(x.get("tenant"))==norm(a.tenant)]
if len(approvals)!=1:
    raise SystemExit(f"Expected exactly one approval for {a.tenant}; found {len(approvals)}")
approval=approvals[0]

verification=json.loads(VERIFY.read_text(encoding="utf8"))
records=verification.get("records",[])
matches=[x for x in records if norm(x.get("club"))==norm(a.tenant)]
if len(matches)!=1:
    raise SystemExit(f"Expected exactly one verification record for {a.tenant}; found {len(matches)}")
cand=matches[0]

approved_ground=norm(approval.get("ground"))
approved_pc=(approval.get("postcode") or "").upper().strip()
cand_ground=norm(cand.get("ground_candidate"))
cand_pc=(cand.get("postcode") or "").upper().strip()

if approved_ground!=cand_ground:
    raise SystemExit(f"Ground mismatch: ledger '{approval.get('ground')}' vs candidate '{cand.get('ground_candidate')}'")
if approved_pc!=cand_pc:
    raise SystemExit(f"Postcode mismatch: ledger '{approved_pc}' vs candidate '{cand_pc}'")
if cand.get("fchd_lat") is None or cand.get("fchd_lon") is None:
    raise SystemExit("Validated candidate has no FCHD coordinates")

text=HTML.read_text(encoding="utf8")
gs,ge=locate_array(text,"GROUNDS")
grounds=json.loads(text[gs:ge])

if any(norm(g.get("name") or g.get("club"))==norm(a.tenant) for g in grounds):
    raise SystemExit(f"{a.tenant} already has a canonical GROUNDS record; refusing duplicate promotion.")

record={
    "name":approval["tenant"],
    "ground":approval["ground"],
    "postcode":approved_pc,
    "lat":float(cand["fchd_lat"]),
    "lon":float(cand["fchd_lon"]),
    "verification":"verified",
    "verification_label":"✅ Verified",
    "source":"Approved current groundshare + v7.6.5 validated candidate",
    "ground_source":cand.get("source") or "FCHD 2025-26 Gazetteer",
    "coordinate_source":"FCHD coordinates; independently checked against Postcodes.io",
    "groundshare_host":approval.get("host",""),
    "groundshare_season":approval.get("season",""),
    "groundshare_source":approval.get("source_url","")
}

if a.publish:
    grounds.append(record)
    HTML.write_text(text[:gs]+json.dumps(grounds,ensure_ascii=False,separators=(",",":"))+text[ge:],encoding="utf8")

REPORT.write_text(
    "# Tin Foil FA Cup — Approved Groundshare Promotion\n\n"
    f"- Mode: **{'PUBLISH' if a.publish else 'DRY RUN'}**\n"
    f"- Tenant: **{approval['tenant']}**\n"
    f"- Host: **{approval.get('host','')}**\n"
    f"- Approved venue: **{approval.get('ground','')} • {approved_pc}**\n"
    "- Ledger approval: **✅**\n"
    "- v7.6.5 candidate agrees: **✅**\n"
    "- Validated coordinates available: **✅**\n"
    "- Ready to promote: **YES**\n"
    f"- Canonical GROUNDS changed: **{'YES' if a.publish else 'NO'}**\n\n"
    "## Candidate\n\n"
    f"- **{record['name']}** — {record['ground']} • {record['postcode']} • `{record['lat']}, {record['lon']}`\n\n"
    f"Independent postcode separation: `{cand.get('distance_km')} km`\n",
    encoding="utf8"
)

print("APPROVED GROUNDSHARE PROMOTION v7.7.3b")
print("Mode:", "PUBLISH" if a.publish else "DRY RUN")
print("READY TO PROMOTE: YES")
print(record)
