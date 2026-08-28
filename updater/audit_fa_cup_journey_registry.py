#!/usr/bin/env python3
"""Read-only reconciliation of the official 2026-27 FA Cup field against Clubfinder's verified origin clubs.

Outputs a report only. It does not modify clubfinder.html, competition.json, GROUNDS, or any canonical data.
"""
from pathlib import Path
import json, re, urllib.request

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / 'clubfinder.html'
OUT_MD = ROOT / 'fa-cup-journey-registry-audit.md'
OUT_JSON = ROOT / 'updater' / 'fa-cup-journey-registry-audit.json'

ACCEPTED_URL = 'https://www.thefa.com/-/media/thefacom-new/files/competitions/2026-27/accepted-exemptions-and-prize-fund/020726/the-emirates-fa-cup---list-of-clubs-accepted.ashx'
EXEMPTIONS_URL = 'https://www.thefa.com/-/media/thefacom-new/files/competitions/2026-27/accepted-exemptions-and-prize-fund/the-emirates-fa-cup---list-of-exemptions.ashx'

# Official accepted list is a PDF. Keep the audit fail-closed rather than guessing if extraction changes.
def pdf_text(url):
    data = urllib.request.urlopen(url, timeout=30).read()
    try:
        from pypdf import PdfReader
        import io
        return '\n'.join((p.extract_text() or '') for p in PdfReader(io.BytesIO(data)).pages)
    except Exception as e:
        raise SystemExit(f'ABORT: cannot parse official FA PDF: {e}')

def key(name):
    s = str(name or '').lower().replace('&',' and ')
    s = re.sub(r'\b(association football club|football club)\b',' ',s)
    s = re.sub(r'\b(fc|afc|cfc)\b',' ',s)
    s = re.sub(r'[^a-z0-9]+',' ',s).strip()
    return re.sub(r'\s+',' ',s)

def extract_js_array(text, name):
    m = re.search(rf'(?:const|let|var)\s+{re.escape(name)}\s*=\s*(\[.*?\])\s*;', text, re.S)
    if not m: raise SystemExit(f'ABORT: {name} array not found')
    return json.loads(m.group(1))

html = HTML.read_text(encoding='utf-8')
eligible = extract_js_array(html, 'ELIGIBLE')
grounds = extract_js_array(html, 'GROUNDS')
verified_names = [x.get('name') or x.get('club') for x in grounds if (x.get('name') or x.get('club'))]
if len(verified_names) != 491:
    raise SystemExit(f'ABORT: expected protected 491 GROUNDS records, found {len(verified_names)}')

accepted_text = pdf_text(ACCEPTED_URL)
# Extract one club per line between header and footer; tolerate PDF page headers.
lines = [re.sub(r'\s+',' ',x).strip() for x in accepted_text.splitlines()]
clubs=[]
for line in lines:
    if not line or line.startswith('THE EMIRATES FA CUP') or line.startswith('SEASON 2026-27') or 'LIST OF 743 CLUBS' in line or line.startswith('Page '): continue
    # FA list entries are club-name lines; reject obvious footer/header prose.
    if len(line) > 90 or line.lower().startswith(('the football association','clubs accepted')): continue
    clubs.append(line)
# Preserve order, exact text.
clubs=list(dict.fromkeys(clubs))
if len(clubs) != 743:
    raise SystemExit(f'ABORT: official accepted-list parser expected 743 clubs, parsed {len(clubs)}')

verified_by_key={key(n):n for n in verified_names}
accepted_by_key={key(n):n for n in clubs}
matched=[]; missing=[]
for c in clubs:
    if key(c) in verified_by_key: matched.append(c)
    else: missing.append(c)
extra=[n for n in verified_names if key(n) not in accepted_by_key]

# Parse exemptions headings + following club names to establish entry-round population.
ex_text=pdf_text(EXEMPTIONS_URL)
ex_lines=[re.sub(r'\s+',' ',x).strip() for x in ex_text.splitlines() if x.strip()]
round_map={}
current=None
for line in ex_lines:
    u=line.upper()
    if 'EXEMPT TO' in u:
        current=re.sub(r'^\d+\s+CLUBS?\s+EXEMPT TO\s+','',u).split('(')[0].strip().title()
        continue
    if current and key(line) in accepted_by_key:
        round_map[key(line)]=current

entry_counts={}
for c in clubs:
    r=round_map.get(key(c),'Extra Preliminary Round')
    entry_counts[r]=entry_counts.get(r,0)+1

report={
 'official_accepted':len(clubs),
 'protected_verified_ground_records':len(verified_names),
 'matched_official_to_verified':len(matched),
 'official_not_in_verified_registry':len(missing),
 'verified_records_not_matched_to_official_list':len(extra),
 'entry_round_counts':entry_counts,
 'missing_clubs':missing,
 'unmatched_verified_records':extra,
 'sources':{'accepted':ACCEPTED_URL,'exemptions':EXEMPTIONS_URL},
 'read_only':True,
}
OUT_JSON.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
md=['# FA Cup Journey Registry — Read-only reconciliation','',f'- Official 2026-27 accepted clubs: **{len(clubs)}**',f'- Protected verified Clubfinder ground records: **{len(verified_names)}**',f'- Matched to official field: **{len(matched)}**',f'- Official clubs outside verified registry: **{len(missing)}**',f'- Protected records not matched to official field: **{len(extra)}**','','## Entry-round population']
for r,n in sorted(entry_counts.items(), key=lambda x:x[0]): md.append(f'- {r}: **{n}**')
md += ['','## Official clubs outside verified registry'] + [f'- {x}' for x in missing]
if extra: md += ['','## Protected records needing identity reconciliation'] + [f'- {x}' for x in extra]
md += ['','## Safety','- READ ONLY: no Clubfinder, competition, ground, venue, mileage or journey data was changed.','- Official accepted/exemption PDFs are the authority for membership and exemption round.']
OUT_MD.write_text('\n'.join(md)+'\n',encoding='utf-8')
print('FA CUP JOURNEY REGISTRY AUDIT: SUCCESS')
print('Official accepted:',len(clubs)); print('Protected verified:',len(verified_names)); print('Matched:',len(matched)); print('Missing:',len(missing)); print('Unmatched protected:',len(extra)); print('READ ONLY: canonical data untouched')
