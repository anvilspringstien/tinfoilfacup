#!/usr/bin/env python3
"""Expand Clubfinder's selectable Law 2 origins from 491 to 651.

Law 2 scope is every 2026-27 FA Cup club whose own campaign begins in the
qualifying competition: Extra Preliminary, Preliminary, First Qualifying,
Second Qualifying or Fourth Qualifying. Third Qualifying remains a journey
round but has no new entrant cohort in the published exemption structure.

Safety:
- never adds First/Third Round Proper entrants;
- never changes competition.json or custody/result logic;
- preserves the protected GROUNDS array;
- keeps supporting FCHD home-ground evidence separate and explicitly
  unverified until stronger evidence is approved;
- preserves the nearest-three UX.
"""
from pathlib import Path
import json
import re
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / 'clubfinder.html'
REGISTRY = ROOT / 'journey-club-registry.json'

LAW2_NEW_ROUNDS = {
    'First Round Qualifying',
    'Second Round Qualifying',
    'Fourth Round Qualifying',
}
LAW2_ALL_ROUNDS = {
    'Extra Preliminary Round',
    'Preliminary Round',
    *LAW2_NEW_ROUNDS,
}
EXPECTED_COUNTS = {
    'Extra Preliminary Round': 438,
    'Preliminary Round': 53,
    'First Round Qualifying': 88,
    'Second Round Qualifying': 48,
    'Fourth Round Qualifying': 24,
}


def norm(s):
    s = str(s or '').lower().replace('&', ' and ')
    s = re.sub(r'\b(fc|afc|cfc)\b', ' ', s)
    return re.sub(r'[^a-z0-9]+', ' ', s).strip()


def locate_array(text, name):
    m = re.search(r'\b(?:const|let|var)\s+' + re.escape(name) + r'\s*=\s*\[', text)
    if not m:
        return None
    start = text.find('[', m.start())
    depth = 0; in_str = False; esc = False; quote = ''
    for i in range(start, len(text)):
        ch = text[i]
        if in_str:
            if esc: esc = False
            elif ch == '\\': esc = True
            elif ch == quote: in_str = False
        else:
            if ch in ('"', "'"):
                in_str = True; quote = ch
            elif ch == '[': depth += 1
            elif ch == ']':
                depth -= 1
                if depth == 0:
                    return start, i + 1
    raise SystemExit(f'ABORT: unbalanced {name} array')


def read_array(text, name):
    loc = locate_array(text, name)
    if not loc:
        raise SystemExit(f'ABORT: {name} array not found')
    a, b = loc
    return json.loads(text[a:b]), a, b


def compact(value):
    return json.dumps(value, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')


def bulk_geocode(postcodes):
    unique = sorted({str(x or '').strip().upper() for x in postcodes if x})
    out = {}
    for pos in range(0, len(unique), 100):
        chunk = unique[pos:pos+100]
        body = json.dumps({'postcodes': chunk}).encode('utf-8')
        req = urllib.request.Request(
            'https://api.postcodes.io/postcodes',
            data=body,
            headers={
                'Content-Type': 'application/json',
                'User-Agent': 'TinFoilFACup-Law2-Origin-Builder/1.0',
            },
            method='POST',
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                payload = json.loads(r.read().decode('utf-8'))
        except Exception as exc:
            raise SystemExit(f'ABORT: Postcodes.io bulk geocode failed: {exc}')
        for item in payload.get('result') or []:
            pc = str(item.get('query') or '').strip().upper()
            res = item.get('result') or {}
            lat, lon = res.get('latitude'), res.get('longitude')
            if pc and lat is not None and lon is not None:
                out[pc] = (float(lat), float(lon))
    missing = [pc for pc in unique if pc not in out]
    if missing:
        raise SystemExit('ABORT: no coordinate result for: ' + ', '.join(missing))
    return out


if not HTML.exists() or not REGISTRY.exists():
    raise SystemExit('ABORT: Clubfinder or journey registry missing')

text = HTML.read_text(encoding='utf-8')
registry = json.loads(REGISTRY.read_text(encoding='utf-8'))
clubs = registry.get('clubs') or []
selected = [x for x in clubs if x.get('entry_round') in LAW2_NEW_ROUNDS]
if len(selected) != 160:
    raise SystemExit(f'ABORT: expected 160 additional Law 2 registry clubs, found {len(selected)}')

eligible, es, ee = read_array(text, 'ELIGIBLE')
grounds, gs, ge = read_array(text, 'GROUNDS')
if len({norm(x.get('name')) for x in eligible}) != len(eligible):
    raise SystemExit('ABORT: duplicate identity already present in ELIGIBLE')

by_eligible = {norm(x.get('name')): x for x in eligible}
by_ground = {norm(x.get('name') or x.get('club')): x for x in grounds}

# Add only the qualifying-round registry identities that are not already present.
for item in selected:
    key = norm(item.get('club'))
    if key not in by_eligible:
        rec = {'name': item['club'], 'entry_round': item['entry_round'], 'fixture': {}}
        eligible.append(rec)
        by_eligible[key] = rec
    else:
        by_eligible[key]['entry_round'] = item['entry_round']

# Protect the constitutional population and cohort counts.
if len(eligible) != 651:
    raise SystemExit(f'ABORT: Law 2 ELIGIBLE population is {len(eligible)}, expected 651')
counts = {}
for c in eligible:
    rnd = c.get('entry_round')
    counts[rnd] = counts.get(rnd, 0) + 1
    if rnd not in LAW2_ALL_ROUNDS:
        raise SystemExit(f"ABORT: non-Law-2 origin slipped into ELIGIBLE: {c.get('name')} — {rnd}")
if counts != EXPECTED_COUNTS:
    raise SystemExit(f'ABORT: Law 2 entry-round cohort drift: {counts}')

# Build a separate supporting-location layer. Existing guarded GROUNDS records
# remain authoritative and are never copied or modified here.
existing_support = []
loc = locate_array(text, 'LAW2_ORIGIN_LOCATIONS')
if loc:
    existing_support = json.loads(text[loc[0]:loc[1]])
existing_by = {norm(x.get('name')): x for x in existing_support}

support = []
needs_coords = []
for item in selected:
    key = norm(item.get('club'))
    if key in by_ground:
        continue
    evidence = item.get('supporting_ground_evidence') or []
    candidates = [x for x in evidence if x.get('ground') and x.get('postcode')]
    if len(candidates) != 1:
        raise SystemExit(f"ABORT: {item.get('club')} needs exactly one usable supporting home-ground candidate; found {len(candidates)}")
    ev = candidates[0]
    old = existing_by.get(key) or {}
    rec = {
        'name': item['club'],
        'ground': ev['ground'],
        'postcode': str(ev['postcode']).strip().upper(),
        'verification': 'supporting-evidence',
        'verification_label': '⚠️ Unverified',
        'source': ev.get('source') or 'FCHD gazetteer candidate evidence',
        'ground_source': 'Law 2 supporting home-ground evidence; not automatically verified',
        'law2_origin_location': True,
    }
    if old.get('postcode') == rec['postcode'] and old.get('lat') is not None and old.get('lon') is not None:
        rec['lat'] = float(old['lat']); rec['lon'] = float(old['lon'])
        rec['coordinate_source'] = old.get('coordinate_source') or 'Postcodes.io postcode centroid'
    else:
        needs_coords.append(rec['postcode'])
    support.append(rec)

if needs_coords:
    geo = bulk_geocode(needs_coords)
    for rec in support:
        if rec.get('lat') is None:
            rec['lat'], rec['lon'] = geo[rec['postcode']]
            rec['coordinate_source'] = 'Postcodes.io postcode centroid'

for rec in support:
    if rec.get('lat') is None or rec.get('lon') is None:
        raise SystemExit(f"ABORT: supplemental origin has no coordinates: {rec.get('name')}")

# Replace ELIGIBLE first, using the original array boundaries.
text = text[:es] + compact(eligible) + text[ee:]

# Install/refresh supporting locations directly after GROUNDS declaration.
# Re-locate GROUNDS after ELIGIBLE changed because character offsets moved.
_, gs, ge = read_array(text, 'GROUNDS')
support_decl = 'const LAW2_ORIGIN_LOCATIONS=' + compact(support) + ';'
loc = locate_array(text, 'LAW2_ORIGIN_LOCATIONS')
if loc:
    # Replace whole declaration including const/name/= and trailing semicolon.
    dm = re.search(r'\bconst\s+LAW2_ORIGIN_LOCATIONS\s*=\s*\[', text)
    if not dm: raise SystemExit('ABORT: supplemental declaration boundary missing')
    semi = text.find(';', loc[1])
    if semi < 0: raise SystemExit('ABORT: supplemental declaration semicolon missing')
    text = text[:dm.start()] + support_decl + text[semi+1:]
else:
    semi = text.find(';', ge)
    if semi < 0: raise SystemExit('ABORT: GROUNDS declaration semicolon missing')
    text = text[:semi+1] + support_decl + text[semi+1:]

# Nearest-club search continues to use the protected GROUNDS first, then the
# supplemental supporting layer. The existing rows.slice(0,3) remains untouched.
old_find = """function findGround(c){
  const candidates=[c.name,aliases[c.name],c.name.replace(/ FC$/,'').replace(/ AFC$/,'').replace(/ CFC$/,'')].filter(Boolean);
  for(const candidate of candidates){
    const n=norm(candidate);
    const g=GROUNDS.find(x=>norm(x.name)===n);
    if(g)return g;
  }
  return null
}"""
new_find = """function findGround(c){
  const candidates=[c.name,aliases[c.name],c.name.replace(/ FC$/,'').replace(/ AFC$/,'').replace(/ CFC$/,'')].filter(Boolean);
  for(const candidate of candidates){
    const n=norm(candidate);
    const g=GROUNDS.find(x=>norm(x.name)===n);
    if(g)return g;
    const s=LAW2_ORIGIN_LOCATIONS.find(x=>norm(x.name)===n);
    if(s)return s;
  }
  return null
}"""
if old_find in text:
    text = text.replace(old_find, new_find, 1)
elif new_find not in text:
    raise SystemExit('ABORT: findGround boundary changed')

# Custodian/fixture ground lookup also needs to know about the supplemental
# origin location layer when a later entrant becomes the current custodian.
old_gbc = """  const g=GROUNDS.find(g=>canonicalClubKey(g.name||g.club)===target);
  if(g)return g;
  const c=ELIGIBLE.find(c=>canonicalClubKey(c.name)===target);"""
new_gbc = """  const g=GROUNDS.find(g=>canonicalClubKey(g.name||g.club)===target);
  if(g)return g;
  const s=LAW2_ORIGIN_LOCATIONS.find(g=>canonicalClubKey(g.name||g.club)===target);
  if(s)return s;
  const c=ELIGIBLE.find(c=>canonicalClubKey(c.name)===target);"""
if old_gbc in text:
    text = text.replace(old_gbc, new_gbc, 1)
elif new_gbc not in text:
    raise SystemExit('ABORT: groundByClubName boundary changed')

# Explain later entry without inventing earlier rounds. This applies to all
# origins entering after the Extra Preliminary Round, including the existing
# Preliminary cohort.
old_prev = """  let body='<div class=\"history\"><div class=\"history-title\">Previous Rounds</div>'+\n    '<div class=\"history-origin\">Journey started with: '+esc(journey.origin.name)+'</div>';\n\n  if(!crumbs.length){"""
new_prev = """  let body='<div class=\"history\"><div class=\"history-title\">Previous Rounds</div>'+\n    '<div class=\"history-origin\">Journey started with: '+esc(journey.origin.name)+'</div>';\n  const entryRound=journey.origin.entry_round||'';\n  if(entryRound&&entryRound!=='Extra Preliminary Round'){\n    body+='<div class=\"history-entry\">'+esc(journey.origin.name)+' enters the competition at '+esc(entryRound)+'.</div>';\n  }\n\n  if(!crumbs.length){"""
if old_prev in text:
    text = text.replace(old_prev, new_prev, 1)
elif new_prev not in text:
    raise SystemExit('ABORT: previousRoundsHtml boundary changed')

# Guard the UX choice explicitly: exactly three original journey choices.
if 'const top=rows.slice(0,3);' not in text:
    raise SystemExit('ABORT: nearest-three selector changed')
if 'rows.slice(0,4)' in text or 'rows.slice(0,5)' in text:
    raise SystemExit('ABORT: nearest-three UX drift detected')

required = (
    'const LAW2_ORIGIN_LOCATIONS=',
    'LAW2_ORIGIN_LOCATIONS.find',
    "enters the competition at '+esc(entryRound)+'.",
    'const top=rows.slice(0,3);',
)
for marker in required:
    if marker not in text:
        raise SystemExit('ABORT: required Law 2 marker missing: ' + marker)

HTML.write_text(text, encoding='utf-8')
print('CLUBFINDER LAW 2 ORIGIN EXPANSION: SUCCESS')
print('Selectable Law 2 origins:', len(eligible))
for rnd in EXPECTED_COUNTS:
    print(rnd + ':', counts.get(rnd, 0))
print('Additional qualifying origins:', len(selected))
print('Supplemental supporting home-ground locations:', len(support))
print('Protected GROUNDS array: UNTOUCHED')
print('Nearest journeys returned: 3')
print('Proper-round-only origins: EXCLUDED')
