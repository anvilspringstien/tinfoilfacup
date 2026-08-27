#!/usr/bin/env python3
import json,re
from pathlib import Path
from datetime import datetime,timezone

ROOT=Path(__file__).resolve().parents[1]
HTML=ROOT/"clubfinder.html"
QUEUE=ROOT/"updater/current-venue-correction-queue.json"
OUT=ROOT/"updater/current-venue-validation.json"
REPORT=ROOT/"current-venue-validation.md"

if not HTML.exists() or not QUEUE.exists(): raise SystemExit("Missing clubfinder.html or v7.9.1 correction queue.")
q=json.loads(QUEUE.read_text(encoding="utf8"))
if q.get("version")!="7.9.1" or q.get("queue_items")!=7 or q.get("published_canonical_records")!=0:
    raise SystemExit("Safety stop: unexpected correction queue source/state.")
held=q.get("held") or []
if len(held)!=1 or held[0].get("clubs") != ["Romulus FC","Sutton Coldfield Town FC"] or held[0].get("status")!="HELD_FOR_MORE_EVIDENCE":
    raise SystemExit("Safety stop: held relationship drift.")

def norm(s):
    s=(s or "").lower().replace("&"," and ").replace("’","'")
    s=re.sub(r"\b(fc|afc|cfc|football club)\b"," ",s)
    return re.sub(r"[^a-z0-9]+"," ",s).strip()

def locate(text,name):
    m=re.search(r"\b(?:const|let|var)\s+"+re.escape(name)+r"\s*=\s*\[",text)
    if not m: raise SystemExit("Could not find "+name)
    s=text.find("[",m.start()); d=0; ins=False; esc=False; quote=""
    for i in range(s,len(text)):
        c=text[i]
        if ins:
            if esc: esc=False
            elif c=="\\": esc=True
            elif c==quote: ins=False
        else:
            if c in ("'",'\"'): ins=True; quote=c
            elif c=="[": d+=1
            elif c=="]":
                d-=1
                if d==0:return s,i+1
    raise SystemExit("Unbalanced "+name)

TARGETS=[
 {"club":"Epsom & Ewell FC","action":"changed_groundshare","host":"Chessington & Hook United FC","ground":"Chalky Lane","postcode":"KT9 2NF","lat":51.346952,"lon":-0.306908,"source":"https://epsomandewellfc.co.uk/club/visiting-us/","coordinate_source":"Open Postcode Geo / KT9 2NF"},
 {"club":"Belper United FC","action":"changed_groundshare","host":"Mickleover FC","ground":"Don Amott Arena","postcode":"DE3 9FB","lat":52.921171,"lon":-1.541750,"source":"https://belperunited.co.uk/contact-us/","coordinate_source":"Open Postcode Geo / DE3 9FB"},
 {"club":"Southall FC","action":"changed_groundshare","host":"Uxbridge FC","ground":"Honeycroft","postcode":"UB7 8HX","lat":51.512049,"lon":-0.457664,"source":"https://www.southallfc.com/contact","coordinate_source":"Open Postcode Geo / UB7 8HX"},
 {"club":"Cobham FC","action":"independent_current_ground","ground":"The Reg Madgwick Stadium","postcode":"KT11 3EP","lat":51.329238,"lon":-0.412258,"source":"https://www.cobhamfootballclub.com/contact","coordinate_source":"Open Postcode Geo / KT11 3EP"},
 {"club":"Eastwood Community FC","action":"independent_current_ground","ground":"Coronation Park","postcode":"NG16 3HB","lat":53.013570,"lon":-1.296344,"source":"https://www.eastwoodcfc.co.uk/contact","coordinate_source":"Open Postcode Geo / NG16 3HB"},
 {"club":"Hayes & Yeading United FC","action":"independent_current_ground","ground":"The SkyEx Community Stadium","postcode":"UB4 0SL","lat":51.509788,"lon":-0.395011,"source":"https://hyufc.ktckts.com/contactus","coordinate_source":"Open Postcode Geo / UB4 0SL"},
 {"club":"Corby Town FC","action":"independent_current_ground","ground":"Steel Park","postcode":"NN17 2AE","lat":52.506286,"lon":-0.705086,"source":"https://www.corbytown.co.uk/a/steel-park-49382.html?page=2","coordinate_source":"Open Postcode Geo / NN17 2AE"},
]

text=HTML.read_text(encoding="utf8")
gs,ge=locate(text,"GROUNDS"); grounds=json.loads(text[gs:ge])
es,ee=locate(text,"ELIGIBLE"); eligible=json.loads(text[es:ee])
eligible_names={norm(x.get("name")):x.get("name") for x in eligible if x.get("name")}
rows=[]
for t in TARGETS:
    key=norm(t["club"]); matches=[g for g in grounds if norm(g.get("name") or g.get("club"))==key]
    current=None
    if len(matches)==1:
        g=matches[0]; current={k:g.get(k) for k in ("name","club","ground","postcode","lat","lon","verification","verification_label","source","ground_source","coordinate_source") if k in g}
        current_pc=(g.get("postcode") or "").upper().strip()
        state="CANONICAL_PRESENT"
        pc_change=current_pc!=t["postcode"]
        ground_change=norm(g.get("ground"))!=norm(t["ground"])
    elif len(matches)==0:
        state="CANONICAL_MISSING"; pc_change=None; ground_change=None
    else:
        state="MULTIPLE_CANONICAL_MATCHES"; pc_change=None; ground_change=None
    rows.append({**t,"eligible_display_name":eligible_names.get(key),"canonical_match_count":len(matches),"canonical_state":state,"current":current,"postcode_change":pc_change,"ground_change":ground_change,"target_coordinates_kind":"postcode_centroid_candidate","publish_ready_after_human_confirmation":state in ("CANONICAL_PRESENT","CANONICAL_MISSING") and key in eligible_names})

if len(rows)!=7: raise SystemExit("Safety stop: validation must contain exactly seven records.")
now=datetime.now(timezone.utc); missing=sum(r["canonical_state"]=="CANONICAL_MISSING" for r in rows); present=sum(r["canonical_state"]=="CANONICAL_PRESENT" for r in rows); multiple=sum(r["canonical_state"]=="MULTIPLE_CANONICAL_MATCHES" for r in rows)
payload={"checked_at":now.isoformat(),"version":"7.9.2","mode":"VALIDATION ONLY / NO CANONICAL WRITE","source_queue_version":"7.9.1","records_checked":7,"canonical_present":present,"canonical_missing":missing,"multiple_matches":multiple,"canonical_records_changed":0,"held_relationships_unchanged":1,"items":rows,"held":held}
OUT.write_text(json.dumps(payload,indent=2,ensure_ascii=False)+"\n",encoding="utf8")
L=["# Tin Foil FA Cup — Current Venue Validation","",f"Last checked: **{now.strftime('%d/%m/%Y, %H:%M:%S UTC')}**","","**v7.9.2 VALIDATION ONLY. No canonical GROUNDS record, approval ledger, `clubfinder.html`, or `competition.json` is changed.**","",f"- Units checked: **7**",f"- Canonical records present: **{present}**",f"- Canonical records missing: **{missing}**",f"- Multiple canonical matches: **{multiple}**","- Canonical records changed: **0**","- Held relationships changed: **0**","","## Canonical comparison",""]
for r in rows:
    c=r["current"] or {}
    cur=(f"**{c.get('ground','(blank)')} • {c.get('postcode','(blank)')}** • `{c.get('lat','?')}, {c.get('lon','?')}`" if c else "**NO CANONICAL GROUNDS RECORD**")
    L += [f"### {r['club']}","",f"- State: `{r['canonical_state']}`",f"- Eligible display name: **{r['eligible_display_name'] or 'NOT FOUND'}**",f"- Action: `{r['action']}`",f"- Current canonical: {cur}",f"- Validated target: **{r['ground']} • {r['postcode']}** • `{r['lat']}, {r['lon']}`",f"- Postcode change required: **{('YES' if r['postcode_change'] else 'NO') if r['postcode_change'] is not None else 'N/A — canonical missing/ambiguous'}**",f"- Ground-name change required: **{('YES' if r['ground_change'] else 'NO') if r['ground_change'] is not None else 'N/A — canonical missing/ambiguous'}**",f"- Venue evidence: {r['source']}",f"- Coordinate basis: {r['coordinate_source']} (postcode centroid candidate)",""]
L += ["## Held outside scope","","- **Romulus FC ↔ Sutton Coldfield Town FC** remains `HELD_FOR_MORE_EVIDENCE` and is not validated, corrected, approved or published by this stage.","","## Safety","","- v7.9.1 must still contain exactly seven queue units and zero published canonical records.","- Missing canonical records are reported, never silently created by this validation stage.","- Multiple canonical matches are reported and block automatic promotion for that club.","- The three stale relationships #8/#10/#14 are not revived.","- Postcode-centroid candidates are not silently substituted for existing exact ground coordinates when the postcode is unchanged.","- This stage writes only the validation JSON/report."]
REPORT.write_text("\n".join(L)+"\n",encoding="utf8")
print("CURRENT VENUE VALIDATION v7.9.2"); print("Units checked: 7"); print("Canonical present:",present); print("Canonical missing:",missing); print("Multiple matches:",multiple); print("Canonical records changed: 0")
for r in rows:
    c=r['current'] or {}; print(f"{r['club']}: {r['canonical_state']} | {c.get('ground','-')} / {c.get('postcode','-')} -> {r['ground']} / {r['postcode']}")
print("Romulus/Sutton Coldfield: HELD, untouched"); print("VALIDATION ONLY / NO CANONICAL WRITE")
