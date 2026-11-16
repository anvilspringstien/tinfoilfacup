"""Convert dated BBC competition score rows to Results observations."""

import re
from html.parser import HTMLParser
from urllib.parse import urlsplit


class ScoreLinks(HTMLParser):
    def __init__(self):
        super().__init__()
        self.labels = set()
        self.match_ids = set()
        self.match_id = None
        self.summary = None

    def handle_starttag(self, tag, attrs):
        if tag == "span" and self.match_id and "visually-hidden" in dict(attrs).get("class", "").split():
            self.summary = []
            return
        if tag != "a":
            return
        attrs = dict(attrs)
        href = urlsplit(attrs.get("href", ""))
        if href.path.startswith("/sport/football/live/") and href.netloc in {
            "", "www.bbc.co.uk", "www.bbc.com",
        }:
            self.match_id = href.path.rsplit("/", 1)[-1]
            self.match_ids.add(self.match_id)

    def handle_data(self, data):
        if self.summary is not None:
            self.summary.append(data)

    def handle_endtag(self, tag):
        if tag == "span" and self.summary is not None:
            self.labels.add((self.match_id, " ".join(self.summary).strip()))
            self.summary = None
        if tag == "a":
            self.match_id = None
            self.summary = None


FULL_TIME = re.compile(
    r"^(.+?)\s+(\d+)\s*,\s*(.+?)\s+(\d+)\s+(at Full time|After extra time)(?:\s|$)",
    re.IGNORECASE,
)
BBC_ALIASES = {"fylde": "AFC Fylde"}


def full_time_observations(raw, fixtures, match_date, source_url, match_fixture, dated_raw):
    """Accept decisive full-time rows from a single dated competition source."""
    dated = [fixture for fixture in fixtures if str(fixture.get("date", ""))[:10] == match_date]
    links = ScoreLinks()
    links.feed(raw)
    dated_links = ScoreLinks()
    dated_links.feed(dated_raw)
    observations = []
    for match_id, label in sorted(links.labels):
        if match_id not in dated_links.match_ids:
            continue
        match = FULL_TIME.match(label)
        if not match:
            continue
        home, home_score, away, away_score, status = match.groups()
        home = BBC_ALIASES.get(home.casefold(), home)
        away = BBC_ALIASES.get(away.casefold(), away)
        home_score, away_score = int(home_score), int(away_score)
        if home_score == away_score:
            continue
        fixture = match_fixture(dated, home, away)
        if fixture is None:
            continue
        observations.append({
            "fixture": fixture,
            "observation": {
                "home": home,
                "away": away,
                "home_score": home_score,
                "away_score": away_score,
                "status": "FT AET" if status.casefold() == "after extra time" else "FT",
                "winner": "",
                "decision": "",
                "date": match_date,
                "source_url": source_url,
            },
        })
    return observations
