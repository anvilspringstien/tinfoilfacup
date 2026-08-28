#!/usr/bin/env python3
import html as htmlmod
import json
import re
import urllib.request
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
COMP=ROOT/'competition.json'
HTML=ROOT/'clubfinder.html'
SOURCE_URL='https://fchd.info/maps/GAZ.htm'

def norm(s):
    s=htmlmod.unescape(s or '').lower().replace('&',' and ')
    s=re.sub(r'\b(fc|afc|cfc|football club)\b',' ',s)
    return re.sub(r'[^a-z0-9]+',' ',s).strip()

def clean_markup(s):
    s=re.sub(r'<br\s*/?>','\n',s,flags=re.I)
    s=re.sub(r'<[^>]+>','\n',s)
    return [htmlmod.unescape(x).strip(' \t\r\n|') for x in s.splitlines() if htmlmod.unescape(x).strip(' \t\r\n|')]

def parse_fchd(raw):
    pat=re.compile(r'<h3\b[^>]*>(.*?)</h3>(.*?)(?=<h3\b|<h1\b|$)',re.I|re.S)
    pc_re=re.compile(r'\b(?:GIR 0AA|(?:[A-Z]{1,2}\d[A-Z\d]?|\d[A-Z]{2})\s*\d[A-Z]{2})\b',re.I)
    rows=[]
    for head,body in pat.findall(raw):
        club=' '.join(clean_markup(head)); lines=clean_markup(body)
        postcode=None
        for line in lines:
            m=pc_re.search(line)
            if m: postcode=m.group(0).upper(); break
        if not club or not postcode: continue
        useful=[x for x in lines if not pc_re.fullmatch(x) and not re.search(r'-?\d{1,2}\.\d+\s*,\s*-?\d{1,3}\.\d+',x) and not x.lower().startswith(('http://','https://'))]
        ground=useful[0] if useful else 'Ground TBC'
        if len(useful)>1 and re.search(r'\b(FC|AFC|CFC|Town|United|Athletic|Rovers|City)$',ground,re.I): ground=useful[1]
        rows.append({'club':club,'ground':ground,'postcode':postcode,'source':SOURCE_URL})
    return rows

def extract_js_array(text,name):
    m=re.search(r'\b(?:const|let|var)\s+'+re.escape(name)+r'\s*=\s*\[',text)
    if not m:return []
    st=text.find('[',m.start());d=0;ins=False;esc=False;q=''
    for i in range(st,len(text)):
        c=text[i]
        if ins:
            if esc:esc=False
            elif c=='\\':esc=True
            elif c==q:ins=False
        else:
            if c in ("'",'"'):ins=True;q=c
            elif c=='[':d+=1
            elif c==']':
                d-=1
                if d==0:return json.loads(text[st:i+1])
    return []

req=urllib.request.Request(SOURCE_URL,headers={'User-Agent':'Mozilla/5.0 TinFoilFACupLaterRoundVenues/7.9.21','Accept':'text/html,*/*'})
with urllib.request.urlopen(req,timeout=40) as r: raw=r.read().decode('utf-8','replace')
gaz=parse_fchd(raw); by={norm(x['club']):x for x in gaz}
comp=json.loads(COMP.read_text(encoding='utf-8'))
html=HTML.read_text(encoding='utf-8')
grounds=extract_js_array(html,'GROUNDS')
known={norm(g.get('name') or g.get('club')) for g in grounds}

fixtures=comp.get('fixtures',{}) or {}
values=list(fixtures.values()) if isinstance(fixtures,dict) else list(fixtures)
enriched_keys=set(); already_keys=set(); unresolved=[]
for f in values:
    if not isinstance(f,dict):continue
    home=f.get('home') or ''
    away=f.get('away') or ''
    if not home:continue
    fixture_key=(norm(home),norm(away),f.get('date',''),f.get('round',''))
    v=f.get('venue') or {}
    if v.get('postcode') and not re.search(r'TBC',str(v.get('postcode')),re.I):
        already_keys.add(fixture_key);continue
    if norm(home) in known:
        # Starter-club venues remain runtime-resolved from protected GROUNDS.
        continue
    row=by.get(norm(home))
    if not row:
        unresolved.append(home);continue
    f['venue']={'ground':row['ground'],'postcode':row['postcode'],'source':row['source'],'verification':'fchd-gazetteer'}
    enriched_keys.add(fixture_key)

comp['fixtures']=fixtures
COMP.write_text(json.dumps(comp,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print('LATER-ROUND VENUE ENRICHMENT v7.9.21')
print('FCHD records parsed:',len(gaz))
print('Fixture lookup entries:',len(values))
print('Unique later-round fixtures enriched:',len(enriched_keys))
print('Unique fixtures already carrying venue:',len(already_keys))
print('Unresolved later-round home clubs:',len(set(unresolved)))
for club in sorted(set(unresolved))[:50]:print('UNRESOLVED:',club)
print('Protected GROUNDS array: UNTOUCHED')
