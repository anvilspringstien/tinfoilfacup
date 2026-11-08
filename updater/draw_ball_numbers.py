"""Parse a published FA Cup ball list separately from the draw pairings."""

import re
from html.parser import HTMLParser
from urllib.parse import urlsplit


class BallLists(HTMLParser):
    def __init__(self):
        super().__init__()
        self.lists = []
        self.rows = None
        self.row = None
        self.number = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "ol" and self.rows is None:
            self.rows = []
            self.number = attrs.get("start", "1")
        elif tag == "li" and self.rows is not None:
            self.row = []
            self.number = attrs.get("value", self.number)

    def handle_data(self, data):
        if self.row is not None:
            self.row.append(data)

    def handle_endtag(self, tag):
        if tag == "li" and self.row is not None:
            label = " ".join("".join(self.row).split())
            self.rows.append((self.number, label))
            self.number = str(int(self.number) + 1) if str(self.number).isdigit() else None
            self.row = None
        elif tag == "ol" and self.rows is not None:
            self.lists.append(self.rows)
            self.rows = None
            self.row = None


def parse_ball_numbers(html, source_url, expected_slots):
    """Return a complete numbered list. Keep unresolved alternatives together."""
    url = urlsplit(source_url)
    if url.scheme != "https" or url.netloc not in {"thefa.com", "www.thefa.com"}:
        raise ValueError("Ball numbers require an official FA source")
    if expected_slots < 2:
        raise ValueError("Expected at least two draw slots")

    parser = BallLists()
    parser.feed(html)
    expected = [str(number) for number in range(1, expected_slots + 1)]
    candidates = [rows for rows in parser.lists if [n for n, _ in rows] == expected]
    if len(candidates) != 1:
        raise ValueError("Expected exactly one complete numbered draw list")

    entries = []
    seen = set()
    for number, label in candidates[0]:
        clubs = re.split(r"\s+or\s+", label, flags=re.IGNORECASE)
        keys = {club.casefold() for club in clubs}
        if "" in keys or len(keys) != len(clubs) or keys & seen:
            raise ValueError("Draw ball list contains a missing or repeated club")
        seen.update(keys)
        entries.append({"number": int(number), "clubs": clubs})
    return {"source_url": source_url, "entries": entries}


def validate_ball_slots(ball_list, fixtures, compatible):
    """Require every published slot to identify one distinct outgoing tie."""
    matched = set()
    for entry in ball_list["entries"]:
        clubs = entry["clubs"]
        if len(clubs) > 2:
            raise ValueError(f'Ball {entry["number"]} has too many alternatives')
        candidates = []
        for index, fixture in enumerate(fixtures):
            home, away = fixture["home"], fixture["away"]
            if len(clubs) == 1:
                matches = compatible(clubs[0], home) or compatible(clubs[0], away)
            else:
                first, second = clubs
                matches = (
                    compatible(first, home) and compatible(second, away)
                ) or (
                    compatible(first, away) and compatible(second, home)
                )
            if matches:
                candidates.append(index)
        if len(candidates) != 1 or candidates[0] in matched:
            raise ValueError(f'Ball {entry["number"]} does not identify a distinct canonical tie')
        matched.add(candidates[0])
    if len(matched) != len(fixtures):
        raise ValueError("Draw ball list does not cover the complete outgoing round")
