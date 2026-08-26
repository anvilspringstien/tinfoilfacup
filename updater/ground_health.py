#!/usr/bin/env python3
import json,re
from collections import defaultdict
from datetime import datetime,timezone
from pathlib import Path
R=Path(__file__).resolve().parents[1]; T=(R/"clubfinder.html").read_text(encoding="utf8")
def n(s):
 s=(s or "").lower().replace("&"," and ");s=re.sub(r"\b(fc|afc|cfc)\b"," ",s);return re.sub(r"[^a-z0-9]+"," ",s).strip()
def a(name):
 m=re.search(r"\b(?:const|let|var)\s+"+re.escape(name)+r"\s*=\s*\[",T)
 if not m:raise SystemExit("Could not find "+name+" array")
 st=T.find("[",m.start());d=0;ins=False;esc=False;q=""
 for i in range(st,len(T)):
  c=T[i]
  if ins:
   if esc:esc=False
   elif c=="\\":esc=True
   elif c==q:ins=False
  else:
   if c in ("'",'"'):ins=True;q=c
   elif c=="[":d+=1
   elif c=="]":
    d-=1
    if d==0:return json.loads(T[st:i+1])
 raise SystemExit("Unbalanced "+name)
E=a("ELIGIBLE");G=a("GROUNDS");by=defaultdict(list);pcd=defaultdict(list)
for g in G:
 by[n(g.get("name") or g.get("club"))].append(g)
 pc=(g.get("postcode") or "").upper()
 if pc:pcd[pc].append(g)
uk=re.compile(r"^(GIR 0AA|(?:[A-Z]{1,2}\d[A-Z\d]?|\d[A-Z]{2})\s*\d[A-Z]{2})$",re.I)
miss=[];bad=[];coords=[];unv=[];dup=[];conf=[];shared=[];good=[]
names={n(x.get("name")):x.get("name") for x in E if x.get("name")}
for k,name in names.items():
 rs=by.get(k,[])
 if not rs:miss.append((name,"No canonical ground record"));continue
 if len(rs)>1:
  dup.append((name,rs))
  if len({(r.get("ground",""),(r.get("postcode") or "").upper()) for r in rs})>1:conf.append((name,rs))
 g=rs[0];pc=(g.get("postcode") or "").upper();ok=True
 if not g.get("ground"):miss.append((name,"Ground name missing"));ok=False
 if not pc:miss.append((name,"Postcode missing"));ok=False
 elif not uk.match(pc):bad.append((name,g.get("ground",""),pc));ok=False
 if g.get("lat") is None or g.get("lon") is None:coords.append((name,g.get("ground",""),pc));ok=False
 if (g.get("verification") or "verified").lower()!="verified":unv.append((name,g.get("ground",""),pc,g.get("verification")));ok=False
 if ok:good.append(name)
for pc,rs in pcd.items():
 clubs=sorted({r.get("name") or r.get("club") or "" for r in rs})
 if len(clubs)>1:shared.append((pc,clubs))
critical=len(miss)+len(conf);review=len(bad)+len(coords)+len(unv)+len(shared)
C={"eligible_clubs":len(names),"ground_records":len(G),"complete_verified":len(good),"critical_items":critical,"review_items":review,"missing_or_incomplete":len(miss),"invalid_postcodes":len(bad),"missing_coordinates":len(coords),"unverified":len(unv),"duplicate_club_records":len(dup),"conflicting_club_records":len(conf),"shared_postcodes":len(shared)}
(R/"updater/ground-health.json").write_text(json.dumps({"checked_at":datetime.now(timezone.utc).isoformat(),"counts":C,"missing_or_incomplete":miss,"invalid_postcodes":bad,"missing_coordinates":coords,"unverified":unv,"shared_postcodes":shared},indent=2)+"\n")
L=["# Tin Foil FA Cup — Ground Health","",f"Last checked: **{datetime.now(timezone.utc).strftime('%d/%m/%Y, %H:%M:%S UTC')}**","",f"- 🟢 Complete verified club-ground records: **{len(good)}**",f"- 🔴 Critical ground-data items: **{critical}**",f"- 🟡 Review items: **{review}**",f"- ⚪ Eligible clubs audited: **{len(names)}**",""]
def sec(h,x,f,e):L.extend(["","## "+h,""]+([f(v) for v in x] if x else [e]))
sec("🔴 Missing / incomplete canonical records",miss,lambda x:f"- **{x[0]}** — {x[1]}","None found.")
sec("🔴 Conflicting duplicate club records",conf,lambda x:f"- **{x[0]}** — "+" | ".join(f"{r.get('ground','TBC')} • {r.get('postcode','TBC')}" for r in x[1]),"None found.")
sec("🟡 Invalid-looking UK postcodes",bad,lambda x:f"- **{x[0]}** — {x[1]} • `{x[2]}`","None found.")
sec("🟡 Missing coordinates",coords,lambda x:f"- **{x[0]}** — {x[1]} • {x[2] or 'Postcode TBC'}","None found.")
sec("🟡 Unverified locations",unv,lambda x:f"- **{x[0]}** — {x[1]} • {x[2]} — `{x[3]}`","None found.")
sec("🟡 Shared postcodes / possible groundshares",shared,lambda x:f"- **{x[0]}** — "+", ".join(x[1]),"None found.")
L+=["","Audit only: no Clubfinder or competition data changed."]
(R/"ground-health.md").write_text("\n".join(L)+"\n")
print("GROUND HEALTH v7.6.2a");[print(k+":",v) for k,v in C.items()];print("AUDIT ONLY.")
