#!/usr/bin/env python3
import json,re
from collections import defaultdict
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
HTML=ROOT/"clubfinder.html"; REPORT=ROOT/"ground-health.md"; J=ROOT/"updater/ground-health.json"
def norm(s):
 s=(s or "").lower().replace("&"," and "); s=re.sub(r"\\b(fc|afc|cfc)\\b"," ",s)
 return re.sub(r"[^a-z0-9]+"," ",s).strip()
def arr(text,name,marker):
 s=text.find("const "+name+"=["); s=text.find("[",s); e=text.find(marker,s); raw=text[s:e]
 d=0;ins=False;esc=False;q="";close=None
 for i,ch in enumerate(raw):
  if ins:
   if esc:esc=False
   elif ch=="\\":esc=True
   elif ch==q:ins=False
  else:
   if ch in ("\'",'"'):ins=True;q=ch
   elif ch=="[":d+=1
   elif ch=="]":
    d-=1
    if d==0:close=i+1;break
 return json.loads(raw[:close])
t=HTML.read_text(encoding="utf8")
eligible=arr(t,"ELIGIBLE","];const GROUNDS="); grounds=arr(t,"GROUNDS","];GROUNDS=GROUNDS.map")
by=defaultdict(list); bypc=defaultdict(list)
for g in grounds:
 by[norm(g.get("name") or g.get("club"))].append(g)
 if g.get("postcode"):bypc[g["postcode"].upper()].append(g)
uk=re.compile(r"^(GIR 0AA|(?:[A-Z]{1,2}\\d[A-Z\\d]?|\\d[A-Z]{2})\\s*\\d[A-Z]{2})$",re.I)
missing=[];badpc=[];coords=[];unver=[];dups=[];conf=[];shared=[];complete=[]
for c in eligible:
 n=c.get("name")
 if not n:continue
 rs=by.get(norm(n),[])
 if not rs:missing.append((n,"No canonical ground record"));continue
 if len(rs)>1:
  dups.append((n,rs))
  if len({(r.get("ground",""),r.get("postcode","")) for r in rs})>1:conf.append((n,rs))
 g=rs[0]; pc=(g.get("postcode") or "").upper(); ok=True
 if not g.get("ground"):missing.append((n,"Ground name missing"));ok=False
 if not pc:missing.append((n,"Postcode missing"));ok=False
 elif not uk.match(pc):badpc.append((n,g.get("ground",""),pc));ok=False
 if g.get("lat") is None or g.get("lon") is None:coords.append((n,g.get("ground",""),pc));ok=False
 if (g.get("verification") or "verified").lower()!="verified":unver.append((n,g.get("ground",""),pc,g.get("verification","unverified")));ok=False
 if ok:complete.append(n)
for pc,rs in bypc.items():
 clubs=sorted({r.get("name") or r.get("club") or "" for r in rs})
 if len(clubs)>1:shared.append((pc,clubs))
critical=len(missing)+len(conf); review=len(badpc)+len(coords)+len(unver)+len(shared)
payload={"checked_at":datetime.now(timezone.utc).isoformat(),"counts":{"eligible_clubs":len({norm(x.get("name")) for x in eligible if x.get("name")}),"ground_records":len(grounds),"complete_verified":len(complete),"critical_items":critical,"review_items":review,"missing_or_incomplete":len(missing),"invalid_postcodes":len(badpc),"missing_coordinates":len(coords),"unverified":len(unver),"duplicate_club_records":len(dups),"conflicting_club_records":len(conf),"shared_postcodes":len(shared)},"missing_or_incomplete":missing,"invalid_postcodes":badpc,"missing_coordinates":coords,"unverified":unver,"shared_postcodes":shared}
J.write_text(json.dumps(payload,indent=2,ensure_ascii=False)+"\n")
L=["# Tin Foil FA Cup — Ground Health","",f"Last checked: **{datetime.now(timezone.utc).strftime('%d/%m/%Y, %H:%M:%S UTC')}**","",f"- 🟢 Complete verified club-ground records: **{len(complete)}**",f"- 🔴 Critical ground-data items: **{critical}**",f"- 🟡 Review items: **{review}**",f"- ⚪ Eligible clubs audited: **{payload['counts']['eligible_clubs']}**","","This report audits the ground registry embedded in `clubfinder.html`. Shared postcodes are review items, not automatic errors.",""]
def sec(title,items,fmt,empty):
 L.extend(["","## "+title,""])
 if not items:L.append(empty)
 else:
  for x in items:L.append(fmt(x))
sec("🔴 Missing / incomplete canonical records",missing,lambda x:f"- **{x[0]}** — {x[1]}","No missing or incomplete canonical ground records found.")
sec("🔴 Conflicting duplicate club records",conf,lambda x:f"- **{x[0]}** — "+" | ".join(f"{r.get('ground','TBC')} • {r.get('postcode','TBC')}" for r in x[1]),"No conflicting duplicate club records found.")
sec("🟡 Invalid-looking UK postcodes",badpc,lambda x:f"- **{x[0]}** — {x[1]} • `{x[2]}`","No invalid-looking UK postcodes found.")
sec("🟡 Missing coordinates",coords,lambda x:f"- **{x[0]}** — {x[1]} • {x[2] or 'Postcode TBC'}","No ground records are missing coordinates.")
sec("🟡 Unverified locations",unver,lambda x:f"- **{x[0]}** — {x[1]} • {x[2]} — `{x[3]}`","No unverified locations found.")
sec("🟡 Shared postcodes / possible groundshares",shared,lambda x:f"- **{x[0]}** — "+", ".join(x[1]),"No shared postcodes found.")
L+=["","## Audit notes","","- Shared postcodes may be legitimate groundshares.","- Sponsored stadium-name changes may change only the name, not the location.","- Missing coordinates can affect nearest-club ranking.","- Audit only: no data is edited."]
REPORT.write_text("\n".join(L)+"\n")
print("GROUND HEALTH v7.6.2")
for k,v in payload["counts"].items():print(k+":",v)
print("AUDIT ONLY: no Clubfinder or competition data changed.")
