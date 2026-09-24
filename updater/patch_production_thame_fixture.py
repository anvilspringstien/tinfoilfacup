# Branch workflow trigger: guarded candidate application only
from pathlib import Path

PATH=Path("clubfinder.html")
text=PATH.read_text(encoding="utf-8")
begin="/* TIN_FOIL_PRODUCTION_THAME_VERIFIED_FIXTURE_BEGIN */"
end="/* TIN_FOIL_PRODUCTION_THAME_VERIFIED_FIXTURE_END */"
helper="""/* TIN_FOIL_PRODUCTION_THAME_VERIFIED_FIXTURE_BEGIN */
function tinFoilVerifiedThameNextFixture(club,nextName){
  // Fixture-local bridge for the FA's exact Third Qualifying draw abbreviation.
  // No generic alias expansion, no guessed winners and no Exmouth promotion.
  if(!club||nextName!=='Third Round Qualifying'||
     !sameClubIdentity(club.name,'Thame United'))return null;
  const fixtures=(LIVE_COMPETITION_DATA||{}).fixtures||{};
  const matches=Object.values(fixtures).filter(f=>
    f&&f.round==='Third Round Qualifying'&&f.date==='2026-10-03'&&
    f.home==='Thame Utd or Exmouth Town'&&f.away==='Eastbourne Borough');
  const unique=[...new Map(matches.map(f=>
    [[f.round,f.date,f.home,f.away].join('|'),f])).values()];
  if(unique.length!==1)return null;
  const resolved=resolveLiveFixtureForCarrier(unique[0],club);
  if(!resolved||resolved.conditional||
     !sameClubIdentity(resolved.home,club.name)||
     !sameClubIdentity(resolved.away,'Eastbourne Borough'))return null;
  return unique[0];
}
/* TIN_FOIL_PRODUCTION_THAME_VERIFIED_FIXTURE_END */
"""
if begin in text:
    if text.count(begin)!=1 or text.count(end)!=1:
        raise SystemExit("ABORT: malformed existing production Thame bridge markers")
else:
    marker="function nextRoundInfo(club){"
    if text.count(marker)!=1:
        raise SystemExit("ABORT: nextRoundInfo boundary is not unique")
    text=text.replace(marker,helper+marker,1)

generic_old="    if(distinct.length===1)nf=distinct[0];"
generic_new="""    if(distinct.length===1){
      const candidate=distinct[0];
      const isThameConditional=nextName==='Third Round Qualifying'&&
        candidate.date==='2026-10-03'&&candidate.home==='Thame Utd or Exmouth Town'&&
        candidate.away==='Eastbourne Borough';
      if(!isThameConditional)nf=candidate;
    }"""
if generic_old in text:
    if text.count(generic_old)!=1:
        raise SystemExit("ABORT: generic fixture fallback assignment is not unique")
    text=text.replace(generic_old,generic_new,1)
elif generic_new not in text:
    raise SystemExit("ABORT: guarded production fixture fallback boundary missing")

call="  if(!nf)nf=tinFoilVerifiedThameNextFixture(club,nextName);\n"
if call not in text:
    needle=generic_new+"\n  }\n  if(!nf&&nextName==='Preliminary Round'){"
    if text.count(needle)!=1:
        raise SystemExit("ABORT: production fixture fallback boundary is not unique")
    text=text.replace(needle,generic_new+"\n  }\n"+call+"  if(!nf&&nextName==='Preliminary Round'){",1)
if text.count(call)!=1:
    raise SystemExit("ABORT: production Thame bridge call is not unique")

PATH.write_text(text,encoding="utf-8")
print("PRODUCTION THAME FIXTURE PATCH: SUCCESS")
