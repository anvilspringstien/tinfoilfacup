#!/usr/bin/env python3
"""Guarded FA Cup result importer with independent fallback parsing.

Primary source remains configurable. Football Web Pages is parsed structurally
against the canonical First Qualifying tie list from two complementary views:

* the fixed First Qualifying round page, which is strict and protects coverage;
* the current FA Cup page, which supplements replay results that can appear
  after the original round page has stopped changing.

The supplemental page is allowed to contain unrelated later-round rows, but a
result is accepted from it only when it maps back to a canonical First
Qualifying pair. This lets postponed replays resolve naturally without weakening
the fail-closed checks on the canonical round source.
"""
import argparse,html as H,json,re,urllib.request
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; DATA=ROOT/"competition.json"
FWP_ROUND_URL="https://www.footballwebpages.co.uk/fa-cup/fixtures-results/first-qualifying-round"
FWP_LIVE_URL="https://www.footballwebpages.co.uk/fa-cup"
SCAN_ROUND="First Round Qualifying"


def norm(s):
 s=(s or "").lower().replace('&',' and '); s=re.sub(r"\b(fc|afc|cfc)\b",' ',s)
 return re.sub(r'[^a-z0-9]+',' ',s).strip()


def strip_seed(s):
 return re.sub(r"^\(\d+\)\s*|\s*\(\d+\)$","",(s or "").strip()).strip()


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


def fixture_values(src):
 vals=src.values() if isinstance(src,dict) else (src or [])
 return [f for f in vals if isinstance(f,dict) and f.get("home") and f.get("away")]


def ties(d):
 """Return the canonical First Qualifying scan set even after active-round promotion."""
 out=[];seen=set()
 archive=(d.get("round_fixtures") or {}).get(SCAN_ROUND)
 if archive is not None:
  sources=[archive]
 elif d.get("source_round")==SCAN_ROUND:
  sources=[d.get("fixtures") or {}]
 else:
  sources=[]

 # Replay fixtures are kept separately from the archived original draw. Include
 # only First Qualifying replay records so a later active round cannot pollute the
 # fixed First Qualifying fallback scan.
 replay_src=[]
 for f in fixture_values(d.get("replays") or {}):
  rnd=str(f.get("round") or "")
  if not rnd or SCAN_ROUND.lower() in rnd.lower(): replay_src.append(f)
 sources.append(replay_src)

 for src in sources:
  for f in fixture_values(src):
   k=(norm(f["home"]),norm(f["away"]),f.get("date",""),f.get("round",""))
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


def date_from_text(text):
 dm=re.search(r"(\d{1,2})(?:st|nd|rd|th)?\s+([A-Za-z]+)\s+(20\d{2})",text or "")
 if not dm:return ""
 try:return datetime.strptime(f"{dm.group(1)} {dm.group(2)} {dm.group(3)}","%d %B %Y").date().isoformat()
 except ValueError:return ""


def parse_fwp(html,known,source_url,strict_unmatched=True):
 """Parse completed FWP rows and map them to canonical First Qualifying ties.

 Strict round pages fail on any completed row that cannot be mapped. A live
 supplemental page may contain later-round rows, so unrelated rows there are
 ignored; mapped rows are still required to match one canonical pair exactly or
 in reversed replay orientation.
 """
 parsed=[]; unmatched=[]; ft_rows=0
 # Date headings on the live/current page can sit outside the fixture <tr>, so
 # seed a page-level date and allow row-level headings to override it.
 current_date=date_from_text(clean(html))
 for row in re.findall(r"<tr\b[^>]*>.*?</tr>",html,re.I|re.S):
  c=[x for x in cells(row) if x]
  if not c:continue
  row_date=date_from_text(" ".join(c))
  if row_date:current_date=row_date
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
  home=strip_seed(" ".join(tail[:i]).strip()); away=strip_seed(tail[i+2].strip())
  if not home or not away:continue
  match=next((f for f in known if norm(f.get("home"))==norm(home) and norm(f.get("away"))==norm(away)),None)
  reverse_replay=False
  if not match:
   match=next((f for f in known if norm(f.get("home"))==norm(away) and norm(f.get("away"))==norm(home)),None)
   reverse_replay=match is not None
  if not match:
   if strict_unmatched:unmatched.append([home,away])
   continue
  # Original ties retain canonical orientation. A completed row with the same
  # two clubs reversed is the replay at the opposite venue, so preserve the
  # observed orientation/date and label it explicitly as a replay.
  if reverse_replay:
   out_home,out_away=home,away
   date=current_date or match.get("date","")
   round_name=SCAN_ROUND+" Replay"
  else:
   out_home,out_away=match["home"],match["away"]
   date=match.get("date","") or current_date
   round_name=match.get("round",SCAN_ROUND)
  winner=out_home if hs>as_ else out_away if as_>hs else ""
  parsed.append({"home":out_home,"away":out_away,"home_score":hs,"away_score":as_,"winner":winner,"status":"FT","decision":"","date":date,"round":round_name,"source_url":source_url})
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
 for r in rs:out[(norm(r["home"]),norm(r["away"]),r.get("home_score"),r.get("away_score"),r.get("date",""),str(r.get("round") or "").lower())]=r
 return list(out.values())


def main():
 ap=argparse.ArgumentParser();ap.add_argument("--url",default="https://www.thefa.com/competitions/thefacup/results");ap.add_argument("--publish",action="store_true");a=ap.parse_args()
 d=json.loads(DATA.read_text()); known=ties(d); existing=sum((v for v in (d.get("result_history",{}) or {}).values() if isinstance(v,list)),[])
 if len([f for f in known if str(f.get("round") or "").lower()==SCAN_ROUND.lower()])<112:
  raise SystemExit(f"Scanner health failure: canonical {SCAN_ROUND} archive is incomplete ({len(known)} known scan ties).")

 primary_html=fetch(a.url); txt=textify(primary_html); primary=[]; amb=[]
 for f in known:
  c=candidates(txt,f["home"],f["away"])
  if len(c)>1:amb.append([f["home"],f["away"],sorted(c)]);continue
  if len(c)!=1:continue
  hs,as_=next(iter(c)); winner=f["home"] if hs>as_ else f["away"] if as_>hs else ""
  primary.append({"home":f["home"],"away":f["away"],"home_score":hs,"away_score":as_,"winner":winner,"status":"FT","decision":"","date":f.get("date",""),"round":f.get("round",SCAN_ROUND),"source_url":a.url})

 round_html=fetch(FWP_ROUND_URL)
 fallback_round,unmatched_round,round_ft_rows=parse_fwp(round_html,known,FWP_ROUND_URL,strict_unmatched=True)
 live_html=fetch(FWP_LIVE_URL)
 fallback_live,_,live_ft_rows=parse_fwp(live_html,known,FWP_LIVE_URL,strict_unmatched=False)
 fallback=dedupe(fallback_round+fallback_live)
 report={"checked_at":datetime.now(timezone.utc).isoformat(),"scan_round":SCAN_ROUND,"active_round":d.get("source_round",""),"primary_source_url":a.url,"fallback_source_url":FWP_ROUND_URL,"supplemental_source_url":FWP_LIVE_URL,"known_ties":len(known),"primary_results_detected":len(primary),"fallback_round_ft_rows":round_ft_rows,"fallback_round_results_detected":len(fallback_round),"supplemental_ft_rows":live_ft_rows,"supplemental_results_detected":len(fallback_live),"fallback_results_detected":len(fallback),"new_results":[],"ambiguous":amb,"unmatched_fallback_rows":unmatched_round,"source_disagreements":[]}
 if round_ft_rows and not fallback_round:
  (ROOT/"updater/results-pilot-report.json").write_text(json.dumps(report,indent=2)+"\n")
  raise SystemExit(f"Parser health failure: strict FWP round source contains {round_ft_rows} FT rows but zero canonical results were parsed.")
 if unmatched_round:
  (ROOT/"updater/results-pilot-report.json").write_text(json.dumps(report,indent=2)+"\n")
  raise SystemExit("Publication blocked: FWP round-source completed rows did not map to canonical ties: "+str(unmatched_round[:10]))

 # Cross-source agreement is required whenever two sources detect the exact same
 # oriented fixture/date. Original tie and reverse-orientation replay are distinct.
 by_tie={}
 disagreements=[]
 for source_name,rows in (("primary",primary),("fallback",fallback)):
  for r in rows:
   k=(norm(r["home"]),norm(r["away"]),r.get("date",""),str(r.get("round") or "").lower())
   if k in by_tie and (by_tie[k][1]["home_score"],by_tie[k][1]["away_score"])!=(r["home_score"],r["away_score"]):
    disagreements.append([r["home"],r["away"],r.get("date",""),by_tie[k][0],by_tie[k][1]["home_score"],by_tie[k][1]["away_score"],source_name,r["home_score"],r["away_score"]])
   else: by_tie[k]=(source_name,r)
 report["source_disagreements"]=disagreements
 if disagreements:
  (ROOT/"updater/results-pilot-report.json").write_text(json.dumps(report,indent=2)+"\n")
  raise SystemExit("Publication blocked: sources disagree: "+str(disagreements[:10]))

 detected=dedupe(primary+fallback)
 new=[r for r in detected if not any(same(x,r) for x in existing)]
 report["new_results"]=new
 print("Scan round:",SCAN_ROUND);print("Active round preserved:",d.get("source_round","UNKNOWN"));print("Known ties checked:",len(known));print("Primary results detected:",len(primary));print("Strict fallback FT rows seen:",round_ft_rows);print("Strict fallback canonical results detected:",len(fallback_round));print("Supplemental live FT rows seen:",live_ft_rows);print("Supplemental canonical results detected:",len(fallback_live));print("Combined fallback results detected:",len(fallback));print("New unambiguous results:",len(new));print("Ambiguous ties rejected:",len(amb))
 for r in new:print(r["home"],r["home_score"],"-",r["away_score"],r["away"],r.get("date",""),r.get("round",""))
 (ROOT/"updater/results-pilot-report.json").write_text(json.dumps(report,indent=2)+"\n")
 if a.publish and amb:raise SystemExit("Publication blocked: ambiguous primary candidates.")
 if a.publish:
  for r in new:merge(d,r)
  if new:d["updated_at"]=datetime.now(timezone.utc).isoformat();DATA.write_text(json.dumps(d,indent=2,ensure_ascii=False)+"\n")
  print("PUBLISHED:",len(new))
 else:print("DRY RUN: competition.json unchanged.")
if __name__=="__main__":main()
