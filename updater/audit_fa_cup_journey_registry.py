#!/usr/bin/env python3
"""Read-only reconciliation of the official 2026-27 FA Cup field against Clubfinder's verified origin clubs.

Outputs reports only. It does not modify clubfinder.html, competition.json, GROUNDS, or canonical journey data.
"""
from pathlib import Path
import json, re, urllib.request

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / 'clubfinder.html'
OUT_MD = ROOT / 'fa-cup-journey-registry-audit.md'
OUT_JSON = ROOT / 'updater' / 'fa-cup-journey-registry-audit.json'
OUT_QUEUE = ROOT / 'updater' / 'journey-club-verification-queue.json'

ACCEPTED_URL = 'https://www.thefa.com/-/media/thefacom-new/files/competitions/2026-27/accepted-exemptions-and-prize-fund/020726/the-emirates-fa-cup---list-of-clubs-accepted.ashx'
EXEMPTIONS_URL = 'https://www.thefa.com/-/media/thefacom-new/files/competitions/2026-27/accepted-exemptions-and-prize-fund/the-emirates-fa-cup---list-of-exemptions.ashx'

# Explicit, evidence-backed identity changes. Never fuzzy-match club identities.
IDENTITY_ALIASES = {
    'Holmesdale FC': 'Petts Wood & Holmesdale FC',
    'Horsham YMCA FC': 'Horsham YM FC',
}

ROUND_NAMES = (
    'Extra Preliminary Round', 'Preliminary Round', 'First Round Qualifying',
    'Second Round Qualifying', 'Third Round Qualifying', 'Fourth Round Qualifying',
    'First Round Proper', 'Second Round Proper', 'Third Round Proper',
)

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

def exemption_round(line):
    u = re.sub(r'\s+',' ',line.upper()).strip()
    if 'EXEMPT TO' not in u: return None
    for r in ROUND_NAMES:
        if r.upper() in u:
            return r
    return None

html = HTML.read_text(encoding='utf-8')
eligible = extract_js_array(html, 'ELIGIBLE')
grounds = extract_js_array(html, 'GROUNDS')
origin_names = [x.get('name') or x.get('club') for x in eligible if (x.get('name') or x.get('club'))]
if len(origin_names) != 491:
    raise SystemExit(f'ABORT: expected protected 491 ELIGIBLE origin clubs, found {len(origin_names)}')

ground_names = [x.get('name') or x.get('club') for x in grounds if (x.get('name') or x.get('club'))]
ground_keys = {key(n) for n in ground_names}
origin_without_ground = [n for n in origin_names if key(n) not in ground_keys]
if origin_without_ground:
    raise SystemExit(f'ABORT: {len(origin_without_ground)} protected origin clubs have no GROUNDS record: {origin_without_ground[:10]}')
origin_keys = {key(x) for x in origin_names}
later_round_ground_records = [n for n in ground_names if key(n) not in origin_keys]

accepted_text = pdf_text(ACCEPTED_URL)
lines = [re.sub(r'\s+',' ',x).strip() for x in accepted_text.splitlines()]
clubs=[]
for line in lines:
    if not line or line.startswith('THE EMIRATES FA CUP') or line.startswith('SEASON 2026-27') or 'LIST OF 743 CLUBS' in line or line.startswith('Page '): continue
    if len(line) > 90 or line.lower().startswith(('the football association','clubs accepted')): continue
    clubs.append(line)
clubs=list(dict.fromkeys(clubs))
if len(clubs) != 743:
    raise SystemExit(f'ABORT: official accepted-list parser expected 743 clubs, parsed {len(clubs)}')
accepted_by_key={key(n):n for n in clubs}

# Apply only explicit identity aliases to the protected origin population.
resolved_origin=[]; alias_reconciliations=[]; unmatched_origin=[]
for n in origin_names:
    if key(n) in accepted_by_key:
        resolved_origin.append(accepted_by_key[key(n)])
        continue
    target=IDENTITY_ALIASES.get(n)
    if target and key(target) in accepted_by_key:
        resolved_origin.append(accepted_by_key[key(target)])
        alias_reconciliations.append({'origin_name':n,'official_name':accepted_by_key[key(target)]})
    else:
        unmatched_origin.append(n)
if unmatched_origin:
    raise SystemExit(f'ABORT: protected origin identities still unmatched after explicit aliases: {unmatched_origin}')
resolved_keys={key(n) for n in resolved_origin}
missing=[c for c in clubs if key(c) not in resolved_keys]
if len(missing) != 252:
    raise SystemExit(f'ABORT: expected 252 additional journey clubs after identity reconciliation, found {len(missing)}')

# Parse exemption headings conservatively: a heading must contain one known round name.
ex_text=pdf_text(EXEMPTIONS_URL)
ex_lines=[re.sub(r'\s+',' ',x).strip() for x in ex_text.splitlines() if x.strip()]
round_map={}; current=None
for line in ex_lines:
    r=exemption_round(line)
    if r:
        current=r
        continue
    if current and key(line) in accepted_by_key:
        round_map[key(line)]=current
entry_counts={}
for c in clubs:
    r=round_map.get(key(c),'Extra Preliminary Round')
    entry_counts[r]=entry_counts.get(r,0)+1
if sum(entry_counts.values()) != 743 or any(r not in ROUND_NAMES for r in entry_counts):
    raise SystemExit(f'ABORT: invalid exemption-round population: {entry_counts}')

# Annotate the exact 252-club queue with any ground record already present.
ground_by_key={key(n):n for n in ground_names}
queue=[]
for c in missing:
    existing=ground_by_key.get(key(c))
    queue.append({
        'club': c,
        'entry_round': round_map.get(key(c),'Extra Preliminary Round'),
        'existing_ground_record': existing,
        'verification_status': 'existing-ground-record-needs-registry-review' if existing else 'pending',
    })
existing_queue=sum(1 for x in queue if x['existing_ground_record'])
pending_queue=len(queue)-existing_queue

report={
 'official_accepted':743,
 'protected_origin_clubs':491,
 'identity_reconciliations':alias_reconciliations,
 'reconciled_origin_clubs':len(resolved_origin),
 'additional_journey_clubs':len(missing),
 'raw_ground_records':len(ground_names),
 'later_round_ground_records_outside_origin_population':len(later_round_ground_records),
 'additional_clubs_with_existing_ground_record':existing_queue,
 'additional_clubs_pending_ground_verification':pending_queue,
 'entry_round_counts':entry_counts,
 'additional_clubs':queue,
 'later_round_ground_records':later_round_ground_records,
 'sources':{'accepted':ACCEPTED_URL,'exemptions':EXEMPTIONS_URL},
 'read_only':True,
}
OUT_JSON.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
OUT_QUEUE.write_text(json.dumps({'generated_by':'audit_fa_cup_journey_registry.py','read_only_source_audit':True,'clubs':queue},indent=2,ensure_ascii=False)+'\n',encoding='utf-8')

md=['# FA Cup Journey Registry — Read-only reconciliation','',
    '- Official 2026-27 accepted clubs: **743**',
    '- Protected verified Clubfinder origin clubs: **491**',
    f'- Explicit identity reconciliations: **{len(alias_reconciliations)}**',
    '- Reconciled protected origin population: **491**',
    '- Additional journey clubs requiring registry coverage: **252**',
    f'- Raw GROUNDS records: **{len(ground_names)}**',
    f'- Existing ground records among the 252: **{existing_queue}**',
    f'- Additional clubs still pending ground verification: **{pending_queue}**','',
    '## Identity reconciliations']
for x in alias_reconciliations: md.append(f"- {x['origin_name']} → {x['official_name']}")
md += ['','## Official entry-round population']
for r in ROUND_NAMES:
    if r in entry_counts: md.append(f'- {r}: **{entry_counts[r]}**')
md += ['','## Additional journey-club verification queue']
for x in queue:
    suffix=f" — existing GROUNDS record: {x['existing_ground_record']}" if x['existing_ground_record'] else ''
    md.append(f"- {x['club']} — {x['entry_round']}{suffix}")
md += ['','## Safety',
       '- READ ONLY: no Clubfinder, competition, ground, venue, mileage or journey data was changed.',
       '- ELIGIBLE remains the protected 491 origin-club population.',
       '- Identity reconciliation uses explicit evidence-backed aliases only; no fuzzy identity guesses.',
       '- Official FA accepted/exemption PDFs remain the authority for membership and entry round.']
OUT_MD.write_text('\n'.join(md)+'\n',encoding='utf-8')
print('FA CUP JOURNEY REGISTRY AUDIT: SUCCESS')
print('Official accepted: 743'); print('Protected origin clubs: 491'); print('Identity reconciliations:',len(alias_reconciliations)); print('Additional journey clubs:',len(missing)); print('Existing ground records in additional queue:',existing_queue); print('Pending ground verification:',pending_queue); print('Entry rounds:',entry_counts); print('READ ONLY: canonical data untouched')
