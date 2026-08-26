#!/usr/bin/env python3
import json,re,urllib.request,urllib.parse
from datetime import datetime,timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
START="https://www.thefa.com/competitions/thefacup/results"
UA={"User-Agent":"Mozilla/5.0 TinFoilFACupSDAPIProbe/7.5.3","Accept":"text/html,application/javascript,*/*"}

def get(url):
    try:
        q=urllib.request.Request(url,headers=UA)
        with urllib.request.urlopen(q,timeout=30) as r:
            return r.status,r.headers.get("content-type",""),r.read().decode("utf-8","replace"),r.geturl()
    except Exception as e:
        return 0,"","",url

status,ctype,page,final=get(START)
if status!=200:
    raise SystemExit(f"Start page failed HTTP {status}")

scripts=[urllib.parse.urljoin(final,x) for x in re.findall(r'<script[^>]+src=["\']([^"\']+)["\']',page,re.I)]

needles=[
 "sdapi","getFootballCompetition","getSdapiFootballMatch","AppSettings",
 "eventoptaid","competition_id","season_id","match_status",
 "api.getFootballCompetition","api.getFootballMatch","FeedManager",
 "opta::","sdapi::"
]

contexts=[]
urls=set()
config_strings=set()

seen=set()
for url in scripts[:40]:
    if url in seen: continue
    seen.add(url)
    st,ct,body,resolved=get(url)
    if not body: continue

    # literal URLs
    for u in re.findall(r'https?://[^"\'\s)]+',body):
        low=u.lower()
        if any(k in low for k in ("sdapi","opta","perform","stats","api","hive")):
            urls.add(u.replace("\\/","/"))

    # likely config literals / resource roots
    for m in re.finditer(r'(?i)(?:res|resource|endpoint|baseurl|apiurl|host|hive|sdapi)[A-Za-z0-9_.$:-]{0,40}',body):
        s=max(0,m.start()-250); e=min(len(body),m.end()+500)
        config_strings.add(body[s:e].replace("\\/","/"))

    # bounded context for known API symbols
    for needle in needles:
        pos=0
        while True:
            i=body.lower().find(needle.lower(),pos)
            if i<0: break
            s=max(0,i-700);e=min(len(body),i+1400)
            contexts.append({
                "script":resolved,
                "needle":needle,
                "context":body[s:e].replace("\\/","/")
            })
            pos=i+len(needle)
            if sum(1 for x in contexts if x["needle"]==needle)>=12:
                break

# De-duplicate contexts by exact text.
dedup=[]; seen_ctx=set()
for c in contexts:
    k=(c["needle"],c["context"])
    if k not in seen_ctx:
        seen_ctx.add(k);dedup.append(c)

report={
 "checked_at":datetime.now(timezone.utc).isoformat(),
 "start_url":START,
 "scripts_seen":len(seen),
 "literal_candidate_urls":sorted(urls),
 "contexts":dedup[:180],
 "config_contexts":list(config_strings)[:100]
}
(ROOT/"updater/fa-sdapi-discovery.json").write_text(
    json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8"
)

print("FA SDAPI DISCOVERY v7.5.3")
print("Scripts inspected:",len(seen))
print("Literal candidate URLs:",len(urls))
for u in sorted(urls)[:30]:
    print("URL",u)
print("API contexts captured:",len(dedup))

# Print compact high-value snippets only.
for c in dedup:
    if c["needle"] in ("getFootballCompetition","getSdapiFootballMatch","AppSettings","sdapi::","FeedManager"):
        text=re.sub(r"\s+"," ",c["context"])
        print("CONTEXT",c["needle"],text[:900])
        if sum(1 for x in dedup[:dedup.index(c)+1] if x["needle"]==c["needle"])>=3:
            pass

print("READ ONLY: competition.json unchanged.")
