#!/usr/bin/env python3
import csv,json,re
from pathlib import Path
R=Path(__file__).resolve().parents[1]
T=(R/'clubfinder.html').read_text(encoding='utf-8')
def arr(name):
    m=re.search(r'\b(?:const|let|var)\s+'+re.escape(name)+r'\s*=\s*\[',T)
    if not m: raise SystemExit(f'{name} not found')
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
E=arr('ELIGIBLE'); G=arr('GROUNDS')
def norm(s):
    s=(s or '').lower().replace('&',' and ').replace('’',"'")
    s=re.sub(r'\b(fc|afc|cfc|football club)\b',' ',s)
    return re.sub(r'[^a-z0-9]+',' ',s).strip()
by={norm(g.get('name') or g.get('club')):g for g in G}
rows=[]
for e in E:
    n=e.get('name',''); g=by.get(norm(n),{})
    rows.append((n,(g.get('postcode') or '').upper()))
rows.sort(key=lambda x:x[0].lower())
if len(rows)!=491 or any(not p for _,p in rows):
    raise SystemExit(f'Refusing export: rows={len(rows)}, missing_postcodes={sum(not p for _,p in rows)}')
out=R/'tester-club-postcodes.csv'
with out.open('w',newline='',encoding='utf-8') as f:
    w=csv.writer(f); w.writerow(['Club','Postcode']); w.writerows(rows)
print(f'Exported {len(rows)} verified eligible club postcodes to {out.name}')
