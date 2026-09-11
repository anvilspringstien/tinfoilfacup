#!/usr/bin/env python3
"""Fail closed if Clubfinder's offline snapshot is stale or bypassed."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "competition.json"
HTML = ROOT / "clubfinder.html"
BEGIN = "/* TIN_FOIL_EMBEDDED_COMPETITION_BEGIN */"
END = "/* TIN_FOIL_EMBEDDED_COMPETITION_END */"


def fail(message):
    raise SystemExit("EMBEDDED SNAPSHOT REGRESSION: FAIL - " + message)


def main():
    canonical = json.loads(DATA.read_text(encoding="utf-8"))
    html = HTML.read_text(encoding="utf-8")

    if html.count(BEGIN) != 1 or html.count(END) != 1:
        fail("expected exactly one embedded competition marker block")

    match = re.search(
        re.escape(BEGIN) + r"\s*const EMBEDDED_COMPETITION_DATA=(.*?);\s*" + re.escape(END),
        html,
        flags=re.S,
    )
    if not match:
        fail("could not parse embedded competition payload")

    try:
        embedded = json.loads(match.group(1).replace("<\\/script", "</script"))
    except json.JSONDecodeError as exc:
        fail(f"embedded payload is not valid canonical JSON: {exc}")

    if embedded != canonical:
        fail(
            "embedded payload differs from competition.json "
            f"(embedded updated_at={embedded.get('updated_at')!r}, canonical updated_at={canonical.get('updated_at')!r})"
        )

    required = [
        "let LIVE_COMPETITION_DATA=EMBEDDED_COMPETITION_DATA;",
        "updated_at:EMBEDDED_COMPETITION_DATA.updated_at||null",
        "LIVE_COMPETITION_DATA=EMBEDDED_COMPETITION_DATA;applyLiveRoundDates();",
        "message:'Embedded snapshot — live data unavailable'",
    ]
    missing = [item for item in required if item not in html]
    if missing:
        fail("offline fallback wiring missing: " + " | ".join(missing))

    if "let LIVE_COMPETITION_DATA=null;" in html:
        fail("legacy null live-data initialisation is still present")

    print("EMBEDDED SNAPSHOT REGRESSION: PASS")
    print("Embedded snapshot exactly matches canonical competition.json")
    print("Snapshot timestamp:", embedded.get("updated_at"))
    print("Live-data failure path retains embedded canonical state: PASS")


if __name__ == "__main__":
    main()
