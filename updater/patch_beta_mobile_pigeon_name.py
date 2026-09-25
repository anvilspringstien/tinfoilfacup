#!/usr/bin/env python3
"""One-off guarded BETA-only correction for long pigeon names on small phones."""
from pathlib import Path

path=Path("beta/clubfinder-beta.html")
text=path.read_text(encoding="utf-8")
changes=[
    (
      ".pigeon-name-input{display:inline-block;width:118px;max-width:40vw;",
      ".pigeon-name-input{display:inline-block;width:25ch;max-width:100%;",
    ),
    (
      ".pigeon-name-input:focus{border:0}.campaign-identity[hidden]{display:none}",
      ".pigeon-name-input:focus{border:0}.campaign-identity[hidden]{display:none}"
      "/* BETA phone identity: show the entire saved name in a wrapping row. */"
      "@media(max-width:480px){.campaign-identity{overflow-wrap:anywhere}"
      ".pigeon-name-divider{display:none}"
      ".pigeon-name-row{display:flex;flex-wrap:wrap;align-items:baseline;column-gap:6px;row-gap:2px;margin-top:4px}"
      ".pigeon-name-input{flex:1 1 190px;min-width:0;width:100%;max-width:100%}}",
    ),
    (
      "return 'Pigeon Call Sign: '+esc(callSign)+' · Pigeon Name: '+tinFoilPigeonNameInputHtml(saved);",
      "return 'Pigeon Call Sign: '+esc(callSign)"
      "+'<span class=\"pigeon-name-divider\"> · </span>'"
      "+'<span class=\"pigeon-name-row\">Pigeon Name: '+tinFoilPigeonNameInputHtml(saved)+'</span>';",
    ),
]
for old,new in changes:
    if text.count(old)!=1:
        raise SystemExit("ABORT: expected exactly one BETA anchor, found %s: %s" % (text.count(old),old[:70]))
    text=text.replace(old,new,1)
assert text.count("maxlength=\"20\"")==1
assert "Pigeon McPigeonface" not in text  # fixture belongs in tests, not saved data
path.write_text(text,encoding="utf-8")
print("BETA mobile Pigeon Name layout: 3 exact replacements; competition snapshot left intact.")
