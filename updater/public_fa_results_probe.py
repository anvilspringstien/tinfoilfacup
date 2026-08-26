#!/usr/bin/env python3
import json,re,urllib.request,urllib.parse
from datetime import datetime,timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
URLS=[
 "https://www.thefa.com/competitions/thefacup/results",
 "https://www.thefa.com/competitions/the-emirates-fa-cup/results",
 "https://www.thefa.com/competitions/thefacup/qualifying-rounds",
 "https://www.thefa.com/Competitions/Fixtures/Fixtures?competitionId=1&page=1",
]
UA={"User-Agent":"Mozilla/5.0 TinFoilFACupPublicResultsProbe/7.5.4","Accept":"text/html,*/*"}

def get(u):
 try:
  q=urllib.request.Request(u,headers=UA)
  with urllib.request.urlopen(q,timeout=30) as r:
   return r.status,r.geturl(),r.headers.get("content-type",""),r.read().decode("utf-8","replace")
 except Exception as e:return 0,u,"","ERROR "+repr(e)

def clean(x):
 x=re.sub(r"<script\b[^>]*>.*?</script>"," ",x,flags=re.I|re.S)
 x=re.sub(r"<style\b[^>]*>.*?</style>"," ",x,flags=re.I|re.S)
 x=re.sub(r"<[^>]+>","\n",x)
 return "\n".join(s.strip() for s in x.splitlines() if s.strip())

def contexts(text,needle,span=450):
 out=[];low=text.lower();n=needle.lower();p=0
 while True:
  i=low.find(n,p)
  if i<0:break
  out.append(re.sub(r"\s+"," ",text[max(0,i-span):min(len(text),i+len(needle)+span)]))
  p=i+len(n)
 return out[:12]

report={"checked_at":datetime.now(timezone.utc).isoformat(),"pages":[]}
for u in URLS:
 st,final,ct,raw=get(u);txt=clean(raw)
 item={"url":u,"final_url":final,"status":st,"content_type":ct,"bytes":len(raw.encode()),
       "heaton":contexts(txt,"Heaton Stannington"),
       "kendal":contexts(txt,"Kendal Town"),
       "score_2_2":contexts(txt,"2-2"),
       "score_4_2":contexts(txt,"4-2"),
       "replay_3R":contexts(txt,"3R"),
       "ft_samples":re.findall(r"(?:FT|AET(?:\+P)?)\s+.{0,100}",txt,re.I)[:20]}
 report["pages"].append(item)
 print("\nPAGE",u,"\nHTTP",st,"bytes",item["bytes"])
 print("Heaton contexts",len(item["heaton"]),"Kendal",len(item["kendal"]),"2-2",len(item["score_2_2"]),"4-2",len(item["score_4_2"]),"3R",len(item["replay_3R"]))
 for label in ("heaton","score_2_2","score_4_2","replay_3R"):
  for x in item[label][:3]: print(label.upper(),x[:700])

(ROOT/"updater/public-fa-results-probe.json").write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
print("\nREAD ONLY: competition.json unchanged.")
