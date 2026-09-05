#!/usr/bin/env python3
"""Guarded FA Cup result importer with independent fallback parsing.

Primary source remains configurable. FootballWebPages is also parsed structurally
against the canonical tie list. A source containing FT rows is not allowed to
silently yield zero parsed results: that is treated as a parser/source-health
failure rather than a green run.
"""
import argparse,html as H,json,re,urllib.request
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; DATA=ROOT/"competition.json"
FWP_URL="https://www.footballwebpages.co.uk/fa-cup/fixtures-results/first-qualifying-round"


def norm(s):
 s=(s or "").lower().replace("&"," and "); s=re.sub(r"\b(fc|afc|cfc)\b"," ",s)
 return re.sub(r"[^a-z0-9]+"," ",s).strip()


def fetch(u):
 q=urllib.request.Request(u,headers={"User-Agent":"Mozilla/5.0 TinFoilFACupUpdater/7.6","Accept":"text/html,application/xhtml+xml"})
 return urllib.request.urlopen(q,timeout=30).read().decode("utf-8","replace")


def textify(x):
 x=re.sub(r"<(script|style)\b[^>]*>.*?</\1>"," ",x,flags=re.I|re.S)
 return "\n".join(y.strip() for y in H.unescape(re.sub(r"<[^>]+>","\n",x)).splitlines() if y.strip())


def clean(x):
 return " ".join(H.unescape(re.sub(r"<[^>]+>"," ",x)).replace("\xa0"," ").split())


def cells(row):
 return [clean(x) for x in re.findall(r"<t[dh]\b[^>]*>(.*?)</t[dh]>",row,re.I|re.S)]


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


def score_cell(s):
 # FWP commonly renders seed positions in parentheses around the real score.
 m=re.fullmatch(r"(?:\(\d+\)\s*)?(\d+)(?:\s*\(\d+\))?",(s or "").strip())
 return int(m.group(1)) if m else None


def parse_fwp(html,known):
 """Parse completed FWP rows, then require each row to map to one canonical tie."""
 parsed=[]; unmatched=[]; ft_rows=0; current_date=""
 for row in re.findall(r"<tr\b[^>]*>.*?</tr>",html,re.I|re.S):
  c=[x for x in cells(row) if x]
  if not c:continue
  heading=" ".join(c)
  dm=re.search(r"(\d{1,2})(?:st|nd|rd|th)?\s+([A-Za-z]+)\s+(20\d{2})",heading)
  if dm:
   try: current_date=datetime.strptime(f"{dm.group(1)} {dm.group(2)} {dm.group(3)}","%d %B %Y").date().isoformat()
   except ValueError: pass
  try: fi=next(i for i,x in enumerate(c) if x.upper().startswith("FT"))
  except StopIteration: continue
  ft_rows+=1
  tail=c[fi+1:]
  pair=None
  for i in range(len(tail)-1):
   a=score_cell(tail[i]); b=score_cell(tail[i+1])
   if a is not None and b is not None and i>=1 and i+2<len(tail):
    pair=(i,a,b); break
  if not pair:continue
  i,hs,as_=pair
  home=" ".join(tail[:i]).strip(); away=tail[i+2].strip()
  # Attendance is after away and therefore ignored.
  if not home or not away:continue
  match=next((f for f in known if norm(f.get("home"))==norm(home) and norm(f.get("away"))==norm(away)),None)
  if not match:
   unmatched.append([home,away]); continue
  date=match.get("date","") or current_date
  winner=match["home"] if hs>as_ else match["away"] if as_>hs else ""
  parsed.append({"home":match["home"],"away":match["away"],"home_score":hs,"away_score":as_,"winner":winner,"status":"FT","decision":"","date":date,"round":match.get("round","FA Cup"),"source_url":FWP_URL})
 return parsed,unmatched,ft_rows


def same(a,b):
 return norm(a.get("home"))==norm(b.get("home")) and norm(a.get("away"))==norm(b.get("away")) and str(a.get("date",""))==str(b.get("date","")) and str(a.get("home_score",""))==str(b.get("home_score","")) and str(a.get("away_score",""))==str(b.get("away_score",""))


def merge(d,r):
 for club in {r["home"],r["away"],re.sub(r"\s+(FC|AFC|CFC)$","",r["home"],flags=re.I),re.sub(r"\s+(FC|AFC|CFC)$","",r["away"],flags=re.I)}:
  a=d.setdefault("result_history",{}).setdefault(club,[])
  old=next((x for x in a if same(x,r)),None)
  if not old:a.append(r);a.sort(key=lambda x:x.get("date",""))
  d.setdefault("results",{})[club]=r


def dedupe(rs):
 out={}
 for r in rs:out[(norm(r["home"]),norm(r["away"]),r.get("home_score"),r.get("away_score"))]=r
 return list(out.values())


def main():
 ap=argparse.ArgumentParser();ap.add_argument("--url",default="https://www.thefa.com/competitions/thefacup/results");ap.add_argument("--publish",action="store_true");a=ap.parse_args()
 d=json.loads(DATA.read_text()); known=ties(d); existing=sum((v for v in (d.get("result_history",{}) or {}).values() if isinstance(v,list)),[])

 primary_html=fetch(a.url); txt=textify(primary_html); primary=[]; amb=[]
 for f in known:
  c=candidates(txt,f["home"],f["away"])
  if len(c)>1:amb.append([f["home"],f["away"],sorted(c)]);continue
  if len(c)!=1:continue
  hs,as_=next(iter(c)); winner=f["home"] if hs>as_ else f["away"] if as_>hs else ""
  primary.append({"home":f["home"],"away":f["away"],"home_score":hs,"away_score":as_,"winner":winner,"status":"FT","decision":"","date":f.get("date",""),"round":f.get("round","FA Cup"),"source_url":a.url})

 fallback_html=fetch(FWP_URL); fallback,unmatched,ft_rows=parse_fwp(fallback_html,known)
 if ft_rows and not fallback:
  raise SystemExit(f"Parser health failure: FWP contains {ft_rows} FT rows but zero canonical results were parsed.")
 if unmatched:
  raise SystemExit("Publication blocked: FWP completed rows did not map to canonical ties: "+str(unmatched[:10]))

 # Cross-source agreement is required whenever both sources detect the same tie.
 by_tie={}
 disagreements=[]
 for source_name,rows in (("primary",primary),("fallback",fallback)):
  for r in rows:
   k=(norm(r["home"]),norm(r["away"]))
   if k in by_tie and (by_tie[k][1]["home_score"],by_tie[k][1]["away_score"])!=(r["home_score"],r["away_score"]):
    disagreements.append([r["home"],r["away"],by_tie[k][0],by_tie[k][1]["home_score"],by_tie[k][1]["away_score"],source_name,r["home_score"],r["away_score"]])
   else: by_tie[k]=(source_name,r)
 if disagreements:raise SystemExit("Publication blocked: sources disagree: "+str(disagreements[:10]))

 detected=dedupe(primary+fallback)
 new=[r for r in detected if not any(same(x,r) for x in existing)]
 print("Known ties checked:",len(known));print("Primary results detected:",len(primary));print("Fallback FT rows seen:",ft_rows);print("Fallback canonical results detected:",len(fallback));print("New unambiguous results:",len(new));print("Ambiguous ties rejected:",len(amb))
 for r in new:print(r["home"],r["home_score"],"-",r["away_score"],r["away"])
 report={"checked_at":datetime.now(timezone.utc).isoformat(),"primary_source_url":a.url,"fallback_source_url":FWP_URL,"known_ties":len(known),"primary_results_detected":len(primary),"fallback_ft_rows":ft_rows,"fallback_results_detected":len(fallback),"new_results":new,"ambiguous":amb,"unmatched_fallback_rows":unmatched,"source_disagreements":disagreements}
 (ROOT/"updater/results-pilot-report.json").write_text(json.dumps(report,indent=2)+"\n")
 if a.publish and amb:raise SystemExit("Publication blocked: ambiguous primary candidates.")
 if a.publish:
  for r in new:merge(d,r)
  if new:d["updated_at"]=datetime.now(timezone.utc).isoformat();DATA.write_text(json.dumps(d,indent=2,ensure_ascii=False)+"\n")
  print("PUBLISHED:",len(new))
 else:print("DRY RUN: competition.json unchanged.")
if __name__=="__main__":main()
