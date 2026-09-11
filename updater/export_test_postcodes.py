#!/usr/bin/env python3
import csv,json,re
from pathlib import Path
R=Path(__file__).resolve().parents[1]
T=(R/'clubfinder.html').read_text(encoding='utf-8')
def arr(name,required=True):
    m=re.search(r'\b(?:const|let|var)\s+'+re.escape(name)+r'\s*=\s*\[',T)
    if not m:
        if required: raise SystemExit(f'{name} not found')
        return []
    s=T.find('[',m.start()); d=0; ins=False; esc=False; q=''
    for i in range(s,len(T)):
        c=T[i]
        if ins:
            if esc: esc=False
            elif c=='\\': esc=True
            elif c==q: ins=False
        else:
            if c in ('\'', '"'): ins=True; q=c
            elif c=='[': d+=1
            elif c==']':
                d-=1
                if d==0: return json.loads(T[s:i+1])
    raise SystemExit(f'{name} unterminated')
E=arr('ELIGIBLE'); G=arr('GROUNDS'); S=arr('LAW2_ORIGIN_LOCATIONS',False)
def norm(s):
    s=(s or '').lower().replace('&',' and ').replace('’',"'")
    s=re.sub(r'\b(fc|afc|cfc|football club)\b',' ',s)
    return re.sub(r'[^a-z0-9]+',' ',s).strip()
canonical={norm(g.get('name') or g.get('club')):g for g in G}
support={norm(g.get('name') or g.get('club')):g for g in S}
rows=[]
for e in E:
    n=e.get('name',''); k=norm(n); g=canonical.get(k) or support.get(k) or {}
    rows.append((n,(g.get('postcode') or '').upper(),e.get('entry_round') or '', 'verified' if k in canonical else g.get('verification') or ''))
rows.sort(key=lambda x:x[0].lower())
missing=sum(not p for _,p,_,_ in rows)
if len(rows)!=651 or missing:
    raise SystemExit(f'Refusing export: rows={len(rows)}, missing_postcodes={missing}')
out=R/'tester-club-postcodes.csv'
with out.open('w',newline='',encoding='utf-8') as f:
    w=csv.writer(f); w.writerow(['Club','Postcode','Entry Round','Location Status']); w.writerows(rows)
print(f'Exported {len(rows)} Law 2 eligible club postcodes to {out.name}')
