#!/usr/bin/env python3
"""Refresh BETA's fallback from canonical competition.json without touching production.

Live ../competition.json is always authoritative. The snapshot is used only if
the live fetch fails; it must be an exact canonical last-known-good copy.
This deliberately does not invoke the production Clubfinder patch pipeline.
"""
import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BETA = ROOT / "beta/clubfinder-beta.html"
DATA = ROOT / "competition.json"
BEGIN = "/* TIN_FOIL_EMBEDDED_COMPETITION_BEGIN */"
END = "/* TIN_FOIL_EMBEDDED_COMPETITION_END */"
FALLBACK = (
    "catch(e){LIVE_COMPETITION_DATA=EMBEDDED_COMPETITION_DATA;"
    "applyLiveRoundDates();"
)


def refresh(html, data):
    if data.get("schema_version") != 1 or not data.get("updated_at"):
        raise ValueError("canonical competition schema/timestamp missing")
    if not data.get("result_history") or not data.get("fixtures"):
        raise ValueError("canonical result history/fixtures missing")
    if html.count(BEGIN) != 1 or html.count(END) != 1:
        raise ValueError("BETA embedded snapshot markers missing or duplicated")
    if html.count("const EMBEDDED_COMPETITION_DATA=") != 1:
        raise ValueError("BETA snapshot declaration missing or duplicated")
    if "const LIVE_COMPETITION_DATA_URL='../competition.json';" not in html:
        raise ValueError("BETA canonical live-data URL changed")
    if "let LIVE_COMPETITION_DATA=EMBEDDED_COMPETITION_DATA;" not in html:
        raise ValueError("BETA embedded initialisation changed")
    if FALLBACK not in html or "async function refreshCompetitionData" not in html:
        raise ValueError("BETA offline fallback boundary changed")
    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    payload = payload.replace("</script", "<\\/script")
    block = BEGIN + "\nconst EMBEDDED_COMPETITION_DATA=" + payload + ";\n" + END
    pattern = re.escape(BEGIN) + r".*?" + re.escape(END)
    updated, count = re.subn(pattern, lambda _match: block, html, count=1, flags=re.S)
    if count != 1 or updated.count(BEGIN) != 1 or updated.count(END) != 1:
        raise ValueError("BETA snapshot replacement was not unique")
    return updated


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true",
                        help="fail if committed BETA fallback differs from competition.json")
    args = parser.parse_args()
    canonical = json.loads(DATA.read_text(encoding="utf-8"))
    before = BETA.read_text(encoding="utf-8")
    after = refresh(before, canonical)
    if args.check and before != after:
        raise SystemExit("BETA FALLBACK GUARD: FAIL — embedded snapshot is stale")
    if not args.check and before != after:
        BETA.write_text(after, encoding="utf-8")
    print("BETA FALLBACK GUARD: PASS")
    print("Canonical snapshot updated_at:", canonical["updated_at"])
    print("Mode:", "check-only" if args.check else "refresh")
    print("Production files: untouched")


if __name__ == "__main__":
    main()
