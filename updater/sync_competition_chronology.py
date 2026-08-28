#!/usr/bin/env python3
"""Synchronise the completed Preliminary Round and current First Qualifying draw.

Free/public source: Football Web Pages. The write is guarded: no competition.json
change is made unless Preliminary fixture coverage, played-result coverage and the
112-tie First Qualifying draw all pass minimum completeness checks.
"""
import json,re,urllib.request
from datetime import datetime,timezone
from html import unescape
from html.parser import HTMLParser
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DATA_PATH=ROOT/'competition.json'
HTML_PATH=ROOT/'clubfinder.html'
BASE='https://www.footballwebpages.co.uk/fa-cup'
RESULT_DATES=['20260821','20260822','20260823','20260825','20260826']
FIXTURES_URL=f'{BASE}/fixtures-results'
UA='TinFoilFACupClubfinder/1.0 (+https://anvilspringstien.github.io/tinfoilfacup/)'

class PageParser(HTMLParser):
    def __init__(self):
        super().__init__(); self.stack=[]; self.buf=[]; self.events=[]; self.row=[]; self.cell=None
    def handle_starttag(self,tag,attrs):
        self.stack.append(tag)
        if tag in ('h2','h3','h4'): self.buf=[]
        if tag=='tr': self.row=[]
        if tag in ('td','th'): self.cell=[]
    def handle_data(self,data):
        if self.stack and self.stack[-1] in ('h2','h3','h4'): self.buf.append(data)
        if self.cell is not None: self.cell.append(data)
    def handle_endtag(self,tag):
        if tag in ('td','th') and self.cell is not None:
            txt=' '.join(''.join(self.cell).split()); self.row.append(unescape(txt)); self.cell=None
        if tag=='tr' and self.row:
            self.events.append(('row',self.row)); self.row=[]
        if tag in ('h2','h3','h4'):
            txt=' '.join(''.join(self.buf).split())
            if txt: self.events.append(('heading',unescape(txt)))
            self.buf=[]
        if self.stack:
            # HTML can be imperfect; remove the nearest matching open tag.
            for i in range(len(self.stack)-1,-1,-1):
                if self.stack[i]==tag:
                    self.stack=self.stack[:i]; break

def fetch(url):
    req=urllib.request.Request(url,headers={'User-Agent':UA,'Accept':'text/html,application/xhtml+xml'})
    with urllib.request.urlopen(req,timeout=30) as r:
        raw=r.read()
    return raw.decode('utf-8','replace')

def norm(s):
    s=(s or '').lower().replace('&',' and ')
    s=re.sub(r'\b(fc|afc|cfc)\b',' ',s)
    return re.sub(r'[^a-z0-9]+',' ',s).strip()

def aliases(name):
    suffix=re.compile(r'\s+(FC|AFC|CFC)$',re.I)
    out={name,suffix.sub('',name)}
    if not suffix.search(name): out|={name+' FC',name+' AFC'}
    return {x for x in out if x}

def parse_date_heading(text):
    m=re.search(r'(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\s+(\d{1,2})(?:st|nd|rd|th)\s+([A-Za-z]+)\s+(20\d{2})',text,re.I)
    if not m:return None
    return datetime.strptime(f'{m.group(2)} {m.group(3)} {m.group(4)}','%d %B %Y').date().isoformat()

def score_int(s):
    return int(s) if re.fullmatch(r'\d+',str(s or '').strip()) else None

def parse_time(s):
    s=(s or '').strip().lower().replace(' ','')
    if not s:return '15:00'
    for fmt in ('%I%p','%I.%M%p','%I:%M%p'):
        try:return datetime.strptime(s,fmt).strftime('%H:%M')
        except ValueError:pass
    return '15:00'

def parse_results(html,url,default_date):
    p=PageParser(); p.feed(html)
    current_date=default_date; current_round='Preliminary Round'; out=[]; last=None
    for kind,val in p.events:
        if kind=='heading':
            d=parse_date_heading(val)
            if d: current_date=d
            low=val.lower()
            if 'preliminary round replay' in low: current_round='Preliminary Round Replay'
            elif 'preliminary round' in low and 'extra' not in low: current_round='Preliminary Round'
            continue
        cells=[c.strip() for c in val if c.strip()]
        joined=' '.join(cells)
        # Penalty-decision detail often follows a level replay in its own row.
        pm=re.search(r'(.+?)\s+win\s+\d+\s*[-–]\s*\d+\s+on penalties',joined,re.I)
        if pm and last and last['home_score']==last['away_score']:
            last['winner']=pm.group(1).strip(); last['decision']=f'winner: {last["winner"]}; penalties'; continue
        if len(cells)<5 or not cells[0].upper().startswith('FT'): continue
        hs,as_=score_int(cells[2]),score_int(cells[3])
        if hs is None or as_ is None: continue
        home,away=cells[1],cells[4]
        rnd=current_round
        # 25 August included one delayed Preliminary Round tie before the replay programme.
        if current_date=='2026-08-25' and norm(home)==norm('Baffins Milton Rovers') and norm(away)==norm('Hartley Wintney'):
            rnd='Preliminary Round'
        elif current_date in ('2026-08-25','2026-08-26'):
            rnd='Preliminary Round Replay'
        winner=home if hs>as_ else away if as_>hs else ''
        decision='' if winner else ('draw-replay' if rnd=='Preliminary Round' else '')
        rec={'home':home,'away':away,'home_score':hs,'away_score':as_,'winner':winner,'status':'FT','decision':decision,'date':current_date,'round':rnd,'source_url':url}
        out.append(rec); last=rec
    return out

def extract_preliminary_fixtures(html):
    m=re.search(r'const PRELIM_FIXTURES_BY_CLUB=(\{.*?\});\s*const CURRENT_RESULT_OVERRIDES=',html,re.S)
    if not m: raise SystemExit('Could not locate PRELIM_FIXTURES_BY_CLUB in clubfinder.html')
    obj=json.loads(m.group(1)); uniq={}
    for f in obj.values():
        if not isinstance(f,dict) or not f.get('home') or not f.get('away'):continue
        key=(str(f.get('number','')),norm(f['home']),norm(f['away']),f.get('date',''))
        uniq.setdefault(key,{**f,'round':'Preliminary Round'})
    return list(uniq.values())

def parse_first_qualifying(html):
    p=PageParser(); p.feed(html)
    date=None; out=[]
    for kind,val in p.events:
        if kind=='heading':
            d=parse_date_heading(val)
            if d:date=d
            continue
        cells=[c.strip() for c in val if c.strip()]
        if len(cells)<4:continue
        # Expected fixture row: time | home | v | away.
        vi=next((i for i,c in enumerate(cells) if c.lower()=='v'),None)
        if vi is None or vi<2 or vi+1>=len(cells):continue
        time,home,away=cells[vi-2],cells[vi-1],cells[vi+1]
        if score_int(time) is not None or home.upper()=='FT':continue
        if not date:continue
        out.append({'round':'First Round Qualifying','home':home,'away':away,'date':date,'kickoff':parse_time(time)})
    uniq={}
    for f in out:uniq[(norm(f['home']),norm(f['away']),f['date'])]=f
    return list(uniq.values())

def result_key(r):
    return (norm(r.get('home')),norm(r.get('away')),r.get('date',''),r.get('home_score'),r.get('away_score'))

def result_same(a,b):return result_key(a)==result_key(b)

def add_result(data,r):
    results=data.setdefault('results',{}); history=data.setdefault('result_history',{})
    for club in aliases(r['home'])|aliases(r['away']):
        arr=history.setdefault(club,[])
        if not any(result_same(x,r) for x in arr):arr.append(r)
        arr.sort(key=lambda x:(x.get('date',''),0 if x.get('round')=='Preliminary Round' else 1))
        results[club]=arr[-1]

def fixture_alias_map(fixtures):
    out={}
    for f in fixtures:
        for club in aliases(f['home'])|aliases(f['away']):out[club]=f
    return out

# Fetch everything before touching disk.
club_html=HTML_PATH.read_text(encoding='utf-8')
prelim_fixtures=extract_preliminary_fixtures(club_html)
all_results=[]
for ds in RESULT_DATES:
    url=f'{BASE}/{ds}'
    all_results.extend(parse_results(fetch(url),url,datetime.strptime(ds,'%Y%m%d').date().isoformat()))
frq_fixtures=parse_first_qualifying(fetch(FIXTURES_URL))

# Safety gates: 136 scheduled Preliminary ties; essentially all are now complete after replays;
# and the published First Qualifying draw must be the known 112 ties.
prelim_unique={(norm(f['home']),norm(f['away']),f.get('date','')) for f in prelim_fixtures}
played_unique={result_key(r) for r in all_results}
if len(prelim_unique)<130: raise SystemExit(f'ABORT: Preliminary fixture scrape/extract too small: {len(prelim_unique)}')
if len(played_unique)<130: raise SystemExit(f'ABORT: Preliminary result scrape too small: {len(played_unique)}')
if len(frq_fixtures)!=112: raise SystemExit(f'ABORT: First Qualifying draw expected 112 ties, got {len(frq_fixtures)}')

# All gates passed: now build and atomically publish canonical competition state.
data=json.loads(DATA_PATH.read_text(encoding='utf-8'))
data['preliminary_fixtures']=fixture_alias_map(prelim_fixtures)
for r in sorted(all_results,key=lambda x:(x['date'],0 if x['round']=='Preliminary Round' else 1)):
    add_result(data,r)
data['fixtures']=fixture_alias_map(frq_fixtures)
data['replays']={}
data['round_dates']={**(data.get('round_dates') or {}),'Preliminary Round':'2026-08-22','First Round Qualifying':'2026-09-05'}
data['updated_at']=datetime.now(timezone.utc).isoformat()
data['competition_sync']={
    'source':'Football Web Pages','source_url':FIXTURES_URL,'synced_at':data['updated_at'],
    'preliminary_unique_fixtures':len(prelim_unique),'preliminary_results_and_replays':len(played_unique),
    'first_qualifying_unique_fixtures':len(frq_fixtures),'result_dates':RESULT_DATES
}

tmp=DATA_PATH.with_suffix('.json.new')
tmp.write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
tmp.replace(DATA_PATH)
print('COMPETITION CHRONOLOGY SYNC: SUCCESS')
print('Preliminary fixtures:',len(prelim_unique))
print('Preliminary results/replays:',len(played_unique))
print('First Qualifying fixtures:',len(frq_fixtures))
print('Ground/location data: UNTOUCHED')
