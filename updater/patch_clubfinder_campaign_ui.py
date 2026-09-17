#!/usr/bin/env python3
"""Restore protected Clubfinder Campaign UI integrations.

Presentation/integration only:
- use the approved PIGEON_MILES_FLOWN Stats roundel from Candidate 13,
- restore the yellow Challenges launcher + Candidate 13 bridge,
- preserve the Challenges <-> Stats return path,
- keep Stats figures from wrapping awkwardly.

Competition data, replay progression, custody and Pigeon Miles arithmetic are untouched.
"""
from pathlib import Path
import base64
import hashlib
import re

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "clubfinder.html"
BETA = ROOT / "beta" / "clubfinder-beta.html"
APPROVED_PIGEON_SHA256 = "143c833d4cdf61581282395a2b9a9d679f2fcdba3e0770198bab8f2562265bbc"

text = HTML.read_text(encoding="utf-8")
beta = BETA.read_text(encoding="utf-8")

# --- Approved Pigeon Miles roundel -------------------------------------------
card_re = re.compile(
    r'<div class="g"><div class="g-label">Pigeon<br>Miles</div>'
    r'<div class="icon-circle"><img src="(data:image/png;base64,[^"]+)" alt="Pigeon Miles Flown"></div>'
    r'<div class="g-num">\'\+certEsc\(pigeonMilesDisplay\)\+\'</div></div>'
)
source_card = card_re.search(beta)
if not source_card:
    raise SystemExit("ABORT: approved Pigeon Miles Flown roundel not found in Candidate 13")
data_uri = source_card.group(1)
try:
    image_bytes = base64.b64decode(data_uri.split(",", 1)[1], validate=True)
except Exception as exc:
    raise SystemExit(f"ABORT: Candidate 13 Pigeon roundel is not valid base64: {exc}")
actual_hash = hashlib.sha256(image_bytes).hexdigest()
if actual_hash != APPROVED_PIGEON_SHA256:
    raise SystemExit(f"ABORT: Candidate 13 Pigeon roundel drifted ({actual_hash})")

approved_card = (
    '<div class="g"><div class="g-label">Pigeon<br>Miles</div>'
    f'<div class="icon-circle"><img src="{data_uri}" alt="Pigeon Miles Flown"></div>'
    '<div class="g-num">\'+certEsc(pigeonMilesDisplay)+\'</div></div>'
)
# Replace any current Pigeon Miles card, including the temporary emoji version.
current_card_re = re.compile(
    r'<div class="g"><div class="g-label">Pigeon<br>Miles</div>.*?'
    r'<div class="g-num">\'\+certEsc\(pigeonMilesDisplay\)\+\'</div></div>',
    re.S,
)
text, n = current_card_re.subn(lambda _: approved_card, text, count=1)
if n != 1:
    raise SystemExit(f"ABORT: expected one current Pigeon Miles card, replaced {n}")

# Keep numeric At-a-Glance figures intact on narrow screens.
if ".g-num{white-space:nowrap;" not in text:
    if text.count(".g-num{") < 1:
        raise SystemExit("ABORT: Stats g-num CSS anchor missing")
    text = text.replace(".g-num{", ".g-num{white-space:nowrap;", 1)

# --- Candidate 13 Challenges bridge -----------------------------------------
bridge_start = beta.find("const TIN_FOIL_CHALLENGE_BRIDGE_KEY='tffc.clubfinderCampaign.v1';")
bridge_end = beta.find("async function journeyCertificate", bridge_start)
if bridge_start < 0 or bridge_end < 0:
    raise SystemExit("ABORT: Candidate 13 bridge block not found")
bridge = beta[bridge_start:bridge_end]

# Production Clubfinder sits one directory above the BETA deck. Accept Candidate
# formatting/path drift but always reconcile to the one production-relative target.
production_target = "window.open('beta/challenges-beta.html','_blank');"
if production_target not in bridge:
    bridge, launch_n = re.subn(
        r"window\.open\(\s*(['\"])[^'\"]*challenges[^'\"]*\1\s*,\s*(['\"])_blank\2\s*\);",
        production_target,
        bridge,
        count=1,
        flags=re.I,
    )
    if launch_n != 1:
        raise SystemExit("ABORT: Candidate 13 Challenges launch call not found")

# Reuse Clubfinder's canonical historical-result venue resolver wherever the
# Candidate bridge still declares its local venue helpers. The fallback bodies
# remain intact for defensive compatibility.
if "function venueForStats(r){" in bridge and "function venueForStats(r){\n    if(typeof completedResultVenue==='function')" not in bridge:
    bridge, n = re.subn(
        r"function venueForStats\(r\)\{",
        "function venueForStats(r){\n    if(typeof completedResultVenue==='function')return completedResultVenue(r);",
        bridge,
        count=1,
    )
    if n != 1:
        raise SystemExit("ABORT: Candidate 13 Stats venue resolver adaptation failed")
if "function venueForChallenge(r){" in bridge and "function venueForChallenge(r){if(typeof completedResultVenue==='function')" not in bridge:
    bridge, n = re.subn(
        r"function venueForChallenge\(r\)\{",
        "function venueForChallenge(r){if(typeof completedResultVenue==='function')return completedResultVenue(r);",
        bridge,
        count=1,
    )
    if n != 1:
        raise SystemExit("ABORT: Candidate 13 Challenge venue resolver adaptation failed")
if production_target not in bridge:
    raise SystemExit("ABORT: production Challenges path adaptation failed")
if ("function venueForStats(r){" in bridge or "function venueForChallenge(r){" in bridge) and "completedResultVenue" not in bridge:
    raise SystemExit("ABORT: canonical historical venue resolver was not wired into Candidate bridge")

# Remove an older bridge if present, then insert the canonical adapted bridge.
existing_bridge = re.compile(
    r"const TIN_FOIL_CHALLENGE_BRIDGE_KEY='tffc\.clubfinderCampaign\.v1';.*?(?=async function journeyCertificate)",
    re.S,
)
text = existing_bridge.sub("", text, count=1)
sig_pos = text.find("async function journeyCertificate")
if sig_pos < 0:
    raise SystemExit("ABORT: journeyCertificate not found")
text = text[:sig_pos] + bridge + text[sig_pos:]

# Make Stats usable from Clubfinder or from the Challenges window.
text, n = re.subn(
    r'async function journeyCertificate\(origin(?:,\s*suppliedWindow=null,\s*returnMode="clubfinder")?\)\{\n\s*const w=(?:suppliedWindow \|\| )?window\.open\("","_blank"\);',
    'async function journeyCertificate(origin, suppliedWindow=null, returnMode="clubfinder"){\n  const w=suppliedWindow || window.open("","_blank");',
    text,
    count=1,
)
if n != 1:
    raise SystemExit(f"ABORT: expected one journeyCertificate popup signature, changed {n}")

stats_return_css = (
    '.stats-return{text-align:center;margin:0 auto 16px}'
    '.stats-return button{border:0;border-radius:20px;background:#084c61;color:#fff;padding:8px 14px;font:600 12px Arial,sans-serif;cursor:pointer}'
    '.stats-return button:hover{filter:brightness(.92)}'
)
if ".stats-return{" not in text:
    anchor = "'@media(max-width:650px){"
    if anchor not in text:
        raise SystemExit("ABORT: Stats mobile CSS anchor missing")
    text = text.replace(anchor, "'" + stats_return_css + "'+\n  " + anchor, 1)

beta_body_start = beta.find("'</style></head><body><div class=\"stats-return\"")
beta_body_end = beta.find("  '<section class=\"top\"", beta_body_start)
if beta_body_start < 0 or beta_body_end < 0:
    raise SystemExit("ABORT: Candidate 13 Stats return body prefix missing")
return_body = beta[beta_body_start:beta_body_end]

plain_body = "'</style></head><body><main class=\"sheet\">'+"
if "Back to Challenges" not in text:
    if plain_body not in text:
        raise SystemExit("ABORT: Stats document body anchor missing")
    text = text.replace(plain_body, return_body, 1)

# Yellow Challenges button styling in Clubfinder itself.
challenge_css = ".challenges-launch{background:#e4bb26!important;color:#111!important}.challenges-launch:hover{filter:brightness(.92)}"
if ".challenges-launch{" not in text:
    first_style_end = text.find("</style>")
    if first_style_end < 0:
        raise SystemExit("ABORT: Clubfinder style boundary missing")
    text = text[:first_style_end] + challenge_css + text[first_style_end:]

# Restore the launcher immediately after Stats in the selected Campaign toolbar.
if "class=\"round challenges-launch\"" not in text:
    toolbar_re = re.compile(
        r"(<button class=\"round stats-action\" type=\"button\" onclick=\\'journeyCertificate\(ELIGIBLE\.find\(c=>norm\(c\.name\)===norm\('\+JSON\.stringify\(origin\.name\)\+'\)\)\)\\'>.*?</button>)"
        r"(?=\'\+\(saved&&saved\.ended\?)"
    )
    m = toolbar_re.search(text)
    if not m:
        raise SystemExit("ABORT: selected Campaign Stats toolbar anchor missing")
    button = (
        '<button class="round challenges-launch" type="button" '
        "onclick=\\'openChallenges(ELIGIBLE.find(c=>norm(c.name)===norm('"
        "+JSON.stringify(origin.name)+'))\\'>Challenges</button>"
    )
    text = text[:m.end()] + button + text[m.end():]

required = [
    'alt="Pigeon Miles Flown"',
    ".g-num{white-space:nowrap;",
    "const TIN_FOIL_CHALLENGE_BRIDGE_KEY='tffc.clubfinderCampaign.v1';",
    "window.name='TFFC_CLUBFINDER'",
    "window.tffcOpenStatsFromChallenges",
    production_target,
    "async function journeyCertificate(origin, suppliedWindow=null, returnMode=\"clubfinder\")",
    "Back to Challenges",
    ".challenges-launch{background:#e4bb26!important;color:#111!important}",
    'class="round challenges-launch"',
]
for item in required:
    if item not in text:
        raise SystemExit(f"ABORT: required restored UI marker missing: {item}")
if "🐦" in text[text.find('<div class="g"><div class="g-label">Pigeon<br>Miles</div>'):][:1000]:
    raise SystemExit("ABORT: temporary Pigeon emoji still present in Stats card")
if text.count("class=\"round challenges-launch\"") != 1:
    raise SystemExit("ABORT: Challenges launcher count is not exactly one")
if text.count("const TIN_FOIL_CHALLENGE_BRIDGE_KEY=") != 1:
    raise SystemExit("ABORT: Challenges bridge count is not exactly one")

HTML.write_text(text, encoding="utf-8")
print("CLUBFINDER CAMPAIGN UI RESTORE: SUCCESS")
print("Pigeon roundel SHA256:", actual_hash)
print("Challenges target: beta/challenges-beta.html")
print("Canonical venue resolver reused by Challenges bridge: YES")
print("Competition data / replay / custody / Pigeon Miles arithmetic: UNTOUCHED")
