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


def main():
    import argparse
    import json

    from auto_draw import DATA, EXPECTED_ROUND_TIES, ROUND_ORDER, compatible, fetch, fixture_values

    cli = argparse.ArgumentParser(description="Check an official FA ball list against the active round")
    cli.add_argument("source_url")
    cli.add_argument("--round", required=True, choices=ROUND_ORDER)
    args = cli.parse_args()
    source = urlsplit(args.source_url)
    if source.scheme != "https" or source.netloc not in {"thefa.com", "www.thefa.com"}:
        cli.error("Ball numbers require an official FA source")
    data = json.loads(DATA.read_text(encoding="utf-8"))
    current = data.get("source_round")
    if current not in ROUND_ORDER[:-1] or ROUND_ORDER[ROUND_ORDER.index(current) + 1] != args.round:
        cli.error("The requested draw is not the next canonical round")
    expected_ties = EXPECTED_ROUND_TIES.get(args.round)
    if expected_ties is None:
        cli.error("No expected slot count for the requested round")
    fixtures = [fixture for fixture in fixture_values(data.get("fixtures") or {})
                if fixture.get("round") == current]
    article = fetch(args.source_url)
    try:
        ball_list = parse_ball_numbers(article, args.source_url, expected_ties * 2)
    except ValueError:
        for anchor in ("ball numbers are listed below", "AFC Fylde", "Salisbury"):
            match = re.search(re.escape(anchor), article, re.IGNORECASE)
            if match:
                print(f"FA markup near {anchor!r}: {article[max(0, match.start()-160):match.end()+650]!r}")
        raise
    validate_ball_slots(ball_list, fixtures, compatible)
    print(json.dumps({"outgoing_round": current, "target_round": args.round, **ball_list}, indent=2))


if __name__ == "__main__":
    main()
