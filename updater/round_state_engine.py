#!/usr/bin/env python3
"""Shared FA Cup match-state classifier.

The key rule is chronology, not source wording or home/away orientation:

* a postponed or abandoned match is unresolved and its later completion is still
  the original tie unless the FA separately awards it;
* a completed draw up to and including Fourth Round Qualifying creates replay
  ancestry;
* only a later observation of that same pair can become a Replay;
* a walkover/award is terminal only when an explicit winner is known;
* Competition Proper draws and qualifying replays must carry an explicit winner
  when level (normally after extra time / penalties).

This module is deliberately source-agnostic. Parsers turn source rows into
observations; this module decides what those observations mean.
"""
import re

REPLAY_ROUNDS = {
    "Extra Preliminary Round",
    "Preliminary Round",
    "First Round Qualifying",
    "Second Round Qualifying",
    "Third Round Qualifying",
    "Fourth Round Qualifying",
}
NON_TERMINAL_STATUSES = {"POSTPONED", "ABANDONED", "SUSPENDED"}
AWARD_STATUSES = {"AWARDED", "WALKOVER"}

TEAM_IDENTITY_ALIASES = {
    "bedfont sports club": "bedfont sports",
    "bournemouth poppies": "bournemouth",
    "atherton lr": "atherton laburnum rovers",
    "irlam": "irlam town",
    "eastwood community": "eastwood",
    "millbrook hampshire": "millbrook",
    "royal wootton bassett town": "royal wootton bassett",
    "sherbourne town": "sherborne town",
    "st helens town": "st helens",
    "sutton united birmingham": "sutton united west midlands",
    "varndeanians": "varndenians",
    "burgess h": "burgess hill town",
    "burgess hill": "burgess hill town",
}


def norm(value):
    value = str(value or "").lower().replace("&", " and ")
    value = re.sub(r"\b(fc|afc|cfc|football club)\b", " ", value)
    value = re.sub(r"[^a-z0-9]+", " ", value).strip()
    return TEAM_IDENTITY_ALIASES.get(value, value)


def compatible(a, b):
    a, b = norm(a), norm(b)
    return bool(a and b and (a == b or a.startswith(b + " ") or b.startswith(a + " ")))


def base_round(name):
    return re.sub(r"\s+Replay$", "", str(name or "").strip(), flags=re.I)


def replay_allowed(round_name):
    return base_round(round_name) in REPLAY_ROUNDS


def pair_key(row):
    return frozenset((norm(row.get("home")), norm(row.get("away"))))


def score_pair(row):
    return row.get("home_score"), row.get("away_score")


def is_draw(row):
    hs, ass = score_pair(row)
    return (
        str(row.get("status") or "").upper().startswith("FT")
        and isinstance(hs, int)
        and isinstance(ass, int)
        and hs == ass
        and not row.get("winner")
    )


def is_terminal(row):
    status = str(row.get("status") or "").upper()
    if status in AWARD_STATUSES:
        return bool(row.get("winner"))
    if not status.startswith("FT"):
        return False
    hs, ass = score_pair(row)
    if not isinstance(hs, int) or not isinstance(ass, int):
        return False
    return hs != ass or bool(row.get("winner"))


def same_result(a, b):
    return (
        pair_key(a) == pair_key(b)
        and str(a.get("date") or "") == str(b.get("date") or "")
        and a.get("home_score") == b.get("home_score")
        and a.get("away_score") == b.get("away_score")
        and norm(a.get("home")) == norm(b.get("home"))
        and norm(a.get("away")) == norm(b.get("away"))
        and norm(a.get("winner")) == norm(b.get("winner"))
        and base_round(a.get("round")) == base_round(b.get("round"))
    )


def unique_history(rows):
    out = []
    for row in rows or []:
        if not isinstance(row, dict) or not row.get("home") or not row.get("away"):
            continue
        if any(same_result(row, existing) for existing in out):
            continue
        out.append(row)
    return out


def _earlier(a, b):
    """True when a is safely earlier than b; blank dates do not prove ancestry."""
    da, db = str(a.get("date") or ""), str(b.get("date") or "")
    return bool(da and db and da < db)


def _winner_from_score(obs):
    hs, ass = score_pair(obs)
    if hs > ass:
        return obs.get("home")
    if ass > hs:
        return obs.get("away")
    return ""


def classify_observation(fixture, observation, history=None):
    """Classify one source observation against one canonical fixture.

    Returns a dictionary with kind in {result,event,duplicate}. Invalid or
    contradictory chronology raises ValueError so callers fail closed.
    """
    if pair_key(fixture) != pair_key(observation):
        raise ValueError("observation does not match canonical fixture pair")

    round_name = base_round(fixture.get("round") or observation.get("round"))
    if not round_name:
        raise ValueError("canonical round is missing")

    status = str(observation.get("status") or "").upper().strip()
    obs = dict(observation)
    obs["round"] = round_name

    if status in NON_TERMINAL_STATUSES:
        obs["status"] = status
        obs["winner"] = ""
        obs["home_score"] = None
        obs["away_score"] = None
        obs["decision"] = (obs.get("decision") or status.lower()).lower()
        return {"kind": "event", "event": obs, "reason": "unresolved-match-state"}

    relevant = [
        row for row in unique_history(history)
        if pair_key(row) == pair_key(fixture) and base_round(row.get("round")) == round_name
    ]

    duplicate_candidate = dict(obs)
    if status.startswith("FT"):
        hs, ass = score_pair(duplicate_candidate)
        if isinstance(hs, int) and isinstance(ass, int) and hs != ass and not duplicate_candidate.get("winner"):
            duplicate_candidate["winner"] = _winner_from_score(duplicate_candidate)
    for previous in relevant:
        candidate = dict(duplicate_candidate)
        candidate["round"] = previous.get("round") or round_name
        if same_result(previous, candidate):
            return {"kind": "duplicate", "result": previous, "reason": "already-recorded"}

    same_date_conflicts = [
        row for row in relevant
        if str(row.get("date") or "")
        and str(row.get("date") or "") == str(obs.get("date") or "")
    ]
    if same_date_conflicts:
        raise ValueError("conflicting observation for a date already recorded for this tie")

    earlier_draws = [
        row for row in relevant
        if base_round(row.get("round")) == round_name
        and not str(row.get("round") or "").lower().endswith(" replay")
        and is_draw(row)
        and _earlier(row, obs)
    ]
    earlier_terminal = [row for row in relevant if is_terminal(row) and _earlier(row, obs)]

    if earlier_terminal:
        raise ValueError("later result observed after tie already had a terminal outcome")

    is_replay = bool(earlier_draws)
    out_round = round_name + " Replay" if is_replay else round_name

    if status in AWARD_STATUSES:
        winner = obs.get("winner") or ""
        if not winner or not any(compatible(winner, side) for side in (obs.get("home"), obs.get("away"))):
            raise ValueError("awarded/walkover observation requires an explicit participating winner")
        obs.update({
            "round": out_round,
            "status": "AWARDED",
            "home_score": None,
            "away_score": None,
            "winner": winner,
            "decision": (obs.get("decision") or "walkover").lower(),
        })
        return {"kind": "result", "result": obs, "reason": "explicit-award"}

    if not status.startswith("FT"):
        raise ValueError(f"unsupported terminal status: {status or 'blank'}")

    hs, ass = score_pair(obs)
    if not isinstance(hs, int) or not isinstance(ass, int):
        raise ValueError("completed result requires integer scores")

    explicit_winner = obs.get("winner") or ""
    score_winner = _winner_from_score(obs)
    if score_winner:
        if explicit_winner and not compatible(explicit_winner, score_winner):
            raise ValueError("explicit winner contradicts decisive scoreline")
        winner = score_winner
        decision = (obs.get("decision") or ("extra-time" if "AET" in status else "")).lower()
    else:
        if explicit_winner:
            if not any(compatible(explicit_winner, side) for side in (obs.get("home"), obs.get("away"))):
                raise ValueError("level result winner is not one of the participating clubs")
            winner = explicit_winner
            decision = (obs.get("decision") or "penalties").lower()
        elif is_replay:
            raise ValueError("level qualifying replay requires explicit extra-time/penalty winner")
        elif replay_allowed(round_name):
            winner = ""
            decision = "draw-replay"
        else:
            raise ValueError("level Competition Proper match requires explicit extra-time/penalty winner")

    obs.update({
        "round": out_round,
        "status": status,
        "winner": winner,
        "decision": decision,
    })
    return {"kind": "result", "result": obs, "reason": "chronology-classified"}
