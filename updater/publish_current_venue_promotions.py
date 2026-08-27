#!/usr/bin/env python3
import json,re
from pathlib import Path
from datetime import datetime,timezone

ROOT=Path(__file__).resolve().parents[1]
HTML=ROOT/"clubfinder.html"
VALIDATION=ROOT/"updater/current-venue-validation.json"
LEDGER=ROOT/"updater/ground-approval-ledger.json"
OUT=ROOT/"updater/current-venue-promotion.json"
REPORT=ROOT/"current-venue-promotion.md"

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

if not (HTML.exists() and VALIDATION.exists() and LEDGER.exists()):
    raise SystemExit("Missing clubfinder.html, v7.9.2 validation, or approval ledger.")
v=json.loads(VALIDATION.read_text(encoding="utf8"))
if v.get("version")!="7.9.2" or v.get("records_checked")!=7 or v.get("canonical_present")!=0 or v.get("canonical_missing")!=7 or v.get("multiple_matches")!=0 or v.get("canonical_records_changed")!=0:
    raise SystemExit("Safety stop: v7.9.2 validation is not the expected seven-missing-record state.")
held=v.get("held") or []
if len(held)!=1 or held[0].get("clubs") != ["Romulus FC","Sutton Coldfield Town FC"] or held[0].get("status")!="HELD_FOR_MORE_EVIDENCE":
    raise SystemExit("Safety stop: held relationship drift.")

# Venue-level coordinates are preferred over postcode centroids.
# FCHD ground coordinates are used where available; Don Amott Arena uses the
# OpenStreetMap pitch location because the older FCHD longitude is inconsistent
# with the current venue/postcode location.
TARGETS=[
 {"name":"Epsom & Ewell FC","ground":"Chalky Lane","postcode":"KT9 2NF","lat":51.350284,"lon":-0.309281,"source":"https://epsomandewellfc.co.uk/club/visiting-us/","ground_source":"Official club current venue; Chessington & Hook United ground mapping","coordinate_source":"FCHD mapped Chessington & Hook United/Chalky Lane ground coordinate"},
 {"name":"Belper United FC","ground":"Don Amott Arena","postcode":"DE3 9FB","lat":52.92371,"lon":-1.54045,"source":"https://belperunited.co.uk/contact-us/","ground_source":"Official club current venue at Mickleover FC","coordinate_source":"OpenStreetMap pitch mapping for Don Amott Arena"},
 {"name":"Southall FC","ground":"Honeycroft","postcode":"UB7 8HX","lat":51.514078,"lon":-0.457668,"source":"https://www.southallfc.com/contact","ground_source":"Official club current venue; Uxbridge FC host","coordinate_source":"FCHD mapped Uxbridge/Honeycroft ground coordinate"},
 {"name":"Cobham FC","ground":"The Reg Madgwick Stadium","postcode":"KT11 3EP","lat":51.329232,"lon":-0.416391,"source":"https://www.cobhamfootballclub.com/contact","ground_source":"Official club current venue/postcode","coordinate_source":"FCHD/ground mapping coordinate for Reg Madgwick Stadium"},
 {"name":"Eastwood Community FC","ground":"Coronation Park","postcode":"NG16 3HB","lat":53.01484,"lon":-1.29749,"source":"https://www.eastwoodcfc.co.uk/contact","ground_source":"Official club current venue/postcode","coordinate_source":"FCHD mapped Coronation Park ground coordinate"},
 {"name":"Hayes & Yeading United FC","ground":"The SkyEx Community Stadium","postcode":"UB4 0SL","lat":51.508276,"lon":-0.394797,"source":"https://hyufc.ktckts.com/contactus","ground_source":"Official club current venue/postcode","coordinate_source":"FCHD mapped SkyEx Community Stadium ground coordinate"},
 {"name":"Corby Town FC","ground":"Steel Park","postcode":"NN17 2AE","lat":52.506582,"lon":-0.718515,"source":"https://www.corbytown.co.uk/a/steel-park-49382.html?page=2","ground_source":"Official club stadium page/current venue/postcode","coordinate_source":"FCHD 2025-26 mapped Steel Park ground coordinate"},
]
RELATIONSHIPS=[
 {"tenant":"Epsom & Ewell FC","host":"Chessington & Hook United FC","ground":"Chalky Lane","postcode":"KT9 2NF","season":"2026-27","evidence":"Epsom & Ewell's current official venue information places its first team at Chalky Lane for 2026/27; this is a new/current relationship and does not revive rejected former pair #8 with Cobham.","source_url":"https://epsomandewellfc.co.uk/club/visiting-us/"},
 {"tenant":"Belper United FC","host":"Mickleover FC","ground":"Don Amott Arena","postcode":"DE3 9FB","season":"2026-27","evidence":"Belper United's current official contact information gives the Don Amott Arena, home of Mickleover FC, as its ground; this replaces the rejected former Eastwood relationship #10.","source_url":"https://belperunited.co.uk/contact-us/"},
 {"tenant":"Southall FC","host":"Uxbridge FC","ground":"Honeycroft","postcode":"UB7 8HX","season":"2026-27","evidence":"Southall's current official site gives Honeycroft as its home and the 2026/27 move was explicitly announced as a groundshare with Uxbridge; this does not revive rejected former pair #14 with Hayes & Yeading United.","source_url":"https://www.southallfc.com/contact"},
]

text=HTML.read_text(encoding="utf8"); gs,ge=locate(text,"GROUNDS"); grounds=json.loads(text[gs:ge]); es,ee=locate(text,"ELIGIBLE"); eligible=json.loads(text[es:ee])
eligible_names={norm(x.get("name")):x.get("name") for x in eligible if x.get("name")}
existing={norm(g.get("name") or g.get("club")):g for g in grounds if norm(g.get("name") or g.get("club"))}
new=[]
for t in TARGETS:
    key=norm(t["name"])
    if key not in eligible_names: raise SystemExit(f"Safety stop: {t['name']} is no longer in ELIGIBLE.")
    if key in existing: raise SystemExit(f"Safety stop: canonical GROUNDS record appeared for {t['name']} after validation; rerun validation instead of overwriting.")
    new.append({"name":eligible_names[key],"ground":t["ground"],"postcode":t["postcode"],"lat":t["lat"],"lon":t["lon"],"verification":"verified","verification_label":"✅ Verified","source":"Current 2026/27 venue evidence: "+t["source"],"ground_source":t["ground_source"],"coordinate_source":t["coordinate_source"]})
if len(new)!=7: raise SystemExit("Safety stop: exactly seven new canonical records required.")

# Add canonical records deterministically; no existing canonical record is overwritten.
new_grounds=grounds+sorted(new,key=lambda x:x["name"].lower())
HTML.write_text(text[:gs]+json.dumps(new_grounds,ensure_ascii=False,separators=(",",":"))+text[ge:],encoding="utf8")

# Preserve the complete ledger, including known_shared_venues and any future fields.
ledger=json.loads(LEDGER.read_text(encoding="utf8")); now=datetime.now(timezone.utc).isoformat(); known=ledger.get("known_groundshares") or []
for r in RELATIONSHIPS:
    entry={**r,"approved_at":now,"status":"current","approval_source":"v7.9.3 current venue promotion after v7.9.2 validation"}
    known=[x for x in known if norm(x.get("tenant"))!=norm(r["tenant"])] + [entry]
ledger["known_groundshares"]=known; ledger["version"]="7.9.3"; ledger["updated_at"]=now
LEDGER.write_text(json.dumps(ledger,indent=2,ensure_ascii=False)+"\n",encoding="utf8")

payload={"published_at":now,"version":"7.9.3","mode":"PUBLISHED / SAFE MISSING-CANONICAL PROMOTION","source_validation":"7.9.2","canonical_records_added":7,"existing_canonical_records_overwritten":0,"current_groundshares_recorded":3,"held_relationships_changed":0,"records":new,"relationships":RELATIONSHIPS,"held":held,"competition_json_changed":False}
OUT.write_text(json.dumps(payload,indent=2,ensure_ascii=False)+"\n",encoding="utf8")
L=["# Tin Foil FA Cup — Current Venue Promotion","",f"Published: **{datetime.now(timezone.utc).strftime('%d/%m/%Y, %H:%M:%S UTC')}**","","**v7.9.3 SAFE PROMOTION — based on v7.9.2 validation showing all seven eligible clubs had no canonical GROUNDS record.**","","- New canonical verified records: **7**","- Existing canonical records overwritten: **0**","- Current groundshare relationships recorded: **3**","- Held relationships changed: **0**","- `competition.json` changed: **NO**","","## Published canonical records",""]
for g in new:L.append(f"- **{g['name']}** — {g['ground']} • {g['postcode']} • `{g['lat']}, {g['lon']}`")
L += ["","## Current groundshares recorded",""]
for r in RELATIONSHIPS:L.append(f"- **{r['tenant']}** → {r['host']} • {r['ground']} • {r['postcode']} • {r['season']}")
L += ["","## Held outside scope","","- **Romulus FC ↔ Sutton Coldfield Town FC** remains `HELD_FOR_MORE_EVIDENCE`; untouched.","","## Safety","","- No existing canonical GROUNDS record was overwritten.","- Publication required v7.9.2 to show exactly seven missing canonical records and zero existing/multiple records.","- Rejected stale pairs #8/#10/#14 remain rejected; the three recorded relationships are new/current 2026/27 relationships.","- Venue-level coordinates are used rather than postcode centroids where reliable mapped ground coordinates were available.","- The full ground-approval ledger is preserved rather than rewritten to a reduced schema.","- `competition.json` is untouched."]
REPORT.write_text("\n".join(L)+"\n",encoding="utf8")
print("CURRENT VENUE PROMOTION v7.9.3")
print("New canonical records: 7")
print("Existing canonical records overwritten: 0")
print("Current groundshares recorded: 3")
print("Romulus/Sutton Coldfield: HELD, untouched")
print("competition.json: untouched")
