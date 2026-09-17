#!/usr/bin/env python3
"""Guard the Clubfinder Campaign UI integrations without exercising competition data."""
from pathlib import Path
import base64
import hashlib
import re

ROOT=Path(__file__).resolve().parents[1]
text=(ROOT/'clubfinder.html').read_text(encoding='utf-8')
EXPECTED='143c833d4cdf61581282395a2b9a9d679f2fcdba3e0770198bab8f2562265bbc'

card=re.search(
    r'<div class="g"><div class="g-label">Pigeon<br>Miles</div>.*?'
    r'<img src="(data:image/png;base64,[^"]+)" alt="Pigeon Miles Flown">.*?'
    r'<div class="g-num">\'\+certEsc\(pigeonMilesDisplay\)\+\'</div></div>',
    text,re.S)
if not card: raise SystemExit('FAIL: approved Pigeon Miles At-a-Glance card missing')
raw=base64.b64decode(card.group(1).split(',',1)[1],validate=True)
h=hashlib.sha256(raw).hexdigest()
if h!=EXPECTED: raise SystemExit(f'FAIL: Pigeon Miles artwork hash drifted: {h}')
if '🐦' in card.group(0): raise SystemExit('FAIL: temporary pigeon emoji remains')

checks={
 'Pigeon number nowrap': '.g-num{white-space:nowrap;',
 'Challenges yellow style': '.challenges-launch{background:#e4bb26!important;color:#111!important}',
 'Challenges launcher': 'class="round challenges-launch"',
 'Campaign bridge key': "const TIN_FOIL_CHALLENGE_BRIDGE_KEY='tffc.clubfinderCampaign.v1';",
 'Clubfinder named window': "window.name='TFFC_CLUBFINDER'",
 'Challenges Stats bridge': 'window.tffcOpenStatsFromChallenges',
 'Production Challenges path': "window.open('beta/challenges-beta.html','_blank');",
 'Supplied Stats window': 'async function journeyCertificate(origin, suppliedWindow=null, returnMode="clubfinder")',
 'Back to Challenges': 'Back to Challenges',
 'Back to Clubfinder': 'Back to Clubfinder',
 'Canonical historical venue resolver in bridge': "typeof completedResultVenue==='function'",
 'Pigeon arithmetic still canonical': '2*hav(start,venue)',
}
for label,needle in checks.items():
    if needle not in text: raise SystemExit(f'FAIL: {label} missing')
if text.count('class="round challenges-launch"')!=1: raise SystemExit('FAIL: Challenges launcher must appear exactly once')
if text.count("const TIN_FOIL_CHALLENGE_BRIDGE_KEY=")!=1: raise SystemExit('FAIL: Challenges bridge must appear exactly once')
if "window.open('challenges-beta.html','_blank');" in text: raise SystemExit('FAIL: root Clubfinder still contains broken BETA-relative Challenges path')

print('CLUBFINDER CAMPAIGN UI REGRESSION: PASS')
print('Pigeon artwork SHA256:',h)
print('Challenges launcher + bridge: PASS')
print('Stats return path: PASS')
print('Canonical historical venue resolver reused: PASS')
