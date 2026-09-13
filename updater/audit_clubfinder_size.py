from pathlib import Path
import gzip
import re

HTML = Path('clubfinder.html')
COMP = Path('competition.json')
OUT = Path('clubfinder-size-audit.md')

text = HTML.read_text(encoding='utf-8')
raw = text.encode('utf-8')

def fmt(n):
    return f"{n:,} bytes ({n/1024:.1f} KiB, {n/1024/1024:.2f} MiB)"

# Measure the real outer document blocks only. The Stats certificate contains
# literal <style> markup inside JavaScript strings, so a whole-file regex would
# double count that text.
script_matches = list(re.finditer(r'<script[^>]*>([\s\S]*?)</script>', text, flags=re.I))
script_ranges = [(m.start(), m.end()) for m in script_matches]
script_bytes = sum(len(m.group(1).encode('utf-8')) for m in script_matches)

def inside_script(pos):
    return any(a <= pos < b for a, b in script_ranges)

style_matches = [m for m in re.finditer(r'<style[^>]*>([\s\S]*?)</style>', text, flags=re.I) if not inside_script(m.start())]
style_bytes = sum(len(m.group(1).encode('utf-8')) for m in style_matches)
# Everything not inside the content of the actual outer script/style blocks.
shell_bytes = len(raw) - script_bytes - style_bytes

# Data URIs are a prime suspect in a standalone evolutionary build.
data_uris = re.findall(r'data:([\w.+-]+/[\w.+-]+);base64,([A-Za-z0-9+/=]+)', text)
data_uri_rows = []
for i, (mime, payload) in enumerate(data_uris, 1):
    size = len((f'data:{mime};base64,' + payload).encode('utf-8'))
    data_uri_rows.append((size, i, mime))
data_uri_rows.sort(reverse=True)
data_uri_total = sum(r[0] for r in data_uri_rows)

# Extract top-level-ish const/let/var assignments by balanced bracket/string scanning.
# This is an audit heuristic, not a source transformer.
assign_re = re.compile(r'\b(const|let|var)\s+([A-Za-z_$][\w$]*)\s*=')
assignments = []
for m in assign_re.finditer(text):
    start = m.start()
    i = m.end()
    depth = {'(':0, '[':0, '{':0}
    quote = None
    esc = False
    while i < len(text):
        ch = text[i]
        if quote:
            if esc:
                esc = False
            elif ch == '\\':
                esc = True
            elif ch == quote:
                quote = None
            i += 1
            continue
        if ch in "'\"`":
            quote = ch
            i += 1
            continue
        if ch == '(':
            depth['('] += 1
        elif ch == ')':
            depth['('] = max(0, depth['(']-1)
        elif ch == '[':
            depth['['] += 1
        elif ch == ']':
            depth['['] = max(0, depth['[']-1)
        elif ch == '{':
            depth['{'] += 1
        elif ch == '}':
            depth['{'] = max(0, depth['{']-1)
        elif ch == ';' and not any(depth.values()):
            end = i + 1
            size = len(text[start:end].encode('utf-8'))
            if size >= 1000:
                assignments.append((size, m.group(2), start))
            break
        i += 1
assignments.sort(reverse=True)

# Large quoted literals, useful for spotting embedded images/templates.
large_strings = []
string_re = re.compile(r'(["\'])(?:(?=(\\?))\2.)*?\1', re.S)
for m in string_re.finditer(text):
    size = len(m.group(0).encode('utf-8'))
    if size >= 10000:
        preview = m.group(0)[1:81].replace('\n',' ')
        large_strings.append((size, preview))
large_strings.sort(reverse=True)

comp_size = COMP.stat().st_size if COMP.exists() else 0
gz = gzip.compress(raw, compresslevel=9)

lines = []
lines += [
    '# Clubfinder Size Audit',
    '',
    'Read-only structural audit of the current production `clubfinder.html`. No Clubfinder behaviour is changed by this audit.',
    '',
    '## Headline',
    '',
    f'- **clubfinder.html:** {fmt(len(raw))}',
    f'- **gzip level 9:** {fmt(len(gz))}',
    f'- **competition.json:** {fmt(comp_size)}',
    '',
    '## Broad composition',
    '',
    f'- Inline `<script>` content: **{fmt(script_bytes)}** ({script_bytes/len(raw)*100:.1f}% of file)',
    f'- Outer-page `<style>` content: **{fmt(style_bytes)}** ({style_bytes/len(raw)*100:.1f}% of file)',
    f'- Remaining HTML/tag shell: **{fmt(shell_bytes)}** ({shell_bytes/len(raw)*100:.1f}% of file)',
    f'- Embedded base64 data URIs: **{fmt(data_uri_total)}** across **{len(data_uri_rows)}** URI(s) ({data_uri_total/len(raw)*100:.1f}% of file)',
    '',
    '## Largest JavaScript assignments (heuristic)',
    '',
]
for size, name, pos in assignments[:25]:
    lines.append(f'- `{name}` — **{fmt(size)}**')
if not assignments:
    lines.append('- No assignments over 1 KiB detected by the heuristic parser.')

lines += ['', '## Embedded base64 payloads', '']
for size, idx, mime in data_uri_rows[:20]:
    lines.append(f'- Data URI #{idx} `{mime}` — **{fmt(size)}**')
if not data_uri_rows:
    lines.append('- None detected.')

lines += ['', '## Large quoted literals', '']
for size, preview in large_strings[:20]:
    lines.append(f'- **{fmt(size)}** — `{preview}…`')
if not large_strings:
    lines.append('- No quoted literals over 10 KiB detected.')

lines += [
    '',
    '## What this means',
    '',
    'This report deliberately separates **payload weight** from **application logic**. A large standalone HTML file is not automatically bloated code: embedded competition snapshots and inline image assets can dominate the byte count while the actual UI/logic remains comparatively small.',
    '',
    'The next step should be to classify the largest assignments and embedded payloads as one of: **required standalone payload**, **replaceable external/static asset**, **duplicated/evolutionary baggage**, or **live application logic**. Only then should a clean-sheet smaller build be attempted.',
]

OUT.write_text('\n'.join(lines) + '\n', encoding='utf-8')
print('\n'.join(lines))
