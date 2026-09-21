from pathlib import Path
import json
import re
import unittest

BETA = Path("beta/clubfinder-beta.html")
COMPETITION = Path("competition.json")


def canon(name):
    value = str(name or "").lower().replace("&", " and ")
    value = re.sub(r"\b(association football club|football club)\b", " ", value)
    value = re.sub(r"\b(fc|afc|cfc)\b", " ", value)
    value = re.sub(r"[^a-z0-9]+", " ", value).strip()
    return re.sub(r"\s+", " ", value)


def draw_identity_compatible(a, b):
    ak, bk = canon(a), canon(b)
    if not ak or not bk:
        return False
    if ak == bk or ak.startswith(bk + " ") or bk.startswith(ak + " "):
        return True
    at, bt = ak.split(), bk.split()
    if at[0] != bt[0]:
        return False
    a_tail = "".join(at[1:])
    b_tail = "".join(bt[1:])
    a_initials = "".join(x[0] for x in at[1:])
    b_initials = "".join(x[0] for x in bt[1:])
    return bool(a_tail and b_tail and (a_tail == b_initials or b_tail == a_initials))


class BetaReplayConditionalDrawRegression(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = BETA.read_text(encoding="utf-8")
        cls.data = json.loads(COMPETITION.read_text(encoding="utf-8"))

    def test_replay_state_keeps_next_round_info(self):
        self.assertIn(
            "next:nextRoundInfo(club,true)",
            self.html,
        )
        self.assertIn(
            "Replay details TBC'+nextProgressHtml(club,s.next)",
            self.html,
        )

    def test_conditional_draw_lookup_is_present(self):
        self.assertIn("function liveConditionalFixtureForClub(name)", self.html)
        self.assertIn("aTail===bInitials||bTail===aInitials", self.html)

    def test_weston_sm_matches_full_club_name(self):
        self.assertTrue(draw_identity_compatible("Weston SM", "Weston Super Mare FC"))

    def test_weston_has_one_third_qualifying_conditional_slot(self):
        seen = set()
        matches = []
        for fixture in (self.data.get("fixtures") or {}).values():
            sig = (
                fixture.get("round"),
                fixture.get("home"),
                fixture.get("away"),
                fixture.get("date"),
                fixture.get("kickoff"),
            )
            if sig in seen:
                continue
            seen.add(sig)
            alternatives = re.split(r"\s+or\s+", str(fixture.get("home") or ""), flags=re.I)
            alternatives += re.split(r"\s+or\s+", str(fixture.get("away") or ""), flags=re.I)
            if any(draw_identity_compatible(x, "Weston Super Mare FC") for x in alternatives):
                matches.append(fixture)

        self.assertEqual(len(matches), 1)
        fixture = matches[0]
        self.assertEqual(fixture.get("round"), "Third Round Qualifying")
        self.assertEqual(fixture.get("date"), "2026-10-03")
        self.assertTrue(fixture.get("conditional"))
        self.assertIn("Wimborne", fixture.get("away", ""))


if __name__ == "__main__":
    unittest.main()
