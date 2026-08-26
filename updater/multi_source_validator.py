import json,re,urllib.request,urllib.parse
from pathlib import Path
D=Path(__file__).resolve().parents[1]/"competition.json"
def n(s): return re.sub(r"[^a-z0-9]+"," ",re.sub(r"\\b(fc|afc|cfc)\\b"," ",(s or "").lower())).strip()
def get(u):
 try:
  q=urllib.request.Request(u,headers={"User-Agent":"Mozilla/5.0 TinFoilFACup/7.5.5"})
  return urllib.request.urlopen(q,timeout=25).read().decode("utf8","replace")
 except:return ""
def score(t,h,a):
 t=re.sub(r"\\s+"," ",re.sub(r"<[^>]+>"," ",t));o=set()
 for p in [rf"{re.escape(h)}\\s*(\\d+)\\s*[-–]\\s*(\\d+)\\s*{re.escape(a)}",rf"{re.escape(h)}.{{0,250}}?(\\d+)\\s*[-–]\\s*(\\d+).{{0,250}}?{re.escape(a)}"]:
  for m in re.finditer(p,t,re.I):o.add((int(m.group(1)),int(m.group(2))))
 return o
d=json.loads(D.read_text()); fs=[];seen=set()
for sec in ("fixtures","replays"):
 for f in (d.get(sec,{}) or {}).values():
  if not isinstance(f,dict) or not f.get("home") or not f.get("away"):continue
  k=(n(f["home"]),n(f["away"]),f.get("date",""))
  if k not in seen:seen.add(k);fs.append(f)
rows=[]
for f in fs:
 q=urllib.parse.quote_plus(f'{f["home"]} {f["away"]} {f.get("date","")} FA Cup')
 src={"footballwebpages":"https://www.footballwebpages.co.uk/search?q="+q,"northernleague":"https://www.northernfootballleague.org/?s="+q}
 votes={}
 for name,u in src.items():
  s=score(get(u),f["home"],f["away"])
  if len(s)==1:votes[name]=list(next(iter(s)))
 counts={}
 for v in votes.values():counts[tuple(v)]=counts.get(tuple(v),0)+1
 c=[k for k,v in counts.items() if v>=2]
 status="AUTO-VERIFIED" if len(c)==1 else ("PENDING" if votes else "NO-EVIDENCE")
 rows.append({"home":f["home"],"away":f["away"],"date":f.get("date",""),"votes":votes,"status":status,"consensus_score":list(c[0]) if len(c)==1 else None})
print("Known ties checked:",len(rows));print("AUTO-VERIFIED:",sum(x["status"]=="AUTO-VERIFIED" for x in rows));print("PENDING:",sum(x["status"]=="PENDING" for x in rows));print("NO-EVIDENCE:",sum(x["status"]=="NO-EVIDENCE" for x in rows))
for x in rows:
 if x["status"]!="NO-EVIDENCE":print(x["status"],x["home"],x["votes"],x["away"])
(Path(__file__).parent/"multi-source-validator-report.json").write_text(json.dumps(rows,indent=2))
print("DRY RUN ONLY: competition.json unchanged.")
