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
