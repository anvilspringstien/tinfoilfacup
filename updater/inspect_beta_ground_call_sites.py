#!/usr/bin/env python3
"""Print targeted BETA Clubfinder ground-location call-sites for review only.
No writes or competition transforms.
"""
from pathlib import Path
import re
source=Path("beta/clubfinder-beta.html").read_text(encoding="utf-8")
patterns=[
 r"Ground location unavailable", r"Postcode unavailable",r"No location data available",
 r"LAW2_ORIGIN_LOCATIONS",r"\bGROUNDS\b", r"current custodian",
 r"function [\w]*[Gg]round",r"function [\w]*[Ll]ocation",
]
for pattern in patterns:
 hits=list(re.finditer(pattern, source, re.IGNORECASE))
 print(f"=== {pattern}: {len(hits)} occurrences ===")
 for hit in hits[:4]:
  start=max(0,hit.start()-460)
  end=min(len(source),hit.end()+680)
  segment=source[start:end].replace("\x00"," ")
  # Public site source only; do not dump hidden tokens or large chunks
  print(f"OFFSET {hit.start()}: {segment[:1200]}\n-----")
