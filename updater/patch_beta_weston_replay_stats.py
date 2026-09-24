#!/usr/bin/env python3
"""Guarded, repeatable BETA-only Weston replay presentation and Stats repair.

Never changes canonical competition data, production Clubfinder, or BETA's
embedded competition snapshot. A missing or changed source anchor fails closed.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BETA = ROOT / "beta/clubfinder-beta.html"
BEGIN = "/* TIN_FOIL_BETA_REPLAY_STATS_BEGIN */"
END = "/* TIN_FOIL_BETA_REPLAY_STATS_END */"
text = BETA.read_text(encoding="utf-8")

helper = r"""/* TIN_FOIL_BETA_REPLAY_STATS_BEGIN */
function tinFoilBetaVerifiedWimborneReplay(r){
  return !!r && String(r.round||'')==='Second Round Qualifying Replay' &&
    String(r.date||'')==='2026-09-22' &&
    sameClubIdentity(r.home,'Wimborne Town') &&
    sameClubIdentity(r.away,'Weston-super-Mare') &&
    sameClubIdentity(r.winner,'Wimborne Town') &&
    Number(r.home_score)===1 && Number(r.away_score)===1 &&
    r.decision==='penalties';
}
function tinFoilBetaPenaltyResultNote(r){
  if(!r||r.decision!=='penalties'||!r.winner)return '';
  // Source chronology records the shootout winner but not numerical pens.
  // This verified 4-3 score is deliberately scoped to one named 2026 tie.
  return tinFoilBetaVerifiedWimborneReplay(r)
    ? 'won 4–3 on penalties' : 'won on penalties';
}
function tinFoilBetaCompletedKickoff(r,rp){
  // Do not let a legacy 15:00 fallback overwrite the verified replay time.
  if(tinFoilBetaVerifiedWimborneReplay(r))return '19:45';
  if(rp&&rp.kickoff)return rp.kickoff;
  if(r&&r.kickoff)return r.kickoff;
  return /Replay/i.test(String((r&&r.round)||''))?'Kick-off TBC':'15:00';
}
/* TIN_FOIL_BETA_REPLAY_STATS_END */
"""

def check_existing(t):
    required = [
        BEGIN, END, "function tinFoilBetaCompletedKickoff(r,rp){",
        "function tinFoilBetaPenaltyResultNote(r){",
        "kickoff:tinFoilBetaCompletedKickoff(r,rp)",
        "kickoff:tinFoilBetaCompletedKickoff(r,null)",
        "penaltyWins=0, penaltyLosses=0",
        "tinFoilBetaPenaltyResultNote(r)",
        "• Shootouts Won: '+penaltyWins",
        "• Shootouts Lost: '+penaltyLosses",
    ]
    for m in required:
        if m not in t:
            raise SystemExit("BETA REPAIR GUARD: incomplete previous patch: " + m)
    if t.count(BEGIN)!=1 or t.count(END)!=1:
        raise SystemExit("BETA REPAIR GUARD: duplicate/missing markers")

if BEGIN in text or END in text:
    check_existing(text)
    print("BETA WESTON REPLAY/STATS PATCH: PASS (already applied; idempotent)")
    raise SystemExit(0)

def replace(old, new, count=1):
    global text
    actual = text.count(old)
    if actual != count:
        raise SystemExit(f"BETA REPAIR GUARD: anchor mismatch: {old[:100]!r} (expected {count}, found {actual})")
    text = text.replace(old, new)

replace("function currentDisplayFixture(club){", helper+"function currentDisplayFixture(club){")
replace("kickoff:rp.kickoff||r.kickoff||'Kick-off TBC'",
        "kickoff:tinFoilBetaCompletedKickoff(r,rp)")
replace("kickoff:r.kickoff||'15:00',venue:completedResultVenue(r)",
        "kickoff:tinFoilBetaCompletedKickoff(r,null),venue:completedResultVenue(r)")
replace("  }else if(r.decision==='a.e.t.'){\n    line+=' • AET';",
        "  }else if(r.decision==='penalties'&&r.winner){\n"
        "    line+=' • '+esc(r.winner)+' '+esc(tinFoilBetaPenaltyResultNote(r));\n"
        "  }else if(r.decision==='a.e.t.'){\n    line+=' • AET';",2)
replace(
    "function resultLinePlain(r){if(!r)return '';if(r.decision==='walkover')return r.home+' (W/O) v '+r.away;let x=r.home+' ('+r.home_score+') v ('+r.away_score+') '+r.away;if(r.decision==='a.e.t.')x+=' • AET';return x}",
    "function resultLinePlain(r){if(!r)return '';if(r.decision==='walkover')return r.home+' (W/O) v '+r.away;let x=r.home+' ('+r.home_score+') v ('+r.away_score+') '+r.away;if(r.decision==='a.e.t.')x+=' • AET';if(r.decision==='penalties'&&r.winner)x+=' • '+r.winner+' '+tinFoilBetaPenaltyResultNote(r);return x}"
)

start = text.index("function tinFoilCertificateWinner(r){")
end = text.index("function tinFoilStatsDisplayClubKey(", start)
part = text[start:end]
old = "if(hs===as)return '';"
if part.count(old)!=1:
    raise SystemExit("BETA REPAIR GUARD: certificate winner equality boundary changed")
part = part.replace(old, "if(hs===as)return r.decision==='penalties'&&r.winner?r.winner:'';")
text = text[:start]+part+text[end:]

replace(
    "  let goals=0, homeGames=0, awayGames=0, custodianWins=0, draws=0, custodianDefeats=0;",
    "  let goals=0, homeGames=0, awayGames=0, custodianWins=0, draws=0, custodianDefeats=0, penaltyWins=0, penaltyLosses=0;"
)
replace(
    """    if(r.winner){
      if(norm(r.winner)===norm(pathCarrier))custodianWins++;
      else if(norm(r.home)===norm(pathCarrier)||norm(r.away)===norm(pathCarrier))custodianDefeats++;
      pathCarrier=r.winner;
    }""",
    """    if(r.winner){
      const isDrawnShootout=r.decision==='penalties'&&
        Number.isFinite(hs)&&Number.isFinite(as)&&hs===as;
      if(isDrawnShootout){
        // The match remains a draw. The shootout transfers custody separately.
        if(norm(r.winner)===norm(pathCarrier))penaltyWins++;
        else if(norm(r.home)===norm(pathCarrier)||norm(r.away)===norm(pathCarrier))penaltyLosses++;
      }else{
        if(norm(r.winner)===norm(pathCarrier))custodianWins++;
        else if(norm(r.home)===norm(pathCarrier)||norm(r.away)===norm(pathCarrier))custodianDefeats++;
      }
      pathCarrier=r.winner;
    }"""
)
replace(
    "'<div class=\"jr-winner\">'+certEsc(tinFoilCertificateWinner(r))+'</div>'+",
    "'<div class=\"jr-winner\">'+certEsc(tinFoilCertificateWinner(r))"
    "+(r.decision==='penalties'&&r.winner?'<br>'+certEsc(tinFoilBetaPenaltyResultNote(r)):'')+'</div>'+"
)
replace("• Wins by Current Custodian: '+custodianWins+'",
        "• Custodian Match Wins: '+custodianWins+'")
replace("• Defeats by Current Custodian: '+custodianDefeats+'",
        "• Custodian Match Defeats: '+custodianDefeats+'<br>• Shootouts Won: '+penaltyWins+'<br>• Shootouts Lost: '+penaltyLosses+'")
check_existing(text)
BETA.write_text(text, encoding="utf-8")
print("BETA WESTON REPLAY/STATS PATCH: PASS")
print("Only beta/clubfinder-beta.html was changed.")
