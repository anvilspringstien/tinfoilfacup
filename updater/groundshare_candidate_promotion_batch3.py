#!/usr/bin/env python3
import argparse, json, re
from pathlib import Path
from datetime import datetime, timezone

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"updater/groundshare-evidence-confirmation-batch3.json"
VERIFY=ROOT/"updater/ground-verification-queue.json"
HTML=ROOT/"clubfinder.html"
LEDGER=ROOT/"updater/ground-approval-ledger.json"
OUT=ROOT/"updater/groundshare-candidate-promotion-batch3.json"
REPORT=ROOT/"groundshare-candidate-promotion-batch3.md"

ap=argparse.ArgumentParser(); ap.add_argument("--publish",action="store_true"); args=ap.parse_args()

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
    if len(hits)!=1: raise SystemExit(f"Safety stop: expected exactly one verification candidate for {club} / {postcode}; found {len(hits)}")
    r=hits[0]
    if r.get("fchd_lat") is None or r.get("fchd_lon") is None: raise SystemExit(f"Safety stop: {club} candidate lacks FCHD coordinates")
    if "SHARED_POSTCODE" not in (r.get("flags") or []): raise SystemExit(f"Safety stop: {club} candidate is not backed by SHARED_POSTCODE review evidence")
    return r

src=json.loads(SOURCE.read_text(encoding="utf8"))
if src.get("version")!="7.8.9" or src.get("batch")!=3: raise SystemExit("Safety stop: unexpected confirmation source/version/batch")
confirmed=src.get("confirmed") or []; rejected=src.get("rejected_not_current") or []
if len(confirmed)!=4 or len(rejected)!=1: raise SystemExit("Safety stop: expected exactly 4 confirmed and 1 rejected Batch 3 relationships")
if {r.get("pair_id") for r in confirmed}!={11,12,13,15}: raise SystemExit("Safety stop: only pairs #11, #12, #13 and #15 may be promoted in Batch 3")
if {r.get("pair_id") for r in rejected}!={14}: raise SystemExit("Safety stop: pair #14 must remain rejected/not-current")
if any(r.get("status")!="HUMAN_CONFIRMED" or r.get("relationship_type")!="DIRECTED_HOST_TENANT" for r in confirmed): raise SystemExit("Safety stop: Batch 3 promotion requires four directed HUMAN_CONFIRMED relationships")
if any(r.get("status")!="HUMAN_REJECTED_NOT_CURRENT" for r in rejected): raise SystemExit("Safety stop: rejected relationship status changed")
for r in confirmed:
    if not r.get("host") or not r.get("tenant") or r["host"] not in r["clubs"] or r["tenant"] not in r["clubs"] or r["host"]==r["tenant"]: raise SystemExit(f"Safety stop: invalid host/tenant direction in pair #{r.get('pair_id')}")

verification=json.loads(VERIFY.read_text(encoding="utf8")).get("records",[])
text=HTML.read_text(encoding="utf8"); gs,ge=locate_array(text,"GROUNDS"); grounds=json.loads(text[gs:ge])
ledger=json.loads(LEDGER.read_text(encoding="utf8")); known=ledger.setdefault("known_groundshares",[])

def canonical_hits(club): return [g for g in grounds if norm(g.get("name") or g.get("club"))==norm(club)]

to_add=[]; existing=[]; plans=[]
for rel in confirmed:
    pc=(rel.get("postcode") or "").upper().strip()
    if not pc or not rel.get("ground") or not rel.get("sources") or not rel.get("evidence_note"): raise SystemExit(f"Safety stop: incomplete confirmed relationship #{rel.get('pair_id')}")
    clubplans=[]
    for club in rel["clubs"]:
        c=find_candidate(verification,club,pc); hits=canonical_hits(club)
        if len(hits)>1: raise SystemExit(f"Safety stop: duplicate canonical records for {club}")
        if hits:
            existing.append(club); clubplans.append({"club":club,"state":"ALREADY_CANONICAL"})
        else:
            rec={"name":club,"ground":rel["ground"],"postcode":pc,"lat":float(c["fchd_lat"]),"lon":float(c["fchd_lon"]),"verification":"verified","verification_label":"✅ Verified","source":"Human-confirmed current groundshare + validated ground candidate","ground_source":rel["sources"][0],"coordinate_source":"FCHD coordinates; independently checked against Postcodes.io","groundshare_season":"2026-27","groundshare_source":rel["sources"][0]}
            rec["groundshare_host"]=rel["host"] if norm(club)==norm(rel["tenant"]) else ""
            rec["groundshare_tenant"]=rel["tenant"] if norm(club)==norm(rel["host"]) else ""
            to_add.append(rec); clubplans.append({"club":club,"state":"READY_TO_ADD","lat":rec["lat"],"lon":rec["lon"]})
    plans.append({"pair_id":rel["pair_id"],"clubs":rel["clubs"],"relationship_type":rel["relationship_type"],"ground":rel["ground"],"postcode":pc,"club_records":clubplans})

ledger_ready=[]
for rel in confirmed:
    dup=[x for x in known if norm(x.get("tenant"))==norm(rel["tenant"]) and norm(x.get("host"))==norm(rel["host"]) and (x.get("postcode") or "").upper().strip()==rel["postcode"]]
    if not dup: ledger_ready.append(rel)

if args.publish:
    now_iso=datetime.now(timezone.utc).isoformat()
    if to_add:
        grounds.extend(to_add); HTML.write_text(text[:gs]+json.dumps(grounds,ensure_ascii=False,separators=(",",":"))+text[ge:],encoding="utf8")
    for rel in ledger_ready:
        known.append({"tenant":rel["tenant"],"host":rel["host"],"ground":rel["ground"],"postcode":rel["postcode"],"season":"2026-27","evidence":rel["evidence_note"],"source_url":rel["sources"][0],"approved_at":now_iso,"status":"current","approval_source":"v7.8.9 human confirmation"})
    ledger["updated_at"]=now_iso; LEDGER.write_text(json.dumps(ledger,indent=2,ensure_ascii=False)+"\n",encoding="utf8")

now=datetime.now(timezone.utc)
payload={"checked_at":now.isoformat(),"version":"7.9.0","batch":3,"mode":"PUBLISH" if args.publish else "DRY RUN","confirmed_relationships":4,"directed_relationships":4,"undirected_shared_venues":0,"rejected_not_current_relationships":1,"canonical_club_records_ready":len(to_add),"existing_canonical_club_records":len(existing),"groundshare_ledger_relationships_ready":len(ledger_ready),"existing_canonical_records_overwritten":0,"published":bool(args.publish),"plans":plans,"rejected_not_current":rejected}
OUT.write_text(json.dumps(payload,indent=2,ensure_ascii=False)+"\n",encoding="utf8")
L=["# Tin Foil FA Cup — Groundshare Candidate Promotion — Batch 3","",f"Last checked: **{now.strftime('%d/%m/%Y, %H:%M:%S UTC')}**","",f"Mode: **{'PUBLISH' if args.publish else 'DRY RUN'}**","","- Confirmed relationships: **4**","- Directed relationships: **4**","- Undirected shared venues: **0**","- Rejected / not-current relationships excluded: **1**",f"- Canonical club records ready to add: **{len(to_add)}**",f"- Existing canonical club records: **{len(existing)}**",f"- Groundshare ledger relationships ready: **{len(ledger_ready)}**","- Existing canonical records overwritten: **0**",f"- Published: **{'YES' if args.publish else 'NO'}**","","## Promotion plan",""]
for p in plans:
    L += [f"### #{p['pair_id']} — {p['clubs'][0]} ↔ {p['clubs'][1]}","",f"- Relationship: **{p['relationship_type']}**",f"- Venue: **{p['ground']} • {p['postcode']}**"]
    for c in p["club_records"]: L.append(f"- **{c['club']}** — {'already canonical' if c['state']=='ALREADY_CANONICAL' else 'ready to add from validated coordinates'}")
    L.append("")
L += ["## Explicitly excluded as not current","",f"- **#14 — {rejected[0]['clubs'][0]} ↔ {rejected[0]['clubs'][1]}** — `HUMAN_REJECTED_NOT_CURRENT`; excluded from this and later groundshare promotion. Current venue research points to **{rejected[0]['current_ground']}**.","","## Safety","","- Only v7.8.9 Batch 3 `HUMAN_CONFIRMED` relationships #11, #12, #13 and #15 are eligible.","- Pair #14 is hard-excluded because v7.8.9 marks it `HUMAN_REJECTED_NOT_CURRENT`.","- Existing canonical `GROUNDS` records are never overwritten.","- Every missing club requires one matching machine-readable verification candidate with FCHD coordinates and `SHARED_POSTCODE` review evidence.","- Current venue names come from the human-confirmed evidence record; coordinates come from the persisted validated FCHD candidate.","- All four promoted relationships preserve explicit host/tenant direction.","- Ledger and canonical-record counts are calculated from current repository state, not hard-coded.","- Southall FC's Honeycroft current-venue correction is deliberately left for a separate correction pipeline.","- `competition.json` is untouched."]
REPORT.write_text("\n".join(L)+"\n",encoding="utf8")
print("GROUNDSHARE CANDIDATE PROMOTION v7.9.0 — BATCH 3")
print("Mode:","PUBLISH" if args.publish else "DRY RUN")
print("Confirmed relationships: 4"); print("Directed relationships: 4"); print("Undirected shared venues: 0"); print("Rejected/not-current relationships excluded: 1")
print("Canonical club records ready to add:",len(to_add)); print("Existing canonical club records:",len(existing)); print("Groundshare ledger relationships ready:",len(ledger_ready)); print("Existing canonical records overwritten: 0"); print("Published:","YES" if args.publish else "NO"); print("READY TO PROMOTE:","YES" if (to_add or ledger_ready) else "NOTHING TO ADD")
