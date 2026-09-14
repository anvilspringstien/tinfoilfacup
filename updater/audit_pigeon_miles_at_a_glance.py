#!/usr/bin/env python3
from pathlib import Path
import re

html=Path('clubfinder.html').read_text(encoding='utf-8')
# Remove enormous inline artwork so the structural Stats markup is readable.
clean=re.sub(r'data:image/[^;]+;base64,[A-Za-z0-9+/=]+','DATA_IMAGE_REDACTED',html)
start=clean.find('<section class="section"><div class="section-title">AT A GLANCE')
end=clean.find('</section>',start)
if start<0 or end<0: raise SystemExit('AT A GLANCE section not found')
glance=clean[start:end+10]
stat_i=clean.find('Pigeon Miles Travelled')
stat_snip=clean[max(0,stat_i-900):stat_i+1200] if stat_i>=0 else 'Pigeon Miles Travelled not found'
out=['# Pigeon Miles At-a-Glance audit','','READ ONLY. Production data unchanged.','','## Current AT A GLANCE markup','','```html',glance,'```','','## Current Pigeon Miles placement','','```html',stat_snip,'```','']
Path('pigeon-miles-at-a-glance-audit.md').write_text('\n'.join(out),encoding='utf-8')
print('PIGEON MILES AT-A-GLANCE AUDIT COMPLETE')
print('At-a-Glance chars:',len(glance))
