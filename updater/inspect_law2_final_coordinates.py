#!/usr/bin/env python3
from pathlib import Path
import json,re
text=Path('clubfinder.html').read_text(encoding='utf-8')
m=re.search(r'\b(?:const|let|var)\s+LAW2_ORIGIN_LOCATIONS\s*=\s*\[',text)
s=text.find('[',m.start()); d=0; ins=False; esc=False; q=''
for i in range(s,len(text)):
 c=text[i]
 if ins:
  if esc: esc=False
  elif c=='\\': esc=True
  elif c==q: ins=False
 else:
  if c in ('"',"'"): ins=True;q=c
  elif c=='[': d+=1
  elif c==']':
   d-=1
   if d==0: e=i+1; break
rows=json.loads(text[s:e])
wanted={'AFC Totton','Basingstoke Town FC','Braintree Town FC','Forest Green Rovers FC','Gateshead FC','Gloucester City FC','Harrogate Town AFC','Horsham FC','Plymouth Parkway FC','Real Bedford FC','Redditch United FC'}
for r in rows:
 if (r.get('name') or r.get('club')) in wanted: print(json.dumps(r,ensure_ascii=False,sort_keys=True))
