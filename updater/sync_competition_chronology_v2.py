#!/usr/bin/env python3
"""Guarded canonical sync for FA Cup chronology.

The First Qualifying draw in competition.json is the canonical 112-tie baseline.
Live source pages are allowed to replace upcoming `v` rows with `FT` result rows
without making the draw appear incomplete. Live rows can enrich/update canonical
fixtures and results, but can never shrink the canonical draw.
"""
import json,re,urllib.request
from datetime import datetime,timezone
from html import unescape
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DATA_PATH=ROOT/'competition.json'
BASE='https://www.footballwebpages.co.uk/fa-cup'
FIXTURES_URL=f'{BASE}/fixtures-results/first-qualifying-round'
KICKOFF_SOURCE_URL='https://kiscofootball.com/fa-cup/2026-27/round/preliminary-round/'
RESULT_DATES=['20260821','20260822','20260823','20260825','20260826']
UA='Mozilla/5.0 TinFoilFACupCompetitionHealth/7.9.22'
EXPECTED_FRQ=112


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


def parse_results(html,date):
    out=[]; last=None; iso=datetime.strptime(date,'%Y%m%d').date().isoformat()
    for row in re.findall(r'<tr\b[^>]*>.*?</tr>',html,re.I|re.S):
        c=[x for x in cells(row) if x]; joined=' '.join(c)
        pm=re.search(r'(.+?)\s+win\s+\d+\s*[-–]\s*\d+\s+on penalties',joined,re.I)
        if pm and last and last['home_score']==last['away_score']:
            last['winner']=strip_seed(pm.group(1)); last['decision']='penalties'; continue
        try:fi=next(i for i,x in enumerate(c) if x.upper().startswith('FT'))
        except StopIteration:continue
        status=c[fi].upper(); tail=c[fi+1:]
        nums=[(i,x) for i,x in enumerate(tail) if re.fullmatch(r'\d+',x)]
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
        out.append(rec); last=rec
    return out


def enrich_kickoffs(results,html):
    text=clean(re.sub(r'<script\b[^>]*>.*?</script>|<style\b[^>]*>.*?</style>',' ',html,flags=re.I|re.S))
    enriched=0
    for r in results:
        hp=re.escape(r['home']); ap=re.escape(r['away']); hs=str(r['home_score']); ass=str(r['away_score'])
        pat=re.compile(r'(\d{1,2}:\d{2})\s+'+hp+r'\s+'+hs+r'\s*[–-]\s*'+ass+r'.{0,40}?'+ap,re.I)
        m=pat.search(text)
        if not m:
            pat=re.compile(r'(\d{1,2}:\d{2})\s+'+hp+r'.{0,60}?'+ap,re.I); m=pat.search(text)
        if m:
            r['kickoff']=parse_time(m.group(1)); r['kickoff_source_url']=KICKOFF_SOURCE_URL; enriched+=1
    return enriched


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


def live_first_qualifying(html):
    """Return upcoming fixture rows and completed result rows from the live page."""
    fixtures=[]; results=[]; current_date=''
    for row in re.findall(r'<tr\b[^>]*>.*?</tr>',html,re.I|re.S):
        c=[x for x in cells(row) if x]
        if not c:continue
        # Date headings such as 'Friday 4th September 2026'.
        heading=' '.join(c)
        dm=re.search(r'(\d{1,2})(?:st|nd|rd|th)?\s+([A-Za-z]+)\s+(20\d{2})',heading)
        if dm:
            try:current_date=datetime.strptime(f'{dm.group(1)} {dm.group(2)} {dm.group(3)}','%d %B %Y').date().isoformat()
            except ValueError:pass
        try:vi=next(i for i,x in enumerate(c) if x.lower()=='v')
        except StopIteration:vi=-1
        if vi>=0:
            # Common row: date, time, home, v, away. Some pages omit repeated date.
            date_s=c[vi-3] if vi>=3 else ''
            time=c[vi-2] if vi>=2 else ''
            home=c[vi-1] if vi>=1 else ''
            away=c[vi+1] if vi+1<len(c) else ''
            m=re.fullmatch(r'(\d{1,2})/(\d{1,2})/(20\d{2})',date_s)
            iso=f'{m.group(3)}-{int(m.group(2)):02d}-{int(m.group(1)):02d}' if m else current_date
            if home and away and iso:
                fixtures.append({'round':'First Round Qualifying','home':strip_seed(home),'away':strip_seed(away),'date':iso,'kickoff':parse_time(time,'15:00'),'source_url':FIXTURES_URL})
            continue
        try:fi=next(i for i,x in enumerate(c) if x.upper().startswith('FT'))
        except StopIteration:continue
        # FWP result rows are normally: date, FT, home, hs, as, away, [attd].
        tail=c[fi+1:]
        nums=[(i,x) for i,x in enumerate(tail) if re.fullmatch(r'\d+',x)]
        if len(nums)<2:continue
        i1,s1=nums[0]; i2,s2=nums[1]
        if i1<1 or i2+1>=len(tail):continue
        home=strip_seed(' '.join(tail[:i1])); away=strip_seed(tail[i2+1])
        # If the first cell is a numeric date, use it; otherwise use current heading.
        iso=current_date
        if fi>0:
            m=re.fullmatch(r'(\d{1,2})/(\d{1,2})/(20\d{2})',c[fi-1])
            if m:iso=f'{m.group(3)}-{int(m.group(2)):02d}-{int(m.group(1)):02d}'
        if not home or not away or not iso:continue
        hs,as_=int(s1),int(s2); winner=home if hs>as_ else away if as_>hs else ''
        results.append({'round':'First Round Qualifying','home':home,'away':away,'home_score':hs,'away_score':as_,'winner':winner,'status':c[fi].upper(),'decision':'','date':iso,'source_url':FIXTURES_URL})
    f_uniq={(norm(f['home']),norm(f['away'])):f for f in fixtures}
    r_uniq={(norm(r['home']),norm(r['away'])):r for r in results}
    return list(f_uniq.values()),list(r_uniq.values())


def canonical_fixtures(data):
    out=[]; seen=set()
    for f in (data.get('fixtures') or {}).values():
        if not isinstance(f,dict) or not f.get('home') or not f.get('away'):continue
        if f.get('round')!='First Round Qualifying':continue
        k=(norm(f['home']),norm(f['away']))
        if k in seen:continue
        seen.add(k); out.append(dict(f))
    return out


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
        if match:match.update(r)
        else:arr.append(r)
        arr.sort(key=lambda x:(x.get('date',''),0 if x.get('round')=='Preliminary Round' else 1))
        data.setdefault('results',{})[club]=arr[-1]


def same_tie(a,b):
    return norm(a.get('home'))==norm(b.get('home')) and norm(a.get('away'))==norm(b.get('away'))


data=json.loads(DATA_PATH.read_text(encoding='utf-8'))
results=[]
for d in RESULT_DATES:results.extend(parse_results(fetch(f'{BASE}/{d}'),d))
kickoff_enriched=enrich_kickoffs(results,fetch(KICKOFF_SOURCE_URL))
prelim=preliminary_fixtures_from_results(results)
prelim_count=len({(norm(f['home']),norm(f['away']),f.get('date','')) for f in prelim})
result_count=len({rkey(r) for r in results})
replay_results=[r for r in results if r.get('round')=='Preliminary Round Replay']
replays_without_time=[r for r in replay_results if not r.get('kickoff')]
frenford=next((r for r in replay_results if norm(r.get('home'))==norm('Frenford') and norm(r.get('away'))==norm('Haringey Borough')),None)

live_html=fetch(FIXTURES_URL)
live_upcoming,live_results=live_first_qualifying(live_html)
canonical=canonical_fixtures(data)

if prelim_count<130:raise SystemExit(f'ABORT: Preliminary fixture coverage {prelim_count}')
if result_count<130:raise SystemExit(f'ABORT: Preliminary result/replay coverage {result_count}')
if len(canonical)!=EXPECTED_FRQ:raise SystemExit(f'ABORT: canonical First Qualifying draw expected {EXPECTED_FRQ} ties, got {len(canonical)}')
if not frenford or frenford.get('kickoff')!='19:45':raise SystemExit(f"ABORT: Frenford replay kick-off unresolved: {None if not frenford else frenford.get('kickoff')}")
if replays_without_time:raise SystemExit(f'ABORT: {len(replays_without_time)} Preliminary replays lack kick-off times')

# Every live row must map to the canonical draw. Unknown ties block publication.
unmatched=[]
for row in live_upcoming+live_results:
    if not any(same_tie(row,f) for f in canonical):unmatched.append(f"{row.get('home')} v {row.get('away')}")
if unmatched:raise SystemExit('ABORT: live First Qualifying rows not in canonical draw: '+', '.join(unmatched[:10]))

# Enrich canonical fixtures from still-upcoming rows; never replace/shrink the draw.
for live in live_upcoming:
    for f in canonical:
        if same_tie(live,f):
            f.update({k:v for k,v in live.items() if v not in (None,'')}); break

# A matchday page can legitimately have fewer than 112 upcoming rows. Coverage means
# upcoming + completed rows observed, while canonical remains exactly 112.
observed_keys={(norm(x['home']),norm(x['away'])) for x in live_upcoming+live_results}
if not observed_keys:
    raise SystemExit('ABORT: no First Qualifying rows observed on live source')

# Preliminary chronology remains fully rebuilt from trusted completed sources.
data['preliminary_fixtures']=fmap(prelim)
for r in sorted(results,key=lambda x:(x['date'],0 if x['round']=='Preliminary Round' else 1)):add_result(data,r)

# Merge live First Qualifying results only after canonical tie validation.
for r in sorted(live_results,key=lambda x:(x['date'],norm(x['home']))):add_result(data,r)

data['fixtures']=fmap(canonical)
data['replays']={}
data['round_dates']={**(data.get('round_dates') or {}),'Preliminary Round':'2026-08-22','First Round Qualifying':'2026-09-05'}
data['updated_at']=datetime.now(timezone.utc).isoformat()
data['competition_sync']={
    'source':'Football Web Pages + static kick-off listing',
    'source_url':FIXTURES_URL,
    'kickoff_source_url':KICKOFF_SOURCE_URL,
    'synced_at':data['updated_at'],
    'preliminary_fixture_source':'played original ties',
    'preliminary_unique_fixtures':prelim_count,
    'preliminary_results_and_replays':result_count,
    'first_qualifying_canonical_fixtures':len(canonical),
    'first_qualifying_live_upcoming':len(live_upcoming),
    'first_qualifying_live_results':len(live_results),
    'first_qualifying_live_rows_observed':len(observed_keys),
    'result_dates':RESULT_DATES,
    'kickoffs_enriched':kickoff_enriched,
    'replay_kickoffs_verified':len(replay_results)
}
tmp=DATA_PATH.with_suffix('.json.new')
tmp.write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
tmp.replace(DATA_PATH)
print('COMPETITION CHRONOLOGY SYNC v3.2: SUCCESS')
print('Preliminary fixtures:',prelim_count)
print('Preliminary results/replays:',result_count)
print('First Qualifying canonical fixtures:',len(canonical))
print('First Qualifying live upcoming:',len(live_upcoming))
print('First Qualifying live results:',len(live_results))
print('First Qualifying live rows observed:',len(observed_keys))
print('Kick-offs enriched:',kickoff_enriched)
print('Replay kick-offs verified:',len(replay_results))
print('Frenford v Haringey Borough replay kick-off:',frenford['kickoff'])
print('Ground/location data: UNTOUCHED')
