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
from retrieve_any_quarantined_replay import normalise, retrieve


def verify(fixture, club_domains=(), search=None, fetch=None):
    kwargs = {"club_domains": club_domains}
    if search is not None:
        kwargs["search"] = search
    found = discover(fixture, **kwargs)
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
    args = p.parse_args()
    with open(args.fixture, encoding="utf-8") as f:
        fixture = json.load(f)
    print(json.dumps(verify(fixture, club_domains=args.club_domains), indent=2))


if __name__ == "__main__":
    main()
