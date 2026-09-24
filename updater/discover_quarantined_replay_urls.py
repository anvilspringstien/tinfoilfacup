#!/usr/bin/env python3
"""Read-only, domain-restricted discovery of original replay reports.

Search results are candidate URLs, NEVER match evidence. The downstream
retriever must fetch each page and independently extract fixture facts.
BRAVE_SEARCH_API_KEY enables the Brave search API; without it, the module
fails closed rather than inventing search results.
"""
import argparse
from datetime import date
import json
import os
from urllib.parse import urlencode, urlparse
from urllib.request import Request, urlopen

# Priority controls discovery order, not authority to overrule contradictory reports.
KNOWN = (("fa", "thefa.com"), ("bbc", "bbc.co.uk"))
REGIONAL = ("southwestsportsnews.com",)
BLOCKED_HOSTS = {"wikipedia.org", "footballwebpages.co.uk"}


def approved_host(url, domain):
    parsed = urlparse(url)
    host = (parsed.hostname or "").lower()
    domain = domain.lower().removeprefix("www.")
    return parsed.scheme == "https" and parsed.username is None and parsed.password is None and (
        host == domain or host.endswith("." + domain)
    )


def fixture_query(fixture):
    match_date = date.fromisoformat(fixture["date"])
    return '"{}" "{}" FA Cup replay {} penalties'.format(
        fixture["home"], fixture["away"], match_date.strftime("%d %B %Y")
    )


def brave_search(query, domain, api_key=None):
    key = api_key or os.environ.get("BRAVE_SEARCH_API_KEY")
    if not key:
        raise RuntimeError("BRAVE_SEARCH_API_KEY is not configured")
    params = urlencode({"q": query + " site:" + domain, "count": 8})
    req = Request("https://api.search.brave.com/res/v1/web/search?" + params,
                  headers={"Accept": "application/json", "X-Subscription-Token": key,
                           "User-Agent": "TinFoilFACupReplayAudit/1.0"})
    with urlopen(req, timeout=15) as response:
        payload = json.load(response)
    return [item.get("url", "") for item in payload.get("web", {}).get("results", [])]


def discover(fixture, club_domains=(), regional_domains=REGIONAL, search=brave_search):
    """Return priority-ordered reviewed-domain candidates and per-tier failures.

    Club domains must come from the reviewed Clubfinder directory, not a
    search-result snippet. Wikipedia and FWP cannot corroborate themselves.
    """
    domains = list(KNOWN)
    domains += [("club", d) for d in club_domains]
    domains += [("regional", d) for d in regional_domains]
    candidates, failures, seen_urls, seen_domains = [], [], set(), set()
    for tier, raw_domain in domains:
        domain = raw_domain.lower().removeprefix("www.")
        if domain in seen_domains or domain in BLOCKED_HOSTS:
            continue
        seen_domains.add(domain)
        try:
            results = search(fixture_query(fixture), domain)
        except Exception as exc:
            failures.append({"tier": tier, "domain": domain, "error": type(exc).__name__})
            continue
        for url in results:
            if approved_host(url, domain) and url not in seen_urls:
                seen_urls.add(url)
                candidates.append({"tier": tier, "domain": domain, "url": url})
    return {"fixture": fixture, "sources": candidates, "failures": failures,
            "production_mutation": False}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--fixture", required=True, help="Quarantined fixture JSON")
    p.add_argument("--club-domains", nargs="*", default=[],
                   help="Reviewed official domains from the Clubfinder club directory")
    args = p.parse_args()
    with open(args.fixture, encoding="utf-8") as f:
        fixture = json.load(f)
    print(json.dumps(discover(fixture, club_domains=args.club_domains), indent=2))


if __name__ == "__main__":
    main()
