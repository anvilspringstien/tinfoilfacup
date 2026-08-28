#!/usr/bin/env python3
"""Guarded canonical sync for the completed Preliminary Round and First Qualifying draw."""
import json,re,urllib.request
from datetime import datetime,timezone
from html import unescape
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DATA_PATH=ROOT/'competition.json'; HTML_PATH=ROOT/'clubfinder.html'
BASE='https://www.footballwebpages.co.uk/fa-cup'; FIXTURES_URL=f'{BASE}/fixtures-results'
RESULT_DATES=['20260821','20260822','20260823','20260825','20260826']
UA='TinFoilFACupClubfinder/1.0 (+https://anvilspringstien.github.io/tinfoilfacup/)'

def fetch(url):
    req=urllib.request.Request(url,headers={'User-Agent':UA,'Accept':'text/html'})
    with urllib.request.urlopen(req,timeout=30) as r:return r.read().decode('utf-8','replace')

def clean(fragment):
    fragment=re.sub(r'<script\b.*?</script>|<style\b.*?</style>',' ',fragment,flags=re.I|re.S)
    fragment=re.sub(r'<[^>]+>',' ',fragment)
    return ' '.join(unescape(fragment).replace('\xa0',' ').split())

def norm(s):
    s=(s or '').lower().replace('&',' and '); s=re.sub(r'\b(fc|afc|cfc)\b',' ',s)
    return re.sub(r'[^a-z0-9]+',' ',s).strip()

def aliases(name):
    suffix=re.compile(r'\s+(FC|AFC|CFC)$',re.I); out={name,suffix.sub('',name)}
    if not suffix.search(name):out|={name+' FC',name+' AFC'}
    return {x for x in out if x}

def cells(row):return [clean(x) for x in re.findall(r'<t[dh]\b[^>]*>(.*?)</t[dh]>',row,re.I|re.S)]

def parse_date(text):
    m=re.search(r'(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\s+(\d{1,2})(?:st|nd|rd|th)\s+([A-Za-z]+)\s+(20\d{2})',text,re.I)
    if not m:return None
    return datetime.strptime(f'{m.group(1)} {m.group(2)} {m.group(3)}','%d %B %Y').date().isoformat()

def parse_time(s):
    s=(s or '').strip().lower().replace(' ','')
    for fmt in ('%I%p','%I.%M%p','%I:%M%p'):
        try:return datetime.strptime(s,fmt).strftime('%H:%M')
        except ValueError:pass
    return '15:00'

def parse_results(html,date):
    rows=re.findall(r'<tr\b[^>]*>.*?</tr>',html,re.I|re.S); out=[]; last=None
    for row in rows:
        c=[x for x in cells(row) if x]
        joined=' '.join(c)
        pm=re.search(r'(.+?)\s+win\s+\d+\s*[-–]\s*\d+\s+on penalties',joined,re.I)
        if pm and last and last['home_score']==last['away_score']:
            last['winner']=pm.group(1).strip(); last['decision']='penalties'; continue
        if len(c)<5 or not c[0].upper().startswith('FT'):continue
        if not re.fullmatch(r'\d+',c[2]) or not re.fullmatch(r'\d+',c[3]):continue
        home,away=c[1],c[4]; hs,as_=int(c[2]),int(c[3]); iso=datetime.strptime(date,'%Y%m%d').date().isoformat()
        rnd='Preliminary Round Replay' if iso in ('2026-08-25','2026-08-26') else 'Preliminary Round'
        if iso=='2026-08-25' and norm(home)==norm('Baffins Milton Rovers') and norm(away)==norm('Hartley Wintney'):rnd='Preliminary Round'
        winner=home if hs>as_ else away if as_>hs else ''
        rec={'home':home,'away':away,'home_score':hs,'away_score':as_,'winner':winner,'status':'FT','decision':'' if winner else ('draw-replay' if rnd=='Preliminary Round' else ''),'date':iso,'round':rnd,'source_url':f'{BASE}/{date}'}
        out.append(rec); last=rec
    return out

def prelim_fixtures(html):
    m=re.search(r'const PRELIM_FIXTURES_BY_CLUB=(\{.*?\});\s*const CURRENT_RESULT_OVERRIDES=',html,re.S)
    if not m:raise SystemExit('ABORT: PRELIM_FIXTURES_BY_CLUB not found')
    obj=json.loads(m.group(1)); uniq={}
    for f in obj.values():
        if isinstance(f,dict) and f.get('home') and f.get('away'):
            k=(str(f.get('number','')),norm(f['home']),norm(f['away']),f.get('date',''))
            uniq.setdefault(k,{**f,'round':'Preliminary Round'})
    return list(uniq.values())

def first_qualifying(html):
    # Walk date headings and table rows in document order so Friday/Sunday changes remain accurate.
    token_re=re.compile(r'<h[234]\b[^>]*>.*?</h[234]>|<tr\b[^>]*>.*?</tr>',re.I|re.S)
    date=None; out=[]
    for token in token_re.findall(html):
        if re.match(r'<h',token,re.I):
            d=parse_date(clean(token)); date=d or date; continue
        c=[x for x in cells(token) if x]
        if len(c)<4 or not date:continue
        try:vi=next(i for i,x in enumerate(c) if x.lower()=='v')
        except StopIteration:continue
        if vi<2 or vi+1>=len(c):continue
        time,home,away=c[vi-2],c[vi-1],c[vi+1]
        if home.upper().startswith('FT'):continue
        out.append({'round':'First Round Qualifying','home':home,'away':away,'date':date,'kickoff':parse_time(time)})
    uniq={}
    for f in out:uniq[(norm(f['home']),norm(f['away']),f['date'])]=f
    return list(uniq.values())

def rkey(r):return (norm(r.get('home')),norm(r.get('away')),r.get('date',''),r.get('home_score'),r.get('away_score'))
def fmap(fixtures):
    out={}
    for f in fixtures:
        for club in aliases(f['home'])|aliases(f['away']):out[club]=f
    return out

def add_result(data,r):
    results=data.setdefault('results',{}); hist=data.setdefault('result_history',{})
    for club in aliases(r['home'])|aliases(r['away']):
        arr=hist.setdefault(club,[])
        if not any(rkey(x)==rkey(r) for x in arr):arr.append(r)
        arr.sort(key=lambda x:(x.get('date',''),0 if x.get('round')=='Preliminary Round' else 1))
        results[club]=arr[-1]

club_html=HTML_PATH.read_text(encoding='utf-8'); prelim=prelim_fixtures(club_html)
results=[]
for d in RESULT_DATES:results.extend(parse_results(fetch(f'{BASE}/{d}'),d))
frq=first_qualifying(fetch(FIXTURES_URL))
prelim_count=len({(norm(f['home']),norm(f['away']),f.get('date','')) for f in prelim})
result_count=len({rkey(r) for r in results})
if prelim_count<130:raise SystemExit(f'ABORT: Preliminary fixture coverage {prelim_count}')
if result_count<130:raise SystemExit(f'ABORT: Preliminary result/replay coverage {result_count}')
if len(frq)!=112:raise SystemExit(f'ABORT: First Qualifying draw expected 112 ties, got {len(frq)}')

data=json.loads(DATA_PATH.read_text(encoding='utf-8'))
data['preliminary_fixtures']=fmap(prelim)
for r in sorted(results,key=lambda x:(x['date'],0 if x['round']=='Preliminary Round' else 1)):add_result(data,r)
data['fixtures']=fmap(frq); data['replays']={}
data['round_dates']={**(data.get('round_dates') or {}),'Preliminary Round':'2026-08-22','First Round Qualifying':'2026-09-05'}
data['updated_at']=datetime.now(timezone.utc).isoformat()
data['competition_sync']={'source':'Football Web Pages','source_url':FIXTURES_URL,'synced_at':data['updated_at'],'preliminary_unique_fixtures':prelim_count,'preliminary_results_and_replays':result_count,'first_qualifying_unique_fixtures':len(frq),'result_dates':RESULT_DATES}
tmp=DATA_PATH.with_suffix('.json.new'); tmp.write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n',encoding='utf-8'); tmp.replace(DATA_PATH)
print('COMPETITION CHRONOLOGY SYNC v2: SUCCESS')
print('Preliminary fixtures:',prelim_count); print('Preliminary results/replays:',result_count); print('First Qualifying fixtures:',len(frq)); print('Ground/location data: UNTOUCHED')
