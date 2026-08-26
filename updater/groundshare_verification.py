#!/usr/bin/env python3
import json,re,urllib.request,urllib.parse,time
from pathlib import Path
from datetime import datetime,timezone

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/"updater/ground-exception-verification.json"
LEDGER=ROOT/"updater/ground-approval-ledger.json"
OUT=ROOT/"updater/groundshare-verification.json"
REPORT=ROOT/"groundshare-verification.md"

if not SRC.exists(): raise SystemExit("Missing updater/ground-exception-verification.json; run v7.6.8 first.")
data=json.loads(SRC.read_text(encoding="utf8"))
records=data.get("records",[])
shares=[r for r in records if r.get("state")=="HUMAN_DECISION" and "shared" in (r.get("reason") or "").lower()]

def norm(s):
 s=(s or "").lower().replace("&"," and ")
 s=s.replace("’","'"); s=re.sub(r"\b(fc|afc|cfc|football club)\b"," ",s)
 return re.sub(r"[^a-z0-9]+"," ",s).strip()

def get_json(url):
 req=urllib.request.Request(url,headers={"User-Agent":"TinFoilFACup-groundshare-verifier/7.7.0"})
 with urllib.request.urlopen(req,timeout=20) as r:
  return json.loads(r.read().decode("utf8"))

# Independent postcode existence check only. It cannot prove a groundshare.
for r in shares:
 pc=(r.get("postcode") or "").strip().upper()
 r["postcode_check"]="UNKNOWN"
 if pc:
  try:
   j=get_json("https://api.postcodes.io/postcodes/"+urllib.parse.quote(pc))
   r["postcode_check"]="VALID" if j.get("status")==200 and j.get("result") else "FAILED"
  except Exception:
   r["postcode_check"]="FAILED"
 time.sleep(.05)

# Group by postcode. Multiple exception candidates at one postcode are stronger evidence of a relationship,
# but never sufficient on their own to auto-confirm a groundshare.
by={}
for r in shares: by.setdefault((r.get("postcode") or "").upper(),[]).append(r)

verified=[]; probable=[]; conflict=[]
for r in shares:
 peers=by.get((r.get("postcode") or "").upper(),[])
 if r["postcode_check"]!="VALID":
  state="CONFLICT"; reason="Independent postcode lookup failed; current venue requires research"
 elif len(peers)>=2:
  state="PROBABLE"; reason=f"Valid postcode and {len(peers)} exception clubs reference it; confirm current groundshare once"
 else:
  state="PROBABLE"; reason="Valid postcode and FCHD ground candidate agree geographically; confirm current host/groundshare relationship once"
 x={**r,"verification_state":state,"verification_reason":reason,
    "postcode_peers":[p.get("club") for p in peers if p.get("club")!=r.get("club")]}
 (conflict if state=="CONFLICT" else probable).append(x)

# Preserve any explicit approvals already made; never invent them.
ledger={"version":"7.7.0","updated_at":datetime.now(timezone.utc).isoformat(),
        "known_groundshares":[],"approved_exceptions":[]}
if LEDGER.exists():
 old=json.loads(LEDGER.read_text(encoding="utf8"))
 ledger["known_groundshares"]=old.get("known_groundshares",[])
 ledger["approved_exceptions"]=old.get("approved_exceptions",[])
LEDGER.write_text(json.dumps(ledger,indent=2,ensure_ascii=False)+"\n",encoding="utf8")

payload={"checked_at":datetime.now(timezone.utc).isoformat(),
 "mode":"verification-only","candidates_checked":len(shares),
 "confirmed":verified,"probable":probable,"conflict":conflict,
 "methodology":{
  "source":"v7.6.8 human-decision shared-postcode candidates",
  "independent_check":"Postcodes.io postcode existence",
  "important_limit":"A valid/shared postcode is not proof of a current groundshare. No relationship is auto-approved."
 }}
OUT.write_text(json.dumps(payload,indent=2,ensure_ascii=False)+"\n",encoding="utf8")

L=["# Tin Foil FA Cup — Groundshare Verification","",
 f"Last checked: **{datetime.now(timezone.utc).strftime('%d/%m/%Y, %H:%M:%S UTC')}**","",
 "**Verification only. No groundshare is approved or published automatically.**","",
 f"- 🏟️ Shared/host candidates checked: **{len(shares)}**",
 f"- 🟢 Confirmed from explicit approval/evidence: **{len(verified)}**",
 f"- 🟡 Probable — one human/current-source confirmation: **{len(probable)}**",
 f"- 🔴 Conflict / postcode failure: **{len(conflict)}**","",
 "A valid postcode or two clubs using the same postcode is **not** treated as proof of a groundshare. This stage deliberately stops one step short of inventing relationships."
]
for title,xs in [("🟢 Confirmed",verified),("🟡 Probable — confirm once",probable),("🔴 Conflict / research",conflict)]:
 L+=["",f"## {title}",""]
 if not xs:L.append("None.")
 for x in sorted(xs,key=lambda q:q.get("club","")):
  bits=[x.get("ground_candidate"),x.get("postcode"),x["verification_reason"]]
  if x.get("postcode_peers"): bits.append("Other queued club(s): "+", ".join(x["postcode_peers"]))
  L.append(f"- **{x.get('club')}** — "+" • ".join(b for b in bits if b))
L+=["","## Approval-ledger rule","",
 "Only an explicitly reviewed relationship should be added to `known_groundshares`. Once approved, a later Ground Health integration can suppress that *known* shared-postcode warning while still detecting new/unexpected sharing.","",
 "## Safety","",
 "- `clubfinder.html` is untouched.",
 "- `competition.json` is untouched.",
 "- Existing canonical GROUNDS records are untouched.",
 "- No yellow relationship becomes green merely because its postcode resolves."]
REPORT.write_text("\n".join(L)+"\n",encoding="utf8")
print("GROUNDSHARE VERIFICATION v7.7.0")
print("Candidates:",len(shares),"Confirmed:",len(verified),"Probable:",len(probable),"Conflict:",len(conflict))
print("VERIFY ONLY: no Clubfinder or competition data changed.")
