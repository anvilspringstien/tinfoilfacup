#!/usr/bin/env python3
"""Give Pigeon Miles equal billing in the Stats certificate AT A GLANCE panel.

Presentation only. The existing Pigeon Miles calculation and detailed Stats line
remain unchanged.
"""
from pathlib import Path

p=Path('clubfinder.html')
text=p.read_text(encoding='utf-8')
marker='TIN_FOIL_PIGEON_MILES_GLANCE'
if marker in text:
    print('Pigeon Miles At-a-Glance patch already present; no change.')
    raise SystemExit(0)

label='Grounds<br>Visited'
pos=text.find(label)
if pos<0: raise SystemExit('ABORT: Grounds Visited At-a-Glance card not found')
section_end=text.find("  '</div></section>'+",pos)
if section_end<0: raise SystemExit('ABORT: AT A GLANCE section end not found')

card=("  /* TIN_FOIL_PIGEON_MILES_GLANCE */\n"
      "  '<div class=\"g\"><div class=\"g-label\">Pigeon<br>Miles</div>"
      "<div class=\"icon-circle\" style=\"font-size:34px;line-height:1;display:flex;align-items:center;justify-content:center\" aria-label=\"Pigeon Miles\">🐦</div>"
      "<div class=\"g-num\">'+certEsc(pigeonMilesDisplay)+'</div></div>'+\n")
text=text[:section_end]+card+text[section_end:]

required=[marker,'Pigeon<br>Miles','🐦',"certEsc(pigeonMilesDisplay)",'Pigeon Miles Flown:','2*hav(start,venue)']
for s in required:
    if s not in text: raise SystemExit('ABORT: required marker missing: '+s)
if text.count(marker)!=1: raise SystemExit('ABORT: At-a-Glance marker count is not one')

p.write_text(text,encoding='utf-8')
print('PIGEON MILES AT-A-GLANCE PATCH: SUCCESS')
print('Calculation unchanged. Challenge thresholds not added.')
