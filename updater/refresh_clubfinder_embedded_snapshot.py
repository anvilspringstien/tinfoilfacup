#!/usr/bin/env python3
"""Embed the latest validated competition.json inside Clubfinder v7.6.

The live ./competition.json fetch remains authoritative when it succeeds. If it
is unavailable, Clubfinder now keeps using this last known-good canonical copy
instead of dropping back to the original August hard-coded journey tables.

Guarded and idempotent: abort if the expected v7.6 live-data boundaries are not
present, and replace only the dedicated embedded-snapshot block on later runs.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "competition.json"
HTML = ROOT / "clubfinder.html"
BEGIN = "/* TIN_FOIL_EMBEDDED_COMPETITION_BEGIN */"
END = "/* TIN_FOIL_EMBEDDED_COMPETITION_END */"

OLD_INIT = """const LIVE_COMPETITION_DATA_URL='./competition.json';\nlet LIVE_COMPETITION_DATA=null;\nlet LIVE_DATA_STATUS={state:'embedded',updated_at:null,message:'Using embedded competition snapshot'};"""
NEW_INIT_TAIL = """let LIVE_COMPETITION_DATA=EMBEDDED_COMPETITION_DATA;\nlet LIVE_DATA_STATUS={state:'embedded',updated_at:EMBEDDED_COMPETITION_DATA.updated_at||null,message:'Using embedded competition snapshot'};"""
OLD_CATCH = """}catch(e){LIVE_DATA_STATUS={state:'embedded',updated_at:null,message:'Embedded snapshot — live data unavailable'};}"""
NEW_CATCH = """}catch(e){LIVE_COMPETITION_DATA=EMBEDDED_COMPETITION_DATA;applyLiveRoundDates();LIVE_DATA_STATUS={state:'embedded',updated_at:EMBEDDED_COMPETITION_DATA.updated_at||null,message:'Embedded snapshot — live data unavailable'};}"""


def fail(message):
    raise SystemExit("EMBEDDED SNAPSHOT REFRESH: ABORT - " + message)


def main():
    data = json.loads(DATA.read_text(encoding="utf-8"))
    if Number := data.get("schema_version"):
        if int(Number) != 1:
            fail(f"unsupported competition schema {Number!r}")
    else:
        fail("competition.json has no schema_version")
    if not data.get("updated_at"):
        fail("competition.json has no updated_at timestamp")
    if not data.get("results") or not data.get("fixtures"):
        fail("competition.json lacks canonical results or active fixtures")

    html = HTML.read_text(encoding="utf-8")
    if "const LIVE_COMPETITION_DATA_URL='./competition.json';" not in html:
        fail("Clubfinder live-data URL boundary not found")
    if "async function refreshCompetitionData" not in html:
        fail("Clubfinder live-data refresh function not found")

    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    # Prevent an unexpected source string from terminating the surrounding script.
    payload = payload.replace("</script", "<\\/script")
    block = f"{BEGIN}\nconst EMBEDDED_COMPETITION_DATA={payload};\n{END}"

    if BEGIN in html or END in html:
        if html.count(BEGIN) != 1 or html.count(END) != 1:
            fail("embedded-snapshot markers are unbalanced")
        html, n = re.subn(
            re.escape(BEGIN) + r".*?" + re.escape(END),
            lambda _m: block,
            html,
            count=1,
            flags=re.S,
        )
        if n != 1:
            fail("could not replace existing embedded-snapshot block")
        old_tail = "let LIVE_COMPETITION_DATA=null;\nlet LIVE_DATA_STATUS={state:'embedded',updated_at:null,message:'Using embedded competition snapshot'};"
        current_tail = "let LIVE_COMPETITION_DATA=EMBEDDED_COMPETITION_DATA;\nlet LIVE_DATA_STATUS={state:'embedded',updated_at:EMBEDDED_COMPETITION_DATA.updated_at||null,message:'Using embedded competition snapshot'};"
        if old_tail in html:
            html = html.replace(old_tail, NEW_INIT_TAIL, 1)
        elif current_tail not in html:
            fail("embedded live-data initialisation boundary drifted")
    else:
        if html.count(OLD_INIT) != 1:
            fail(f"expected one original live-data initialisation block, found {html.count(OLD_INIT)}")
        replacement = "const LIVE_COMPETITION_DATA_URL='./competition.json';\n" + block + "\n" + NEW_INIT_TAIL
        html = html.replace(OLD_INIT, replacement, 1)

    if OLD_CATCH in html:
        html = html.replace(OLD_CATCH, NEW_CATCH, 1)
    elif NEW_CATCH not in html:
        fail("live-data fallback catch boundary drifted")

    if html.count(BEGIN) != 1 or html.count(END) != 1:
        fail("final embedded-snapshot marker count is not exactly one")
    if "let LIVE_COMPETITION_DATA=EMBEDDED_COMPETITION_DATA;" not in html:
        fail("Clubfinder does not initialise from embedded competition data")
    if "LIVE_COMPETITION_DATA=EMBEDDED_COMPETITION_DATA;applyLiveRoundDates();" not in html:
        fail("Clubfinder failure path does not restore embedded competition data")

    HTML.write_text(html, encoding="utf-8")
    print("EMBEDDED SNAPSHOT REFRESH: PASS")
    print("Competition snapshot timestamp:", data["updated_at"])
    print("Active fixtures embedded:", len(data.get("fixtures") or {}))
    print("Canonical result aliases embedded:", len(data.get("results") or {}))


if __name__ == "__main__":
    main()
