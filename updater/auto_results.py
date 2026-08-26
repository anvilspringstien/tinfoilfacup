#!/usr/bin/env python3
import argparse,html as H,json,re,urllib.request
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; DATA=ROOT/"competition.json"
def norm(s):
 s=(s or "").lower().replace("&"," and "); s=re.sub(r"\b(fc|afc|cfc)\b"," ",s)
 return re.sub(r"[^a-z0-9]+"," ",s).strip()
def fetch(u):
 q=urllib.request.Request(u,headers={"User-Agent":"Mozilla/5.0 TinFoilFACupUpdater/7.5"})
 return urllib.request.urlopen(q,timeout=30).read().decode("utf-8","replace")
def textify(x):
 x=re.sub(r"<(script|style)\b[^>]*>.*?</\1>"," ",x,flags=re.I|re.S)
 return "\n".join(y.strip() for y in H.unescape(re.sub(r"<[^>]+>","\n",x)).splitlines() if y.strip())
def ties(d):
 out=[];seen=set()
 for sec in ("fixtures","replays"):
  vals=(d.get(sec,{}) or {}).values()
  for f in vals:
   if not isinstance(f,dict) or not f.get("home") or not f.get("away"):continue
   k=(norm(f["home"]),norm(f["away"]),f.get("date",""))
   if k not in seen:seen.add(k);out.append(f)
 return out
def candidates(txt,home,away):
 ls=txt.splitlines();out=[]
 for i,line in enumerate(ls):
  if norm(home) not in norm(line):continue
  w=" ".join(ls[i:i+12])
  if norm(away) not in norm(w):continue
  for p in (rf"{re.escape(home)}\s*(\d+)\s*[-–:]\s*(\d+)\s*{re.escape(away)}",rf"{re.escape(home)}\s*\(?(\d+)\)?\s+.*?{re.escape(away)}\s*\(?(\d+)\)?"):
   m=re.search(p,w,re.I)
   if m:out.append((int(m.group(1)),int(m.group(2))))
 return set(out)
def same(a,b):
 return norm(a.get("home"))==norm(b.get("home")) and norm(a.get("away"))==norm(b.get("away")) and str(a.get("date",""))==str(b.get("date","")) and str(a.get("home_score",""))==str(b.get("home_score","")) and str(a.get("away_score",""))==str(b.get("away_score",""))
def merge(d,r):
 for club in {r["home"],r["away"],re.sub(r"\s+(FC|AFC|CFC)$","",r["home"],flags=re.I),re.sub(r"\s+(FC|AFC|CFC)$","",r["away"],flags=re.I)}:
  a=d.setdefault("result_history",{}).setdefault(club,[])
  if not any(same(x,r) for x in a):a.append(r);a.sort(key=lambda x:x.get("date",""))
  d.setdefault("results",{})[club]=r
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--url",default="https://www.thefa.com/competitions/thefacup/results");ap.add_argument("--publish",action="store_true");a=ap.parse_args()
 d=json.loads(DATA.read_text());txt=textify(fetch(a.url));new=[];amb=[]
 existing=sum((v for v in (d.get("result_history",{}) or {}).values() if isinstance(v,list)),[])
 for f in ties(d):
  c=candidates(txt,f["home"],f["away"])
  if len(c)>1:amb.append([f["home"],f["away"],sorted(c)]);continue
  if len(c)!=1:continue
  hs,as_=next(iter(c)); winner=f["home"] if hs>as_ else f["away"] if as_>hs else ""
  r={"home":f["home"],"away":f["away"],"home_score":hs,"away_score":as_,"winner":winner,"status":"FT","decision":"","date":f.get("date",""),"round":f.get("round","FA Cup"),"source_url":a.url}
  if not any(same(x,r) for x in existing):new.append(r)
 print("Known ties checked:",len(ties(d)));print("New unambiguous results:",len(new));print("Ambiguous ties rejected:",len(amb))
 for r in new:print(r["home"],r["home_score"],"-",r["away_score"],r["away"])
 report={"checked_at":datetime.now(timezone.utc).isoformat(),"source_url":a.url,"new_results":new,"ambiguous":amb}
 (ROOT/"updater/results-pilot-report.json").write_text(json.dumps(report,indent=2)+"\n")
 if a.publish and amb:raise SystemExit("Publication blocked: ambiguous candidates.")
 if a.publish:
  for r in new:merge(d,r)
  if new:d["updated_at"]=datetime.now(timezone.utc).isoformat();DATA.write_text(json.dumps(d,indent=2,ensure_ascii=False)+"\n")
  print("PUBLISHED:",len(new))
 else:print("DRY RUN: competition.json unchanged.")
if __name__=="__main__":main()
