#!/usr/bin/env python3
"""Apply the reviewed current Gloucester City identity/ground correction.

Internal matching remains suffix-insensitive; this patch changes only the
current Clubfinder-facing club name/location records. Historical match venues
are not rewritten.
"""
from pathlib import Path
import json,re

ROOT=Path(__file__).resolve().parents[1]
P=ROOT/"clubfinder.html"
SOURCE="https://www.gloucestercityafc.com/tigerturfstadium"

def norm(s):
    s=str(s or "").lower().replace("&"," and ")
    s=re.sub(r"\b(fc|afc|cfc|football club)\b"," ",s)
    return re.sub(r"[^a-z0-9]+"," ",s).strip()

def locate(text,name):
    m=re.search(r"\b(?:const|let|var)\s+"+re.escape(name)+r"\s*=\s*\[",text)
    if not m: raise SystemExit("ABORT: "+name+" missing")
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
                if depth==0:return s,i+1
    raise SystemExit("ABORT: unbalanced "+name)

def replace_array(text,name,mutate):
    s,e=locate(text,name)
    rows=json.loads(text[s:e])
    mutate(rows)
    return text[:s]+json.dumps(rows,ensure_ascii=False,separators=(",",":")).replace("</","<\\/")+text[e:]

def one(rows,label):
    matches=[r for r in rows if norm(r.get("name") or r.get("club"))=="gloucester city"]
    if len(matches)!=1: raise SystemExit(f"ABORT: expected one Gloucester City record in {label}, got {len(matches)}")
    return matches[0]

text=P.read_text(encoding="utf-8")

def eligible(rows):
    r=one(rows,"ELIGIBLE")
    r["name"]="Gloucester City AFC"

def current_location(rows):
    r=one(rows,"current location layer")
    r["name"]="Gloucester City AFC"
    r["ground"]="The KMM Energy Stadium"
    r["postcode"]="GL2 5HD"
    r["lat"]=51.860888
    r["lon"]=-2.260038
    r["verification"]="verified"
    r["verification_label"]="✅ Verified"
    r["source"]=SOURCE
    r["ground_source"]="Current official Gloucester City AFC stadium information"
    r["coordinate_source"]="ONS postcode centroid for GL2 5HD"

text=replace_array(text,"ELIGIBLE",eligible)
text=replace_array(text,"GROUNDS",current_location)
text=replace_array(text,"LAW2_ORIGIN_LOCATIONS",current_location)
P.write_text(text,encoding="utf-8")
print("GLOUCESTER CURRENT IDENTITY: Gloucester City AFC")
print("GLOUCESTER CURRENT GROUND: The KMM Energy Stadium • GL2 5HD")
print("Historical match venues: UNTOUCHED")
