#!/usr/bin/env python3
"""Disposable experiment: blank the old preliminary fallback tables in Clubfinder.

This is NOT a production patch. It mutates the checked-out working copy only so
CI can prove whether modern canonical competition data is sufficient without
PRELIM_FIXTURES_BY_CLUB and EPR_RESULTS_BY_TIE.
"""
from pathlib import Path
import re

HTML = Path('clubfinder.html')
text = HTML.read_text(encoding='utf-8')


def replace_assignment(source: str, name: str) -> str:
    m = re.search(r'\bconst\s+' + re.escape(name) + r'\s*=', source)
    if not m:
        raise SystemExit(f'EXPERIMENT ABORT: {name} declaration not found')
    i = m.end()
    while i < len(source) and source[i].isspace():
        i += 1
    if i >= len(source) or source[i] not in '[{':
        raise SystemExit(f'EXPERIMENT ABORT: {name} is not an object/array literal')
    open_ch = source[i]
    close_ch = '}' if open_ch == '{' else ']'
    depth = 0
    quote = None
    esc = False
    j = i
    while j < len(source):
        ch = source[j]
        if quote:
            if esc:
                esc = False
            elif ch == '\\':
                esc = True
            elif ch == quote:
                quote = None
        else:
            if ch in "'\"`":
                quote = ch
            elif ch == open_ch:
                depth += 1
            elif ch == close_ch:
                depth -= 1
                if depth == 0:
                    k = j + 1
                    while k < len(source) and source[k].isspace():
                        k += 1
                    if k >= len(source) or source[k] != ';':
                        raise SystemExit(f'EXPERIMENT ABORT: {name} declaration terminator not found')
                    replacement = '{}' if open_ch == '{' else '[]'
                    return source[:i] + replacement + source[j + 1:]
        j += 1
    raise SystemExit(f'EXPERIMENT ABORT: unbalanced {name} declaration')

before = len(text.encode('utf-8'))
for target in ('PRELIM_FIXTURES_BY_CLUB', 'EPR_RESULTS_BY_TIE'):
    text = replace_assignment(text, target)

if not re.search(r'const\s+PRELIM_FIXTURES_BY_CLUB\s*=\s*\{\}\s*;', text):
    raise SystemExit('EXPERIMENT ABORT: preliminary fixture table was not blanked')
if not re.search(r'const\s+EPR_RESULTS_BY_TIE\s*=\s*\{\}\s*;', text):
    raise SystemExit('EXPERIMENT ABORT: EPR result table was not blanked')

HTML.write_text(text, encoding='utf-8')
after = len(text.encode('utf-8'))
print('NO-LEGACY-PRELIM EXPERIMENT: TABLES DISABLED')
print('PRELIM_FIXTURES_BY_CLUB -> {}')
print('EPR_RESULTS_BY_TIE -> {}')
print('Working-copy reduction:', before - after, 'bytes')
print('Production main: UNTOUCHED')
