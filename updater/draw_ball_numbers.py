"""Parse a published FA Cup ball list separately from the draw pairings."""

import re
from datetime import date
from html import unescape
from html.parser import HTMLParser
from urllib.error import URLError
from urllib.parse import urljoin, urlsplit


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
    paragraphs = re.findall(
        r"<p\b[^>]*>\s*The ball numbers are listed below:\s*</p>\s*<p\b[^>]*>(.*?)</p>",
        html, re.IGNORECASE | re.DOTALL,
    )
    for paragraph in paragraphs:
        rows = []
        for line in re.split(r"<br\s*/?>", paragraph, flags=re.IGNORECASE):
            label = " ".join(unescape(re.sub(r"<[^>]+>", "", line)).split())
            if not label:
                continue
            match = re.fullmatch(r"(\d+)\.\s+(.+)", label)
            rows.append(match.groups() if match else (None, label))
        parser.lists.append(rows)
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


def validate_ball_slots(ball_list, fixtures, compatible, normalize=str.casefold):
    """Require every published slot to identify one distinct outgoing tie."""
    matched = {}

    for entry in ball_list["entries"]:
        clubs = entry["clubs"]
        if len(clubs) > 2:
            raise ValueError(f'Ball {entry["number"]} has too many alternatives')
        candidates = []
        exact = []
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
                sides = {normalize(home), normalize(away)}
                if {normalize(club) for club in clubs} <= sides:
                    exact.append(index)
        candidates = exact or candidates
        if len(candidates) != 1 or candidates[0] in matched:
            ties = [(fixtures[index]["home"], fixtures[index]["away"]) for index in candidates]
            raise ValueError(
                f'Ball {entry["number"]} {clubs!r} does not identify a distinct canonical tie '
                f'(matching ties: {ties!r}; already assigned: {any(index in matched for index in candidates)})'
            )
        matched[candidates[0]] = entry
    if len(matched) != len(fixtures):
        raise ValueError("Draw ball list does not cover the complete outgoing round")
    return matched


def verify_article_context(html, source_url, target, fixtures):
    path = urlsplit(source_url).path
    stamp = re.match(r"/news/(\d{4})/([a-z]{3})/(\d{2})/", path, re.I)
    if not stamp:
        raise ValueError("Official article has no dated FA news path")
    from datetime import datetime

    published = datetime.strptime("-".join(stamp.groups()), "%Y-%b-%d").date()

    def season_start(day):
        return day.year - (day.month < 7)

    season = season_start(published)
    if any(season_start(date.fromisoformat(fixture["date"])) != season for fixture in fixtures):
        raise ValueError("Official article and outgoing fixtures are in different seasons")
    headings = re.findall(r"<h1\b[^>]*>(.*?)</h1>", html, re.I | re.S)
    title = " ".join(unescape(re.sub(r"<[^>]+>", "", heading)) for heading in headings)
    round_label = re.escape(target.removesuffix(" Proper"))
    if not re.search(rf"\bFA Cup\b.*\b{round_label}\b(?:\s+proper)?\s+draw\b", title, re.I):
        raise ValueError("Official article heading does not identify the target FA Cup draw")
    return f"{season}-{str(season + 1)[-2:]}"


def draw_schedule(html):
    """Read explicit draw schedule wording from the official announcement."""
    paragraphs = [
        " ".join(unescape(re.sub(r"<[^>]+>", "", paragraph)).split())
        for paragraph in re.findall(r"<p\b[^>]*>(.*?)</p>", html, re.I | re.S)
    ]
    dates = {
        match.group(1)
        for paragraph in paragraphs
        if (match := re.search(
            r"\bdraw will be (?:made|held|conducted).*?\bon "
            r"((?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday) "
            r"\d{1,2} [A-Za-z]+)\b", paragraph, re.I,
        ))
    }
    times = {
        match.group(1)
        for paragraph in paragraphs
        if (match := re.search(
            r"\bdraw will (?:take place|be made|be held).*?\bat "
            r"((?:approximately |around )?\d{1,2}(?:[.:]\d{2})?\s*(?:am|pm)\s+(?:GMT|BST))\b",
            paragraph, re.I,
        ))
    }
    return {
        "date_text": next(iter(dates)) if len(dates) == 1 else None,
        "time_text": next(iter(times)) if len(times) == 1 else None,
    }


def classify_ball_slots(matched, fixtures, history, normalize):
    verified, withheld = [], []
    for index, entry in matched.items():
        if len(entry["clubs"]) != 1:
            withheld.append({**entry, "reason": "unresolved_tie"})
            continue
        fixture = fixtures[index]
        sides = {normalize(fixture["home"]), normalize(fixture["away"])}
        winners = {
            normalize(result["winner"])
            for result in history
            if result.get("source_url") and result.get("winner")
            and str(result.get("status", "")).startswith("FT")
            and (
                (result.get("round") == fixture["round"] and result.get("date") == fixture["date"])
                or (result.get("round") == fixture["round"] + " Replay"
                    and result.get("date", "") > fixture["date"])
            )
            and {normalize(result.get("home")), normalize(result.get("away"))} == sides
        }
        if winners == {normalize(entry["clubs"][0])}:
            verified.append(entry)
        else:
            withheld.append({**entry, "reason": "winner_unverified", "canonical_winners": sorted(winners)})
    return verified, withheld


FA_NEWS_INDEXES = (
    "https://www.thefa.com/competitions/thefacup",
    "https://www.thefa.com/",
)


def official_fa_url(url):
    parsed = urlsplit(url)
    return parsed.scheme == "https" and parsed.netloc in {"thefa.com", "www.thefa.com"}


def discover_article_urls(fetch, saved_url=None):
    urls = set()
    for index in FA_NEWS_INDEXES:
        try:
            html = fetch(index)
        except (URLError, TimeoutError) as error:
            print(f"FA index unavailable: {index}: {error}")
            continue
        draw_links = re.findall(r"/news/\d{4}/[a-z]{3}/\d{2}/[a-z0-9-]*draw[a-z0-9-]*", html, re.I)
        for link in draw_links:
            urls.add(urljoin(index, link))
        print(f"FA discovery index {index}: {len(draw_links)} draw article references")
        for href in re.findall(r"""\bhref\s*=\s*["']([^"']+)["']""", html, re.I):
            url = urljoin(index, unescape(href))
            parts = urlsplit(url)
            if official_fa_url(url) and re.fullmatch(r"/news/\d{4}/[a-z]{3}/\d{2}/[^/]*draw[^/]*", parts.path, re.I):
                urls.add(urljoin("https://www.thefa.com/", parts.path))
    def publication_date(url):
        from datetime import datetime

        try:
            return datetime.strptime(urlsplit(url).path[6:17], "%Y/%b/%d")
        except ValueError:
            return datetime.min
    ordered = sorted(urls, key=lambda url: (publication_date(url), url), reverse=True)
    if saved_url and official_fa_url(saved_url) and saved_url not in ordered[:8]:
        ordered.insert(0, saved_url)
    return ordered[:8]


def main():
    import argparse
    import json

    from auto_draw import DATA, EXPECTED_ROUND_TIES, ROUND_ORDER, compatible, fetch, fixture_values, norm

    cli = argparse.ArgumentParser(description="Check an official FA ball list against the active round")
    cli.add_argument("source_url", nargs="?", help="Official article URL for a diagnostic run")
    cli.add_argument("--round", choices=ROUND_ORDER)
    cli.add_argument("--stage", action="store_true", help="Stage validated metadata in the local competition candidate")
    args = cli.parse_args()
    if args.source_url and not official_fa_url(args.source_url):
        cli.error("Ball numbers require an official FA source")
    data = json.loads(DATA.read_text(encoding="utf-8"))
    current = data.get("source_round")
    if current not in ROUND_ORDER[:-1]:
        cli.error("No next canonical round")
    target = ROUND_ORDER[ROUND_ORDER.index(current) + 1]
    if args.round and args.round != target:
        cli.error("The requested draw is not the next canonical round")
    expected_ties = EXPECTED_ROUND_TIES.get(target)
    if expected_ties is None:
        cli.error("No expected slot count for the requested round")
    fixtures = [fixture for fixture in fixture_values(data.get("fixtures") or {})
                if fixture.get("round") == current]
    history = [row for rows in (data.get("result_history") or {}).values() for row in rows]
    saved = data.get("draw_preview") or {}
    urls = [args.source_url] if args.source_url else discover_article_urls(
        fetch, saved.get("source_url") if saved.get("target_round") == target else None,
    )
    for url in urls:
        try:
            article = fetch(url)
            season = verify_article_context(article, url, target, fixtures)
            ball_list = parse_ball_numbers(article, url, expected_ties * 2)
            matched = validate_ball_slots(ball_list, fixtures, compatible, norm)
            verified, withheld = classify_ball_slots(matched, fixtures, history, norm)
            if not verified:
                raise ValueError("No verified ball numbers")
        except (ValueError, URLError, TimeoutError) as error:
            print(f"FA draw article rejected: {url}: {error}")
            if args.source_url:
                raise
            continue
        preview = {
            "season": season, "outgoing_round": current, "target_round": target,
            "source_url": url, "draw_schedule": draw_schedule(article),
            "entries": verified,
        }
        break
    else:
        cli.error(f"No verified official FA draw article found for {target}")
    if args.stage:
        if not verified:
            cli.error("No verified ball numbers to stage")
        if data.get("draw_preview") != preview:
            data["draw_preview"] = preview
            temporary = DATA.with_suffix(".json.draw-preview.tmp")
            temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            temporary.replace(DATA)
    print(json.dumps({**preview, "withheld": withheld}, indent=2))


if __name__ == "__main__":
    main()
