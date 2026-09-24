#!/usr/bin/env python3
"""BETA-only public display identity for the 2026 Holmesdale merger.

Keep legacy persisted keys and surveyed ground data intact; change only
user-visible club names and season-specific Stats identity accounting.
"""
from pathlib import Path
import argparse

BETA=Path('beta/clubfinder-beta.html')
BEGIN='/* TIN_FOIL_BETA_HOLMESDALE_DISPLAY_BEGIN */'
END='/* TIN_FOIL_BETA_HOLMESDALE_DISPLAY_END */'
HELPER="""/* TIN_FOIL_BETA_HOLMESDALE_DISPLAY_BEGIN */
// The original Holmesdale FC key remains the stable postcode / saved campaign
// identifier. Use the merged 2026 name solely where users see club identities.
function tinFoilBetaDisplayClubName(name){
  return canonicalClubKey(name)==='holmesdale'&&tinFoilBetaHolmesdale2026Ready()
    ?'Petts Wood & Holmesdale FC':String(name||'');
}
/* TIN_FOIL_BETA_HOLMESDALE_DISPLAY_END */
"""
def replace_exact(s,old,new,count=1):
    found=s.count(old)
    if found==count:
        if s.count(new):raise RuntimeError('mixed old/new display variants: '+old[:80])
        return s.replace(old,new)
    if found==0 and s.count(new)==count:return s
    raise RuntimeError(f'anchor mismatch old={found},new={s.count(new)},wanted={count}: {old[:100]}')

def patch(s):
    anchor='/* TIN_FOIL_BETA_HOLMESDALE_2026_END */'
    if BEGIN not in s and END not in s:
        if s.count(anchor)!=1:raise RuntimeError('existing Holmesdale identity guard absent')
        s=s.replace(anchor,HELPER+anchor,1)
    else:
        if s.count(BEGIN)!=1 or s.count(END)!=1 or s.count(HELPER)!=1:
            raise RuntimeError('Holmesdale display helper was modified or duplicated')
    replacements=[
        ("'This Campaign starts with: '+esc(journey.origin.name)",
         "'This Campaign starts with: '+esc(tinFoilBetaDisplayClubName(journey.origin.name))"),
        ("body+='<div class=\"history-entry\">'+esc(journey.origin.name)+' enters the competition at '",
         "body+='<div class=\"history-entry\">'+esc(tinFoilBetaDisplayClubName(journey.origin.name))+' enters the competition at '"),
        ("if(!journey||!journey.carrier||norm(journey.carrier.name)===norm(journey.origin.name))return '';",
         "if(!journey||!journey.carrier||sameClubIdentity(journey.carrier.name,journey.origin.name))return '';"),
        ("'Replace your saved Tin Foil FA Cup Campaign with '+o.name+' starting from '",
         "'Replace your saved Tin Foil FA Cup Campaign with '+tinFoilBetaDisplayClubName(o.name)+' starting from '"),
        ("addClub(origin.name)",
         "addClub(tinFoilBetaDisplayClubName(origin.name))",2),
        ("return {season:'2026–27',origin:origin.name,currentCustodian:",
         "return {season:'2026–27',origin:tinFoilBetaDisplayClubName(origin.name),currentCustodian:"),
        ("'<div class=\"club\">'+certEsc(origin.name)+'</div>'",
         "'<div class=\"club\">'+certEsc(tinFoilBetaDisplayClubName(origin.name))+'</div>'"),
        ("<h2>\${oi===0&&origin.hasCoords?'Nearest: ':''}\${esc(origin.name)}</h2>",
         "<h2>\${oi===0&&origin.hasCoords?'Nearest: ':''}\${esc(tinFoilBetaDisplayClubName(origin.name))}</h2>"),
    ]
    for item in replacements:
        old,new,*n=item
        s=replace_exact(s,old,new,n[0] if n else 1)
    # Stats and the Challenge bridge must not miscount the old name and the
    # merged name as two different custodians before the first replay.
    for name in ('home','away','winner'):
        old=f'norm(r.{name})===norm(pathCarrier)'
        new=f'sameClubIdentity(r.{name},pathCarrier)'
        count={'home':4,'away':4,'winner':2}[name]
        s=replace_exact(s,old,new,count)
    if s.count(BEGIN)!=1 or s.count(END)!=1:
        raise RuntimeError('display patch marker corruption')
    return s

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--check',action='store_true')
    args=ap.parse_args()
    before=BETA.read_text(encoding='utf8')
    after=patch(before)
    if args.check:
        if after!=before:raise SystemExit('BETA Holmesdale display patch missing')
        print('BETA Holmesdale visible naming patch idempotency: PASS')
    elif after==before:print('BETA Holmesdale display already applied')
    else:
        BETA.write_text(after,encoding='utf8')
        print('Patched BETA public Holmesdale name and Stats identity; production unchanged')
if __name__=='__main__':main()
