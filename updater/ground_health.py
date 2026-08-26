#!/usr/bin/env python3
import json,re
from collections import defaultdict
from datetime import datetime,timezone
from pathlib import Path
R=Path(__file__).resolve().parents[1]; T=(R/"clubfinder.html").read_text(); L=R/"updater/ground-approval-ledger.json"
def norm(s):
 s=(s or "").lower().replace("&"," and ").replace("’","'"); s=re.sub(r"\b(fc|afc|cfc|football club)\b"," ",s); return re.sub(r"[^a-z0-9]+"," ",s).strip()
def arr(name):
 m=re.search(r"\b(?:const|let|var)\s+"+re.escape(name)+r"\s*=\s*\[",T); s=T.find("[",m.start()); d=0; ins=False; esc=False; q=""
 for i in range(s,len(T)):
  c=T[i]
  if ins:
   if esc: esc=False
   elif c=="\\": esc=True
   elif c==q: ins=False
  else:
   if c in ("'",'"'): ins=True;q=c
   elif c=="[": d+=1
   elif c=="]":
    d-=1
    if d==0:return json.loads(T[s:i+1])
E=arr("ELIGIBLE"); G=arr("GROUNDS"); approved={}
if L.exists():
 for a in json.loads(L.read_text()).get("known_groundshares",[]):
  approved[norm(a.get("tenant"))]={"postcode":(a.get("postcode") or "").upper(),"host":a.get("host") or "","season":a.get("season") or ""}
by=defaultdict(list); pcd=defaultdict(list)
for g in G:
 by[norm(g.get("name") or g.get("club"))].append(g); pc=(g.get("postcode") or "").upper()
 if pc: pcd[pc].append(g)
uk=re.compile(r"^(GIR 0AA|(?:[A-Z]{1,2}\d[A-Z\d]?|\d[A-Z]{2})\s*\d[A-Z]{2})$",re.I)
names={norm(x.get("name")):x.get("name") for x in E if x.get("name")}
miss=[];bad=[];coords=[];unv=[];conf=[];good=[];shared=[];known=[]
for k,n in names.items():
 rs=by.get(k,[])
 if not rs: miss.append((n,"No canonical ground record")); continue
 g=rs[0]; pc=(g.get("postcode") or "").upper(); ok=True
 if not g.get("ground"): miss.append((n,"Ground name missing")); ok=False
 if not pc: miss.append((n,"Postcode missing")); ok=False
 elif not uk.match(pc): bad.append((n,g.get("ground",""),pc)); ok=False
 if g.get("lat") is None or g.get("lon") is None: coords.append((n,g.get("ground",""),pc)); ok=False
 if (g.get("verification") or "verified").lower()!="verified": unv.append((n,g.get("ground",""),pc,g.get("verification"))); ok=False
 if ok: good.append(n)
for pc,rs in pcd.items():
 clubs=sorted({r.get("name") or r.get("club") or "" for r in rs})
 if len(clubs)<=1: continue
 if len(clubs)==2:
  approved_members=[c for c in clubs if norm(c) in approved and approved[norm(c)]["postcode"]==pc]
  if len(approved_members)==1:
   tenant=approved_members[0]; host=[c for c in clubs if c!=tenant][0]; a=approved[norm(tenant)]
   if not a["host"] or norm(a["host"])==norm(host):
    known.append({"postcode":pc,"tenant":tenant,"host":host,"season":a["season"]}); continue
 shared.append((pc,clubs))
critical=len(miss)+len(conf); review=len(bad)+len(coords)+len(unv)+len(shared)
counts={"eligible_clubs":len(names),"complete_verified":len(good),"critical_items":critical,"review_items":review,"shared_postcodes":len(shared),"known_approved_groundshares":len(known),"unverified":len(unv)}
(R/"updater/ground-health.json").write_text(json.dumps({"checked_at":datetime.now(timezone.utc).isoformat(),"counts":counts,"missing_or_incomplete":miss,"shared_postcodes":shared,"known_approved_groundshares":known,"unverified":unv},indent=2)+"\n")
lines=["# Tin Foil FA Cup — Ground Health","",f"- 🟢 Complete verified club-ground records: **{len(good)}**",f"- 🔴 Critical ground-data items: **{critical}**",f"- 🟡 Review items: **{review}**",f"- ⚪ Eligible clubs audited: **{len(names)}**",f"- 🏟️ Known approved groundshares suppressed from warnings: **{len(known)}**","","## 🟡 Shared postcodes / possible groundshares",""]
lines += [f"- **{pc}** — "+", ".join(clubs) for pc,clubs in shared] or ["No unexplained shared postcodes found."]
lines += ["","## 🏟️ Known approved groundshares",""]
lines += [f"- **{x['tenant']}** → {x['host']} • {x['postcode']} • {x['season'] or 'Current period'}" for x in known] or ["None."]
(R/"ground-health.md").write_text("\n".join(lines)+"\n")
print("GROUND HEALTH v7.7.2",counts)
