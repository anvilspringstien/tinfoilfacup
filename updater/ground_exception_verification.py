#!/usr/bin/env python3
import json,re
from pathlib import Path
from datetime import datetime,timezone

ROOT=Path(__file__).resolve().parents[1]
HTML=ROOT/"clubfinder.html"
OLD=ROOT/"updater/ground-exception-verification.json"
LEDGER=ROOT/"updater/ground-approval-ledger.json"
OUT=ROOT/"updater/ground-exception-verification.json"
REPORT=ROOT/"ground-exception-verification.md"

def norm(s):
    s=(s or "").lower().replace("&"," and ").replace("’","'").replace("'","")
    s=re.sub(r"\b(fc|afc|cfc|football club)\b"," ",s)
    return re.sub(r"[^a-z0-9]+"," ",s).strip()

def js_array(text,name):
    m=re.search(r"\b(?:const|let|var)\s+"+re.escape(name)+r"\s*=\s*\[",text)
    if not m: raise SystemExit("Could not find "+name+" array")
    start=text.find("[",m.start()); depth=0; ins=False; esc=False; q=""
    for i in range(start,len(text)):
        ch=text[i]
        if ins:
            if esc: esc=False
            elif ch=="\\": esc=True
            elif ch==q: ins=False
        else:
            if ch in ("'",'"'): ins=True; q=ch
            elif ch=="[": depth+=1
            elif ch=="]":
                depth-=1
                if depth==0: return json.loads(text[start:i+1])
    raise SystemExit("Unbalanced "+name)

if not OLD.exists():
    raise SystemExit("Missing updater/ground-exception-verification.json. Run the existing verification once first.")

old=json.loads(OLD.read_text(encoding="utf8"))
records=old.get("records",[])
text=HTML.read_text(encoding="utf8")
grounds=js_array(text,"GROUNDS")
canonical={norm(g.get("name") or g.get("club")):g for g in grounds}

approved_groundshares={}
if LEDGER.exists():
    led=json.loads(LEDGER.read_text(encoding="utf8"))
    for x in led.get("known_groundshares",[]):
        if isinstance(x,dict) and x.get("tenant"):
            approved_groundshares[norm(x["tenant"])]=x

resolved=[]
active=[]

for r in records:
    club=r.get("club") or ""
    key=norm(club)
    rr=dict(r)

    # v7.7.4 identity correction carried forward:
    # Bishop's Cleeve vs Bishops Cleeve is punctuation-only, not unsafe fuzzy identity.
    if key==norm("Bishop's Cleeve FC"):
        match=norm(r.get("fchd_match") or "")
        if match==norm("Bishops Cleeve"):
            rr["state"]="HUMAN_DECISION"
            rr["reason"]="Mechanical apostrophe/name-format variant; confirm current ground once"

    if key in canonical:
        g=canonical[key]
        reason="Canonical GROUNDS record now present"
        approval=approved_groundshares.get(key)
        if approval:
            reason += "; approved groundshare relationship recorded"
        resolved.append({
            "club":club,
            "ground":g.get("ground"),
            "postcode":g.get("postcode"),
            "resolution":reason,
            "previous_state":rr.get("state")
        })
        continue

    active.append(rr)

states=("APPROVED_CANDIDATE","HUMAN_DECISION","GROUND_RESEARCH")
counts={s:sum(x.get("state")==s for x in active) for s in states}
active_total=sum(counts.values())

payload={
    "checked_at":datetime.now(timezone.utc).isoformat(),
    "mode":"resolution-aware verification/triage",
    "active_total":active_total,
    "resolved_total":len(resolved),
    "counts":counts,
    "records":active,
    "resolved_since_verification":resolved,
    "rules_version":"7.7.4"
}
OUT.write_text(json.dumps(payload,indent=2,ensure_ascii=False)+"\n",encoding="utf8")

titles={
    "APPROVED_CANDIDATE":"🟢 Approved candidates",
    "HUMAN_DECISION":"🟡 One human decision required",
    "GROUND_RESEARCH":"🔴 Genuine ground research required"
}

L=[
"# Tin Foil FA Cup — Ground Exception Verification","",
f"Last checked: **{datetime.now(timezone.utc).strftime('%d/%m/%Y, %H:%M:%S UTC')}**","",
"**Resolution-aware verification/triage only. Nothing is published automatically.**","",
f"- 🟢 Approved candidates: **{counts['APPROVED_CANDIDATE']}**",
f"- 🟡 One human decision required: **{counts['HUMAN_DECISION']}**",
f"- 🔴 Genuine ground research required: **{counts['GROUND_RESEARCH']}**",
f"- ✅ Resolved since earlier verification: **{len(resolved)}**",
f"- ⚪ Current actionable exception total: **{active_total}**","",
"Clubs that now have a canonical `GROUNDS` record are removed from the actionable totals rather than being reported forever as stale exceptions."
]

for state in states:
    L+=["",f"## {titles[state]}",""]
    xs=[x for x in active if x.get("state")==state]
    if not xs:
        L.append("None.")
    for x in sorted(xs,key=lambda z:(z.get("club") or "").lower()):
        bits=[]
        if x.get("fchd_match") and norm(x.get("fchd_match"))!=norm(x.get("club")):
            bits.append(f"FCHD: **{x.get('fchd_match')}**")
        if x.get("ground_candidate"): bits.append(x["ground_candidate"])
        if x.get("postcode"): bits.append(x["postcode"])
        if x.get("distance_km") is not None: bits.append(f"separation `{x['distance_km']} km`")
        if x.get("reason"): bits.append(x["reason"])
        L.append(f"- **{x.get('club')}** — "+" • ".join(bits))

L+=["","## ✅ Resolved since earlier verification",""]
if resolved:
    for x in sorted(resolved,key=lambda z:z["club"].lower()):
        L.append(f"- **{x['club']}** — {x.get('ground') or 'Ground TBC'} • {x.get('postcode') or 'Postcode TBC'} — {x['resolution']}")
else:
    L.append("None.")

L+=["","## Rules","",
"- Canonical clubs are excluded from actionable exception counts.",
"- Bishop's Cleeve / Bishops Cleeve is treated as a punctuation/name-format variant, not an unsafe fuzzy match.",
"- 🟢 clears an exception rule only; it is not auto-published.",
"- 🟡 requires one explicit human approval/current-ground check.",
"- 🔴 requires another free/public source or genuine research.",
"- `clubfinder.html` and `competition.json` are untouched by this verification step."
]

REPORT.write_text("\n".join(L)+"\n",encoding="utf8")
print("GROUND EXCEPTION VERIFICATION v7.7.4")
print("Approved candidates:",counts["APPROVED_CANDIDATE"])
print("Human decisions:",counts["HUMAN_DECISION"])
print("Ground research:",counts["GROUND_RESEARCH"])
print("Resolved:",len(resolved))
print("Current actionable total:",active_total)
print("TRIAGE ONLY.")
