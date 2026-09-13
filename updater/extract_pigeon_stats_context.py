from pathlib import Path

src = Path('clubfinder.html').read_text(encoding='utf-8')
needles = [
    'function journeyCertificate(origin)',
    'function venueForResult(r)',
    'let goals=0',
    "'<section class=\"bottom\"",
    'Travel mileage is deliberately not counted yet.',
    'window.open',
    'document.write',
]
parts = []
for needle in needles:
    positions = []
    pos = src.find(needle)
    while pos >= 0 and len(positions) < 4:
        positions.append(pos)
        pos = src.find(needle, pos + 1)
    parts.append(f'===== {needle!r} | matches={len(positions)} =====')
    for n, pos in enumerate(positions, 1):
        lo = max(0, pos - 1800)
        hi = min(len(src), pos + len(needle) + 2600)
        parts.append(f'--- match {n} at {pos} ---\n{src[lo:hi]}')

out = '\n\n'.join(parts)
Path('updater/pigeon_stats_context.txt').write_text(out, encoding='utf-8')
print(f'Extracted targeted Stats context: {len(out)} chars')
