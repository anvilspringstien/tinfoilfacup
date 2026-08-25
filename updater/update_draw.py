#!/usr/bin/env python3
import html as htmllib
import json, re, subprocess, sys, urllib.parse, urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
JSON_PATH=ROOT/'competition.json'
SOURCE_URL=sys.argv[1] if len(sys.argv)>1 else ''
ROUND=sys.argv[2] if len(sys.argv)>2 else 'First Round Qualifying'
DATE=sys.argv[3] if len(sys.argv)>3 else '2026-09-05'
if not SOURCE_URL:
    raise SystemExit('Usage: update_draw.py SOURCE_URL [ROUND] [YYYY-MM-DD]')

UA={'User-Agent':'Mozilla/5.0 TinFoilFACupDataUpdater/1.1'}

def fetch(url):
    req=urllib.request.Request(url,headers=UA)
    with urllib.request.urlopen(req,timeout=40) as r:
        return r.read(), r.headers.get('Content-Type',''), r.geturl()

def html_text(raw):
    s=raw.decode('utf-8','ignore')
    s=re.sub(r'(?is)<script.*?</script>',' ',s)
    s=re.sub(r'(?is)<style.*?</style>',' ',s)
    s=re.sub(r'(?s)<[^>]+>','\n',s)
    return htmllib.unescape(s)

def parse(text):
    ties=[]; seen=set()
    for raw in text.splitlines():
        line=re.sub(r'\s+',' ',raw).strip()
        line=re.sub(r'^\d{1,3}\s+','',line)
        if not line or len(line)>180: continue
        m=re.match(r'^(.+?)\s+v(?:\.|s\.?)?\s+(.+?)$',line,re.I)
        if not m: continue
        home=re.sub(r'\s+',' ',m.group(1)).strip(' .')
        away=re.sub(r'\s+',' ',m.group(2)).strip(' .')
        if not home or not away: continue
        key=(home.lower(),away.lower())
        if key not in seen:
            seen.add(key); ties.append((home,away))
    return ties

def discover(raw,base):
    src=raw.decode('utf-8','ignore')
    hrefs=re.findall(r'href\s*=\s*["\']([^"\']+)["\']',src,re.I)
    scored=[]
    for href in hrefs:
        url=urllib.parse.urljoin(base,htmllib.unescape(href))
        low=url.lower(); score=0
        if '.ashx' in low or '.pdf' in low: score+=10
        if 'fa-cup' in low or 'facup' in low or 'emirates-fa-cup' in low: score+=5
        if '1q' in low or 'qualifying' in low or 'draw' in low: score+=5
        if 'thefa.com' in low: score+=2
        if score: scored.append((score,url))
    scored.sort(reverse=True)
    return scored[0][1] if scored else None

def pdf_text(raw):
    pdf=ROOT/'updater/_source.pdf'; txt=ROOT/'updater/_source.txt'
    pdf.write_bytes(raw)
    subprocess.run(['pdftotext','-layout',str(pdf),str(txt)],check=True)
    return txt.read_text(errors='ignore')

raw,ctype,final=fetch(SOURCE_URL)
if raw[:4]==b'%PDF' or 'pdf' in ctype.lower() or '.ashx' in final.lower() or '.pdf' in final.lower():
    text=pdf_text(raw); resolved=final
else:
    text=html_text(raw); resolved=final
    if len(parse(text))<20:
        doc=discover(raw,final)
        if not doc:
            raise SystemExit('Validation failed: no draw rows and no official draw document link found.')
        print('Discovered draw document:',doc)
        raw2,ctype2,final2=fetch(doc); resolved=final2
        if raw2[:4]==b'%PDF' or 'pdf' in ctype2.lower() or '.ashx' in final2.lower() or '.pdf' in final2.lower():
            text=pdf_text(raw2)
        else:
            text=html_text(raw2)

ties=parse(text)
print('Parsed ties:',len(ties))
if len(ties)<20:
    raise SystemExit(f'Validation failed: only {len(ties)} ties parsed; JSON unchanged.')
if ROUND=='First Round Qualifying' and not (105<=len(ties)<=118):
    raise SystemExit(f'Validation failed: expected about 112 ties, parsed {len(ties)}; JSON unchanged.')

data=json.loads(JSON_PATH.read_text())
fixtures={}; suffix=re.compile(r'\s+(FC|AFC|CFC)$',re.I)
for home,away in ties:
    rec={'round':ROUND,'home':home,'away':away,'date':DATE,'kickoff':'15:00'}
    if ' or ' in home.lower() or ' or ' in away.lower(): rec['conditional']=True
    clubs=[x.strip() for x in re.split(r'\s+or\s+',home,flags=re.I) if x.strip()]
    clubs += [x.strip() for x in re.split(r'\s+or\s+',away,flags=re.I) if x.strip()]
    for club in clubs:
        fixtures[club]=rec
        fixtures.setdefault(suffix.sub('',club),rec)

data['fixtures']=fixtures
data['updated_at']=datetime.now(timezone.utc).isoformat()
data['source_url']=resolved
data['source_round']=ROUND
data['source_tie_count']=len(ties)
tmp=JSON_PATH.with_suffix('.json.new')
tmp.write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n')
tmp.replace(JSON_PATH)
print(f'SUCCESS: published {len(ties)} ties')
