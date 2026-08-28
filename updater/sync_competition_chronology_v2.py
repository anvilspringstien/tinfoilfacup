#!/usr/bin/env python3
"""Guarded canonical sync for the completed Preliminary Round and First Qualifying draw."""
import json,re,urllib.request
from datetime import datetime,timezone
from html import unescape
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DATA_PATH=ROOT/'competition.json'
BASE='https://www.footballwebpages.co.uk/fa-cup'
FIXTURES_URL=f'{BASE}/fixtures-results'
FA_FIXTURES_URL='https://www.thefa.com/competitions/thefacup/fixtures?fs=e&s=cl'
RESULT_DATES=['20260821','20260822','20260823','20260825','20260826']
UA='Mozilla/5.0'

def fetch(url):
    req=urllib.request.Request(url,headers={'User-Agent':UA,'Accept':'text/html,application/xhtml+xml'})
    return urllib.request.urlopen(req,timeout=30).read().decode('utf-8','replace')

def clean(x):
    return ' '.join(unescape(re.sub(r'<[^>]+>',' ',x)).replace('\xa0',' ').split())

def norm(s):
    s=(s or '').lower().replace('&',' and ')
    s=re.sub(r'\b(fc|afc|cfc)\b',' ',s)
    return re.sub(r'[^a-z0-9]+',' ',s).strip()

def aliases(n):
    suf=re.compile(r'\s+(FC|AFC|CFC)$',re.I)
    out={n,suf.sub('',n)}
    if not suf.search(n): out|={n+' FC',n+' AFC'}
    return {x for x in out if x}

def cells(row):
    return [clean(x) for x in re.findall(r'<t[dh]\b[^>]*>(.*?)</t[dh]>',row,re.I|re.S)]

def parse_time(s,default=None):
    s=(s or '').strip().lower().replace(' ','')
    if re.fullmatch(r'\d{1,2}:\d{2}',s):
        h,m=map(int,s.split(':'))
        if 0<=h<=23 and 0<=m<=59:return f'{h:02d}:{m:02d}'
    for fmt in ('%I%p','%I.%M%p','%I:%M%p'):
        try:return datetime.strptime(s,fmt).strftime('%H:%M')
        except ValueError:pass
    return default

def strip_seed(s):
    return re.sub(r'^\(\d+\)\s*|\s*\(\d+\)$','',s).strip()

def fa_kickoff_map(html):
    """Extract authoritative FA kick-off times keyed by home/away identity."""
    out={}
    for row in re.findall(r'<tr\b[^>]*>.*?</tr>',html,re.I|re.S):
        c=[x for x in cells(row) if x]
        try:vi=next(i for i,x in enumerate(c) if x.strip().lower() in ('vs','v'))
        except StopIteration:continue
        if vi<1 or vi+1>=len(c):continue
        home,away=c[vi-1],c[vi+1]
        if not home or not away:continue
        ko=None
        for x in reversed(c[:vi-1]):
            ko=parse_time(x)
            if ko:break
        if ko:out[(norm(home),norm(away))]=ko
    return out

def parse_results(html,date,kickoffs):
    out=[]; last=None; iso=datetime.strptime(date,'%Y%m%d').date().isoformat()
    for row in re.findall(r'<tr\b[^>]*>.*?</tr>',html,re.I|re.S):
        c=[x for x in cells(row) if x]; joined=' '.join(c)
        pm=re.search(r'(.+?)\s+win\s+\d+\s*[-–]\s*\d+\s+on penalties',joined,re.I)
        if pm and last and last['home_score']==last['away_score']:
            last['winner']=strip_seed(pm.group(1)); last['decision']='penalties'; continue
        try:fi=next(i for i,x in enumerate(c) if x.upper().startswith('FT'))
        except StopIteration:continue
        status=c[fi].upper()
        tail=c[fi+1:]; nums=[(i,x) for i,x in enumerate(tail) if re.fullmatch(r'\d+',x)]
        if len(nums)<2:continue
        i1,s1=nums[-2]; i2,s2=nums[-1]
        if i1<1 or i2+1>=len(tail):continue
        home=strip_seed(' '.join(tail[:i1])); away=strip_seed(' '.join(tail[i2+1:])); hs,as_=int(s1),int(s2)
        if not home or not away:continue
        rnd='Preliminary Round Replay' if iso in ('2026-08-25','2026-08-26') else 'Preliminary Round'
        if iso=='2026-08-25' and norm(home)==norm('Baffins Milton Rovers') and norm(away)==norm('Hartley Wintney'):rnd='Preliminary Round'
        winner=home if hs>as_ else away if as_>hs else ''
        decision='aet' if 'AET' in status else ('' if winner else ('draw-replay' if rnd=='Preliminary Round' else ''))
        rec={'home':home,'away':away,'home_score':hs,'away_score':as_,'winner':winner,'status':status,'decision':decision,'date':iso,'round':rnd,'source_url':f'{BASE}/{date}'}
        ko=kickoffs.get((norm(home),norm(away)))
        if ko:
            rec['kickoff']=ko
            rec['kickoff_source_url']=FA_FIXTURES_URL
        out.append(rec); last=rec
    return out

def preliminary_fixtures_from_results(results):
    first_legs=[]; seen=set()
    for r in results:
        if r.get('round')!='Preliminary Round':continue
        key=(norm(r.get('home')),norm(r.get('away')),r.get('date',''))
        if key in seen:continue
        seen.add(key)
        f={'round':'Preliminary Round','home':r['home'],'away':r['away'],'date':r['date'],'source_url':r.get('source_url','')}
        if r.get('kickoff'):f['kickoff']=r['kickoff']
        first_legs.append(f)
    first_legs.sort(key=lambda f:(f.get('date',''),norm(f.get('home')),norm(f.get('away'))))
    for i,f in enumerate(first_legs,1):f['number']=i
    return first_legs

def first_qualifying(html):
    out=[]
    for row in re.findall(r'<tr\b[^>]*>.*?</tr>',html,re.I|re.S):
        c=[x for x in cells(row) if x]
        try:vi=next(i for i,x in enumerate(c) if x.lower()=='v')
        except StopIteration:continue
        if vi<3 or vi+1>=len(c):continue
        date_s,time,home,away=c[vi-3],c[vi-2],c[vi-1],c[vi+1]
        m=re.fullmatch(r'(\d{1,2})/(\d{1,2})/(20\d{2})',date_s)
        if not m:continue
        iso=f'{m.group(3)}-{int(m.group(2)):02d}-{int(m.group(1)):02d}'
        out.append({'round':'First Round Qualifying','home':home,'away':away,'date':iso,'kickoff':parse_time(time,'15:00')})
    uniq={}
    for f in out:uniq[(norm(f['home']),norm(f['away']),f['date'])]=f
    return list(uniq.values())

def rkey(r):
    return (norm(r.get('home')),norm(r.get('away')),r.get('date',''),r.get('home_score'),r.get('away_score'))

def fmap(fs):
    out={}
    for f in fs:
        for club in aliases(f['home'])|aliases(f['away']):out[club]=f
    return out

def add_result(data,r):
    for club in aliases(r['home'])|aliases(r['away']):
        arr=data.setdefault('result_history',{}).setdefault(club,[])
        match=next((x for x in arr if rkey(x)==rkey(r)),None)
        if match:
            match.update(r)
        else:
            arr.append(r)
        arr.sort(key=lambda x:(x.get('date',''),0 if x.get('round')=='Preliminary Round' else 1))
        data.setdefault('results',{})[club]=arr[-1]

kickoffs=fa_kickoff_map(fetch(FA_FIXTURES_URL))
results=[]
for d in RESULT_DATES:results.extend(parse_results(fetch(f'{BASE}/{d}'),d,kickoffs))
prelim=preliminary_fixtures_from_results(results)
frq=first_qualifying(fetch(FIXTURES_URL))
prelim_count=len({(norm(f['home']),norm(f['away']),f.get('date','')) for f in prelim})
result_count=len({rkey(r) for r in results})
replay_results=[r for r in results if r.get('round')=='Preliminary Round Replay']
replays_without_time=[r for r in replay_results if not r.get('kickoff')]
frenford=next((r for r in replay_results if norm(r.get('home'))==norm('Frenford') and norm(r.get('away'))==norm('Haringey Borough')),None)

if prelim_count<130:raise SystemExit(f'ABORT: Preliminary fixture coverage {prelim_count}')
if result_count<130:raise SystemExit(f'ABORT: Preliminary result/replay coverage {result_count}')
if len(frq)!=112:raise SystemExit(f'ABORT: First Qualifying draw expected 112 ties, got {len(frq)}')
if not frenford or frenford.get('kickoff')!='19:45':raise SystemExit(f"ABORT: authoritative Frenford replay kick-off unresolved: {None if not frenford else frenford.get('kickoff')}")
if replays_without_time:raise SystemExit(f'ABORT: {len(replays_without_time)} Preliminary replays lack authoritative kick-off times')

data=json.loads(DATA_PATH.read_text(encoding='utf-8'))
data['preliminary_fixtures']=fmap(prelim)
for r in sorted(results,key=lambda x:(x['date'],0 if x['round']=='Preliminary Round' else 1)):add_result(data,r)
data['fixtures']=fmap(frq)
data['replays']={}
data['round_dates']={**(data.get('round_dates') or {}),'Preliminary Round':'2026-08-22','First Round Qualifying':'2026-09-05'}
data['updated_at']=datetime.now(timezone.utc).isoformat()
data['competition_sync']={'source':'Football Web Pages + The FA','source_url':FIXTURES_URL,'kickoff_source_url':FA_FIXTURES_URL,'synced_at':data['updated_at'],'preliminary_fixture_source':'played original ties','preliminary_unique_fixtures':prelim_count,'preliminary_results_and_replays':result_count,'first_qualifying_unique_fixtures':len(frq),'result_dates':RESULT_DATES,'authoritative_replay_kickoffs':len(replay_results)}
tmp=DATA_PATH.with_suffix('.json.new')
tmp.write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
tmp.replace(DATA_PATH)
print('COMPETITION CHRONOLOGY SYNC v3.1: SUCCESS')
print('Preliminary fixtures:',prelim_count)
print('Preliminary results/replays:',result_count)
print('First Qualifying fixtures:',len(frq))
print('Authoritative replay kick-offs:',len(replay_results))
print('Frenford v Haringey Borough replay kick-off:',frenford['kickoff'])
print('Ground/location data: UNTOUCHED')
