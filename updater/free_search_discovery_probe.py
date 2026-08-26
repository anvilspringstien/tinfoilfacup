#!/usr/bin/env python3
import html,json,re,urllib.parse,urllib.request
from datetime import datetime,timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
TESTS=[
 {"id":"original","q":'"Kendal Town" "Heaton Stannington" "FA Cup" "22 August 2026"',
  "want":["footballwebpages.co.uk","kendal-town","heaton-stannington"]},
 {"id":"replay","q":'"Heaton Stannington" "Kendal Town" "FA Cup" "25 August 2026"',
  "want":["footballwebpages.co.uk","heaton-stannington","kendal-town"]}
]
UA="Mozilla/5.0 TinFoilFACupDiscoveryProbe/7.5.6"

def fetch(url,data=None):
 try:
  req=urllib.request.Request(url,data=data,headers={
   "User-Agent":UA,"Accept":"text/html,application/xhtml+xml,*/*",
   "Referer":"https://html.duckduckgo.com/"
  })
  with urllib.request.urlopen(req,timeout=30) as r:
   return r.status,r.geturl(),r.read().decode("utf-8","replace")
 except Exception as e:return 0,url,"ERROR "+repr(e)

def links(body):
 out=[]
 for href in re.findall(r'href=["\']([^"\']+)["\']',body,re.I):
  href=html.unescape(href).replace("\\/","/")
  # DDG redirect links carry target in uddg
  p=urllib.parse.urlparse(href)
  qs=urllib.parse.parse_qs(p.query)
  if "uddg" in qs: href=qs["uddg"][0]
  if href.startswith("http"): out.append(href)
 return list(dict.fromkeys(out))

def run_ddg(q,mode):
 endpoint="https://html.duckduckgo.com/html/" if mode=="html" else "https://lite.duckduckgo.com/lite/"
 data=urllib.parse.urlencode({"q":q,"kl":"uk-en"}).encode()
 st,final,body=fetch(endpoint,data)
 return {"provider":"duckduckgo-"+mode,"status":st,"final_url":final,"bytes":len(body.encode()),"links":links(body)[:50]}

report={"checked_at":datetime.now(timezone.utc).isoformat(),"tests":[]}
for t in TESTS:
 row={"id":t["id"],"query":t["q"],"providers":[],"matches":[]}
 for mode in ("html","lite"):
  p=run_ddg(t["q"],mode); row["providers"].append(p)
  for u in p["links"]:
   low=u.lower()
   if all(x.lower() in low for x in t["want"]):
    row["matches"].append({"provider":p["provider"],"url":u})
 row["matches"]=list({x["provider"]+"|"+x["url"]:x for x in row["matches"]}.values())
 report["tests"].append(row)
 print("\nTEST",t["id"])
 for p in row["providers"]: print(p["provider"],"HTTP",p["status"],"bytes",p["bytes"],"links",len(p["links"]))
 for m in row["matches"]: print("MATCH",m["provider"],m["url"])
 print("PASS" if row["matches"] else "FAIL")

(ROOT/"updater/free-search-discovery-report.json").write_text(json.dumps(report,indent=2)+"\n")
print("\nREAD ONLY. competition.json unchanged.")
