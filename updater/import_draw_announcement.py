#!/usr/bin/env python3
"""Import an official draw announcement, separately from published fixtures.

Example:
 python updater/import_draw_announcement.py URL --round 'First Round Proper' \
   --at 2026-10-19T18:35:00+01:00 --expected-balls 80 --publish

The time is explicitly supplied and checked against the source announcement.
Dry run by default. Never advances the active round or creates fixtures.
"""
import argparse
import html
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]


def parse_announcement(raw, source_url, round_name, at, expected_balls):
    if expected_balls < 2:
        raise ValueError('A draw requires at least two balls')
    url = urlparse(source_url)
    if url.scheme != 'https' or url.hostname not in ('www.thefa.com', 'thefa.com'):
        raise ValueError('Only an official HTTPS FA announcement is accepted')
    stamp = datetime.fromisoformat(at)
    if stamp.utcoffset() is None:
        raise ValueError('Draw time requires an explicit timezone')
    text = re.sub(r'(?is)<(script|style)\b.*?</\1>', '', raw)
    text = re.sub(r'(?i)<br\s*/?>|</p>|</li>', '\n', text)
    text = html.unescape(re.sub(r'<[^>]*>', '', text))
    flat = re.sub(r'\s+', ' ', text).lower()
    round_label = round_name.lower().replace(' proper', '')
    if not any(label + ' draw' in flat for label in (round_label, round_name.lower())):
        raise ValueError('Announcement does not identify the requested round')
    date_label = f'{stamp.day} {stamp.strftime("%B")}'.lower()
    time_label = stamp.strftime('%I.%M').lstrip('0') + ('pm' if stamp.hour >= 12 else 'am')
    zone = 'bst' if stamp.utcoffset().total_seconds() == 3600 else 'gmt'
    if date_label not in flat or str(stamp.year) not in flat or time_label + ' ' + zone not in flat:
        raise ValueError('Supplied draw date/time not confirmed by source')
    # An article may contain unrelated numbers: accept only the announced list.
    marker = re.search(r'ball numbers are listed below\s*:', text, re.I)
    if not marker:
        raise ValueError('Official ball-number list missing')
    pairs = re.findall(r'^\s*(\d{1,3})\s*\.\s*([^\n]+)', text[marker.end():], re.M)
    numbers = [int(number) for number, _ in pairs]
    if numbers != list(range(1, expected_balls + 1)):
        raise ValueError('Ball list incomplete, duplicated or out of order')
    return {'at': stamp.isoformat(), 'approximate': True, 'source_url': source_url,
            'ball_numbers': {club.strip(): int(number) for number, club in pairs}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source_url')
    parser.add_argument('--round', required=True)
    parser.add_argument('--at', required=True)
    parser.add_argument('--expected-balls', required=True, type=int)
    parser.add_argument('--publish', action='store_true')
    args = parser.parse_args()
    request = Request(args.source_url, headers={'User-Agent': 'TinFoilFACupAnnouncement/1.0'})
    with urlopen(request, timeout=30) as response:
        source = response.geturl()
        raw = response.read().decode('utf-8')
    announcement = parse_announcement(raw, source, args.round, args.at, args.expected_balls)
    if args.publish:
        path = ROOT / 'competition.json'
        data = json.loads(path.read_text())
        start_year = int(data['season'].split('-')[0])
        if not start_year <= datetime.fromisoformat(args.at).year <= start_year + 1:
            raise ValueError('Announcement is outside the canonical season')
        if data.get('draw_announcements', {}).get(args.round) == announcement:
            print('Announcement already current; no publication needed')
            return
        data.setdefault('draw_announcements', {})[args.round] = announcement
        data['updated_at'] = datetime.now(timezone.utc).isoformat()
        pending = path.with_suffix('.json.new')
        pending.write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n')
        pending.replace(path)
    print(('Published' if args.publish else 'Validated (dry run)'), args.round,
          announcement['at'], len(announcement['ball_numbers']), 'balls; fixtures unchanged')


if __name__ == '__main__':
    main()
