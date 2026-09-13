from pathlib import Path

src = Path('clubfinder.html').read_text(encoding='utf-8')
needle = 'function journeyCertificate(origin)'
start = src.find(needle)
if start < 0:
    raise SystemExit('journeyCertificate not found')
brace = src.find('{', start)
if brace < 0:
    raise SystemExit('journeyCertificate opening brace not found')

depth = 0
quote = None
escape = False
line_comment = False
block_comment = False
i = brace
while i < len(src):
    ch = src[i]
    nxt = src[i+1] if i + 1 < len(src) else ''
    if line_comment:
        if ch == '\n':
            line_comment = False
        i += 1
        continue
    if block_comment:
        if ch == '*' and nxt == '/':
            block_comment = False
            i += 2
            continue
        i += 1
        continue
    if quote:
        if escape:
            escape = False
        elif ch == '\\':
            escape = True
        elif ch == quote:
            quote = None
        i += 1
        continue
    if ch == '/' and nxt == '/':
        line_comment = True
        i += 2
        continue
    if ch == '/' and nxt == '*':
        block_comment = True
        i += 2
        continue
    if ch in ('\'', '"', '`'):
        quote = ch
        i += 1
        continue
    if ch == '{':
        depth += 1
    elif ch == '}':
        depth -= 1
        if depth == 0:
            end = i + 1
            break
    i += 1
else:
    raise SystemExit('journeyCertificate closing brace not found')

context = src[start:end]
Path('updater/pigeon_stats_context.txt').write_text(context, encoding='utf-8')
print(f'Extracted journeyCertificate: {len(context)} chars')
