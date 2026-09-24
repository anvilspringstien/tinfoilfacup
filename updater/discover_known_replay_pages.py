#!/usr/bin/env python3
"""Zero-cost known-page discovery for FA Cup replay verification.

No search provider or API key. Fetch public FA and BBC competition fixture
pages using stable known URLs, then use exact fixture names/date to identify
candidate original pages. This module discovers candidates; it does NOT
treat pages or snippets as independent verification or write production.
"""
from datetime import date
from html.parser import HTMLParser
import re
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen

FA_FIXTURES = "https://www.thefa.com/competitions/thefacup/fixtures"
FA_RESULTS = "https://www.thefa.com/competitions/thefacup/results"
BBC_MONTH = "https://www.bbc.co.uk/sport/football/fa-cup/scores-fixtures/{month}"


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.current = None
        self.text = []
        self.all_text = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self.current = dict(attrs).get("href")
            self.text = []

    def handle_data(self, data):
        self.all_text.append(data)
        if self.current is not None:
            self.text.append(data)

    def handle_endtag(self, tag):
        if tag == "a" and self.current is not None:
            self.links.append((self.current, " ".join(self.text)))
            self.current = None


def fetch(url):
    req = Request(url, headers={"User-Agent": "TinFoilFACupReplayAudit/1.0"})
    with urlopen(req, timeout=15) as response:
        return response.read().decode("utf-8", errors="replace")


def discover_known_pages(fixture, get=fetch):
    day = date.fromisoformat(fixture["date"])
    pages = [
        ("fa", FA_FIXTURES),
        ("fa", FA_RESULTS),
        ("bbc", BBC_MONTH.format(month=day.strftime("%Y-%m"))),
    ]
    sources, failures, seen = [], [], set()
    home = fixture["home"].casefold()
    away = fixture["away"].casefold()
    for tier, url in pages:
        try:
            html = get(url)
            parser = Links()
            parser.feed(html)
            # A known competition page is a candidate only if both teams
            # appear. The evidence parser must still confirm the exact match.
            text = re.sub(r"\s+", " ", " ".join(parser.all_text)).casefold()
            if home not in text or away not in text:
                failures.append({"tier": tier, "url": url, "reason": "fixture not present"})
                continue
            if url not in seen:
                sources.append({"tier": tier, "domain": urlparse(url).hostname, "url": url})
                seen.add(url)
            for href, label in parser.links:
                target = urljoin(url, href)
                host = urlparse(target).hostname or ""
                # Only follow original publisher pages. Never trust arbitrary
                # external links or claim an article matches based on snippets.
                if (urlparse(target).scheme == "https" and
                    (host == urlparse(url).hostname or
                     host.endswith("." + urlparse(url).hostname)) and
                    (home in label.casefold() or away in label.casefold()) and
                    target not in seen):
                    sources.append({"tier": tier, "domain": host, "url": target})
                    seen.add(target)
        except Exception as exc:
            failures.append({"tier": tier, "url": url, "reason": type(exc).__name__})
    return {"fixture": fixture, "sources": sources, "failures": failures,
            "production_mutation": False}
