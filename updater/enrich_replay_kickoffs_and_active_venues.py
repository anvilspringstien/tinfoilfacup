#!/usr/bin/env python3
"""Guarded enrichment for replay kick-off times and active-round venues.

This stage repairs two presentation gaps without changing journey logic:
1. First Qualifying replay results gain verified kick-off times from Football Web Pages match pages.
2. Active fixtures with TBC venues are resolved from protected Clubfinder GROUNDS first,
   then from the FCHD gazetteer. Ambiguous or missing venue matches remain untouched.

No guessed kick-off time or venue is ever written.
"""
import html as htmlmod
import json
import re
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMP = ROOT / "competition.json"
HTML = ROOT / "clubfinder.html"
REPORT = ROOT / "updater" / "kickoff-venue-enrichment-report.json"
FWP_BASE = "https://www.footballwebpages.co.uk"
FCHD_URL = "https://fchd.info/maps/GAZ.htm"
REPLAY_ROUND = "First Round Qualifying Replay"
UA = "Mozilla/5.0 TinFoilFACupKickoffVenueEnrichment/7.9.26"


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/html,application/xhtml+xml,*/*"})
    return urllib.request.urlopen(req, timeout=40).read().decode("utf-8", "replace")


def norm(s):
    s = htmlmod.unescape(str(s or "")).lower().replace("&", " and ")
    s = re.sub(r"\b(fc|afc|cfc|football club)\b", " ", s)
    return re.sub(r"[^a-z0-9]+", " ", s).strip()


def fixture_values(src):
    return list(src.values()) if isinstance(src, dict) else list(src or [])


def clean_text(raw):
    raw = re.sub(r"<(script|style)\b[^>]*>.*?</\1>", " ", raw, flags=re.I | re.S)
    return " ".join(htmlmod.unescape(re.sub(r"<[^>]+>", " ", raw)).replace("\xa0", " ").split())


def parse_time(text):
    s = str(text or "").strip().lower().replace(" ", "")
    s = s.replace(".", ":")
    m = re.fullmatch(r"(\d{1,2})(?::(\d{2}))?(am|pm)?", s)
    if not m:
        return None
    h = int(m.group(1)); minute = int(m.group(2) or 0); ap = m.group(3)
    if minute > 59:
        return None
    if ap:
        if not 1 <= h <= 12:
            return None
        if ap == "pm" and h != 12:
            h += 12
        if ap == "am" and h == 12:
            h = 0
    elif h > 23:
        return None
    return f"{h:02d}:{minute:02d}"


def replay_identity(r):
    return (norm(r.get("home")), norm(r.get("away")), str(r.get("date") or ""), str(r.get("round") or ""))


def unique_replays(data):
    out = {}
    for rows in (data.get("result_history") or {}).values():
        if not isinstance(rows, list):
            continue
        for r in rows:
            if isinstance(r, dict) and str(r.get("round") or "") == REPLAY_ROUND:
                out.setdefault(replay_identity(r), r)
    for r in (data.get("results") or {}).values():
        if isinstance(r, dict) and str(r.get("round") or "") == REPLAY_ROUND:
            out.setdefault(replay_identity(r), r)
    return list(out.values())


def discover_match_pages(date):
    ymd = date.replace("-", "")
    page = fetch(f"{FWP_BASE}/fa-cup/{ymd}")
    links = []
    for href in re.findall(r'href=["\']([^"\']+)["\']', page, flags=re.I):
        if "/match/2026-2027/fa-cup/" not in href:
            continue
        url = urllib.parse.urljoin(FWP_BASE, href)
        if url not in links:
            links.append(url)
    return links


def replay_source_details(replays):
    by_date = {}
    for r in replays:
        if not r.get("kickoff"):
            by_date.setdefault(str(r.get("date") or ""), []).append(r)
    details = {}
    fetched = 0
    for date, rows in sorted(by_date.items()):
        if not date:
            continue
        links = discover_match_pages(date)
        pages = []
        for url in links:
            raw = fetch(url); fetched += 1
            text = clean_text(raw)
            if norm(REPLAY_ROUND) not in norm(text):
                continue
            pages.append((url, text))
        for r in rows:
            matches = []
            hn, an = norm(r.get("home")), norm(r.get("away"))
            for url, text in pages:
                nt = norm(text)
                if hn not in nt or an not in nt:
                    continue
                m = re.search(r"Kick-off:\s*([0-9]{1,2}(?:[\.:][0-9]{2})?\s*(?:am|pm)?)", text, flags=re.I)
                ko = parse_time(m.group(1)) if m else None
                if ko:
                    matches.append((url, ko))
            if len(matches) == 1:
                details[replay_identity(r)] = matches[0]
            elif len(matches) > 1:
                raise SystemExit(f"ABORT: ambiguous FWP match-page mapping for {r.get('home')} v {r.get('away')}")
    return details, fetched


def apply_replay_kickoffs(data, details):
    changed = 0
    for container in ((data.get("result_history") or {}).values(), [(data.get("results") or {})]):
        if isinstance(container, list) and container and isinstance(container[0], dict):
            pass
    rows = []
    for arr in (data.get("result_history") or {}).values():
        if isinstance(arr, list): rows.extend(x for x in arr if isinstance(x, dict))
    rows.extend(x for x in (data.get("results") or {}).values() if isinstance(x, dict))
    for r in rows:
        if str(r.get("round") or "") != REPLAY_ROUND:
            continue
        detail = details.get(replay_identity(r))
        if not detail:
            continue
        url, ko = detail
        if r.get("kickoff") != ko or r.get("kickoff_source_url") != url:
            r["kickoff"] = ko
            r["kickoff_source_url"] = url
            changed += 1
    return changed


def extract_js_array(text, name):
    m = re.search(r"\b(?:const|let|var)\s+" + re.escape(name) + r"\s*=\s*\[", text)
    if not m: return []
    st = text.find("[", m.start()); depth = 0; in_str = False; esc = False; quote = ""
    for i in range(st, len(text)):
        c = text[i]
        if in_str:
            if esc: esc = False
            elif c == "\\": esc = True
            elif c == quote: in_str = False
        else:
            if c in ("'", '"'): in_str = True; quote = c
            elif c == "[": depth += 1
            elif c == "]":
                depth -= 1
                if depth == 0:
                    return json.loads(text[st:i+1])
    return []


def clean_markup(s):
    s = re.sub(r"<br\s*/?>", "\n", s, flags=re.I)
    s = re.sub(r"<[^>]+>", "\n", s)
    return [htmlmod.unescape(x).strip(" \t\r\n|") for x in s.splitlines() if htmlmod.unescape(x).strip(" \t\r\n|")]


def parse_fchd(raw):
    pat = re.compile(r"<h3\b[^>]*>(.*?)</h3>(.*?)(?=<h3\b|<h1\b|$)", re.I | re.S)
    pc_re = re.compile(r"\b(?:GIR 0AA|(?:[A-Z]{1,2}\d[A-Z\d]?|\d[A-Z]{2})\s*\d[A-Z]{2})\b", re.I)
    rows = []
    for head, body in pat.findall(raw):
        club = " ".join(clean_markup(head)); lines = clean_markup(body)
        postcode = None
        for line in lines:
            m = pc_re.search(line)
            if m: postcode = m.group(0).upper(); break
        if not club or not postcode: continue
        useful = [x for x in lines if not pc_re.fullmatch(x) and not re.search(r"-?\d{1,2}\.\d+\s*,\s*-?\d{1,3}\.\d+", x) and not x.lower().startswith(("http://", "https://"))]
        ground = useful[0] if useful else "Ground TBC"
        if len(useful) > 1 and re.search(r"\b(FC|AFC|CFC|Town|United|Athletic|Rovers|City)$", ground, re.I): ground = useful[1]
        rows.append({"club": club, "ground": ground, "postcode": postcode, "source": FCHD_URL})
    return rows


def unique_lookup(rows, club):
    n = norm(club)
    exact = [r for r in rows if norm(r.get("club")) == n]
    if len(exact) == 1: return exact[0]
    loose = [r for r in rows if norm(r.get("club")).startswith(n + " ") or n.startswith(norm(r.get("club")) + " ")]
    return loose[0] if len(loose) == 1 else None


def valid_venue(v):
    return isinstance(v, dict) and v.get("postcode") and not re.search(r"TBC", str(v.get("postcode")), re.I)


def enrich_active_venues(data):
    html = HTML.read_text(encoding="utf-8")
    grounds = extract_js_array(html, "GROUNDS")
    canonical = {norm(g.get("name") or g.get("club")): g for g in grounds if g.get("postcode") and not re.search(r"TBC", str(g.get("postcode")), re.I)}
    fchd = parse_fchd(fetch(FCHD_URL))
    changed = 0; canonical_hits = 0; fchd_hits = 0; unresolved = []
    fixtures = data.get("fixtures") or {}
    for f in fixture_values(fixtures):
        if not isinstance(f, dict) or not f.get("home") or valid_venue(f.get("venue")):
            continue
        home = f.get("home")
        g = canonical.get(norm(home))
        if g:
            f["venue"] = {"ground": g.get("ground") or "Ground TBC", "postcode": g.get("postcode"), "source": g.get("source") or "protected Clubfinder GROUNDS", "verification": "clubfinder-canonical"}
            changed += 1; canonical_hits += 1; continue
        row = unique_lookup(fchd, home)
        if row:
            f["venue"] = {"ground": row["ground"], "postcode": row["postcode"], "source": row["source"], "verification": "fchd-gazetteer"}
            changed += 1; fchd_hits += 1; continue
        unresolved.append(home)
    data["fixtures"] = fixtures
    return changed, canonical_hits, fchd_hits, sorted(set(unresolved))


def find_replay(replays, home, away):
    hn, an = norm(home), norm(away)
    return next((r for r in replays if norm(r.get("home")) == hn and norm(r.get("away")) == an), None)


def main():
    data = json.loads(COMP.read_text(encoding="utf-8"))
    replays = unique_replays(data)
    details, pages_fetched = replay_source_details(replays)
    replay_changes = apply_replay_kickoffs(data, details)
    after = unique_replays(data)
    missing = [f"{r.get('home')} v {r.get('away')}" for r in after if not r.get("kickoff")]
    if missing:
        raise SystemExit("ABORT: First Qualifying replay kick-offs still missing: " + ", ".join(missing[:10]))

    # Regression anchors observed directly on Football Web Pages.
    for home, away in (("Exmouth Town", "Banbury United"), ("Welling United", "Faversham Town"), ("AFC Whyteleafe", "Crowborough Athletic")):
        r = find_replay(after, home, away)
        if not r or r.get("kickoff") != "19:45":
            raise SystemExit(f"ABORT: replay kick-off regression for {home} v {away}: {None if not r else r.get('kickoff')}")

    venue_changes, canonical_hits, fchd_hits, unresolved = enrich_active_venues(data)
    if replay_changes or venue_changes:
        data["updated_at"] = datetime.now(timezone.utc).isoformat()
        COMP.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    report = {
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "status": "PASS",
        "first_qualifying_replays": len(after),
        "replay_records_changed": replay_changes,
        "fwp_match_pages_fetched": pages_fetched,
        "active_venue_records_changed": venue_changes,
        "active_venue_canonical_hits": canonical_hits,
        "active_venue_fchd_hits": fchd_hits,
        "active_venue_unresolved_home_clubs": unresolved,
    }
    REPORT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("REPLAY KICK-OFF + ACTIVE VENUE ENRICHMENT: PASS")
    print("First Qualifying replays:", len(after))
    print("Replay records changed:", replay_changes)
    print("FWP match pages fetched:", pages_fetched)
    print("Active venues changed:", venue_changes)
    print("Protected GROUNDS hits:", canonical_hits)
    print("FCHD hits:", fchd_hits)
    print("Unresolved active home clubs:", len(unresolved))
    for club in unresolved[:50]: print("UNRESOLVED:", club)


if __name__ == "__main__":
    main()
