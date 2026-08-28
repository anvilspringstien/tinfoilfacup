#!/usr/bin/env python3
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
P=ROOT/'clubfinder.html'
text=P.read_text(encoding='utf-8')

old_round="+'</strong> • '+esc(next.name)+"
new_round="+'</strong> • '+esc(k.round||next.name)+"
old_link='s.next.drawUrl'
new_link='s.next.fixturesUrl'

rc_old=text.count(old_round); rc_new=text.count(new_round)
lc_old=text.count(old_link); lc_new=text.count(new_link)
if rc_old==1 and rc_new==0:text=text.replace(old_round,new_round,1)
elif not (rc_old==0 and rc_new>=1):raise SystemExit(f'ABORT: unexpected round renderer state old={rc_old} new={rc_new}')
if lc_old==1:text=text.replace(old_link,new_link,1)
elif lc_old!=0:raise SystemExit(f'ABORT: unexpected drawUrl reference count {lc_old}')
if 's.next.drawUrl' in text:raise SystemExit('ABORT: drawUrl reference remains')
if "esc(k.round||next.name)" not in text:raise SystemExit('ABORT: live fixture round patch missing')
P.write_text(text,encoding='utf-8')
print('CLUBFINDER COMPETITION PRESENTATION PATCH: SUCCESS')
print('Known next fixture uses its canonical round.')
print('View Next Round uses fixturesUrl.')
print('Ground/location logic: UNTOUCHED')

for needle in ('function resultFor','function currentDisplayFixture','function currentCarrier','function journey','function previous','function history','The current custodian of your Tin Foil FA Cup is:'):
    pos=text.find(needle)
    if pos>=0:
        start=max(0,pos-1400); end=min(len(text),pos+5200)
        print(f'--- DIAGNOSTIC {needle} ---')
        print(text[start:end].replace('\n',' '))
