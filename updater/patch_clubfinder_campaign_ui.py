#!/usr/bin/env python3
"""Restore approved Clubfinder Campaign UI integrations without changing journey logic.

Presentation/integration only:
- restores the approved Pigeon Miles roundel image in Stats At a Glance,
- keeps the displayed Pigeon Miles value on one line,
- restores the yellow Challenges launcher and Candidate 13 bridge.

The Candidate 13 files are read-only reference material. This patch never modifies them.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / 'clubfinder.html'
BETA = ROOT / 'beta' / 'clubfinder-beta.html'
text = HTML.read_text(encoding='utf-8')
beta = BETA.read_text(encoding='utf-8')

PIGEON_MARKER = '/* TIN_FOIL_PIGEON_MILES_GLANCE */'
BRIDGE_MARKER = "const TIN_FOIL_CHALLENGE_BRIDGE_KEY='tffc.clubfinderCampaign.v1';"

# Candidate 13 carries the approved six-roundel artwork as an inline data URI.
beta_label = "'<div class=\"g\"><div class=\"g-label\">Pigeon<br>Miles</div><div class=\"icon-circle\"><img src=\"data:image/png;base64,"
bp = beta.find(beta_label)
if bp < 0:
    raise SystemExit('ABORT: approved Pigeon Miles card not found in frozen BETA reference')
be = beta.find("</div></div>'+", bp)
if be < 0:
    raise SystemExit('ABORT: approved Pigeon Miles card end not found')
approved_pigeon_card = beta[bp:be + len("</div></div>'+ ".rstrip())]
if 'alt="Pigeon Miles Flown"' not in approved_pigeon_card:
    raise SystemExit('ABORT: approved Pigeon Miles artwork marker missing')

pm = text.find(PIGEON_MARKER)
if pm < 0:
    raise SystemExit('ABORT: production Pigeon Miles At-a-Glance marker missing')
ps = text.find("'<div class=\"g\"><div class=\"g-label\">Pigeon<br>Miles", pm)
pe = text.find("</div></div>'+", ps)
if ps < 0 or pe < 0:
    raise SystemExit('ABORT: production Pigeon Miles card not found')
pe += len("</div></div>'+")
text = text[:ps] + approved_pigeon_card + text[pe:]

# Keep the approved card value on one line on narrow devices.
gnum_old = '.g-num{font-stretch:condensed;font-family:Arial Narrow,Arial,Helvetica,sans-serif;font-size:20pt;font-weight:700;line-height:1}'
gnum_new = '.g-num{font-stretch:condensed;font-family:Arial Narrow,Arial,Helvetica,sans-serif;font-size:20pt;font-weight:700;line-height:1;white-space:nowrap}'
if gnum_new not in text:
    if text.count(gnum_old) != 1:
        raise SystemExit(f'ABORT: expected one Stats g-num style anchor, found {text.count(gnum_old)}')
    text = text.replace(gnum_old, gnum_new, 1)

# Copy the tested Candidate 13 bridge, changing only the production-relative URL.
if BRIDGE_MARKER not in text:
    bs = beta.find(BRIDGE_MARKER)
    bridge_end = beta.find('async function journeyCertificate', bs)
    if bs < 0 or bridge_end < 0:
        raise SystemExit('ABORT: Candidate 13 bridge block not found')
    bridge = beta[bs:bridge_end]
    bridge = bridge.replace("window.open('challenges-beta.html','_blank');", "window.open('beta/challenges-beta.html','_blank');")
    # Use production's canonical historical venue resolver when present.
    old_venue_stats = "  function venueForStats(r){\n    if(!r)return {ground:'Venue TBC',postcode:'Postcode TBC'};"
    new_venue_stats = "  function venueForStats(r){\n    if(typeof completedResultVenue==='function')return completedResultVenue(r);\n    if(!r)return {ground:'Venue TBC',postcode:'Postcode TBC'};"
    bridge = bridge.replace(old_venue_stats, new_venue_stats, 1)
    old_venue_challenge = " function venueForChallenge(r){if(!r)return {postcode:'Postcode TBC'};"
    new_venue_challenge = " function venueForChallenge(r){if(typeof completedResultVenue==='function')return completedResultVenue(r);if(!r)return {postcode:'Postcode TBC'};"
    bridge = bridge.replace(old_venue_challenge, new_venue_challenge, 1)
    sig = 'async function journeyCertificate(origin){'
    if text.count(sig) != 1:
        raise SystemExit(f'ABORT: expected one journeyCertificate insertion anchor, found {text.count(sig)}')
    text = text.replace(sig, bridge + 'async function journeyCertificate(origin, suppliedWindow=null, returnMode="clubfinder"){', 1)

legacy_popup = '  const w=window.open("","_blank");'
reuse_popup = '  const w=suppliedWindow || window.open("","_blank");'
if reuse_popup not in text:
    if text.count(legacy_popup) != 1:
        raise SystemExit(f'ABORT: expected one Stats popup anchor, found {text.count(legacy_popup)}')
    text = text.replace(legacy_popup, reuse_popup, 1)

stats_print = '.print button{font:inherit;font-size:11px;padding:7px 12px}'
stats_return_css = '.stats-return{text-align:center;margin:0 auto 16px}.stats-return button{border:0;border-radius:20px;background:#084c61;color:#fff;padding:8px 14px;font:600 12px Arial,sans-serif;cursor:pointer}.stats-return button:hover{filter:brightness(.92)}'
if stats_return_css not in text:
    if text.count(stats_print) != 1:
        raise SystemExit(f'ABORT: expected one Stats print CSS anchor, found {text.count(stats_print)}')
    text = text.replace(stats_print, stats_print + stats_return_css, 1)

legacy_body = "  '</style></head><body><main class=\"sheet\">'+"
return_body = "  '</style></head><body><div class=\"stats-return\"><button type=\"button\" onclick=\"'+(returnMode===\"challenges\"?\"var c=window.open(&quot;&quot;,&quot;TFFC_CHALLENGES&quot;);if(c&amp;&amp;!c.closed){c.focus();window.close();}else{history.back();}\":\"if(window.opener&amp;&amp;!window.opener.closed){window.opener.focus();window.close();}else{history.back();}\")+'\">'+(returnMode===\"challenges\"?\"Back to Challenges\":\"Back to Clubfinder\")+'</button></div><main class=\"sheet\">'+"
if return_body not in text:
    if text.count(legacy_body) != 1:
        raise SystemExit(f'ABORT: expected one Stats body anchor, found {text.count(legacy_body)}')
    text = text.replace(legacy_body, return_body, 1)

challenge_css = '.challenges-launch{background:#e4bb26!important;color:#111!important}.challenges-launch:hover{filter:brightness(.92)}'
if challenge_css not in text:
    if text.count('</style></head><body>') != 1:
        raise SystemExit('ABORT: main style closing anchor not unique')
    text = text.replace('</style></head><body>', challenge_css + '</style></head><body>', 1)

tool_start = text.find("if(selected&&!showOriginal)tools=")
tool_end = text.find("else if(selected&&showOriginal)tools=", tool_start)
if tool_start < 0 or tool_end < 0:
    raise SystemExit('ABORT: selected Campaign toolbar not found')
toolbar = text[tool_start:tool_end]
challenge_button = "<button class=\"round challenges-launch\" type=\"button\" onclick=\\'openChallenges(ELIGIBLE.find(c=>norm(c.name)===norm('+JSON.stringify(origin.name)+')))\\'>Challenges</button>"
if 'class="round challenges-launch"' not in toolbar:
    anchor = "</button>'+(saved&&saved.ended?"
    ap = toolbar.find(anchor)
    if ap < 0:
        raise SystemExit('ABORT: Stats-to-Campaign-controls toolbar anchor not found')
    ap += len('</button>')
    toolbar = toolbar[:ap] + challenge_button + toolbar[ap:]
    text = text[:tool_start] + toolbar + text[tool_end:]

required = [
    PIGEON_MARKER, 'alt="Pigeon Miles Flown"', gnum_new, BRIDGE_MARKER,
    "window.open('beta/challenges-beta.html','_blank');", "window.name='TFFC_CLUBFINDER'",
    'window.tffcOpenStatsFromChallenges=', 'async function openChallenges(origin)',
    'async function journeyCertificate(origin, suppliedWindow=null, returnMode="clubfinder")',
    'Back to Challenges', challenge_css, 'class="round challenges-launch"',
]
for item in required:
    if item not in text:
        raise SystemExit('ABORT: required Campaign UI marker missing: ' + item)
if '>🐦</div>' in text[text.find(PIGEON_MARKER):text.find(PIGEON_MARKER)+1000]:
    raise SystemExit('ABORT: emoji Pigeon Miles fallback remains')
if text.count('class="round challenges-launch"') != 1:
    raise SystemExit('ABORT: Challenges launcher must appear exactly once in Campaign toolbar')

HTML.write_text(text, encoding='utf-8')
print('CLUBFINDER CAMPAIGN UI PATCH: SUCCESS')
print('Pigeon Miles: approved roundel restored; calculation untouched.')
print('Challenges: yellow Candidate 13 launcher/bridge restored at beta/challenges-beta.html.')
print('Replay, custody, competition data and Challenge Deck: UNTOUCHED')
