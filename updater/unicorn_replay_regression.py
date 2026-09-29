#!/usr/bin/env python3
import json,re
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
gclubs=[x for x in eligible if norm(x.get("name"))=="gloucester city"]
require(len(gclubs)==1 and gclubs[0]["name"]=="Gloucester City AFC","current display identity is not Gloucester City AFC")
gg=[x for x in grounds if norm(x.get("name") or x.get("club"))=="gloucester city"]
require(len(gg)==1,"Gloucester current ground is missing/ambiguous")
require(gg[0].get("ground")=="The KMM Energy Stadium" and gg[0].get("postcode")=="GL2 5HD","Gloucester current ground/postcode drifted")
require(gg[0].get("verification")=="verified","Gloucester current ground is not verified")

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
third=[f for f in fixtures if f.get("round")=="Third Round Qualifying" and f.get("date")=="2026-10-03" and norm(f.get("home"))=="mulbarton wanderers" and norm(f.get("away"))=="gloucester city"]
require(bool(third),"Mulbarton v Gloucester City Third Qualifying slot missing")
require(all((f.get("venue") or {}).get("postcode")=="NR14 8AE" for f in third),"Third Qualifying home venue is not Mulberry Park NR14 8AE")

require("voided-replay-ordered" in text and "status==='VOID'" in text,"Clubfinder void-result guard missing")
print("UNICORN REGRESSION: PASS")
print("19 September result: VOIDED / replay ordered")
print("29 September replay: Mulbarton Wanderers 2-0 Woodford Town")
print("3 October: Mulbarton Wanderers v Gloucester City AFC")
print("Gloucester current ground: The KMM Energy Stadium • GL2 5HD")
