#!/usr/bin/env python3
"""Read-only excerpts for branch-scoped BETA replay and Stats diagnosis."""
import json,re
from pathlib import Path
html=Path('beta/clubfinder-beta.html').read_text()
data=json.loads(Path('competition.json').read_text())
for marker,span in [
 ('function resultTeamLine(',1800),
 ('function resultLinePlain(',1400),
 ('function tinFoilCertificateWinner(',1000),
 ('function replayFixtureFor(',1500),
 ('function currentDisplayFixture(',1600),
 ('function drawAlternatives(',900),
 ('async function journeyCertificate(',2900),
 ("'<div class=\\\"jr-winner\\\">'",700),
 ('const historyRows=crumbs.length',700),
 ('function completedResultDateLabel(',500)
]:
 i=html.find(marker)
 print('\n===',marker,'position',i,'===\n',html[i:i+span] if i>=0 else 'ABSENT')
for kind in ('results','result_history','replays'):
 matches=[]
 for rows in (data.get(kind) or {}).values():
  for r in rows if isinstance(rows,list) else [rows]:
   if not isinstance(r,dict):continue
   if r.get('date')=='2026-09-22' and 'Wimborne' in str(r.get('home')) and 'Weston' in str(r.get('away')):
    matches.append({k:r.get(k) for k in ('home','away','home_score','away_score','decision','winner','kickoff','round','date')})
 print('CANONICAL',kind,'matched',len(matches),'sample',json.dumps(matches[:1]))
