#!/usr/bin/env python3
"""Read-only diagnosis: reveal only focused BETA source excerpts and replay fields."""
import json,re
from pathlib import Path
html=Path('beta/clubfinder-beta.html').read_text()
data=json.loads(Path('competition.json').read_text())
print('BETA source length',len(html),'lines',html.count('\n')+1)
for pattern,left,right,limit in [
 ('function journeyCertificate(',300,10500,1),
 ('custodianDefeats',700,1100,3),
 ('custodianWins',450,1000,2),
 ('const draws',400,800,2),
 ("r.kickoff||",450,600,3),
 ('function completedResultVenue(',50,600,1),
 ('function canonicalResultWinner(',50,1000,1),
 ("r.decision==='penalties'",400,850,2),
 ('function resultLine(',150,1500,1),
 ('function resultFor(',50,800,1)
]:
  matches=list(re.finditer(re.escape(pattern),html))
  print('\n===',pattern,'matches',len(matches),'===')
  for m in matches[:limit]:
    lo=max(0,m.start()-left);hi=min(len(html),m.start()+right)
    s=html[lo:hi]
    # Embedded competition data should never be printed
    if s.count('{')>400: print('SKIPPED HUGE JSON'); continue
    print('pos',m.start(),'\n',s)
def target(r):
 return isinstance(r,dict) and r.get('date')=='2026-09-22' and 'Wimborne' in str(r.get('home')) and 'Weston' in str(r.get('away'))
for kind in ('results','result_history'):
 found=[]
 for rows in (data.get(kind) or {}).values():
  for r in rows if isinstance(rows,list) else [rows]:
   if target(r): found.append(r)
 print(kind,'Wimborne rows',json.dumps(found[:3],ensure_ascii=False))
