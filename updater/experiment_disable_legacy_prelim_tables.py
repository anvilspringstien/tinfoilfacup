#!/usr/bin/env python3
"""Disposable experiment: blank selected old preliminary fallback tables.

Usage:
  python updater/experiment_disable_legacy_prelim_tables.py prelim
  python updater/experiment_disable_legacy_prelim_tables.py epr
  python updater/experiment_disable_legacy_prelim_tables.py both

This is NOT a production patch. It mutates the checked-out working copy only.
"""
from pathlib import Path
import re
import sys

HTML = Path('clubfinder.html')
text = HTML.read_text(encoding='utf-8')

MODES = {
    'prelim': ('PRELIM_FIXTURES_BY_CLUB',),
    'epr': ('EPR_RESULTS_BY_TIE',),
    'both': ('PRELIM_FIXTURES_BY_CLUB', 'EPR_RESULTS_BY_TIE'),
}
mode = (sys.argv[1] if len(sys.argv) > 1 else 'both').lower()
if mode not in MODES:
    raise SystemExit('EXPERIMENT ABORT: mode must be prelim, epr or both')


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
for target in MODES[mode]:
    text = replace_assignment(text, target)
    if not re.search(r'const\s+' + re.escape(target) + r'\s*=\s*\{\}\s*;', text):
        raise SystemExit(f'EXPERIMENT ABORT: {target} was not blanked')

HTML.write_text(text, encoding='utf-8')
after = len(text.encode('utf-8'))
print('NO-LEGACY-PRELIM EXPERIMENT MODE:', mode)
for target in MODES[mode]:
    print(target, '-> {}')
print('Working-copy reduction:', before - after, 'bytes')
print('Production main: UNTOUCHED')
