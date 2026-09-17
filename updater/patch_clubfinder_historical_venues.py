#!/usr/bin/env python3
"""Make every Clubfinder historical-result consumer honour canonical result.venue.

Match-specific venue data in competition.json takes precedence over club-home
fallbacks. This keeps the main Campaign card, Stats/Print and Pigeon Miles on the
same canonical historical venue.
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

venue_stats = r'''  function venueForStats(r){
    const v=completedResultVenue(r);
    return {ground:v.ground||'Venue TBC',postcode:v.postcode||'Postcode TBC'};
  }'''
pat = re.compile(r'^  function venueForStats\(r\)\{.*?^  \}', re.S | re.M)
text, n = pat.subn(lambda m: venue_stats, text, count=1)
if n != 1:
    raise SystemExit(f'ABORT: expected one venueForStats function, replaced {n}')

venue_result = r'''  function venueForResult(r){
    const v=completedResultVenue(r);
    return {ground:v.ground||'Venue TBC',postcode:v.postcode||'Postcode TBC'};
  }'''
pat = re.compile(r'^  function venueForResult\(r\)\{.*?^  \}', re.S | re.M)
text, n = pat.subn(lambda m: venue_result, text, count=1)
if n != 1:
    raise SystemExit(f'ABORT: expected one venueForResult function, replaced {n}')

pat = re.compile(r'^ function venueForChallenge\(r\)\{.*\}$', re.M)
text, n = pat.subn(" function venueForChallenge(r){return completedResultVenue(r);}", text, count=1)
if n != 1:
    raise SystemExit(f'ABORT: expected one venueForChallenge function, replaced {n}')

required = (
    "const rv=result.venue||{};",
    "function venueForChallenge(r){return completedResultVenue(r);}",
    "const v=completedResultVenue(r);",
)
for marker in required:
    if marker not in text:
        raise SystemExit(f'ABORT: historical venue consumption marker missing: {marker}')

HTML.write_text(text, encoding='utf-8')
print('CLUBFINDER HISTORICAL VENUE PATCH: SUCCESS')
print('Main Campaign, Stats/Print and Pigeon Miles now prefer canonical result.venue.')
print('Verified match overrides and club-ground lookup remain guarded fallbacks.')
print('Competition data: UNTOUCHED')
