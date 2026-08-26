#!/usr/bin/env python3
import json,re,urllib.request
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; BASE="https://www.thefa.com"
URLS=[
 ("fixtures-control","/Competitions/Fixtures/Fixtures?competitionId=1&page=1"),
 ("results-endpoint","/Competitions/Fixtures/Results?competitionId=1&page=1"),
 ("results-page","/competitions/thefacup/results"),
 ("qualifying-page","/competitions/thefacup/qualifying-rounds")]
def get(path):
 try:
  q=urllib.request.Request(BASE+path,headers={"User-Agent":"Mozilla/5.0 TinFoilFACupProbe/7.5.1","Accept":"text/html,application/json,*/*"})
  with urllib.request.urlopen(q,timeout=30) as r:return r.status,r.headers.get("content-type",""),r.read().decode("utf-8","replace")
 except Exception as e:return 0,"","ERROR "+repr(e)
def main():
 report={"checked_at":datetime.now(timezone.utc).isoformat(),"probes":[],"endpoint_strings":[]};eps=set()
 for label,path in URLS:
  status,ctype,b=get(path)
  plain=re.sub(r"<[^>]+>"," ",b)
  scores=re.findall(r"\b\d{1,2}\s*[-–:]\s*\d{1,2}\b",plain)[:20]
  p={"label":label,"path":path,"status":status,"content_type":ctype,"bytes":len(b.encode()),"heaton":"Heaton Stannington" in b,"kendal":"Kendal Town" in b,"tie_3R":bool(re.search(r"\b3R\b",b)),"score_samples":scores}
  report["probes"].append(p)
  for x in re.findall(r'["\']([^"\']*(?:fixture|result|competition|match)[^"\']*)["\']',b,re.I):
   if len(x)<300 and not x.startswith("data:"):eps.add(x.replace("\\/","/"))
  print(label,"status",status,"bytes",p["bytes"],"Heaton",p["heaton"],"Kendal",p["kendal"],"3R",p["tie_3R"],"scores",scores[:5])
 report["endpoint_strings"]=sorted(eps)[:500]
 (ROOT/"updater/fa-feed-probe-report.json").write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
 print("Endpoint-like strings:",len(report["endpoint_strings"]))
 print("READ ONLY: competition.json unchanged.")
if __name__=="__main__":main()
