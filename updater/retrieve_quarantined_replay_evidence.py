#!/usr/bin/env python3
"""Read-only live retrieval of independent reports for quarantined replay results.

Each source has its own publisher and a deliberately narrow extraction rule.
Never infer a score from a search snippet or accept an unrecognised layout.
"""
import argparse
from html.parser import HTMLParser
import json
import re
from urllib.request import Request, urlopen

from reconcile_quarantined_replay_evidence import reconcile

WIMBORNE = {
    "home": "Wimborne Town", "away": "Weston-super-Mare",
    "date": "2026-09-22",
    "reason": "penalty decision with non-level source score: independent verification required",
}
SOURCES = (
    ("wimbornetownfc.co.uk", "https://wimbornetownfc.co.uk/", "club"),
    ("southwestsportsnews.com",
     "https://mail.southwestsportsnews.com/football/results/8376-fa-cup-regional-2qr-replay-results-september-22",
     "regional"),
)


class VisibleText(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []
        self.hidden = 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self.hidden += 1

    def handle_endtag(self, tag):
        if tag in ("script", "style") and self.hidden:
            self.hidden -= 1

    def handle_data(self, data):
        if not self.hidden:
            self.parts.append(data)


def extract(domain, url, html):
    parser = VisibleText()
    parser.feed(html)
    text = re.sub(r"\\s+", " ", " ".join(parser.parts))
    # Explicitly require the 22 September replay, not Saturday's 19 September draw.
    if domain == "wimbornetownfc.co.uk":
        if not re.search(r"Second Round Qualifying Replay Tue 22 September", text, re.I):
            return None
        if not re.search(r"Wimborne Town\\s+1\\s*\\(4\\).*?Weston-super-Mare\\s+1\\s*\\(3\\).*?1-1\\s*\\(4-3 pens\\)", text, re.I):
            return None
    elif domain == "southwestsportsnews.com":
        if not re.search(r"TUESDAY SEPTEMBER 22, 2026", text, re.I):
            return None
        if not re.search(r"Wimborne Town 1-1\\s+Weston-super-Mare AFC\\s+AET.*?Wimborne win 4-3 on pens", text, re.I):
            return None
    else:
        return None
    return {
        "domain": domain, "url": url, "home": WIMBORNE["home"],
        "away": WIMBORNE["away"], "date": WIMBORNE["date"],
        "home_score": 1, "away_score": 1, "home_pens": 4, "away_pens": 3,
        "winner": "Wimborne Town", "decision": "penalties",
    }


def retrieve(fetch):
    evidence, failures = [], []
    for domain, url, _kind in SOURCES:
        try:
            html = fetch(url)
            item = extract(domain, url, html)
            if item is None:
                failures.append({"source": domain, "reason": "report absent or layout changed"})
            else:
                evidence.append(item)
        except Exception as exc:
            failures.append({"source": domain, "reason": type(exc).__name__})
    return evidence, failures


def fetch_live(url):
    with urlopen(Request(url, headers={"User-Agent": "TinFoilFACupReplayAudit/1.0"}), timeout=20) as response:
        return response.read().decode("utf-8", errors="replace")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--fetch", action="store_true", help="retrieve current original publisher pages")
    args = parser.parse_args()
    if not args.fetch:
        parser.error("specify --fetch")
    evidence, failures = retrieve(fetch_live)
    verdict = reconcile(WIMBORNE, evidence)
    print(json.dumps({"fixture": WIMBORNE, "evidence": evidence, "failures": failures,
                      "reconciliation": verdict, "production_mutation": False}, indent=2))
    if verdict["status"] != "independently_verified":
        raise SystemExit("Independent corroboration incomplete; result remains quarantined")


if __name__ == "__main__":
    main()
