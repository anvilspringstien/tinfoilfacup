"""Convert dated BBC FA Cup score rows to Results observations."""

import re
from html.parser import HTMLParser


class ScoreLinks(HTMLParser):
    def __init__(self):
        super().__init__()
        self.labels = []

    def handle_starttag(self, tag, attrs):
        if tag != "a":
            return
        attrs = dict(attrs)
        if attrs.get("href", "").startswith("/sport/football/live/"):
            self.labels.append(attrs.get("aria-label", ""))


FULL_TIME = re.compile(
    r"^(.+?)\s+(\d+)\s*,\s*(.+?)\s+(\d+)\s+at Full time(?:\s|$)",
    re.IGNORECASE,
)
BBC_ALIASES = {"fylde": "AFC Fylde"}


def full_time_observations(raw, fixtures, match_date, source_url, match_fixture):
    """Accept decisive full-time rows from a single dated FA Cup source."""
    dated = [fixture for fixture in fixtures if fixture.get("date") == match_date]
    links = ScoreLinks()
    links.feed(raw)
    observations = []
    for label in links.labels:
        match = FULL_TIME.match(label)
        if not match:
            continue
        home, home_score, away, away_score = match.groups()
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
                "status": "FT",
                "winner": "",
                "decision": "",
                "date": match_date,
                "source_url": source_url,
            },
        })
    return observations
