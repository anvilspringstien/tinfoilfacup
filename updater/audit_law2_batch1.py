#!/usr/bin/env python3
from pathlib import Path
import json,re

HTML=Path('clubfinder.html')
OUT=Path('law2-batch1-audit.json')
MD=Path('law2-batch1-audit.md')
TARGETS=['AFC Fylde','AFC Totton','AFC Whyteleafe','Anstey Nomads FC','Aveley FC','Avro FC','Bamber Bridge FC','Banbury United FC']

def arr(text,name):
    m=re.search(r'\b(?:const|let|var)\s+'+re.escape(name)+r'\s*=\s*\[',text)
    if not m: raise SystemExit(f'ABORT: {name} not found')
    s=text.find('[',m.start()); d=0; ins=False; esc=False; q=''
    for i in range(s,len(text)):
        c=text[i]
        if ins:
            if esc: esc=False
            elif c=='\\': esc=True
            elif c==q: ins=False
        else:
            if c in ('"',"'"): ins=True; q=c
            elif c=='[': d+=1
            elif c==']':
                d-=1
                if d==0: return json.loads(text[s:i+1])
    raise SystemExit(f'ABORT: {name} unbalanced')

def norm(s):
    s=str(s or '').lower().replace('&',' and ')
    s=re.sub(r'\b(fc|afc|cfc)\b',' ',s)
    return re.sub(r'[^a-z0-9]+',' ',s).strip()

text=HTML.read_text(encoding='utf-8')
rows=arr(text,'LAW2_ORIGIN_LOCATIONS')
by={norm(r.get('name') or r.get('club')):r for r in rows}
found=[]
for club in TARGETS:
    r=by.get(norm(club))
    if r is None: raise SystemExit(f'ABORT: target missing: {club}')
    found.append({'club':club,'record':r})
OUT.write_text(json.dumps({'targets':found},indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
lines=['# Law 2 Batch 1 audit','','READ ONLY. No Clubfinder data modified.','']
for x in found:
    lines += [f"## {x['club']}",'','```json',json.dumps(x['record'],indent=2,ensure_ascii=False),'```','']
MD.write_text('\n'.join(lines),encoding='utf-8')
print('LAW 2 BATCH 1 AUDIT COMPLETE:',len(found),'records')
