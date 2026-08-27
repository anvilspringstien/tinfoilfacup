#!/usr/bin/env python3
import argparse, json, re
from pathlib import Path
from datetime import datetime, timezone

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"updater/groundshare-evidence-confirmation-batch2.json"
VERIFY=ROOT/"updater/ground-verification-queue.json"
HTML=ROOT/"clubfinder.html"
LEDGER=ROOT/"updater/ground-approval-ledger.json"
OUT=ROOT/"updater/groundshare-candidate-promotion-batch2.json"
REPORT=ROOT/"groundshare-candidate-promotion-batch2.md"

ap=argparse.ArgumentParser()
ap.add_argument("--publish",action="store_true")
args=ap.parse_args()

def norm(s):
    s=(s or "").lower().replace("&"," and ").replace("’","'")
    s=re.sub(r"\b(fc|afc|cfc|football club)\b"," ",s)
    return re.sub(r"[^a-z0-9]+"," ",s).strip()

def locate_array(text,name):
    m=re.search(r"\b(?:const|let|var)\s+"+re.escape(name)+r"\s*=\s*\[",text)
    if not m: raise SystemExit(f"Could not find {name} array")
    start=text.find("[",m.start()); depth=0; ins=False; esc=False; quote=""
    for i in range(start,len(text)):
        ch=text[i]
        if ins:
            if esc: esc=False
            elif ch=="\\": esc=True
            elif ch==quote: ins=False
        else:
            if ch in ("'",'"'): ins=True; quote=ch
            elif ch=="[": depth+=1
            elif ch=="]":
                depth-=1
                if depth==0:return start,i+1
    raise SystemExit(f"Unbalanced {name} array")

def find_candidate(records,club,postcode):
    hits=[r for r in records if norm(r.get("club"))==norm(club) and (r.get("postcode") or "").upper().strip()==postcode]
    if len(hits)!=1:
        raise SystemExit(f"Safety stop: expected exactly one verification candidate for {club} / {postcode}; found {len(hits)}")
    r=hits[0]
    if r.get("fchd_lat") is None or r.get("fchd_lon") is None:
        raise SystemExit(f"Safety stop: {club} candidate lacks FCHD coordinates")
    if "SHARED_POSTCODE" not in (r.get("flags") or []):
        raise SystemExit(f"Safety stop: {club} candidate is not backed by SHARED_POSTCODE review evidence")
    return r

src=json.loads(SOURCE.read_text(encoding="utf8"))
if src.get("version")!="7.8.6" or src.get("batch")!=2:
    raise SystemExit("Safety stop: unexpected confirmation source/version/batch")
confirmed=src.get("confirmed") or []
rejected=src.get("rejected_not_current") or []
if len(confirmed)!=3 or len(rejected)!=2:
    raise SystemExit("Safety stop: expected exactly 3 confirmed and 2 rejected Batch 2 relationships")
if any(r.get("status")!="HUMAN_CONFIRMED" for r in confirmed):
    raise SystemExit("Safety stop: non-human-confirmed relationship in promotion scope")
if any(r.get("status")!="HUMAN_REJECTED_NOT_CURRENT" for r in rejected):
    raise SystemExit("Safety stop: rejected relationship status changed")
if {r.get("pair_id") for r in confirmed}!={6,7,9}:
    raise SystemExit("Safety stop: only pairs #6, #7 and #9 may be promoted in Batch 2")
if {r.get("pair_id") for r in rejected}!={8,10}:
    raise SystemExit("Safety stop: pairs #8 and #10 must remain rejected/not-current")

directed=[r for r in confirmed if r.get("relationship_type")=="DIRECTED_HOST_TENANT"]
undirected=[r for r in confirmed if r.get("relationship_type")=="CONFIRMED_SHARED_VENUE_UNDIRECTED"]
if len(directed)!=2 or len(undirected)!=1:
    raise SystemExit("Safety stop: expected 2 directed and 1 undirected confirmed relationship")
for r in directed:
    if not r.get("host") or not r.get("tenant") or r["host"] not in r["clubs"] or r["tenant"] not in r["clubs"] or r["host"]==r["tenant"]:
        raise SystemExit(f"Safety stop: invalid host/tenant direction in pair #{r.get('pair_id')}")
for r in undirected:
    if r.get("host") or r.get("tenant"):
        raise SystemExit(f"Safety stop: undirected pair #{r.get('pair_id')} unexpectedly has host/tenant direction")

verification=json.loads(VERIFY.read_text(encoding="utf8")).get("records",[])
text=HTML.read_text(encoding="utf8"); gs,ge=locate_array(text,"GROUNDS"); grounds=json.loads(text[gs:ge])
ledger=json.loads(LEDGER.read_text(encoding="utf8"))
known=ledger.setdefault("known_groundshares",[])
shared=ledger.setdefault("known_shared_venues",[])

def canonical_hits(club):
    return [g for g in grounds if norm(g.get("name") or g.get("club"))==norm(club)]

to_add=[]; existing=[]; plans=[]
for rel in confirmed:
    pc=(rel.get("postcode") or "").upper().strip()
    if not pc or not rel.get("ground") or not rel.get("sources") or not rel.get("evidence_note"):
        raise SystemExit(f"Safety stop: incomplete confirmed relationship #{rel.get('pair_id')}")
    clubplans=[]
    for club in rel["clubs"]:
        c=find_candidate(verification,club,pc)
        hits=canonical_hits(club)
        if len(hits)>1:
            raise SystemExit(f"Safety stop: duplicate canonical records for {club}")
        if hits:
            existing.append(club)
            clubplans.append({"club":club,"state":"ALREADY_CANONICAL"})
        else:
            rec={
              "name":club,"ground":rel["ground"],"postcode":pc,
              "lat":float(c["fchd_lat"]),"lon":float(c["fchd_lon"]),
              "verification":"verified","verification_label":"✅ Verified",
              "source":"Human-confirmed current groundshare + validated ground candidate",
              "ground_source":rel["sources"][0],
              "coordinate_source":"FCHD coordinates; independently checked against Postcodes.io",
              "groundshare_season":"2026-27","groundshare_source":rel["sources"][0]
            }
            if rel["relationship_type"]=="DIRECTED_HOST_TENANT":
                rec["groundshare_host"]=rel["host"] if norm(club)==norm(rel["tenant"]) else ""
                rec["groundshare_tenant"]=rel["tenant"] if norm(club)==norm(rel["host"]) else ""
            else:
                rec["shared_venue_with"]=[x for x in rel["clubs"] if norm(x)!=norm(club)]
                rec["groundshare_direction"]="unresolved"
            to_add.append(rec)
            clubplans.append({"club":club,"state":"READY_TO_ADD","lat":rec["lat"],"lon":rec["lon"]})
    plans.append({"pair_id":rel["pair_id"],"clubs":rel["clubs"],"relationship_type":rel["relationship_type"],"ground":rel["ground"],"postcode":pc,"club_records":clubplans})

ledger_ready=[]
for rel in confirmed:
    pc=rel["postcode"]
    if rel["relationship_type"]=="DIRECTED_HOST_TENANT":
        dup=[x for x in known if norm(x.get("tenant"))==norm(rel["tenant"]) and norm(x.get("host"))==norm(rel["host"]) and (x.get("postcode") or "").upper().strip()==pc]
        if not dup: ledger_ready.append(("directed",rel))
    else:
        target=sorted(norm(x) for x in rel["clubs"])
        dup=[x for x in shared if sorted(norm(y) for y in (x.get("clubs") or []))==target and (x.get("postcode") or "").upper().strip()==pc]
        if not dup: ledger_ready.append(("undirected",rel))

if args.publish:
    now_iso=datetime.now(timezone.utc).isoformat()
    if to_add:
        grounds.extend(to_add)
        HTML.write_text(text[:gs]+json.dumps(grounds,ensure_ascii=False,separators=(",",":"))+text[ge:],encoding="utf8")
    for typ,rel in ledger_ready:
        base={"ground":rel["ground"],"postcode":rel["postcode"],"season":"2026-27","evidence":rel["evidence_note"],"source_url":rel["sources"][0],"approved_at":now_iso,"status":"current","approval_source":"v7.8.6 human confirmation"}
        if typ=="directed":
            known.append({"tenant":rel["tenant"],"host":rel["host"],**base})
        else:
            shared.append({"clubs":rel["clubs"],"relationship_type":"confirmed_shared_venue_undirected",**base})
    ledger["updated_at"]=now_iso
    LEDGER.write_text(json.dumps(ledger,indent=2,ensure_ascii=False)+"\n",encoding="utf8")

now=datetime.now(timezone.utc)
payload={
  "checked_at":now.isoformat(),"version":"7.8.7","batch":2,
  "mode":"PUBLISH" if args.publish else "DRY RUN",
  "confirmed_relationships":3,"directed_relationships":2,"undirected_shared_venues":1,
  "rejected_not_current_relationships":2,
  "canonical_club_records_ready":len(to_add),"existing_canonical_club_records":len(existing),
  "groundshare_ledger_relationships_ready":len(ledger_ready),
  "existing_canonical_records_overwritten":0,"published":bool(args.publish),
  "plans":plans,"rejected_not_current":rejected
}
OUT.write_text(json.dumps(payload,indent=2,ensure_ascii=False)+"\n",encoding="utf8")

L=["# Tin Foil FA Cup — Groundshare Candidate Promotion — Batch 2","",f"Last checked: **{now.strftime('%d/%m/%Y, %H:%M:%S UTC')}**","",f"Mode: **{'PUBLISH' if args.publish else 'DRY RUN'}**","","- Confirmed relationships: **3**","- Directed relationships: **2**","- Undirected shared venues: **1**","- Rejected / not-current relationships excluded: **2**",f"- Canonical club records ready to add: **{len(to_add)}**",f"- Existing canonical club records: **{len(existing)}**",f"- Groundshare ledger relationships ready: **{len(ledger_ready)}**","- Existing canonical records overwritten: **0**",f"- Published: **{'YES' if args.publish else 'NO'}**","","## Promotion plan",""]
for p in plans:
    L += [f"### #{p['pair_id']} — {p['clubs'][0]} ↔ {p['clubs'][1]}","",f"- Relationship: **{p['relationship_type']}**",f"- Venue: **{p['ground']} • {p['postcode']}**"]
    for c in p["club_records"]:
        L.append(f"- **{c['club']}** — {'already canonical' if c['state']=='ALREADY_CANONICAL' else 'ready to add from validated coordinates'}")
    L.append("")
L += ["## Explicitly excluded as not current",""]
for r in rejected:
    L += [f"- **#{r['pair_id']} — {r['clubs'][0]} ↔ {r['clubs'][1]}** — `HUMAN_REJECTED_NOT_CURRENT`; excluded from this and later groundshare promotion. Current venue research points to **{r['current_ground']}**."]
L += ["","## Safety","","- Only v7.8.6 Batch 2 `HUMAN_CONFIRMED` relationships #6, #7 and #9 are eligible.","- Pairs #8 and #10 are hard-excluded because v7.8.6 marks them `HUMAN_REJECTED_NOT_CURRENT`.","- Existing canonical `GROUNDS` records are never overwritten.","- Every missing club requires one matching machine-readable verification candidate with FCHD coordinates and `SHARED_POSTCODE` review evidence.","- Current venue names come from the human-confirmed evidence record; coordinates come from the persisted validated FCHD candidate.","- Directed relationships preserve explicit host/tenant direction.","- Walthamstow FC ↔ West Essex FC remains an undirected shared-venue relationship; no host is invented.","- Ledger and canonical-record counts are calculated from current repository state, not hard-coded.","- Epsom & Ewell FC and Belper United FC current-venue corrections are deliberately left for a separate correction pipeline.","- `competition.json` is untouched."]
REPORT.write_text("\n".join(L)+"\n",encoding="utf8")

print("GROUNDSHARE CANDIDATE PROMOTION v7.8.7 — BATCH 2")
print("Mode:","PUBLISH" if args.publish else "DRY RUN")
print("Confirmed relationships: 3")
print("Directed relationships: 2")
print("Undirected shared venues: 1")
print("Rejected/not-current relationships excluded: 2")
print("Canonical club records ready to add:",len(to_add))
print("Existing canonical club records:",len(existing))
print("Groundshare ledger relationships ready:",len(ledger_ready))
print("Existing canonical records overwritten: 0")
print("Published:","YES" if args.publish else "NO")
print("READY TO PROMOTE:","YES" if (to_add or ledger_ready) else "NOTHING TO ADD")
