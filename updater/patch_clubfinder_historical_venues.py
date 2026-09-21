#!/usr/bin/env python3
"""Make Clubfinder historical-result consumers honour canonical result.venue.

Match-specific venue data in competition.json takes precedence over club-home
fallbacks. This keeps the main Campaign card and any still-present Stats/Print
or Pigeon Miles helpers on the same canonical historical venue.

Some older helper functions have been retired by later Clubfinder patches. The
canonical completedResultVenue hook remains mandatory; legacy consumers are
patched when present rather than being required as an implementation detail.
"""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / 'clubfinder.html'
text = HTML.read_text(encoding='utf-8')

completed = r'''function completedResultVenue(result){
  if(!result)return {ground:'Venue TBC',postcode:'Postcode TBC'};
  const rv=result.venue||{};
  if((rv.ground&&!/TBC/i.test(String(rv.ground)))||(rv.postcode&&!/TBC/i.test(String(rv.postcode)))){
    return {ground:rv.ground||'Venue TBC',postcode:rv.postcode||'Postcode TBC',lat:rv.lat,lon:rv.lon,verification:rv.verification||'verified'};
  }
  const pairKey=[String(result.home||'').toLowerCase(),String(result.away||'').toLowerCase()].join('|');
  const knownHistorical={
    'petts wood & holmesdale|windsor & eton':{ground:'The New Inn Stadium',postcode:'BR2 8HQ',lat:51.384,lon:0.022}
  };
  const kh=knownHistorical[pairKey];
  if(kh)return {...kh,verification:'verified'};
  const ov=VERIFIED_MATCH_VENUE_OVERRIDES[result.home]||VERIFIED_MATCH_VENUE_OVERRIDES[(candidateClubByName(result.home)||{}).name]||null;
  if(ov)return {ground:ov.ground||'Venue TBC',postcode:ov.postcode||'Postcode TBC',lat:ov.lat,lon:ov.lon,verification:'verified'};
  const homeClub=candidateClubByName(result.home);
  const hg=groundByClubName(homeClub?homeClub.name:result.home);
  return {
    ground:(hg&&hg.ground)||'Venue TBC',
    postcode:(hg&&hg.postcode)||'Postcode TBC',
    lat:hg&&hg.lat,lon:hg&&hg.lon,
    verification:(hg&&hg.verification)||'unverified'
  };
}'''
pat = re.compile(r'function completedResultVenue\(result\)\{.*?^\}', re.S | re.M)
text, n = pat.subn(lambda m: completed, text, count=1)
if n != 1:
    raise SystemExit(f'ABORT: expected one completedResultVenue function, replaced {n}')

optional_replacements = []

venue_stats = r'''  function venueForStats(r){
    const v=completedResultVenue(r);
    return {ground:v.ground||'Venue TBC',postcode:v.postcode||'Postcode TBC'};
  }'''
pat = re.compile(r'^  function venueForStats\(r\)\{.*?^  \}', re.S | re.M)
text, n = pat.subn(lambda m: venue_stats, text, count=1)
if n > 1:
    raise SystemExit(f'ABORT: expected at most one venueForStats function, replaced {n}')
optional_replacements.append(('venueForStats', n))

venue_result = r'''  function venueForResult(r){
    const v=completedResultVenue(r);
    return {ground:v.ground||'Venue TBC',postcode:v.postcode||'Postcode TBC'};
  }'''
pat = re.compile(r'^  function venueForResult\(r\)\{.*?^  \}', re.S | re.M)
text, n = pat.subn(lambda m: venue_result, text, count=1)
if n > 1:
    raise SystemExit(f'ABORT: expected at most one venueForResult function, replaced {n}')
optional_replacements.append(('venueForResult', n))

pat = re.compile(r'^ function venueForChallenge\(r\)\{.*\}$', re.M)
text, n = pat.subn(" function venueForChallenge(r){return completedResultVenue(r);}", text, count=1)
if n > 1:
    raise SystemExit(f'ABORT: expected at most one venueForChallenge function, replaced {n}')
optional_replacements.append(('venueForChallenge', n))

# Mandatory canonical behaviour: the helper itself must prefer result.venue.
for marker in (
    "function completedResultVenue(result){",
    "const rv=result.venue||{};",
    "const homeClub=candidateClubByName(result.home);",
    "'petts wood & holmesdale|windsor & eton':{ground:'The New Inn Stadium',postcode:'BR2 8HQ'",
):
    if marker not in text:
        raise SystemExit(f'ABORT: historical venue consumption marker missing: {marker}')

# If a legacy helper still exists, it must now delegate to completedResultVenue.
for name, replaced in optional_replacements:
    if replaced and name == 'venueForChallenge' and "function venueForChallenge(r){return completedResultVenue(r);}" not in text:
        raise SystemExit('ABORT: venueForChallenge did not delegate to completedResultVenue')
    if replaced and name in ('venueForStats', 'venueForResult'):
        marker = f'function {name}(r){{'
        start = text.find(marker)
        if start < 0 or 'const v=completedResultVenue(r);' not in text[start:start + 260]:
            raise SystemExit(f'ABORT: {name} did not delegate to completedResultVenue')

HTML.write_text(text, encoding='utf-8')
print('CLUBFINDER HISTORICAL VENUE PATCH: SUCCESS')
print('Main Campaign historical venue resolver prefers canonical result.venue.')
for name, replaced in optional_replacements:
    print(f'{name}:', 'PATCHED' if replaced else 'RETIRED / NOT PRESENT')
print('Later Stats, journey and historical Campaign regressions remain behavioural guards.')
print('Verified match overrides and club-ground lookup remain guarded fallbacks.')
print('Competition data: UNTOUCHED')
