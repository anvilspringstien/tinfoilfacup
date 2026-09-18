#!/usr/bin/env python3
from __future__ import annotations

import re
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHALLENGES = ROOT / "beta" / "challenges-beta.html"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected exactly 1 match, found {count}")
    return text.replace(old, new, 1)


def extract_inline_scripts(html: str) -> list[str]:
    return re.findall(r"<script(?:\s[^>]*)?>([\s\S]*?)</script>", html, flags=re.I)


def check_js_syntax(html: str) -> None:
    if not shutil.which("node"):
        raise RuntimeError("node is required for inline JavaScript syntax checks")
    for idx, code in enumerate(extract_inline_scripts(html)):
        with tempfile.NamedTemporaryFile("w", suffix=".js", encoding="utf-8", delete=False) as fh:
            fh.write(code)
            path = fh.name
        try:
            result = subprocess.run(["node", "--check", path], text=True, capture_output=True)
            if result.returncode:
                raise RuntimeError(
                    f"Challenges inline script {idx} failed syntax check:\n"
                    + result.stdout
                    + result.stderr
                )
        finally:
            Path(path).unlink(missing_ok=True)


def main() -> None:
    s = CHALLENGES.read_text(encoding="utf-8")

    if 'id="maybeLater"' in s:
        print("Maybe Later already present; nothing to do.")
        return

    s = replace_once(
        s,
        '''      <div class="actions">
        <button id="openDeck" class="challenge-btn beta-splash-go">Challenges</button>
      </div>''',
        '''      <div class="actions">
        <button id="openDeck" class="challenge-btn beta-splash-go">Challenges</button>
        <button id="maybeLater" class="challenge-btn beta-splash-later" type="button">Maybe Later</button>
      </div>''',
        "Maybe Later splash button",
    )

    anchor = '''#openDeck.challenge-btn.beta-splash-go:active{
  transform:translateY(1px)!important;
  box-shadow:0 2px 0 #7c6511!important;
}'''
    extra = '''
.hero.beta-splash .actions{justify-content:flex-start;gap:12px;flex-wrap:nowrap;margin-top:0}
.hero.beta-splash .actions #openDeck,
.hero.beta-splash .actions #maybeLater{
  width:165px!important;
  min-width:0!important;
  max-width:calc((100% - 12px)/2)!important;
  flex:0 1 165px;
}
#maybeLater.challenge-btn.beta-splash-later{
  margin-top:11px!important;
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
}'''
    s = replace_once(s, anchor, anchor + extra, "Maybe Later CSS")

    s = replace_once(
        s,
        '''$("openDeck").onclick=()=>{ document.body.classList.remove("tffc-stats-view"); openAt(0); };
$("deckStatsBtn").onclick=()=>{ openCampaignStatsFromDeck(); };''',
        '''$("openDeck").onclick=()=>{ document.body.classList.remove("tffc-stats-view"); openAt(0); };
$("maybeLater").onclick=(e)=>{
  /* CANDIDATE 13 — same-tab return to the exact Clubfinder Campaign. */
  e.preventDefault();
  e.stopPropagation();
  e.stopImmediatePropagation();
  history.back();
};
$("deckStatsBtn").onclick=()=>{ openCampaignStatsFromDeck(); };''',
        "Maybe Later return handler",
    )

    if s.count('id="maybeLater"') != 1:
        raise RuntimeError("Maybe Later button post-check failed")
    if "#084c61" not in s:
        raise RuntimeError("Maybe Later teal post-check failed")
    if 'id="truthCallSign"' in s:
        raise RuntimeError("Unexpected call-sign change present")
    if 'section class="stats" id="stats"' not in s:
        raise RuntimeError("Unexpected Stats consolidation present")

    check_js_syntax(s)
    CHALLENGES.write_text(s, encoding="utf-8")
    print("Applied Maybe Later splash change only.")


if __name__ == "__main__":
    main()
