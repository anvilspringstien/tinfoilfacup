#!/usr/bin/env python3
import json,re
from collections import defaultdict
from datetime import datetime,timezone
from pathlib import Path
R=Path(__file__).resolve().parents[1]; T=(R/"clubfinder.html").read_text(); L=R/"updater/ground-approval-ledger.json"
def norm(s):
 s=(s or "").lower().replace("&"," and ").replace("’","'"); s=re.sub(r"\b(fc|afc|cfc|football club)\b"," ",s); return re.sub(r"[^a-z0-9]+"," ",s).strip()
def arr(name,required=True):
 m=re.search(r"\b(?:const|let|var)\s+"+re.escape(name)+r"\s*=\s*\[",T)
 if not m:
  if required: raise SystemExit(f"Missing {name} array")
  return []
 s=T.find("[",m.start()); d=0; ins=False; esc=False; q=""
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
 raise SystemExit(f"Unbalanced {name} array")
E=arr("ELIGIBLE"); G=arr("GROUNDS"); S=arr("LAW2_ORIGIN_LOCATIONS",False); ledger={}; approved={}; shared_approved=[]
if L.exists():
 ledger=json.loads(L.read_text())
 for a in ledger.get("known_groundshares",[]):
  approved[norm(a.get("tenant"))]={"postcode":(a.get("postcode") or "").upper(),"host":a.get("host") or "","season":a.get("season") or "","tenant":a.get("tenant") or ""}
 shared_approved=ledger.get("known_shared_venues",[]) or []
by=defaultdict(list); support=defaultdict(list); pcd=defaultdict(list)
for g in G:
 by[norm(g.get("name") or g.get("club"))].append(g); pc=(g.get("postcode") or "").upper()
 if pc: pcd[pc].append(g)
for g in S: support[norm(g.get("name") or g.get("club"))].append(g)
uk=re.compile(r"^(GIR 0AA|(?:[A-Z]{1,2}\d[A-Z\d]?|\d[A-Z]{2})\s*\d[A-Z]{2})$",re.I)
names={norm(x.get("name")):x.get("name") for x in E if x.get("name")}
miss=[];bad=[];coords=[];unv=[];conf=[];good=[];support_good=[];support_bad=[];shared=[];known=[];known_shared=[];known_keys=set();pending=[]
for k,n in names.items():
 rs=by.get(k,[])
 if rs:
  g=rs[0]; pc=(g.get("postcode") or "").upper(); ok=True
  if not g.get("ground"): miss.append((n,"Ground name missing")); ok=False
  if not pc: miss.append((n,"Postcode missing")); ok=False
  elif not uk.match(pc): bad.append((n,g.get("ground",""),pc)); ok=False
  if g.get("lat") is None or g.get("lon") is None: coords.append((n,g.get("ground",""),pc)); ok=False
  if (g.get("verification") or "verified").lower()!="verified": unv.append((n,g.get("ground",""),pc,g.get("verification"))); ok=False
  if ok: good.append(n)
  continue
 ss=support.get(k,[])
 if len(ss)!=1:
  miss.append((n,"No canonical ground record or unique Law 2 supporting location")); continue
 g=ss[0];pc=(g.get("postcode") or "").upper();reasons=[]
 if not g.get("ground"):reasons.append("ground name missing")
 if not pc:reasons.append("postcode missing")
 elif not uk.match(pc):reasons.append("postcode invalid")
 if g.get("lat") is None or g.get("lon") is None:reasons.append("coordinates missing")
 if (g.get("verification") or "").lower()!="supporting-evidence":reasons.append("supporting-evidence marker missing")
 if not g.get("source"):reasons.append("source missing")
 if reasons:support_bad.append((n,g.get("ground",""),pc,"; ".join(reasons)))
 else:support_good.append(n)
for tk,a in approved.items():
 trs=by.get(tk,[]); hk=norm(a["host"]); hrs=by.get(hk,[]); pc=a["postcode"]
 if len(trs)==1 and len(hrs)==1 and (trs[0].get("postcode") or "").upper()==pc and (hrs[0].get("postcode") or "").upper()==pc:
  tenant=trs[0].get("name") or trs[0].get("club") or a["tenant"]; host=hrs[0].get("name") or hrs[0].get("club") or a["host"]
  known.append({"postcode":pc,"tenant":tenant,"host":host,"season":a["season"]}); known_keys.add((pc,tuple(sorted((norm(tenant),norm(host))))))
 else:
  pending.append({"postcode":pc,"tenant":a["tenant"],"host":a["host"],"season":a["season"],"tenant_canonical_matches":len(trs),"host_canonical_matches":len(hrs),"reason":"Approved relationship is retained in ledger but cannot yet be reconciled to exactly one canonical tenant and host at the approved postcode."})
for a in shared_approved:
 pc=(a.get("postcode") or "").upper(); clubs=a.get("clubs") or []; resolved=[]; ok=bool(pc) and len(clubs)>=2
 for club in clubs:
  rs=by.get(norm(club),[])
  if len(rs)!=1 or (rs[0].get("postcode") or "").upper()!=pc: ok=False; break
  resolved.append(rs[0].get("name") or rs[0].get("club") or club)
 if ok:
  key=(pc,tuple(sorted(norm(c) for c in resolved))); known_keys.add(key)
  known_shared.append({"postcode":pc,"clubs":resolved,"season":a.get("season") or "","relationship_type":a.get("relationship_type") or "confirmed_shared_venue_undirected"})
for pc,rs in pcd.items():
 clubs=sorted({r.get("name") or r.get("club") or "" for r in rs})
 if len(clubs)<=1: continue
 if (pc,tuple(sorted(norm(c) for c in clubs))) in known_keys: continue
 shared.append((pc,clubs))
critical=len(miss)+len(conf)+len(support_bad); review=len(bad)+len(coords)+len(unv)+len(shared); selectable=len(good)+len(support_good)
counts={"eligible_clubs":len(names),"complete_verified":len(good),"law2_supporting_locations":len(support_good),"selectable_location_coverage":selectable,"critical_items":critical,"review_items":review,"shared_postcodes":len(shared),"known_approved_groundshares":len(known),"known_confirmed_shared_venues":len(known_shared),"approved_groundshares_pending_canonical_reconciliation":len(pending),"unverified":len(unv)}
(R/"updater/ground-health.json").write_text(json.dumps({"checked_at":datetime.now(timezone.utc).isoformat(),"counts":counts,"missing_or_incomplete":miss,"invalid_supporting_locations":support_bad,"shared_postcodes":shared,"known_approved_groundshares":known,"known_confirmed_shared_venues":known_shared,"approved_groundshares_pending_canonical_reconciliation":pending,"unverified":unv},indent=2)+"\n")
lines=["# Tin Foil FA Cup — Ground Health","",f"- 🟢 Complete verified canonical club-ground records: **{len(good)}**",f"- 🟦 Law 2 supporting origin locations: **{len(support_good)}**",f"- ⚪ Selectable origin location coverage: **{selectable}/{len(names)}**",f"- 🔴 Critical ground-data items: **{critical}**",f"- 🟡 Review items: **{review}**",f"- ⚪ Eligible clubs audited: **{len(names)}**",f"- 🏟️ Known approved groundshares reconciled to canonical records: **{len(known)}**",f"- 🤝 Confirmed shared venues reconciled without forced direction: **{len(known_shared)}**",f"- ⏳ Approved groundshares pending canonical host/tenant reconciliation: **{len(pending)}**","","Supporting Law 2 origin locations are usable for distance selection but remain explicitly unverified until promoted through the guarded ground process.","","## 🔴 Critical missing/incomplete origin locations",""]
lines += [f"- **{club}** — {reason}" for club,reason in miss] or ["None."]
lines += ["","## 🔴 Invalid Law 2 supporting locations",""]
lines += [f"- **{club}** — {ground} • {pc} — {reason}" for club,ground,pc,reason in support_bad] or ["None."]
lines += ["","## 🟡 Shared postcodes / possible groundshares",""]
lines += [f"- **{pc}** — "+", ".join(clubs) for pc,clubs in shared] or ["No unexplained shared postcodes found."]
lines += ["","## 🏟️ Known approved groundshares",""]
lines += [f"- **{x['tenant']}** → {x['host']} • {x['postcode']} • {x['season'] or 'Current period'}" for x in known] or ["None."]
lines += ["","## 🤝 Confirmed shared venues without forced direction",""]
lines += [f"- **{', '.join(x['clubs'])}** • {x['postcode']} • {x['season'] or 'Current period'}" for x in known_shared] or ["None."]
lines += ["","## ⏳ Approved relationships awaiting canonical counterpart",""]
lines += [f"- **{x['tenant']}** → {x['host']} • {x['postcode']} • {x['season'] or 'Current period'} — canonical tenant matches: {x['tenant_canonical_matches']}; canonical host matches: {x['host_canonical_matches']}" for x in pending] or ["None."]
(R/"ground-health.md").write_text("\n".join(lines)+"\n")
print("GROUND HEALTH v7.10.0",counts)
