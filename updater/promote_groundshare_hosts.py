#!/usr/bin/env python3
import json,re
from pathlib import Path
from datetime import datetime,timezone

ROOT=Path(__file__).resolve().parents[1]
HTML=ROOT/"clubfinder.html"
HEALTH=ROOT/"updater/ground-health.json"
LEDGER=ROOT/"updater/ground-approval-ledger.json"
OUT=ROOT/"updater/groundshare-host-promotion.json"
REPORT=ROOT/"groundshare-host-promotion.md"

def norm(s):
    s=(s or "").lower().replace("&"," and ").replace("’","'")
    s=re.sub(r"\b(fc|afc|cfc|football club)\b"," ",s)
    return re.sub(r"[^a-z0-9]+"," ",s).strip()

def locate(text,name):
    m=re.search(r"\b(?:const|let|var)\s+"+re.escape(name)+r"\s*=\s*\[",text)
    if not m: raise SystemExit("Could not find "+name)
    s=text.find("[",m.start()); d=0; ins=False; esc=False; q=""
    for i in range(s,len(text)):
        c=text[i]
        if ins:
            if esc: esc=False
            elif c=="\\": esc=True
            elif c==q: ins=False
        else:
            if c in ("'",'\"'): ins=True;q=c
            elif c=="[": d+=1
            elif c=="]":
                d-=1
                if d==0:return s,i+1
    raise SystemExit("Unbalanced "+name)

if not (HTML.exists() and HEALTH.exists() and LEDGER.exists()):
    raise SystemExit("Missing clubfinder.html, Ground Health, or approval ledger.")
health=json.loads(HEALTH.read_text(encoding="utf8"))
pending=health.get("approved_groundshares_pending_canonical_reconciliation") or []
expected={("Epsom & Ewell FC","Chessington & Hook United FC","KT9 2NF"),("Southall FC","Uxbridge FC","UB7 8HX")}
actual={(x.get("tenant"),x.get("host"),x.get("postcode")) for x in pending}
if actual!=expected:
    raise SystemExit(f"Safety stop: expected exactly the two v7.9.4 pending host relationships; found {actual}")

TARGETS=[
 {"name":"Chessington & Hook United FC","ground":"Chalky Lane","postcode":"KT9 2NF","lat":51.350284,"lon":-0.309281,"source":"https://www.chufc.co.uk/contact","ground_source":"Current official Chessington & Hook United contact/2026-27 club information","coordinate_source":"FCHD mapped Chalky Lane ground coordinate"},
 {"name":"Uxbridge FC","ground":"Honeycroft","postcode":"UB7 8HX","lat":51.514078,"lon":-0.457668,"source":"https://www.uxbridgefc.com/how-to-find-us","ground_source":"Current official Uxbridge FC venue/directions and 2026-27 information","coordinate_source":"FCHD mapped Uxbridge/Honeycroft ground coordinate"},
]

text=HTML.read_text(encoding="utf8"); s,e=locate(text,"GROUNDS"); grounds=json.loads(text[s:e]); by={}
for g in grounds:
    k=norm(g.get("name") or g.get("club"))
    if k: by.setdefault(k,[]).append(g)
# Existing tenant records must remain present and match the approved postcode.
for tenant,host,pc in expected:
    rs=by.get(norm(tenant),[])
    if len(rs)!=1 or (rs[0].get("postcode") or "").upper()!=pc:
        raise SystemExit(f"Safety stop: tenant canonical state drift for {tenant}")
# Hosts must still be absent; never overwrite an existing host record.
for t in TARGETS:
    if by.get(norm(t["name"])):
        raise SystemExit(f"Safety stop: canonical host record already exists for {t['name']}; rerun Ground Health instead of overwriting.")

new=[]
for t in TARGETS:
    new.append({"name":t["name"],"ground":t["ground"],"postcode":t["postcode"],"lat":t["lat"],"lon":t["lon"],"verification":"verified","verification_label":"✅ Verified","source":"Current 2026/27 host venue evidence: "+t["source"],"ground_source":t["ground_source"],"coordinate_source":t["coordinate_source"]})
new_grounds=grounds+sorted(new,key=lambda x:x["name"].lower())
HTML.write_text(text[:s]+json.dumps(new_grounds,ensure_ascii=False,separators=(",",":"))+text[e:],encoding="utf8")

now=datetime.now(timezone.utc).isoformat()
payload={"published_at":now,"version":"7.9.5","mode":"SAFE CANONICAL HOST PROMOTION","canonical_host_records_added":2,"existing_records_overwritten":0,"relationships_modified":0,"records":new,"competition_json_changed":False}
OUT.write_text(json.dumps(payload,indent=2,ensure_ascii=False)+"\n",encoding="utf8")
L=["# Tin Foil FA Cup — Groundshare Host Promotion","",f"Published: **{datetime.now(timezone.utc).strftime('%d/%m/%Y, %H:%M:%S UTC')}**","","**v7.9.5 SAFE HOST PROMOTION. Existing canonical records and groundshare relationships are not overwritten or altered.**","","- New canonical host records: **2**","- Existing canonical records overwritten: **0**","- Groundshare relationships modified: **0**","- `competition.json` changed: **NO**","","## Published host records",""]
for g in new:L.append(f"- **{g['name']}** — {g['ground']} • {g['postcode']} • `{g['lat']}, {g['lon']}`")
L += ["","## Safety","","- Promotion requires Ground Health v7.9.4 to show exactly the two expected pending approved relationships.","- The tenant canonical record must already exist at the approved postcode.","- A host record must still be absent; an existing host record causes a safety stop rather than an overwrite.","- The approval ledger is not changed by this stage.","- `competition.json` is untouched."]
REPORT.write_text("\n".join(L)+"\n",encoding="utf8")
print("GROUNDSHARE HOST PROMOTION v7.9.5")
print("New canonical host records: 2")
print("Existing records overwritten: 0")
print("Relationships modified: 0")
print("competition.json: untouched")
