#!/usr/bin/env python3
import argparse, json, re
from pathlib import Path
from datetime import datetime, timezone

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"updater/groundshare-evidence-confirmation-batch1.json"
VERIFY=ROOT/"updater/ground-verification-queue.json"
HTML=ROOT/"clubfinder.html"
LEDGER=ROOT/"updater/ground-approval-ledger.json"
OUT=ROOT/"updater/groundshare-candidate-promotion-batch1.json"
REPORT=ROOT/"groundshare-candidate-promotion-batch1.md"

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
                if depth==0: return start,i+1
    raise SystemExit(f"Unbalanced {name} array")

def find_candidate(records,club,postcode):
    hits=[r for r in records if norm(r.get("club"))==norm(club) and (r.get("postcode") or "").upper().strip()==postcode]
    if len(hits)!=1: raise SystemExit(f"Safety stop: expected exactly one verification candidate for {club} / {postcode}; found {len(hits)}")
    r=hits[0]
    if r.get("fchd_lat") is None or r.get("fchd_lon") is None: raise SystemExit(f"Safety stop: {club} candidate lacks coordinates")
    if "SHARED_POSTCODE" not in (r.get("flags") or []): raise SystemExit(f"Safety stop: {club} candidate is not SHARED_POSTCODE validated/reviewed data")
    return r

src=json.loads(SOURCE.read_text(encoding="utf8"))
if src.get("version")!="7.8.3" or src.get("batch")!=1: raise SystemExit("Safety stop: unexpected confirmation source/version/batch")
confirmed=src.get("confirmed") or []; held=src.get("held") or []
if len(confirmed)!=4 or len(held)!=1: raise SystemExit("Safety stop: expected exactly 4 confirmed and 1 held Batch 1 relationship")
if any(r.get("status")!="HUMAN_CONFIRMED" for r in confirmed): raise SystemExit("Safety stop: non-human-confirmed relationship in promotion scope")
if held[0].get("pair_id")!=1 or held[0].get("status")!="HELD_FOR_MORE_EVIDENCE": raise SystemExit("Safety stop: Romulus/Sutton Coldfield hold boundary changed")

directed=[r for r in confirmed if r.get("relationship_type")=="DIRECTED_HOST_TENANT"]
undirected=[r for r in confirmed if r.get("relationship_type")=="CONFIRMED_SHARED_VENUE_UNDIRECTED"]
if len(directed)!=3 or len(undirected)!=1: raise SystemExit("Safety stop: expected 3 directed and 1 undirected relationship")
for r in directed:
    if not r.get("host") or not r.get("tenant") or r["host"] not in r["clubs"] or r["tenant"] not in r["clubs"]: raise SystemExit(f"Safety stop: invalid direction pair #{r.get('pair_id')}")
for r in undirected:
    if r.get("host") or r.get("tenant"): raise SystemExit("Safety stop: undirected shared venue unexpectedly has host/tenant")

verification=json.loads(VERIFY.read_text(encoding="utf8")).get("records",[])
text=HTML.read_text(encoding="utf8"); gs,ge=locate_array(text,"GROUNDS"); grounds=json.loads(text[gs:ge])
ledger=json.loads(LEDGER.read_text(encoding="utf8"))
known=ledger.setdefault("known_groundshares",[])
shared=ledger.setdefault("known_shared_venues",[])

def canonical_hits(club): return [g for g in grounds if norm(g.get("name") or g.get("club"))==norm(club)]

to_add=[]; existing=[]; plans=[]
for rel in confirmed:
    pc=(rel.get("postcode") or "").upper().strip()
    if not pc or not rel.get("ground") or not rel.get("sources") or not rel.get("evidence_note"): raise SystemExit(f"Safety stop: incomplete confirmed relationship #{rel.get('pair_id')}")
    clubplans=[]
    for club in rel["clubs"]:
        c=find_candidate(verification,club,pc)
        hits=canonical_hits(club)
        if len(hits)>1: raise SystemExit(f"Safety stop: duplicate canonical records for {club}")
        if hits:
            existing.append(club); clubplans.append({"club":club,"state":"ALREADY_CANONICAL"})
        else:
            rec={"name":club,"ground":rel["ground"],"postcode":pc,"lat":float(c["fchd_lat"]),"lon":float(c["fchd_lon"]),"verification":"verified","verification_label":"✅ Verified","source":"Human-confirmed current groundshare + validated ground candidate","ground_source":c.get("source") or "FCHD 2025-26 Gazetteer","coordinate_source":"FCHD coordinates; independently checked against Postcodes.io","groundshare_season":"2026-27","groundshare_source":rel["sources"][0]}
            if rel["relationship_type"]=="DIRECTED_HOST_TENANT":
                rec["groundshare_host"]=rel["host"] if norm(club)==norm(rel["tenant"]) else ""
                rec["groundshare_tenant"]=rel["tenant"] if norm(club)==norm(rel["host"]) else ""
            else:
                rec["shared_venue_with"]=[x for x in rel["clubs"] if norm(x)!=norm(club)]
                rec["groundshare_direction"]="unresolved"
            to_add.append(rec); clubplans.append({"club":club,"state":"READY_TO_ADD","lat":rec["lat"],"lon":rec["lon"]})
    plans.append({"pair_id":rel["pair_id"],"clubs":rel["clubs"],"relationship_type":rel["relationship_type"],"ground":rel["ground"],"postcode":pc,"club_records":clubplans})

ledger_ready=[]
for rel in confirmed:
    pc=rel["postcode"]
    if rel["relationship_type"]=="DIRECTED_HOST_TENANT":
        dup=[x for x in known if norm(x.get("tenant"))==norm(rel["tenant"]) and norm(x.get("host"))==norm(rel["host"]) and (x.get("postcode") or "").upper()==pc]
        if not dup: ledger_ready.append(("directed",rel))
    else:
        target=sorted(norm(x) for x in rel["clubs"])
        dup=[x for x in shared if sorted(norm(y) for y in (x.get("clubs") or []))==target and (x.get("postcode") or "").upper()==pc]
        if not dup: ledger_ready.append(("undirected",rel))

if args.publish:
    now=datetime.now(timezone.utc).isoformat()
    if to_add:
        grounds.extend(to_add)
        HTML.write_text(text[:gs]+json.dumps(grounds,ensure_ascii=False,separators=(",",":"))+text[ge:],encoding="utf8")
    for typ,rel in ledger_ready:
        base={"ground":rel["ground"],"postcode":rel["postcode"],"season":"2026-27","evidence":rel["evidence_note"],"source_url":rel["sources"][0],"approved_at":now,"status":"current","approval_source":"v7.8.3 human confirmation"}
        if typ=="directed": known.append({"tenant":rel["tenant"],"host":rel["host"],**base})
        else: shared.append({"clubs":rel["clubs"],"relationship_type":"confirmed_shared_venue_undirected",**base})
    ledger["updated_at"]=now
    LEDGER.write_text(json.dumps(ledger,indent=2,ensure_ascii=False)+"\n",encoding="utf8")

now=datetime.now(timezone.utc)
payload={"checked_at":now.isoformat(),"version":"7.8.4","batch":1,"mode":"PUBLISH" if args.publish else "DRY RUN","confirmed_relationships":4,"directed_relationships":3,"undirected_shared_venues":1,"canonical_club_records_ready":len(to_add),"existing_canonical_club_records":len(existing),"groundshare_ledger_relationships_ready":len(ledger_ready),"held_relationships":1,"existing_canonical_records_overwritten":0,"published":bool(args.publish),"plans":plans,"held":held}
OUT.write_text(json.dumps(payload,indent=2,ensure_ascii=False)+"\n",encoding="utf8")
L=["# Tin Foil FA Cup — Groundshare Candidate Promotion — Batch 1","",f"Last checked: **{now.strftime('%d/%m/%Y, %H:%M:%S UTC')}**","",f"Mode: **{'PUBLISH' if args.publish else 'DRY RUN'}**","","- Confirmed relationships: **4**","- Directed relationships: **3**","- Undirected shared venues: **1**",f"- Canonical club records ready to add: **{len(to_add)}**",f"- Existing canonical club records: **{len(existing)}**",f"- Groundshare ledger relationships ready: **{len(ledger_ready)}**","- Held relationships: **1**","- Existing canonical records overwritten: **0**",f"- Published: **{'YES' if args.publish else 'NO'}**","","## Promotion plan",""]
for p in plans:
    L += [f"### #{p['pair_id']} — {p['clubs'][0]} ↔ {p['clubs'][1]}","",f"- Relationship: **{p['relationship_type']}**",f"- Venue: **{p['ground']} • {p['postcode']}**"]
    for c in p["club_records"]: L.append(f"- **{c['club']}** — {'already canonical' if c['state']=='ALREADY_CANONICAL' else 'ready to add from validated coordinates'}")
    L.append("")
L += ["## Held","",f"- **{held[0]['clubs'][0]} ↔ {held[0]['clubs'][1]}** — remains HELD_FOR_MORE_EVIDENCE; not promotion-eligible.","","## Safety","","- Only v7.8.3 `HUMAN_CONFIRMED` Batch 1 relationships are eligible.","- Romulus FC ↔ Sutton Coldfield Town FC remains excluded.","- Existing canonical `GROUNDS` records are never overwritten.","- Every missing club requires one matching machine-readable verification candidate with FCHD coordinates and `SHARED_POSTCODE` evidence.","- Directed relationships preserve explicit host/tenant direction.","- Soul Tower Hamlets FC ↔ Sporting Bengal United FC remains an undirected shared-venue relationship; no host is invented.","- Ledger counts and canonical-record counts are calculated from current repository state, not hard-coded.","- `competition.json` is untouched."]
REPORT.write_text("\n".join(L)+"\n",encoding="utf8")
print("GROUNDSHARE CANDIDATE PROMOTION v7.8.4 — BATCH 1")
print("Mode:","PUBLISH" if args.publish else "DRY RUN")
print("Confirmed relationships: 4")
print("Directed relationships: 3")
print("Undirected shared venues: 1")
print("Canonical club records ready to add:",len(to_add))
print("Existing canonical club records:",len(existing))
print("Groundshare ledger relationships ready:",len(ledger_ready))
print("Held relationships: 1")
print("Existing canonical records overwritten: 0")
print("Published:","YES" if args.publish else "NO")
print("READY TO PROMOTE:","YES" if (to_add or ledger_ready) else "NOTHING TO ADD")
