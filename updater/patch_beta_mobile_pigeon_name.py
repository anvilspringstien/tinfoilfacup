#!/usr/bin/env python3
"""Guarded, idempotent BETA-only mobile pigeon-name presentation patch."""
import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "beta" / "clubfinder-beta.html"

MOBILE_CSS = """
/* BETA mobile: put the Call Sign and the full Pigeon Name on separate lines. */
@media(max-width:680px){
 .campaign-identity{white-space:normal}
 .campaign-call-sign{display:block;overflow-wrap:anywhere}
 .campaign-identity-separator{display:none}
 .campaign-pigeon-name{display:flex;align-items:baseline;flex-wrap:wrap;gap:2px 6px;min-width:0;margin-top:4px}
 .campaign-pigeon-label{flex:0 0 auto;white-space:nowrap}
 .campaign-pigeon-name .pigeon-name-input{display:block;flex:1 1 205px;min-width:0;width:auto;max-width:none;padding:0 2px 1px;line-height:1.4}
}
"""

OLD_JS = "return 'Pigeon Call Sign: '+esc(callSign)+' · Pigeon Name: '+tinFoilPigeonNameInputHtml(saved);"
NEW_JS = """return '<span class="campaign-call-sign">Pigeon Call Sign: '+esc(callSign)+'</span><span class="campaign-identity-separator" aria-hidden="true"> · </span><span class="campaign-pigeon-name"><span class="campaign-pigeon-label">Pigeon Name:</span> '+tinFoilPigeonNameInputHtml(saved)+'</span>';"""

REPLACEMENTS = [
    (
        ".pigeon-name-input{display:inline-block;width:118px;max-width:40vw",
        ".pigeon-name-input{display:inline-block;width:200px;max-width:40vw",
        "existing pigeon input width",
    ),
    (
        ".campaign-identity[hidden]{display:none}</style></head>",
        ".campaign-identity[hidden]{display:none}" + MOBILE_CSS + "</style></head>",
        "head style boundary",
    ),
    (OLD_JS, NEW_JS, "existing identity display"),
]


def patch(text):
    count = 0
    for before, after, label in REPLACEMENTS:
        if text.count(after) == 1 and text.count(before) == 0:
            continue  # Already patched; safe to run again.
        if text.count(before) != 1 or text.count(after) != 0:
            raise SystemExit(f"ABORT: {label} drifted or patch only partially applied")
        text = text.replace(before, after, 1)
        count += 1
    if 'maxlength="20"' not in text or "function tinFoilSavePigeonName" not in text:
        raise SystemExit("ABORT: pigeon naming or its 20-character limit changed")
    return text, count


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Require the committed BETA artifact to be fully patched")
    args = parser.parse_args()
    original = TARGET.read_text(encoding="utf-8")
    revised, count = patch(original)
    if args.check and count:
        raise SystemExit(f"FAIL: BETA artifact still needs {count} mobile pigeon-name patches")
    if revised != original and not args.check:
        TARGET.write_text(revised, encoding="utf-8")
    print(f"BETA mobile Pigeon Name: {'PASS (already patched)' if not count else 'PATCHED'}")


if __name__ == "__main__":
    main()
