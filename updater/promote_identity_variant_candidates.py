#!/usr/bin/env python3
import argparse,json,re
from pathlib import Path
from datetime import datetime,timezone

ROOT=Path(__file__).resolve().parents[1]
HTML=ROOT/"clubfinder.html"
CONF=ROOT/"updater/identity-variant-confirmation.json"
DISC=ROOT/"updater/ground-discovery-queue.json"
OUT=ROOT/"updater/identity-variant-promotion.json"
REPORT=ROOT/"ground-identity-variant-promotion.md"


def norm(s):
    s=(s or "").lower().replace("&"," and ").replace("’","'").replace("'","")
    s=re.sub(r"\b(fc|afc|cfc|football club)\b"," ",s)
    return re.sub(r"[^a-z0-9]+"," ",s).strip()


def locate_array(text,name):
    m=re.search(r"\b(?:const|let|var)\s+"+re.escape(name)+r"\s*=\s*\[",text)
    if not m: raise SystemExit("Safety stop: could not locate "+name+" in clubfinder.html")
    s=text.find("[",m.start()); depth=0; ins=False; esc=False; q=""
    for i in range(s,len(text)):
        ch=text[i]
        if ins:
            if esc: esc=False
            elif ch=="\\": esc=True
            elif ch==q: ins=False
        else:
            if ch in ("'",'\"'): ins=True; q=ch
            elif ch=="[": depth+=1
            elif ch=="]":
                depth-=1
                if depth==0:return s,i+1
    raise SystemExit("Safety stop: unbalanced "+name+" array")


ap=argparse.ArgumentParser()
ap.add_argument("--publish",action="store_true")
a=ap.parse_args()

if not CONF.exists(): raise SystemExit("Missing updater/identity-variant-confirmation.json. Run v7.7.9 first.")
if not DISC.exists(): raise SystemExit("Missing updater/ground-discovery-queue.json.")

conf=json.loads(CONF.read_text(encoding="utf8"))
if conf.get("version")!="7.7.9" or conf.get("confirmed_count")!=3 or conf.get("held_count")!=0:
    raise SystemExit("Safety stop: v7.7.9 confirmation is not the expected clean 3/0 state.")
rows=conf.get("records",[])
if len(rows)!=3 or any(r.get("decision")!="IDENTITY_CONFIRMED" for r in rows):
    raise SystemExit("Safety stop: all three records must be IDENTITY_CONFIRMED.")

disc=json.loads(DISC.read_text(encoding="utf8"))
queue=disc.get("queue",[])

text=HTML.read_text(encoding="utf8")
s,e=locate_array(text,"GROUNDS")
grounds=json.loads(text[s:e])
existing={norm(g.get("name") or g.get("club")) for g in grounds}

ready=[]; held=[]; skipped=[]
for r in rows:
    club=r.get("club")
    if norm(club) in existing:
        skipped.append({"club":club,"reason":"Canonical GROUNDS record already exists; overwrite prohibited"})
        continue

    hits=[x for x in queue if norm(x.get("eligible_club"))==norm(club)]
    if len(hits)!=1:
        held.append({"club":club,"reason":f"Expected exactly one discovery candidate; found {len(hits)}"})
        continue
    q=hits[0]

    if (q.get("postcode") or "").upper().strip()!=(r.get("postcode") or "").upper().strip():
        held.append({"club":club,"reason":"Discovery postcode no longer matches confirmed current postcode"})
        continue
    if q.get("lat") is None or q.get("lon") is None:
        held.append({"club":club,"reason":"Discovery candidate has no coordinates"})
        continue
    if norm(q.get("club"))!=norm(r.get("fchd_match")):
        held.append({"club":club,"reason":"Discovery FCHD identity no longer matches v7.7.9 confirmation"})
        continue

    rec={
        "name":club,
        "ground":r.get("current_ground"),
        "postcode":r.get("postcode"),
        "lat":q.get("lat"),
        "lon":q.get("lon"),
        "verification":"verified",
        "verification_label":"✅ Verified",
        "source":"v7.7.9 identity confirmation + FCHD 2025-26 coordinate candidate",
        "ground_source":r.get("evidence_url"),
        "coordinate_source":q.get("source") or "FCHD 2025-26 Gazetteer",
        "identity_validation":"v7.7.9",
        "fchd_identity":r.get("fchd_match"),
    }
    if not rec["ground"] or not rec["postcode"]:
        held.append({"club":club,"reason":"Confirmed current ground/postcode incomplete"})
        continue
    ready.append(rec)

published=False
if a.publish:
    if held or skipped:
        raise SystemExit("Safety stop: held/skipped records exist; nothing published.")
    grounds.extend(ready)
    HTML.write_text(text[:s]+json.dumps(grounds,ensure_ascii=False,separators=(",",":"))+text[e:],encoding="utf8")
    published=True

payload={
    "checked_at":datetime.now(timezone.utc).isoformat(),
    "version":"7.8.0",
    "mode":"PUBLISH" if a.publish else "DRY RUN",
    "confirmed_identity_candidates":len(rows),
    "ready_to_promote":len(ready),
    "held":len(held),
    "skipped_safety":len(skipped),
    "overwrites":0,
    "published":published,
    "promotion_records":ready,
    "held_records":held,
    "skipped_records":skipped,
}
OUT.write_text(json.dumps(payload,indent=2,ensure_ascii=False)+"\n",encoding="utf8")

L=[
"# Tin Foil FA Cup — Identity Variant Promotion","",
f"Last checked: **{datetime.now(timezone.utc).strftime('%d/%m/%Y, %H:%M:%S UTC')}**","",
f"Mode: **{payload['mode']}**","",
f"- Confirmed identity candidates: **{len(rows)}**",
f"- Ready to promote: **{len(ready)}**",
f"- Held: **{len(held)}**",
f"- Skipped by safety checks: **{len(skipped)}**",
"- Existing canonical records overwritten: **0**",
f"- Published: **{'YES' if published else 'NO'}**","",
"## Promotion records",""
]
for x in ready:
    L.append(f"- **{x['name']}** — {x['ground']} • {x['postcode']} • `{x['lat']}, {x['lon']}` • identity confirmed by v7.7.9")
L += ["","## Held / skipped",""]
if held:
    for x in held:L.append(f"- **{x['club']}** — {x['reason']}")
if skipped:
    for x in skipped:L.append(f"- **{x['club']}** — {x['reason']}")
if not held and not skipped:L.append("None.")
L += ["","## Safety","",
"- Only the three clean v7.7.9 `IDENTITY_CONFIRMED` records are eligible.",
"- Discovery FCHD identity and postcode must still match the confirmation exactly.",
"- Coordinates come from the persisted FCHD discovery candidate; current ground naming comes from v7.7.9 evidence.",
"- Pershore therefore keeps the confirmed current venue name rather than reverting to the older FCHD sponsor name.",
"- Existing canonical `GROUNDS` records are never overwritten.",
"- `competition.json` is untouched."
]
REPORT.write_text("\n".join(L)+"\n",encoding="utf8")

print("IDENTITY VARIANT PROMOTION v7.8.0")
print("Mode:","PUBLISH" if a.publish else "DRY RUN")
print("Confirmed identity candidates:",len(rows))
print("Ready to promote:",len(ready))
print("Held:",len(held))
print("Skipped by safety checks:",len(skipped))
print("Existing canonical records overwritten: 0")
print("Published:","YES" if published else "NO")
