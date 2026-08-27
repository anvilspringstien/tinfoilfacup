#!/usr/bin/env python3
import argparse,json,re
from pathlib import Path
from datetime import datetime,timezone
R=Path(__file__).resolve().parents[1]; H=R/"clubfinder.html"; L=R/"updater/ground-approval-ledger.json"; V=R/"updater/ground-verification-queue.json"; REP=R/"approved-groundshare-promotion.md"
def n(s):
 s=(s or "").lower().replace("&"," and ").replace("’","'"); s=re.sub(r"\\b(fc|afc|cfc|football club)\\b"," ",s); return re.sub(r"[^a-z0-9]+"," ",s).strip()
def loc(t,name):
 m=re.search(r"\\b(?:const|let|var)\\s+"+re.escape(name)+r"\\s*=\\s*\\[",t)
 if not m: raise SystemExit("Could not find "+name)
 s=t.find("[",m.start()); d=0; ins=False; esc=False; q=""
 for i in range(s,len(t)):
  c=t[i]
  if ins:
   if esc: esc=False
   elif c=="\\\\": esc=True
   elif c==q: ins=False
  else:
   if c in ("'",'"'): ins=True; q=c
   elif c=="[": d+=1
   elif c=="]":
    d-=1
    if d==0:return s,i+1
 raise SystemExit("Unbalanced "+name)
ap=argparse.ArgumentParser(); ap.add_argument("--tenant",required=True); ap.add_argument("--publish",action="store_true"); a=ap.parse_args()
ledger=json.loads(L.read_text()); approvals=[x for x in ledger.get("known_groundshares",[]) if n(x.get("tenant"))==n(a.tenant)]
if len(approvals)!=1: raise SystemExit(f"Expected one approval, found {len(approvals)}")
approval=approvals[0]
ver=json.loads(V.read_text()); recs=[x for x in ver.get("records",[]) if n(x.get("club"))==n(a.tenant)]
if len(recs)!=1: raise SystemExit(f"Expected one verification record, found {len(recs)}")
c=recs[0]
if n(approval.get("ground"))!=n(c.get("ground_candidate")): raise SystemExit("Ground mismatch")
if (approval.get("postcode") or "").upper().strip()!=(c.get("postcode") or "").upper().strip(): raise SystemExit("Postcode mismatch")
if c.get("fchd_lat") is None or c.get("fchd_lon") is None: raise SystemExit("Missing validated coordinates")
t=H.read_text(); s,e=loc(t,"GROUNDS"); grounds=json.loads(t[s:e])
if any(n(g.get("name") or g.get("club"))==n(a.tenant) for g in grounds): raise SystemExit("Tenant already canonical; refusing duplicate")
r={"name":approval["tenant"],"ground":approval["ground"],"postcode":approval["postcode"].upper(),"lat":float(c["fchd_lat"]),"lon":float(c["fchd_lon"]),"verification":"verified","verification_label":"✅ Verified","source":"Approved current groundshare + v7.6.5 validated candidate","ground_source":c.get("source") or "FCHD 2025-26 Gazetteer","coordinate_source":"FCHD coordinates; independently checked against Postcodes.io","groundshare_host":approval.get("host",""),"groundshare_season":approval.get("season",""),"groundshare_source":approval.get("source_url","")}
if a.publish:
 grounds.append(r); H.write_text(t[:s]+json.dumps(grounds,ensure_ascii=False,separators=(",",":"))+t[e:])
REP.write_text(f"# Tin Foil FA Cup — Approved Groundshare Promotion\\n\\n- Mode: **{'PUBLISH' if a.publish else 'DRY RUN'}**\\n- Tenant: **{approval['tenant']}**\\n- Host: **{approval.get('host','')}**\\n- Approved venue: **{approval.get('ground','')} • {approval.get('postcode','')}**\\n- Ledger approval: **✅**\\n- v7.6.5 candidate agrees: **✅**\\n- Validated coordinates available: **✅**\\n- Ready to promote: **YES**\\n- Canonical GROUNDS changed: **{'YES' if a.publish else 'NO'}**\\n\\n## Candidate\\n\\n- **{r['name']}** — {r['ground']} • {r['postcode']} • `{r['lat']}, {r['lon']}`\\n\\nIndependent postcode separation: `{c.get('distance_km')} km`\\n")
print("APPROVED GROUNDSHARE PROMOTION v7.7.3a"); print("Mode:", "PUBLISH" if a.publish else "DRY RUN"); print("READY TO PROMOTE: YES")
