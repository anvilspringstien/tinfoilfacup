#!/usr/bin/env python3
"""Guardedly replace the active Second Qualifying draw with its resolved 80 ties."""
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
EXPECTED=80
UA="Mozilla/5.0 TinFoilFACupCompetitionHealth/7.9.25"

def report(stage,**details): REPORT.write_text(json.dumps({"checked_at":datetime.now(timezone.utc).isoformat(),"stage":stage,**details},indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
def fail(stage,message,**details): report(stage,status="FAIL",message=message,**details); raise SystemExit(message)
def fetch(url):
    req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":"text/html,application/xhtml+xml"}); return urllib.request.urlopen(req,timeout=30).read().decode("utf-8","replace")
def clean(x): return " ".join(unescape(re.sub(r"<[^>]+>"," ",x)).replace("\xa0"," ").split())
def cells(row): return [clean(x) for x in re.findall(r"<t[dh]\b[^>]*>(.*?)</t[dh]>",row,re.I|re.S)]
def norm(s):
    s=(s or "").lower().replace("&"," and "); s=re.sub(r"\b(fc|afc|cfc)\b"," ",s); return re.sub(r"[^a-z0-9]+"," ",s).strip()
def parse_time(s):
    s=(s or "").strip().lower().replace(" ",""); m=re.fullmatch(r"(\d{1,2})(?::(\d{2}))?(am|pm)",s)
    if m:
        h=int(m.group(1))%12+(12 if m.group(3)=="pm" else 0); return f"{h:02d}:{int(m.group(2) or 0):02d}"
    if re.fullmatch(r"\d{1,2}:\d{2}",s):
        h,mm=map(int,s.split(":")); return f"{h:02d}:{mm:02d}"
    return "15:00"
def parse(page):
    fixtures=[]; samples=[]
    for row in re.findall(r"<tr\b[^>]*>.*?</tr>",page,re.I|re.S):
        c=[x for x in cells(row) if x]
        if c and len(samples)<20:samples.append(c)
        try:vi=next(i for i,x in enumerate(c) if x.lower()=="v")
        except StopIteration:continue
        if vi<1 or vi+1>=len(c):continue
        home=c[vi-1].strip(); away=c[vi+1].strip(); time=c[vi-2].strip() if vi>=2 else "3pm"
        if home and away:fixtures.append({"round":ROUND,"home":home,"away":away,"date":DATE,"kickoff":parse_time(time),"source_url":URL})
    unique={}
    for f in fixtures:unique[tuple(sorted((norm(f["home"]),norm(f["away"]))))]=f
    return list(unique.values()),samples

def aliases(name):
    suffix=re.compile(r"\s+(FC|AFC|CFC)$",re.I);out={name,suffix.sub("",name)}
    if not suffix.search(name):out|={name+" FC",name+" AFC"}
    return {x for x in out if x}
def fmap(fixtures):
    out={}
    for f in fixtures:
        for club in aliases(f["home"])|aliases(f["away"]):out[club]=f
    return out
def has_fixture(fixtures,a,b):
    target=tuple(sorted((norm(a),norm(b))));return any(tuple(sorted((norm(f["home"]),norm(f["away"]))))==target for f in fixtures)
def main():
    data=json.loads(DATA.read_text(encoding="utf-8")); page=fetch(URL); fixtures,samples=parse(page)
    if len(fixtures)!=EXPECTED:fail("parse",f"SECOND QUALIFYING RESOLVED SYNC: ABORT - expected {EXPECTED} ties, found {len(fixtures)}",html_bytes=len(page),parsed_count=len(fixtures),parsed_fixtures=[f"{f['home']} v {f['away']}" for f in fixtures[:100]],row_samples=samples)
    required=[("Hampton & Richmond Borough","Crowborough Athletic"),("Dulwich Hamlet","Welling United"),("Thame United","Exmouth Town"),("Needham Market","Braintree Town"),("Hemel Hempstead Town","Wingate & Finchley")]
    missing=[f"{a} v {b}" for a,b in required if not has_fixture(fixtures,a,b)]
    if missing:fail("canaries","SECOND QUALIFYING RESOLVED SYNC: ABORT - required fixtures missing",missing=missing)
    data["fixtures"]=fmap(fixtures);data["source_round"]=ROUND;data.setdefault("round_dates",{})[ROUND]=DATE;data["updated_at"]=datetime.now(timezone.utc).isoformat();data["second_qualifying_sync"]={"source":"Football Web Pages","source_url":URL,"synced_at":data["updated_at"],"unique_fixtures":len(fixtures),"resolved":True};DATA.write_text(json.dumps(data,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    report("complete",status="PASS",resolved_ties=len(fixtures));print("SECOND QUALIFYING RESOLVED SYNC: PASS");print("Resolved ties:",len(fixtures))
if __name__=="__main__":main()
