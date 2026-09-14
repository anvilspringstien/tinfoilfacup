#!/usr/bin/env python3
"""Prepare the reviewed Law 2 batch 1 candidate using the established guarded ledger.

Updates only explicitly reviewed supplemental Law 2 records, appends their evidence
into the canonical verified-location ledger, then leaves promotion to the existing
promote_verified_law2_locations.py guard.
"""
from pathlib import Path
import json,re

ROOT=Path(__file__).resolve().parents[1]
HTML=ROOT/'clubfinder.html'
LEDGER=ROOT/'updater'/'law2-verified-location-ledger.json'
EVIDENCE=ROOT/'updater'/'law2-batch1-evidence.json'

def norm(s):
    s=str(s or '').lower().replace('&',' and ')
    s=re.sub(r'\b(fc|afc|cfc)\b',' ',s)
    return re.sub(r'[^a-z0-9]+',' ',s).strip()

def locate(t,n):
    m=re.search(r'\b(?:const|let|var)\s+'+re.escape(n)+r'\s*=\s*\[',t)
    if not m: raise SystemExit(f'ABORT: {n} missing')
    s=t.find('[',m.start()); d=0; ins=False; esc=False; q=''
    for i in range(s,len(t)):
        c=t[i]
        if ins:
            if esc: esc=False
            elif c=='\\': esc=True
            elif c==q: ins=False
        else:
            if c in ('"',"'"): ins=True;q=c
            elif c=='[':d+=1
            elif c==']':
                d-=1
                if d==0:return s,i+1
    raise SystemExit(f'ABORT: unbalanced {n}')

def compact(x):
    return json.dumps(x,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')

text=HTML.read_text(encoding='utf-8')
evidence=json.loads(EVIDENCE.read_text(encoding='utf-8'))
ledger=json.loads(LEDGER.read_text(encoding='utf-8'))
items=evidence.get('verified_locations') or []
if len(items)!=7: raise SystemExit(f'ABORT: expected 7 verified batch items, got {len(items)}')
if len(evidence.get('held_for_review') or [])!=1: raise SystemExit('ABORT: expected one held item')

p=locate(text,'LAW2_ORIGIN_LOCATIONS')
rows=json.loads(text[p[0]:p[1]])
by={norm(x.get('name') or x.get('club')):x for x in rows}

# Explicit current-ground corrections established by the batch review.
for item in items:
    club=item['club']; row=by.get(norm(club))
    if not row: raise SystemExit(f'ABORT: supplemental record missing for {club}')
    row['ground']=item['ground']
    row['postcode']=item['postcode']
    if 'latitude' in item:
        row['latitude']=item['latitude']; row['longitude']=item['longitude']
        row['coordinate_source']='Open Postcode Geo postcode centroid'
    row['ground_source']='Law 2 independently reviewed current home-ground evidence'

# AFC Totton remains deliberately unverified in this batch.
totton=by.get(norm('AFC Totton'))
if not totton: raise SystemExit('ABORT: AFC Totton record missing')
if str(totton.get('verification') or '').lower()=='verified':
    raise SystemExit('ABORT: AFC Totton unexpectedly already verified')

text=text[:p[0]]+compact(rows)+text[p[1]:]
HTML.write_text(text,encoding='utf-8')

existing=ledger.setdefault('verified_locations',[])
existing_by={norm(x.get('club')):x for x in existing}
for item in items:
    canonical={
        'club':item['club'],'ground':item['ground'],'postcode':item['postcode'],
        'verified_at':evidence['reviewed_at'],'sources':item['sources']
    }
    key=norm(item['club'])
    if key in existing_by:
        old=existing_by[key]
        if old!=canonical: raise SystemExit(f'ABORT: ledger already contains differing record for {item["club"]}')
    else:
        existing.append(canonical)
ledger['verified_locations']=existing
LEDGER.write_text(json.dumps(ledger,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print('LAW 2 BATCH 1 PREPARATION: SUCCESS')
print('Reviewed promotions prepared:',len(items))
print('Held for review: AFC Totton')
