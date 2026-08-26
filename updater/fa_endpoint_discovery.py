#!/usr/bin/env python3
import json,re,urllib.request,urllib.parse
from datetime import datetime,timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
START="https://www.thefa.com/competitions/thefacup/results"
UA={"User-Agent":"Mozilla/5.0 TinFoilFACupEndpointProbe/7.5.2","Accept":"text/html,application/javascript,*/*"}

def get(url):
    try:
        req=urllib.request.Request(url,headers=UA)
        with urllib.request.urlopen(req,timeout=30) as r:
            return r.status,r.headers.get("content-type",""),r.read().decode("utf-8","replace"),r.geturl()
    except Exception as e:
        return 0,"","",url

def interesting_strings(text):
    pats=[
      r'https?://[^"\'\s)]+',
      r'["\']([^"\']*(?:api|graphql|fixture|result|competition|match|score|live)[^"\']*)["\']'
    ]
    out=set()
    for p in pats:
        for m in re.finditer(p,text,re.I):
            s=m.group(0) if m.lastindex is None else m.group(1)
            s=s.replace("\\/","/").strip()
            if 3<len(s)<500 and not s.startswith("data:"):
                out.add(s)
    return out

status,ctype,html,final=get(START)
if status!=200:
    raise SystemExit(f"Failed to fetch start page: HTTP {status}")

scripts=[]
for src in re.findall(r'<script[^>]+src=["\']([^"\']+)["\']',html,re.I):
    scripts.append(urllib.parse.urljoin(final,src))

report={
 "checked_at":datetime.now(timezone.utc).isoformat(),
 "start_url":START,
 "start_status":status,
 "script_count":len(scripts),
 "scripts":[],
 "candidate_endpoints":[]
}

candidates=set(interesting_strings(html))

# Limit bundle fetches to avoid hammering: first 30 unique scripts.
seen=set()
for url in scripts:
    if url in seen: continue
    seen.add(url)
    if len(report["scripts"])>=30: break
    st,ct,body,resolved=get(url)
    strings=interesting_strings(body) if body else set()
    candidates.update(strings)
    report["scripts"].append({
      "url":resolved,
      "status":st,
      "content_type":ct,
      "bytes":len(body.encode("utf-8")) if body else 0,
      "interesting_count":len(strings)
    })

# Rank useful candidates.
ranked=[]
for s in candidates:
    low=s.lower()
    score=0
    if "api" in low: score+=10
    if "graphql" in low: score+=10
    if "fixture" in low: score+=7
    if "result" in low: score+=7
    if "competition" in low: score+=5
    if "match" in low: score+=4
    if "score" in low: score+=4
    if "live" in low: score+=3
    if "thefa.com" in low: score+=2
    if score:
        ranked.append((score,s))
ranked.sort(key=lambda x:(-x[0],x[1]))

report["candidate_endpoints"]=[{"score":a,"value":b} for a,b in ranked[:300]]

(ROOT/"updater/fa-endpoint-discovery.json").write_text(
    json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8"
)

print("FA ENDPOINT DISCOVERY v7.5.2")
print("Start page:",status,ctype,"scripts:",len(scripts))
print("Bundles inspected:",len(report["scripts"]))
print("Ranked candidates:",len(report["candidate_endpoints"]))
for item in report["candidate_endpoints"][:40]:
    print(item["score"],item["value"])
print("READ ONLY: competition.json unchanged.")
