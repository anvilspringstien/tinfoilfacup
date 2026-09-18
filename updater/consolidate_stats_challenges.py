#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLUBFINDER = ROOT / "clubfinder.html"
CHALLENGES = ROOT / "beta" / "challenges-beta.html"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected exactly 1 match, found {count}")
    return text.replace(old, new, 1)


def replace_roundel(text: str, alt: str, data_uri: str) -> str:
    pattern = re.compile(
        r'(<img src=")data:image/png;base64,[^"]+(" alt="' + re.escape(alt) + r'">)'
    )
    text, count = pattern.subn(lambda m: m.group(1) + data_uri + m.group(2), text)
    if count != 1:
        raise RuntimeError(f"{alt}: expected one Stats roundel, found {count}")
    return text


def extract_inline_scripts(html: str) -> list[str]:
    return re.findall(r"<script(?:\s[^>]*)?>([\s\S]*?)</script>", html, flags=re.I)


def check_js_syntax(label: str, html: str) -> None:
    if not shutil.which("node"):
        raise RuntimeError("node is required for inline JavaScript syntax checks")
    for idx, code in enumerate(extract_inline_scripts(html)):
        with tempfile.NamedTemporaryFile("w", suffix=".js", encoding="utf-8", delete=False) as fh:
            fh.write(code)
            path = fh.name
        try:
            result = subprocess.run(
                ["node", "--check", path],
                text=True,
                capture_output=True,
            )
            if result.returncode:
                raise RuntimeError(
                    f"{label} inline script {idx} failed syntax check:\n"
                    + result.stdout
                    + result.stderr
                )
        finally:
            Path(path).unlink(missing_ok=True)


def update_clubfinder(clubfinder: str, challenges_source: str) -> str:
    # The six files supplied on 18 Sep are already embedded byte-for-byte in the
    # current Challenges BETA Stats renderer. Reuse those exact canonical assets.
    match = re.search(
        r"const TFFC_STATS_ROUNDELS=(\[[\s\S]*?\]);",
        challenges_source,
    )
    if not match:
        raise RuntimeError("Canonical TFFC_STATS_ROUNDELS array not found")
    roundels = json.loads(match.group(1))
    if len(roundels) != 6:
        raise RuntimeError(f"Expected six canonical roundels, found {len(roundels)}")

    alts = [
        "Rounds Completed",
        "Matches Played",
        "Clubs Encountered",
        "Goals Seen",
        "Grounds Visited",
        "Pigeon Miles Flown",
    ]
    for alt, data_uri in zip(alts, roundels):
        clubfinder = replace_roundel(clubfinder, alt, data_uri)

    if "const TIN_FOIL_STATS_REQUEST_KEY=" not in clubfinder:
        clubfinder = replace_once(
            clubfinder,
            "const TIN_FOIL_CHALLENGE_BRIDGE_KEY='tffc.clubfinderCampaign.v1';",
            "const TIN_FOIL_CHALLENGE_BRIDGE_KEY='tffc.clubfinderCampaign.v1';\n"
            "const TIN_FOIL_STATS_REQUEST_KEY='tffc.clubfinderStatsRequest.v1';",
            "Stats request key",
        )

    if "window.tffcOpenChallengesByOriginName=" not in clubfinder:
        clubfinder = replace_once(
            clubfinder,
            "return true;\n};\n\nfunction tinFoilChallengeStatsSnapshot",
            """return true;
};
window.tffcOpenChallengesByOriginName=function(originName){
  const origin=ELIGIBLE.find(c=>norm(c.name)===norm(originName));
  if(!origin)return false;
  openChallenges(origin);
  return true;
};

function tinFoilChallengeStatsSnapshot""",
            "Stats Challenges bridge",
        )

    if "async function tinFoilHandleStatsRequest()" not in clubfinder:
        clubfinder = replace_once(
            clubfinder,
            """ window.location.href='beta/challenges-beta.html';
}
/* TIN_FOIL_PRODUCTION_CHALLENGE_BRIDGE_END */""",
            """ window.location.href='beta/challenges-beta.html';
}
async function tinFoilHandleStatsRequest(){
  let request=null;
  try{request=JSON.parse(localStorage.getItem(TIN_FOIL_STATS_REQUEST_KEY)||'null');}catch(e){}
  if(!request||request.source!=='Challenges')return false;
  localStorage.removeItem(TIN_FOIL_STATS_REQUEST_KEY);
  if(Date.now()-Number(request.requestedAt||0)>120000)return false;
  const origin=ELIGIBLE.find(c=>norm(c.name)===norm(request.originName));
  if(!origin)return false;
  const statsWindow=window.open('','TFFC_STATS');
  if(!statsWindow)return false;
  await journeyCertificate(origin,statsWindow,'challenges');
  return true;
}
window.addEventListener('pageshow',()=>{setTimeout(()=>{tinFoilHandleStatsRequest();},0);});
/* TIN_FOIL_PRODUCTION_CHALLENGE_BRIDGE_END */""",
            "Stats request handler",
        )

    if 'window.open("","TFFC_STATS")' not in clubfinder:
        clubfinder = replace_once(
            clubfinder,
            'const w=suppliedWindow || window.open("","_blank");',
            'const w=suppliedWindow || window.open("","TFFC_STATS");',
            "Named Stats window",
        )

    if "function tinFoilStatsNavHtml(origin)" not in clubfinder:
        marker = 'async function journeyCertificate(origin,suppliedWindow=null,returnMode="clubfinder"){'
        helper = """function tinFoilStatsNavHtml(origin){
  const originArg=certEsc(JSON.stringify(origin.name));
  return '<div class="stats-return">'+
    '<button class="stats-campaign" type="button" onclick="if(window.opener&amp;&amp;!window.opener.closed){window.opener.focus();window.close();}else{window.location.href=&quot;https://anvilspringstien.github.io/tinfoilfacup/clubfinder.html&quot;;}">Campaign</button>'+
    '<button class="stats-challenges" type="button" onclick="var o=window.opener;if(o&amp;&amp;!o.closed&amp;&amp;typeof o.tffcOpenChallengesByOriginName===&quot;function&quot;){o.tffcOpenChallengesByOriginName('+originArg+');o.focus();window.close();}else{window.location.href=&quot;https://anvilspringstien.github.io/tinfoilfacup/beta/challenges-beta.html&quot;;}">Challenges</button>'+
  '</div>';
}
"""
        clubfinder = replace_once(
            clubfinder,
            marker,
            helper + marker,
            "Stats nav helper",
        )

    old_css = (
        ".stats-return{text-align:center;margin:0 auto 16px}"
        ".stats-return button{border:0;border-radius:20px;background:#084c61;color:#fff;"
        "padding:8px 14px;font:600 12px Arial,sans-serif;cursor:pointer}"
        ".stats-return button:hover{filter:brightness(.92)}"
    )
    new_css = (
        ".stats-return{display:flex;justify-content:center;gap:10px;flex-wrap:wrap;"
        "margin:0 auto 16px}"
        ".stats-return button{min-width:112px;border:0;border-radius:20px;padding:8px 14px;"
        "font:600 12px Arial,sans-serif;cursor:pointer}"
        ".stats-return .stats-campaign{background:#084c61;color:#fff}"
        ".stats-return .stats-challenges{background:#e4bb26;color:#111}"
        ".stats-return button:hover{filter:brightness(.92)}"
    )
    if old_css in clubfinder:
        clubfinder = replace_once(clubfinder, old_css, new_css, "Stats nav CSS")
    elif new_css not in clubfinder:
        raise RuntimeError("Stats nav CSS is neither old nor new")

    if ".print,.stats-return{display:none}}" not in clubfinder:
        clubfinder = replace_once(
            clubfinder,
            ".print{display:none}}",
            ".print,.stats-return{display:none}}",
            "Print Stats nav hide",
        )

    old_start = """'</style></head><body><div class="stats-return">"""
    if old_start in clubfinder:
        start = clubfinder.index(old_start)
        end_marker = """</button></div><main class="sheet">'+"""
        end_at = clubfinder.index(end_marker, start)
        end = end_at + len(end_marker)
        clubfinder = (
            clubfinder[:start]
            + """'</style></head><body>'+tinFoilStatsNavHtml(origin)+'<main class="sheet">'+"""
            + clubfinder[end:]
        )

    required = [
        "function tinFoilStatsNavHtml(origin)",
        "stats-campaign",
        "stats-challenges",
        "tffc.clubfinderStatsRequest.v1",
        "window.tffcOpenChallengesByOriginName",
    ]
    for marker in required:
        if marker not in clubfinder:
            raise RuntimeError(f"Clubfinder post-check missing {marker}")

    for data_uri in roundels:
        if data_uri not in clubfinder:
            raise RuntimeError("A canonical Stats roundel did not reach Clubfinder")

    return clubfinder


def update_challenges(challenges: str) -> str:
    # Retire the old standalone prototype Stats page.
    stats_start = challenges.find('  <section class="stats" id="stats">')
    if stats_start >= 0:
        stats_end = challenges.find("  </section>", stats_start)
        if stats_end < 0:
            raise RuntimeError("Could not find end of old Challenges Stats section")
        challenges = challenges[:stats_start] + challenges[stats_end + len("  </section>"):]

    if 'id="maybeLater"' not in challenges:
        challenges = replace_once(
            challenges,
            """      <div class="actions">
        <button id="openDeck" class="challenge-btn beta-splash-go">Challenges</button>
      </div>""",
            """      <div class="actions">
        <button id="openDeck" class="challenge-btn beta-splash-go">Challenges</button>
        <button id="maybeLater" class="challenge-btn beta-splash-later">Maybe Later</button>
      </div>""",
            "Maybe Later splash button",
        )

    if "#maybeLater.challenge-btn.beta-splash-later" not in challenges:
        anchor = """#openDeck.challenge-btn.beta-splash-go:active{
  transform:translateY(1px)!important;
  box-shadow:0 2px 0 #7c6511!important;
}"""
        extra = """
.hero.beta-splash .actions{gap:12px;flex-wrap:wrap}
#maybeLater.challenge-btn.beta-splash-later{
  margin-top:11px!important;
  min-width:165px!important;
  height:44px!important;
  padding:0 22px!important;
  border:2px solid #fafafa!important;
  border-radius:9px!important;
  background:#084c61!important;
  color:#fafafa!important;
  box-shadow:0 3px 0 #04323f!important;
  font:800 13px/1 Arial,Helvetica,sans-serif!important;
  letter-spacing:.045em!important;
}
#maybeLater.challenge-btn.beta-splash-later:hover,
#maybeLater.challenge-btn.beta-splash-later:focus-visible{
  filter:brightness(1.08)!important;
  color:#fff!important;
  border-color:#fff!important;
  box-shadow:0 3px 0 #04323f!important;
  transform:none!important;
}
#maybeLater.challenge-btn.beta-splash-later:active{
  transform:translateY(1px)!important;
  box-shadow:0 2px 0 #04323f!important;
}"""
        challenges = replace_once(
            challenges,
            anchor,
            anchor + extra,
            "Maybe Later splash CSS",
        )

    challenges = challenges.replace(
        "body.tffc-stats-view .hero.beta-splash{display:none}"
        "body.tffc-stats-view #stats{display:block;margin-top:3vh}"
        "body.tffc-stats-view{scroll-behavior:auto}",
        "",
    )

    old_truth = (
        '<div class="campaign-truth" aria-label="Current Campaign standing">'
        '<span>Pigeon Miles Travelled: <strong id="truthPigeonMiles">0</strong></span>'
        '<span>Current Campaign Round: <strong id="truthCampaignRound">'
        'Extra Preliminary Round</strong></span></div>'
    )
    new_truth = (
        '<div class="campaign-truth" aria-label="Current Campaign standing">'
        '<span id="truthCallSignWrap" hidden>Pigeon Call Sign: '
        '<strong id="truthCallSign"></strong></span>'
        '<span>Pigeon Miles Flown: <strong id="truthPigeonMiles">0</strong></span>'
        '<span>Current Campaign Round: <strong id="truthCampaignRound">'
        'Extra Preliminary Round</strong></span></div>'
    )
    if old_truth in challenges:
        challenges = replace_once(
            challenges, old_truth, new_truth, "Challenge Campaign identity strip"
        )
    elif new_truth not in challenges:
        raise RuntimeError("Campaign truth strip is neither old nor new")

    challenges = challenges.replace("Pigeon Miles Travelled", "Pigeon Miles Flown")

    old_truth_css = (
        ".campaign-truth{margin-bottom:22px;display:flex;align-items:center;"
        "justify-content:center;gap:22px;margin:8px auto 0;max-width:500px;"
        "font-family:Arial,sans-serif;font-size:10px;letter-spacing:.06em;"
        "text-transform:uppercase;color:#c9c4b8;white-space:nowrap}"
    )
    new_truth_css = (
        ".campaign-truth{margin-bottom:22px;display:flex;align-items:center;"
        "justify-content:center;gap:8px 22px;flex-wrap:wrap;margin:8px auto 0;"
        "max-width:650px;font-family:Arial,sans-serif;font-size:10px;"
        "letter-spacing:.06em;text-transform:uppercase;color:#c9c4b8;"
        "white-space:nowrap}"
    )
    if old_truth_css in challenges:
        challenges = replace_once(
            challenges, old_truth_css, new_truth_css, "Campaign truth wrap"
        )
    elif new_truth_css not in challenges:
        raise RuntimeError("Campaign truth CSS is neither old nor new")

    # Remove the duplicate self-contained Stats renderer + embedded roundels.
    legacy_start = challenges.find("const TFFC_STATS_ROUNDELS=")
    if legacy_start >= 0:
        legacy_end = challenges.find("\n\nfunction tinFoilConfirm", legacy_start)
        if legacy_end < 0:
            raise RuntimeError("Could not find end of duplicate Challenges Stats renderer")
        bridge = """function readClubfinderBridge(){
  try { return JSON.parse(localStorage.getItem(CLUBFINDER_BRIDGE_KEY)||"null"); } catch(e) { return null; }
}
const TFFC_STATS_REQUEST_KEY="tffc.clubfinderStatsRequest.v1";
function returnToClubfinder(){
  try{
    const ref=document.referrer?new URL(document.referrer):null;
    if(ref&&ref.origin===location.origin&&/\\/clubfinder\\.html$/i.test(ref.pathname)){history.back();return;}
  }catch(e){}
  location.href="../clubfinder.html";
}
function openCampaignStatsFromDeck(){
  const bridge=readClubfinderBridge();
  if(!bridge||!bridge.originName){
    $("feedback").textContent="Campaign Stats are not available yet. Return to Clubfinder and reopen Challenges.";
    return;
  }
  const statsWindow=window.open("","TFFC_STATS");
  if(!statsWindow){
    $("feedback").textContent="Please allow the Stats window, then try again.";
    return;
  }
  try{
    statsWindow.document.open();
    statsWindow.document.write('<!doctype html><html><head><title>Tin Foil FA Cup — Stats</title></head><body style="font-family:Arial,sans-serif;padding:24px">Loading Campaign Stats…</body></html>');
    statsWindow.document.close();
  }catch(e){}
  localStorage.setItem(TFFC_STATS_REQUEST_KEY,JSON.stringify({source:"Challenges",originName:bridge.originName,requestedAt:Date.now()}));
  returnToClubfinder();
}"""
        challenges = challenges[:legacy_start] + bridge + challenges[legacy_end:]

    handler_start = challenges.find('$("openDeck").onclick=')
    if handler_start >= 0:
        handler_end = challenges.find('overlay.addEventListener("click"', handler_start)
        if handler_end < 0:
            raise RuntimeError("Could not find end of Challenges navigation handlers")
        handlers = """$("openDeck").onclick=()=>{ openAt(0); };
$("maybeLater").onclick=(e)=>{ e.preventDefault(); returnToClubfinder(); };
$("deckStatsBtn").onclick=()=>{ openCampaignStatsFromDeck(); };
$("exitBtn").onclick=(e)=>{
  e.preventDefault();
  e.stopPropagation();
  e.stopImmediatePropagation();
  returnToClubfinder();
};
"""
        challenges = challenges[:handler_start] + handlers + challenges[handler_end:]

    old_render = """function renderStats() {
  const challengeList=CHALLENGES.filter(c=>c.type!=="foundation");
  const completed=challengeList.filter(c=>!!state.completed[c.id]);
  const available=challengeList.filter(c=>isUnlocked(c) && !state.completed[c.id]);
  const campaignUnlocked=challengeList.filter(c=>c.type==="campaign" && isUnlocked(c));
  $("statsCompleted").textContent=completed.length;
  $("statsAvailable").textContent=available.length;
  $("statsJourney").textContent=campaignUnlocked.length;"""
    new_render = """function renderStats() {
  const challengeList=CHALLENGES.filter(c=>c.type!=="foundation");
  const completed=challengeList.filter(c=>!!state.completed[c.id]);"""
    if old_render in challenges:
        challenges = replace_once(
            challenges, old_render, new_render, "Deleted Stats DOM references"
        )

    old_call = """  $("truthPigeonMiles").textContent=Math.max(0,Math.round(state.pigeonMiles)).toLocaleString("en-GB");
  $("truthCampaignRound").textContent=$("campaignRound").options[$("campaignRound").selectedIndex].textContent;"""
    new_call = """  $("truthPigeonMiles").textContent=Math.max(0,Math.round(state.pigeonMiles)).toLocaleString("en-GB");
  {
    const bridge=readClubfinderBridge(),callSign=String(bridge&&bridge.callSign||"").trim();
    $("truthCallSign").textContent=callSign;
    $("truthCallSignWrap").hidden=!callSign;
  }
  $("truthCampaignRound").textContent=$("campaignRound").options[$("campaignRound").selectedIndex].textContent;"""
    if old_call in challenges:
        challenges = replace_once(
            challenges, old_call, new_call, "Render Pigeon Call Sign"
        )

    forbidden = [
        "Pigeon Miles Travelled",
        "tffcCampaignStatsPanel",
        "TFFC_STATS_ROUNDELS",
        'id="statsOpenDeck"',
        'section class="stats" id="stats"',
        "tffc-stats-view",
    ]
    for marker in forbidden:
        if marker in challenges:
            raise RuntimeError(f"Challenges cleanup still contains {marker}")

    required = [
        'id="maybeLater"',
        "Pigeon Miles Flown",
        'id="truthCallSign"',
        "tffc.clubfinderStatsRequest.v1",
        "openCampaignStatsFromDeck",
    ]
    for marker in required:
        if marker not in challenges:
            raise RuntimeError(f"Challenges post-check missing {marker}")

    return challenges


def main() -> None:
    original_clubfinder = CLUBFINDER.read_text(encoding="utf-8")
    original_challenges = CHALLENGES.read_text(encoding="utf-8")

    new_clubfinder = update_clubfinder(original_clubfinder, original_challenges)
    new_challenges = update_challenges(original_challenges)

    check_js_syntax("clubfinder.html", new_clubfinder)
    check_js_syntax("beta/challenges-beta.html", new_challenges)

    CLUBFINDER.write_text(new_clubfinder, encoding="utf-8")
    CHALLENGES.write_text(new_challenges, encoding="utf-8")

    print(
        "UI consolidation complete:",
        f"clubfinder {len(original_clubfinder)} -> {len(new_clubfinder)} bytes;",
        f"challenges {len(original_challenges)} -> {len(new_challenges)} bytes",
    )


if __name__ == "__main__":
    main()
