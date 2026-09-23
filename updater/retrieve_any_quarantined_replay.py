#!/usr/bin/env python3
"""Generic read-only retrieval for any quarantined replay; no publication.

The caller supplies quarantined fixtures and a per-fixture list of authoritative
source URLs and publisher identities. This avoids inventing a club's official
domain or treating search snippets as evidence. Each original page is fetched,
its visible text checked for the fixture and replay date, and explicit score
and penalty statements extracted. Missing/ambiguous reports stay quarantined.
"""
import argparse
from datetime import date
from html.parser import HTMLParser
import json
import re
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from reconcile_quarantined_replay_evidence import reconcile


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


def normalise(text):
    return re.sub(r"[^a-z0-9]+", " ", text.casefold()).strip()


def visible(html):
    parser = VisibleText()
    parser.feed(html)
    return re.sub(r"\s+", " ", " ".join(parser.parts))


def extract(fixture, source, html):
    """Extract only explicit score+penalty evidence, not inferred match winners."""
    url = source["url"]
    host = urlparse(url).hostname or ""
    publisher = source["domain"].lower().removeprefix("www.")
    if urlparse(url).scheme != "https" or not (
        host == publisher or host.endswith("." + publisher)
    ):
        return None
    text = visible(html)
    home, away = fixture["home"], fixture["away"]
    if normalise(home) not in normalise(text) or normalise(away) not in normalise(text):
        return None
    match_date = date.fromisoformat(fixture["date"])
    # Require explicit date and replay context on the original page.
    date_forms = (
        match_date.strftime("%d %B %Y").lstrip("0"),
        match_date.strftime("%d %b %Y").lstrip("0"),
        match_date.strftime("%B %d, %Y").replace(" 0", " "),
        match_date.strftime("%A %B %d, %Y").replace(" 0", " "),
    )
    if not any(d.casefold() in text.casefold() for d in date_forms):
        return None
    if not re.search(r"replay|after extra time|\\bAET\\b|penalt(?:y|ies)|\\bpens\\b", text, re.I):
        return None
    # Only parse a single explicitly labelled, adjacent score line for both clubs.
    escaped_home, escaped_away = re.escape(home), re.escape(away)
    score_patterns = [
        (re.compile(escaped_home + r"\\s+(\\d{1,2})\\s*[-–:]\\s*(\\d{1,2})\\s+" + escaped_away, re.I), False),
        (re.compile(escaped_home + r"\\s+(\\d{1,2})\\s+" + escaped_away + r"\\s+(\\d{1,2})", re.I), False),
        (re.compile(escaped_away + r"\\s+(\\d{1,2})\\s*[-–:]\\s*(\\d{1,2})\\s+" + escaped_home, re.I), True),
    ]
    scores = set()
    for pattern, reverse in score_patterns:
        for m in pattern.finditer(text):
            pair = (int(m[1]), int(m[2]))
            scores.add(pair[::-1] if reverse else pair)
    if len(scores) != 1:
        return None
    home_score, away_score = scores.pop()
    if home_score != away_score:
        return None
    # Penalty winner must be explicit. Accept either "home win 4-3 on pens"
    # or "home won 4-3 on penalties"; never guess from score alone.
    pens = []
    for club, opponent, home_won in ((home, away, True), (away, home, False)):
        pattern = re.compile(re.escape(club) + r".{0,45}?\\b(?:win|wins|won)\\s+(\\d{1,2})\\s*[-–]\\s*(\\d{1,2})\\s+(?:on|after)\\s+(?:pens|penalties)", re.I)
        for m in pattern.finditer(text):
            winner_pens, loser_pens = int(m[1]), int(m[2])
            if winner_pens <= loser_pens:
                continue
            pens.append((winner_pens, loser_pens, home_won))
    if len(set(pens)) != 1:
        return None
    winner_pens, loser_pens, home_won = pens[0]
    return {
        "domain": publisher, "url": url, "home": home, "away": away,
        "date": fixture["date"], "home_score": home_score, "away_score": away_score,
        "home_pens": winner_pens if home_won else loser_pens,
        "away_pens": loser_pens if home_won else winner_pens,
        "winner": home if home_won else away, "decision": "penalties",
    }


def fetch_live(url):
    with urlopen(Request(url, headers={"User-Agent": "TinFoilFACupReplayAudit/1.0"}), timeout=20) as response:
        return response.read().decode("utf-8", errors="replace")


def retrieve(fixtures, source_manifest, fetch=fetch_live):
    output = []
    for fixture in fixtures:
        key = fixture["date"] + "|" + normalise(fixture["home"]) + "|" + normalise(fixture["away"])
        sources = source_manifest.get(key, [])
        evidence, failures = [], []
        for source in sources:
            try:
                item = extract(fixture, source, fetch(source["url"]))
                if item:
                    evidence.append(item)
                else:
                    failures.append({"url": source["url"], "reason": "no unambiguous replay score and penalties"})
            except Exception as exc:
                failures.append({"url": source["url"], "reason": type(exc).__name__})
        verdict = reconcile(fixture, evidence)
        output.append({"fixture": fixture, "evidence": evidence, "failures": failures,
                       "reconciliation": verdict, "production_mutation": False})
    return output


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--quarantine", required=True, help="JSON list of blocked fixtures")
    parser.add_argument("--sources", required=True, help="JSON map of fixture keys to official publisher URLs")
    args = parser.parse_args()
    with open(args.quarantine, encoding="utf-8") as f:
        fixtures = json.load(f)
    with open(args.sources, encoding="utf-8") as f:
        sources = json.load(f)
    print(json.dumps(retrieve(fixtures, sources), indent=2))


if __name__ == "__main__":
    main()
