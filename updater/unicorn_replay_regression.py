#!/usr/bin/env python3
import json,re,math
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
HTML=ROOT/"clubfinder.html"

def norm(s):
    s=str(s or "").lower().replace("&"," and ")
    s=re.sub(r"\b(fc|afc|cfc|football club)\b"," ",s)
    return re.sub(r"[^a-z0-9]+"," ",s).strip()

def locate(text,name):
    m=re.search(r"\b(?:const|let|var)\s+"+re.escape(name)+r"\s*=\s*\[",text)
    if not m: raise SystemExit("UNICORN REGRESSION: missing "+name)
    s=text.find("[",m.start()); depth=0; ins=False; esc=False; quote=""
    for i in range(s,len(text)):
        ch=text[i]
        if ins:
            if esc: esc=False
            elif ch=="\\": esc=True
            elif ch==quote: ins=False
        else:
            if ch in ("'",'"'): ins=True; quote=ch
            elif ch=="[": depth+=1
            elif ch=="]":
                depth-=1
                if depth==0:return json.loads(text[s:i+1])
    raise SystemExit("UNICORN REGRESSION: unbalanced "+name)

def require(ok,msg):
    if not ok: raise SystemExit("UNICORN REGRESSION: FAIL - "+msg)

text=HTML.read_text(encoding="utf-8")
eligible=locate(text,"ELIGIBLE")
grounds=locate(text,"GROUNDS")
supplemental=locate(text,"LAW2_ORIGIN_LOCATIONS")
gclubs=[x for x in eligible if norm(x.get("name"))=="gloucester city"]
require(len(gclubs)==1 and gclubs[0]["name"]=="Gloucester City AFC","current display identity is not Gloucester City AFC")
gg=[x for x in grounds if norm(x.get("name") or x.get("club"))=="gloucester city"]
sg=[x for x in supplemental if norm(x.get("name") or x.get("club"))=="gloucester city"]
current_gloucester=gg+sg
require(len(current_gloucester)==1,"Gloucester current ground is missing/ambiguous across GROUNDS/Law2")
require(current_gloucester[0].get("ground")=="The KMM Energy Stadium" and current_gloucester[0].get("postcode")=="GL2 5HD","Gloucester current ground/postcode drifted")
require(current_gloucester[0].get("verification")=="verified","Gloucester current ground is not verified")

# Reproduce the user's GL1 1AJ canary from its published postcode centroid.
# Gloucester City need not be the nearest club, but it must appear in the
# nearest three under its current AFC identity and current KMM ground record.
def hav_miles(a,b):
    r=3958.7613
    p1,p2=math.radians(a[0]),math.radians(b[0])
    dp=math.radians(b[0]-a[0]); dl=math.radians(b[1]-a[1])
    h=math.sin(dp/2)**2+math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 2*r*math.atan2(math.sqrt(h),math.sqrt(1-h))
locations={norm(x.get("name") or x.get("club")):x for x in supplemental}
locations.update({norm(x.get("name") or x.get("club")):x for x in grounds})
origin=(51.861614,-2.221328)
ranked=[]
for club in eligible:
    g=locations.get(norm(club.get("name")))
    if not g: continue
    try: point=(float(g.get("lat")),float(g.get("lon")))
    except (TypeError,ValueError): continue
    ranked.append((hav_miles(origin,point),club.get("name"),g))
ranked.sort(key=lambda x:x[0])
top3=ranked[:3]
require(any(name=="Gloucester City AFC" and g.get("postcode")=="GL2 5HD" for _,name,g in top3),"GL1 1AJ nearest-three canary does not return Gloucester City AFC at GL2 5HD")

m=re.search(r"const EMBEDDED_COMPETITION_DATA=(\{.*?\});\s*/\* TIN_FOIL_EMBEDDED_COMPETITION_END \*/",text,re.S)
require(bool(m),"embedded competition snapshot missing")
data=json.loads(m.group(1))

hist=[]
for bucket in (data.get("result_history") or {}).values():
    if isinstance(bucket,list):
        for row in bucket:
            if isinstance(row,dict) and {norm(row.get("home")),norm(row.get("away"))}=={"woodford town","mulbarton wanderers"}:
                hist.append(row)

voided=[r for r in hist if r.get("date")=="2026-09-19" and str(r.get("status") or "").upper() in {"VOID","VOIDED"} and r.get("decision")=="voided-replay-ordered"]
replay=[r for r in hist if r.get("date")=="2026-09-29" and r.get("round")=="Second Round Qualifying Replay" and norm(r.get("home"))=="mulbarton wanderers" and r.get("home_score")==2 and r.get("away_score")==0 and norm(r.get("winner"))=="mulbarton wanderers"]
require(bool(voided),"superseded 19 September result is not explicitly voided")
require(bool(replay),"29 September Mulbarton 2-0 replay result missing")

fixtures=list((data.get("fixtures") or {}).values()) if isinstance(data.get("fixtures"),dict) else (data.get("fixtures") or [])
require(not any(f.get("round")=="Third Round Qualifying" for f in fixtures),
        "post-promotion canary expected active fixtures to have advanced beyond Third Qualifying")
archived=(data.get("round_fixtures") or {}).get("Third Round Qualifying") or []
archived=list(archived.values()) if isinstance(archived,dict) else archived
third=[f for f in archived if f.get("round")=="Third Round Qualifying" and f.get("date")=="2026-10-03" and norm(f.get("home"))=="mulbarton wanderers" and norm(f.get("away"))=="gloucester city"]
require(bool(third),"archived Mulbarton v Gloucester City Third Qualifying slot missing")
require(all((f.get("venue") or {}).get("postcode")=="NR14 8AE" for f in third),"archived Third Qualifying home venue is not Mulberry Park NR14 8AE")
require(all(f.get("round")=="Fourth Round Qualifying" for f in fixtures),
        "active fixture set is not protected Fourth Round Qualifying state")
require(len(fixtures)==32,"active Fourth Round Qualifying draw is not exactly 32 ties")

require("voided-replay-ordered" in text and "status==='VOID'" in text,"Clubfinder void-result guard missing")
print("UNICORN REGRESSION: PASS")
print("19 September result: VOIDED / replay ordered")
print("29 September replay: Mulbarton Wanderers 2-0 Woodford Town")
print("3 October archived TRQ: Mulbarton Wanderers v Gloucester City AFC")
print("Active FQR draw: 32 ties / untouched")
print("Gloucester current ground: The KMM Energy Stadium • GL2 5HD")
print("GL1 1AJ nearest three:", " | ".join(name for _,name,_ in top3))
