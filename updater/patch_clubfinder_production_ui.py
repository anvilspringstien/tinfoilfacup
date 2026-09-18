#!/usr/bin/env python3
"""Restore and guard approved production Campaign UI after Clubfinder rebuilds.

Presentation/bridge only:
- Campaign terminology on the live Clubfinder and Stats certificate.
- Candidate 13 yellow Challenges launcher + same-tab bridge into beta/.
- Approved Pigeon Miles roundel as the sixth At-a-Glance card, without desktop wrap.

Competition data, custody, result chronology, grounds and mileage formula are untouched.
"""
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[1]
HTML=ROOT/'clubfinder.html'
BRIDGE=ROOT/'updater'/'clubfinder-production-challenge-bridge.js'
ROUNDEL=ROOT/'updater'/'pigeon-miles-roundel-data-uri.txt'

text=HTML.read_text(encoding='utf-8')
bridge=BRIDGE.read_text(encoding='utf-8').strip()+"\n"
roundel=ROUNDEL.read_text(encoding='utf-8').strip()

if not roundel.startswith('data:image/png;base64,'):
    raise SystemExit('ABORT: approved Pigeon Miles roundel data URI missing')
if 'TIN_FOIL_PRODUCTION_CHALLENGE_BRIDGE_BEGIN' not in bridge or 'beta/challenges-beta.html' not in bridge:
    raise SystemExit('ABORT: approved production Challenges bridge invalid')

# --- Campaign terminology: user-facing text only -----------------------------------
literal_replacements={
    'Find your three nearest eligible clubs and follow your Tin Foil FA Cup Journey.':
        'Find your three nearest eligible clubs and follow your Tin Foil FA Cup Campaign.',
    'Tin Foil FA Cup Journey':'Tin Foil FA Cup Campaign',
    'Finding your Tin Foil FA Cup journey…':'Finding your Tin Foil FA Cup Campaign…',
    'View Original Journeys':'View Original Campaigns',
    'Resume My Journey':'Resume My Campaign',
    'End My Journey':'End My Campaign',
    'Return to My Journey':'Return to My Campaign',
    'Journey completed here.':'Campaign completed here.',
    'Journey started with: ':'This Campaign starts with: ',
    'YOUR TIN FOIL FA CUP JOURNEY':'YOUR TIN FOIL FA CUP CAMPAIGN',
    'THE JOURNEY SO FAR':'THE CAMPAIGN SO FAR',
    'The Journey Itself is The Source of Truth':'The Campaign Itself is The Source of Truth',
    'my journey':'my Campaign',
    ' Tin Foil FA Cup journeys found for ':' Tin Foil FA Cup Campaigns found for ',
}
for old,new in literal_replacements.items():
    text=text.replace(old,new)

# --- Yellow Challenges launcher ------------------------------------------------------
challenge_css='.challenges-launch{background:#e4bb26!important;color:#111!important}.challenges-launch:hover{filter:brightness(.92)}'
if challenge_css not in text:
    boundary='</style></head>'
    if boundary not in text:
        raise SystemExit('ABORT: main-page style boundary missing')
    text=text.replace(boundary,challenge_css+boundary,1)

if 'class="round challenges-launch"' not in text:
    stats_tail="'+(saved&&saved.ended?'Stats':'Stats')+'</button>'+(saved&&saved.ended?"
    if text.count(stats_tail)!=1:
        raise SystemExit(f'ABORT: expected one Stats-toolbar insertion boundary, found {text.count(stats_tail)}')
    challenges="'+(saved&&saved.ended?'Stats':'Stats')+'</button><button class=\"round challenges-launch\" type=\"button\" onclick=\\'openChallenges(ELIGIBLE.find(c=>norm(c.name)===norm('+JSON.stringify(origin.name)+')))\\'>Challenges</button>'+(saved&&saved.ended?"
    text=text.replace(stats_tail,challenges,1)

# Keep the approved bridge as a separately retained source, and replace/insert it
# deterministically on every rebuild.
bridge_pat=re.compile(
    r'/\* TIN_FOIL_PRODUCTION_CHALLENGE_BRIDGE_BEGIN \*/.*?/\* TIN_FOIL_PRODUCTION_CHALLENGE_BRIDGE_END \*/\n?',
    re.S,
)
if bridge_pat.search(text):
    text=bridge_pat.sub(lambda m:bridge,text,count=1)
else:
    boundary='async function journeyCertificate('
    pos=text.find(boundary)
    if pos<0:
        raise SystemExit('ABORT: journeyCertificate insertion boundary missing')
    text=text[:pos]+bridge+text[pos:]

old_sig='async function journeyCertificate(origin){\n  const w=window.open("","_blank");'
new_sig='async function journeyCertificate(origin,suppliedWindow=null,returnMode="clubfinder"){\n  const w=suppliedWindow || window.open("","_blank");'
if old_sig in text:
    text=text.replace(old_sig,new_sig,1)
elif new_sig not in text:
    raise SystemExit('ABORT: Stats certificate signature boundary missing')

stats_return_css='.stats-return{text-align:center;margin:0 auto 16px}.stats-return button{border:0;border-radius:20px;background:#084c61;color:#fff;padding:8px 14px;font:600 12px Arial,sans-serif;cursor:pointer}.stats-return button:hover{filter:brightness(.92)}'
if stats_return_css not in text:
    css_anchor=".print{text-align:center}.print button{font:inherit;font-size:11px;padding:7px 12px}'+"
    if text.count(css_anchor)!=1:
        raise SystemExit(f'ABORT: Stats return CSS boundary count {text.count(css_anchor)}')
    text=text.replace(css_anchor,css_anchor[:-2]+stats_return_css+"'+",1)

old_body="'</style></head><body><main class=\"sheet\">'+"
new_body="'</style></head><body><div class=\"stats-return\"><button type=\"button\" onclick=\"'+(returnMode===\"challenges\"?\"var c=window.open(&quot;&quot;,&quot;TFFC_CHALLENGES&quot;);if(c&amp;&amp;!c.closed){c.focus();window.close();}else{history.back();}\":\"if(window.opener&amp;&amp;!window.opener.closed){window.opener.focus();window.close();}else{history.back();}\")+'\">'+(returnMode===\"challenges\"?\"Back to Challenges\":\"Back to Clubfinder\")+'</button></div><main class=\"sheet\">'+"
if old_body in text:
    text=text.replace(old_body,new_body,1)
elif new_body not in text:
    raise SystemExit('ABORT: Stats return button boundary missing')

# --- Canonical Pigeon Miles wording -------------------------------------------------
# The pigeon does the work: user-facing distance copy is always "Flown".
text=text.replace('Pigeon Miles Travelled:','Pigeon Miles Flown:')
text=text.replace('Pigeon Miles Traveled:','Pigeon Miles Flown:')

# --- Approved Pigeon Miles roundel + six-column desktop layout -----------------------
old_grid='.glance{display:grid;grid-template-columns:repeat(5,1fr);'
new_grid='.glance{display:grid;grid-template-columns:repeat(6,minmax(0,1fr));'
if old_grid in text:
    text=text.replace(old_grid,new_grid,1)
elif new_grid not in text:
    raise SystemExit('ABORT: Stats At-a-Glance desktop grid boundary missing')

text=text.replace('.g{text-align:center;padding:3px 7px;', '.g{text-align:center;padding:3px 4px;',1)
text=text.replace('.g:last-child{grid-column:1/-1}', '.g:last-child{grid-column:auto}',1)

generic_card=(
    "  /* TIN_FOIL_PIGEON_MILES_GLANCE */\n"
    "  '<div class=\"g\"><div class=\"g-label\">Pigeon<br><span style=\"white-space:nowrap\">Miles Flown</span></div>"
    "<div class=\"icon-circle\" style=\"font-size:34px;line-height:1;display:flex;align-items:center;justify-content:center\" aria-label=\"Pigeon Miles\">🐦</div>"
    "<div class=\"g-num\">'+certEsc(pigeonMilesDisplay)+'</div></div>'+"
)
approved_card=(
    "  /* TIN_FOIL_PIGEON_MILES_GLANCE */\n"
    "  '<div class=\"g\"><div class=\"g-label\">Pigeon<br><span style=\"white-space:nowrap\">Miles Flown</span></div>"
    "<div class=\"icon-circle\"><img src=\""+roundel+"\" alt=\"Pigeon Miles Flown\"></div>"
    "<div class=\"g-num\">'+certEsc(pigeonMilesDisplay)+'</div></div>'+"
)
if generic_card in text:
    text=text.replace(generic_card,approved_card,1)
elif approved_card not in text:
    # Tolerate a prior approved card with the same marker by replacing only that card.
    card_pat=re.compile(
        r'  /\* TIN_FOIL_PIGEON_MILES_GLANCE \*/\n'
        r"  '<div class=\\?\"g\\?\"><div class=\\?\"g-label\\?\">Pigeon<br>Miles(?:<br>Flown)?</div>.*?"
        r"<div class=\\?\"g-num\\?\">\'\+certEsc\(pigeonMilesDisplay\)\+\'</div></div>\'\+",
        re.S,
    )
    if card_pat.search(text):
        text=card_pat.sub(lambda m:approved_card,text,count=1)
    else:
        raise SystemExit('ABORT: Pigeon Miles At-a-Glance card boundary missing')

# --- Fail-closed guard ---------------------------------------------------------------
required=(
    'My Tin Foil FA Cup Campaign',
    'View Original Campaigns',
    'End My Campaign',
    'This Campaign starts with: ',
    'YOUR TIN FOIL FA CUP CAMPAIGN',
    'THE CAMPAIGN SO FAR',
    'The Campaign Itself is The Source of Truth',
    'class="round challenges-launch"',
    'async function openChallenges(origin)',
    "window.location.href='beta/challenges-beta.html';",
    'TIN_FOIL_PRODUCTION_CHALLENGE_BRIDGE_BEGIN',
    'completedResultVenue(r)',
    'Pigeon Miles Flown',
    'Pigeon Miles Flown:',
    'Pigeon<br><span style="white-space:nowrap">Miles Flown</span>',
    'grid-template-columns:repeat(6,minmax(0,1fr))',
    '.g:last-child{grid-column:auto}',
    'certEsc(pigeonMilesDisplay)',
)
for marker in required:
    if marker not in text:
        raise SystemExit('ABORT: protected production UI marker missing: '+marker)

for forbidden in (
    'My Tin Foil FA Cup Journey',
    'View Original Journeys',
    'End My Journey',
    'Journey started with: ',
    'YOUR TIN FOIL FA CUP JOURNEY',
    'THE JOURNEY SO FAR',
    '>🐦</div><div class="g-num">',
    'Pigeon Miles Travelled:',
    'Pigeon Miles Traveled:',
    '<div class="g-label">Pigeon<br>Miles</div>',
    '<div class="g-label">Pigeon<br>Miles<br>Flown</div>',
):
    if forbidden in text:
        raise SystemExit('ABORT: retired production UI marker remains: '+forbidden)

if text.count('TIN_FOIL_PRODUCTION_CHALLENGE_BRIDGE_BEGIN')!=1:
    raise SystemExit('ABORT: Challenges bridge must appear exactly once')
if text.count('alt="Pigeon Miles Flown"')!=1:
    raise SystemExit('ABORT: approved Pigeon Miles roundel must appear exactly once')

HTML.write_text(text,encoding='utf-8')
print('CLUBFINDER PRODUCTION UI PATCH: SUCCESS')
print('Campaign terminology: RESTORED')
print('Challenges launcher/bridge: RESTORED')
print('Pigeon Miles approved roundel: RESTORED')
print('Pigeon Miles wording: FLOWN')
print('At-a-Glance desktop columns: 6 (no wrapped sixth card)')
print('Competition/custody/grounds/mileage formula: UNTOUCHED')
