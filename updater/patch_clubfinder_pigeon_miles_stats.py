"""Add Pigeon Miles to the Clubfinder Stats certificate without touching journey custody logic.

Pigeon Miles are 2 x straight-line distance from the saved Campaign start postcode
out to each completed tie venue. Precise miles are accumulated; only the display is
rounded. If any required location cannot be resolved, Stats says so rather than
inventing a total.
"""
from pathlib import Path

HTML = Path('clubfinder.html')
text = HTML.read_text(encoding='utf-8')

MARKER = '/* TIN_FOIL_PIGEON_MILES_STATS_BEGIN */'
if MARKER in text:
    print('Pigeon Miles Stats patch already present; no change.')
    raise SystemExit(0)

# Open the certificate window before the first await so browser popup protection
# continues to see the window.open call as part of the user's Stats click.
old_popup = '  const w=window.open("","_blank");\n'
if text.count(old_popup) != 1:
    raise SystemExit(f'ABORT: expected one Stats popup anchor, found {text.count(old_popup)}')
text = text.replace(old_popup, '', 1)

sig = 'function journeyCertificate(origin){\n'
if text.count(sig) != 1:
    raise SystemExit(f'ABORT: expected one journeyCertificate signature, found {text.count(sig)}')

helper = r'''/* TIN_FOIL_PIGEON_MILES_STATS_BEGIN */
const TIN_FOIL_PIGEON_COORD_CACHE=new Map();
async function tinFoilPigeonCoords(postcode){
  const pc=String(postcode||'').trim().toUpperCase();
  if(!pc||/TBC/i.test(pc))return null;
  if(TIN_FOIL_PIGEON_COORD_CACHE.has(pc))return TIN_FOIL_PIGEON_COORD_CACHE.get(pc);
  try{
    const r=await fetch(PCAPI+encodeURIComponent(pc));
    if(!r.ok){TIN_FOIL_PIGEON_COORD_CACHE.set(pc,null);return null;}
    const j=await r.json();
    const hit=j&&j.result;
    const coord=hit&&Number.isFinite(Number(hit.latitude))&&Number.isFinite(Number(hit.longitude))
      ? {lat:Number(hit.latitude),lon:Number(hit.longitude)} : null;
    TIN_FOIL_PIGEON_COORD_CACHE.set(pc,coord);
    return coord;
  }catch(e){
    TIN_FOIL_PIGEON_COORD_CACHE.set(pc,null);
    return null;
  }
}
async function tinFoilPigeonMilesForStats(crumbs,startPostcode,venueForResult){
  const played=(crumbs||[]).filter(cr=>String(((cr||{}).result||{}).decision||'').toLowerCase()!=='walkover');
  if(!played.length)return {miles:0,display:'0',unresolved:0};
  const start=await tinFoilPigeonCoords(startPostcode);
  if(!start)return {miles:null,display:'Awaiting venue location',unresolved:played.length};
  const venues=await Promise.all(played.map(cr=>{
    const v=venueForResult(((cr||{}).result)||{});
    return tinFoilPigeonCoords(v&&v.postcode);
  }));
  if(venues.some(v=>!v))return {miles:null,display:'Awaiting venue location',unresolved:venues.filter(v=>!v).length};
  const miles=venues.reduce((sum,venue)=>sum+(2*hav(start,venue)),0);
  return {miles,display:String(Math.round(miles)),unresolved:0};
}
/* TIN_FOIL_PIGEON_MILES_STATS_END */
'''
text = text.replace(sig, helper + 'async function journeyCertificate(origin){\n  const w=window.open("","_blank");\n', 1)

venue_anchor = "    return {ground:(g&&g.ground)||'Venue TBC',postcode:(g&&g.postcode)||'Postcode TBC'};\n  }\n\n\n  const clubs=[];"
if text.count(venue_anchor) != 1:
    raise SystemExit(f'ABORT: expected one venueForResult completion anchor, found {text.count(venue_anchor)}')
pigeon_calc = "    return {ground:(g&&g.ground)||'Venue TBC',postcode:(g&&g.postcode)||'Postcode TBC'};\n  }\n\n  const savedJourneyForStats=loadSavedJourney();\n  const pigeonStats=await tinFoilPigeonMilesForStats(crumbs,savedJourneyForStats&&savedJourneyForStats.postcode,venueForResult);\n  const pigeonMilesDisplay=pigeonStats.display;\n\n\n  const clubs=[];"
text = text.replace(venue_anchor, pigeon_calc, 1)

stats_old = "• Home Games Played: '+homeGames+'<br>• Away Games Played: '+awayGames+'<br>• Wins by Current Custodian: '+custodianWins+'<br>• Draws: '+draws+'<br>• Defeats by Current Custodian: '+custodianDefeats+'"
stats_new = "• Home Games Played: '+homeGames+'<br>• Away Games Played: '+awayGames+'<br>• Wins by Current Custodian: '+custodianWins+'<br>• Draws: '+draws+'<br>• Defeats by Current Custodian: '+custodianDefeats+'<br>• Pigeon Miles Travelled: '+certEsc(pigeonMilesDisplay)+'"
if text.count(stats_old) != 1:
    raise SystemExit(f'ABORT: expected one Stats list anchor, found {text.count(stats_old)}')
text = text.replace(stats_old, stats_new, 1)

notes_old = 'Travel mileage is deliberately not counted yet.<br>Straight-line distance would not represent the user’s actual journey.'
notes_new = 'Pigeon Miles = twice the straight-line distance from your Campaign start postcode to each tie venue.'
if text.count(notes_old) != 1:
    raise SystemExit(f'ABORT: expected one old mileage note, found {text.count(notes_old)}')
text = text.replace(notes_old, notes_new, 1)

required = [
    MARKER,
    'async function journeyCertificate(origin)',
    '2*hav(start,venue)',
    'savedJourneyForStats&&savedJourneyForStats.postcode',
    'Pigeon Miles Travelled:',
    'Awaiting venue location',
    'Pigeon Miles = twice the straight-line distance from your Campaign start postcode to each tie venue.',
]
for item in required:
    if item not in text:
        raise SystemExit(f'ABORT: required Pigeon Miles marker missing: {item}')
if notes_old in text:
    raise SystemExit('ABORT: obsolete mileage note remains')
if text.count('const w=window.open("","_blank");') != 1:
    raise SystemExit('ABORT: Stats popup must be opened exactly once')

HTML.write_text(text, encoding='utf-8')
print('CLUBFINDER PIGEON MILES STATS PATCH: SUCCESS')
print('Formula: sum of 2 x straight-line start-postcode-to-tie-venue distance.')
print('Walkovers excluded because no tie was played.')
print('Unresolved start/venue locations fail closed as Awaiting venue location.')
print('Competition data and custody logic: UNTOUCHED')
