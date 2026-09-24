#!/usr/bin/env python3
"""Wimborne Verification Process: discover -> fetch -> reconcile, read-only.

Usage:
  BRAVE_SEARCH_API_KEY=... python updater/verify_discovered_replay.py \
    --fixture /tmp/quarantined-wimborne.json \
    --club-domains wsmafc.co.uk wimbornetownfc.co.uk

The source manifest is built from discovered original-page URLs; search
snippets are never evidence. No result is published by this program.
"""
import argparse
import json

from discover_quarantined_replay_urls import discover
from discover_known_replay_pages import discover_known_pages
from retrieve_any_quarantined_replay import normalise, retrieve


def verify(fixture, club_domains=(), search=None, fetch=None, known_pages=None):
    kwargs = {"club_domains": club_domains}
    if search is not None:
        kwargs["search"] = search
    # Free known-page discovery is the default; optional search requires explicit opt-in.
    found = (discover_known_pages(fixture, get=known_pages) if known_pages is not None
             else discover_known_pages(fixture)) if search is None else discover(fixture, **kwargs)
    key = fixture["date"] + "|" + normalise(fixture["home"]) + "|" + normalise(fixture["away"])
    sources = [{"domain": x["domain"], "url": x["url"]} for x in found["sources"]]
    options = {"fetch": fetch} if fetch is not None else {}
    rows = retrieve([fixture], {key: sources}, **options)
    return {"discovery": found, "verification": rows[0],
            "production_mutation": False}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--fixture", required=True)
    p.add_argument("--club-domains", nargs="*", default=[])
    p.add_argument("--paid-search", action="store_true", help="Explicit optional Brave search")
    args = p.parse_args()
    with open(args.fixture, encoding="utf-8") as f:
        fixture = json.load(f)
    from discover_quarantined_replay_urls import brave_search
    print(json.dumps(verify(fixture, club_domains=args.club_domains,
                            search=brave_search if args.paid_search else None), indent=2))


if __name__ == "__main__":
    main()
