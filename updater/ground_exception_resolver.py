#!/usr/bin/env python3
import json,re
from collections import defaultdict
from datetime import datetime,timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DISC=ROOT/"updater/ground-discovery-queue.json"
VER=ROOT/"updater/ground-verification-queue.json"
HEALTH=ROOT/"updater/ground-health.json"
REPORT=ROOT/"ground-exceptions.md"
JOUT=ROOT/"updater/ground-exceptions.json"

def norm(s):
 s=(s or "").lower().replace("&"," and ")
 s=re.sub(r"\b(fc|afc|cfc|football club)\b"," ",s)
 return re.sub(r"[^a-z0-9]+"," ",s).strip()

for p in (DISC,VER,HEALTH):
 if not p.exists(): raise SystemExit(f"Missing prerequisite: {p.relative_to(ROOT)}")

d=json.loads(DISC.read_text(encoding="utf8"))
v=json.loads(VER.read_text(encoding="utf8"))
h=json.loads(HEALTH.read_text(encoding="utf8"))

# Health file is authoritative for what remains unresolved now.
missing=[]
for x in h.get("missing_or_incomplete",[]):
 if isinstance(x,list): missing.append(x[0])
 elif isinstance(x,dict): missing.append(x.get("club") or x.get("name"))
missing=[x for x in missing if x]

dq={norm(x.get("eligible_club")):x for x in d.get("queue",[]) if x.get("eligible_club")}
vq={norm(x.get("club")):x for x in v.get("records",[]) if x.get("club")}

cats=defaultdict(list)
for club in missing:
 k=norm(club); di=dq.get(k,{}); vi=vq.get(k,{})
 row={"club":club,
      "discovery_confidence":di.get("confidence"),
      "fchd_match":di.get("club"),
      "ground_candidate":vi.get("ground_candidate") or di.get("ground_candidate"),
      "postcode":vi.get("postcode") or di.get("postcode"),
      "flags":vi.get("flags",[]),
      "distance_km":vi.get("distance_km"),
      "raw_lines":di.get("raw_lines",[])}
 if vi.get("status")=="INVESTIGATE":
  cat="GEOGRAPHY / POSTCODE INVESTIGATION"
 elif vi.get("status")=="REVIEW":
  if "SHARED_POSTCODE" in vi.get("flags",[]) or "GROUND_NAME_MAY_BE_HOST_CLUB" in vi.get("flags",[]):
   cat="GROUNDSHARE / HOST-GROUND REVIEW"
  else:
   cat="GEOGRAPHY / POSTCODE REVIEW"
 elif di.get("confidence")=="REVIEW":
  cat="FUZZY CLUB-NAME MATCH"
 elif di.get("confidence")=="NO MATCH" or not di:
  cat="NO FCHD MATCH"
 else:
  cat="OTHER EXCEPTION"
 cats[cat].append(row)

# Current yellow health flags, including already-canonical records.
yellow={
 "unverified_locations":h.get("unverified",[]),
 "shared_postcodes":h.get("shared_postcodes",[])
}

order=["GROUNDSHARE / HOST-GROUND REVIEW","GEOGRAPHY / POSTCODE REVIEW",
       "GEOGRAPHY / POSTCODE INVESTIGATION","FUZZY CLUB-NAME MATCH",
       "NO FCHD MATCH","OTHER EXCEPTION"]
counts={k:len(cats.get(k,[])) for k in order}
payload={"checked_at":datetime.now(timezone.utc).isoformat(),"mode":"triage-only",
         "missing_total":len(missing),"category_counts":counts,
         "categories":{k:cats.get(k,[]) for k in order},"existing_yellow_health":yellow}
JOUT.write_text(json.dumps(payload,indent=2,ensure_ascii=False)+"\n",encoding="utf8")

L=["# Tin Foil FA Cup — Ground Exceptions","",
 f"Last checked: **{datetime.now(timezone.utc).strftime('%d/%m/%Y, %H:%M:%S UTC')}**","",
 "This dashboard triages the remaining ground exceptions. **Nothing is published automatically.**","",
 f"- 🔴 Missing canonical ground records: **{len(missing)}**"]
labels={
"GROUNDSHARE / HOST-GROUND REVIEW":"🏟️ Groundshare / host-ground review",
"GEOGRAPHY / POSTCODE REVIEW":"📍 Geography / postcode review",
"GEOGRAPHY / POSTCODE INVESTIGATION":"🔴 Geography / postcode investigation",
"FUZZY CLUB-NAME MATCH":"🔤 Fuzzy club-name match",
"NO FCHD MATCH":"🔎 No FCHD match",
"OTHER EXCEPTION":"❓ Other exception"}
for k in order:L.append(f"- {labels[k]}: **{counts[k]}**")

for k in order:
 L+=["",f"## {labels[k]}",""]
 xs=cats.get(k,[])
 if not xs:L.append("None.")
 for x in xs:
  bits=[]
  if x.get("fchd_match") and x["fchd_match"]!=x["club"]:bits.append(f"FCHD: **{x['fchd_match']}**")
  if x.get("ground_candidate"):bits.append(x["ground_candidate"])
  if x.get("postcode"):bits.append(x["postcode"])
  if x.get("distance_km") is not None:bits.append(f"separation `{x['distance_km']} km`")
  if x.get("flags"):bits.append(", ".join(x["flags"]))
  L.append(f"- **{x['club']}** — "+(" • ".join(bits) if bits else "No candidate data"))

L+=["","## Existing canonical yellow flags","",
 f"- Unverified-location flags: **{len(yellow['unverified_locations'])}**",
 f"- Shared-postcode flags: **{len(yellow['shared_postcodes'])}**","",
 "## Resolution philosophy","",
 "- Groundshares are not errors merely because two clubs use one postcode.",
 "- A known/approved groundshare should eventually be stored explicitly so Ground Health can stop warning about it.",
 "- Fuzzy names are never promoted without confirming club identity.",
 "- Failed/large postcode disagreements remain red until independently resolved.",
 "- No-match clubs form the final discovery queue for other free/public sources.",
 "- Audit/triage only: `clubfinder.html` and `competition.json` are untouched."]
REPORT.write_text("\n".join(L)+"\n",encoding="utf8")
print("GROUND EXCEPTION RESOLVER v7.6.7 — TRIAGE")
print("Missing:",len(missing))
for k in order:print(k+":",counts[k])
print("TRIAGE ONLY: no Clubfinder or competition data changed.")
