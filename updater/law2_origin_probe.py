#!/usr/bin/env python3
from pathlib import Path
import json,re
ROOT=Path(__file__).resolve().parents[1]
text=(ROOT/'clubfinder.html').read_text(encoding='utf-8')

def arr(name):
    m=re.search(rf'(?:const|let|var)\s+{re.escape(name)}\s*=\s*(\[.*?\])\s*;',text,re.S)
    if not m: raise SystemExit(f'ABORT: {name} missing')
    return json.loads(m.group(1))

def snippet(label, token, before=500, after=1400):
    p=text.find(token)
    if p<0:
        print('LAW2 PROBE token',label,': NOT FOUND')
        return
    s=max(0,p-before); e=min(len(text),p+len(token)+after)
    print('LAW2 PROBE token',label,':',text[s:e].replace('\n','\\n'))

eligible=arr('ELIGIBLE'); grounds=arr('GROUNDS')
print('LAW2 PROBE eligible count:',len(eligible))
for club in ('Leatherhead FC','Epsom & Ewell FC','Newton Aycliffe FC'):
    x=next((r for r in eligible if (r.get('name') or r.get('club'))==club),None)
    g=next((r for r in grounds if (r.get('name') or r.get('club'))==club),None)
    print('LAW2 PROBE club',club,'eligible=',json.dumps(x,ensure_ascii=False,sort_keys=True),'ground=',json.dumps(g,ensure_ascii=False,sort_keys=True))
snippet('nearest-search','const rows=[]',before=4200,after=5200)
snippet('find-ground','function findGround',before=400,after=1500)
snippet('previous-rounds','function previousRoundsHtml',before=200,after=1300)
