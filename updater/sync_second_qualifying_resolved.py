#!/usr/bin/env python3
"""Guardedly refresh the active Second Qualifying draw.

As of 11 September 2026, 79 of the 80 Second Qualifying ties are resolved.
The remaining slot is legitimately conditional because Burgess Hill Town v
Jersey Bulls finished 0-0 and its replay, originally due 8 September, was
postponed to 15 September. We therefore merge the 79 published resolved ties
with exactly one retained canonical conditional fixture: Hanwell Town v
Burgess Hill Town or Jersey Bulls. The script fails closed if that real-world
shape changes unexpectedly.
"""
import json
import re
import urllib.request
from datetime import datetime, timezone
from html import unescape
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"competition.json"
REPORT=ROOT/"updater"/"second-qualifying-sync-report.json"
URL="https://www.footballwebpages.co.uk/fa-cup/fixtures-results"
ROUND="Second Round Qualifying"
DATE="2026-09-19"
EXPECTED_RESOLVED=79
EXPECTED_TOTAL=80
PENDING_HOME="Hanwell Town"
PENDING_ALTERNATIVES=("Burgess Hill Town","Jersey Bulls")
UA="Mozilla/5.0 TinFoilFACupCompetitionHealth/7.9.25"

def report(stage,**details): REPORT.write_text(json.dumps({"checked_at":datetime.now(timezone.utc).isoformat(),"stage":stage,**details},indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
def fail(stage,message,**details): report(stage,status="FAIL",message=message,**details); raise SystemExit(message)
def fetch(url):
    req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":"text/html,application/xhtml+xml"}); return urllib.request.urlopen(req,timeout=30).read().decode("utf-8","replace")
def clean(x): return " ".join(unescape(re.sub(r"<[^>]+>"," ",x)).replace("\xa0"," ").split())
def cells(row): return [clean(x) for x in re.findall(r"<t[dh]\b[^>]*>(.*?)</t[dh]>",row,re.I|re.S)]
def norm(s):
    s=(s or "").lower().replace("&"," and "); s=re.sub(r"\b(fc|afc|cfc)\b"," ",s); return re.sub(r"[^a-z0-9]+"," ",s).strip()
def compatible(a,b):
    a,b=norm(a),norm(b); return bool(a and b and (a==b or a.startswith(b+" ") or b.startswith(a+" ")))
def parse_time(s):
    s=(s or "").strip().lower().replace(" ",""); m=re.fullmatch(r"(\d{1,2})(?::(\d{2}))?(am|pm)",s)
    if m:
        h=int(m.group(1))%12+(12 if m.group(3)=="pm" else 0); return f"{h:02d}:{int(m.group(2) or 0):02d}"
    if re.fullmatch(r"\d{1,2}:\d{2}",s):
        h,mm=map(int,s.split(":")); return f"{h:02d}:{mm:02d}"
    return "15:00"
def parse(page):
    fixtures=[]
    for row in re.findall(r"<tr\b[^>]*>.*?</tr>",page,re.I|re.S):
        c=[x for x in cells(row) if x]
        try:vi=next(i for i,x in enumerate(c) if x.lower()=="v")
        except StopIteration:continue
        if vi<1 or vi+1>=len(c):continue
        home=c[vi-1].strip(); away=c[vi+1].strip(); time=c[vi-2].strip() if vi>=2 else "3pm"
        if home and away:fixtures.append({"round":ROUND,"home":home,"away":away,"date":DATE,"kickoff":parse_time(time),"source_url":URL})
    unique={}
    for f in fixtures:unique[tuple(sorted((norm(f["home"]),norm(f["away"]))))]=f
    return list(unique.values())
def aliases(name):
    suffix=re.compile(r"\s+(FC|AFC|CFC)$",re.I);out={name,suffix.sub("",name)}
    if not suffix.search(name):out|={name+" FC",name+" AFC"}
    return {x for x in out if x}
def fmap(fixtures):
    out={}
    for f in fixtures:
        for club in aliases(f["home"])|aliases(f["away"]):out[club]=f
    return out
def unique_fixtures(src):
    vals=src.values() if isinstance(src,dict) else (src or []); out={}
    for f in vals:
        if not isinstance(f,dict) or not f.get("home") or not f.get("away"):continue
        key=(norm(f.get("home")),norm(f.get("away")),f.get("date","") or "")
        out[key]=dict(f)
    return list(out.values())
def conditional_alternatives(side): return [x.strip() for x in re.split(r"\s+or\s+",str(side or ""),flags=re.I) if x.strip()]
def pending_fixture(fixtures):
    matches=[]
    for f in fixtures:
        home=f.get("home",""); away=f.get("away","")
        for fixed,conditional in ((home,away),(away,home)):
            if not compatible(fixed,PENDING_HOME):continue
            alts=conditional_alternatives(conditional)
            if len(alts)!=2:continue
            if all(any(compatible(alt,want) for alt in alts) for want in PENDING_ALTERNATIVES):matches.append(dict(f))
    return matches
def has_fixture(fixtures,a,b):
    target=tuple(sorted((norm(a),norm(b))));return any(tuple(sorted((norm(f["home"]),norm(f["away"]))))==target for f in fixtures)
def main():
    data=json.loads(DATA.read_text(encoding="utf-8")); resolved=parse(fetch(URL))
    if len(resolved)!=EXPECTED_RESOLVED:fail("parse",f"SECOND QUALIFYING RESOLVED SYNC: ABORT - expected {EXPECTED_RESOLVED} currently resolved ties, found {len(resolved)}",parsed_count=len(resolved),parsed_fixtures=[f"{f['home']} v {f['away']}" for f in resolved])
    current=unique_fixtures(data.get("fixtures") or {})
    pending=pending_fixture(current)
    if len(pending)!=1:fail("pending_slot",f"SECOND QUALIFYING RESOLVED SYNC: ABORT - expected exactly one retained Hanwell/Burgess Hill/Jersey conditional slot, found {len(pending)}",current_unique=len(current),matches=pending)
    required=[("Hampton & Richmond Borough","Crowborough Athletic"),("Dulwich Hamlet","Welling United"),("Thame United","Exmouth Town"),("Needham Market","Braintree Town"),("Hemel Hempstead Town","Wingate & Finchley")]
    missing=[f"{a} v {b}" for a,b in required if not has_fixture(resolved,a,b)]
    if missing:fail("canaries","SECOND QUALIFYING RESOLVED SYNC: ABORT - required resolved fixtures missing",missing=missing)
    retained=pending[0]
    retained.update({"round":ROUND,"date":DATE})
    final=resolved+[retained]
    if len(final)!=EXPECTED_TOTAL:fail("final_count",f"SECOND QUALIFYING RESOLVED SYNC: ABORT - expected {EXPECTED_TOTAL} total ties after retaining pending slot, found {len(final)}")
    data["fixtures"]=fmap(final);data["source_round"]=ROUND;data.setdefault("round_dates",{})[ROUND]=DATE;data["updated_at"]=datetime.now(timezone.utc).isoformat();data["second_qualifying_sync"]={"source":"Football Web Pages + retained pending replay slot","source_url":URL,"synced_at":data["updated_at"],"resolved_fixtures":len(resolved),"pending_replay_slots":1,"total_fixtures":len(final),"pending":"Hanwell Town v Burgess Hill Town or Jersey Bulls"};DATA.write_text(json.dumps(data,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    report("complete",status="PASS",resolved_ties=len(resolved),pending_slots=1,total_ties=len(final),pending_fixture=retained)
    print("SECOND QUALIFYING RESOLVED SYNC: PASS");print("Resolved ties:",len(resolved));print("Pending replay slots: 1");print("Total ties:",len(final))
if __name__=="__main__":main()
