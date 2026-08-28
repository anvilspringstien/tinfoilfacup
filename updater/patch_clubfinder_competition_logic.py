#!/usr/bin/env python3
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
P=ROOT/'clubfinder.html'
text=P.read_text(encoding='utf-8')

old_round="+'</strong> • '+esc(next.name)+"
new_round="+'</strong> • '+esc(k.round||next.name)+"
old_link='s.next.drawUrl'
new_link='s.next.fixturesUrl'

rc=text.count(old_round)
lc=text.count(old_link)
if rc!=1: raise SystemExit(f'ABORT: expected exactly one known-fixture round renderer, found {rc}')
if lc!=1: raise SystemExit(f'ABORT: expected exactly one broken drawUrl reference, found {lc}')

text=text.replace(old_round,new_round,1).replace(old_link,new_link,1)
if 's.next.drawUrl' in text: raise SystemExit('ABORT: drawUrl reference remains')
if "esc(k.round||next.name)" not in text: raise SystemExit('ABORT: live fixture round patch missing')

P.write_text(text,encoding='utf-8')
print('CLUBFINDER COMPETITION PRESENTATION PATCH: SUCCESS')
print('Known next fixture now displays its canonical round.')
print('View Next Round now uses fixturesUrl.')
print('Ground/location logic: UNTOUCHED')
