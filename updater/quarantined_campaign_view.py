#!/usr/bin/env python3
"""Read-only UX contract for campaigns with an unresolved quarantined result.

Never infer a winner, custodian, fixture, ground or additional Pigeon Miles
from an unverified result. The existing verified snapshot remains authoritative.
"""
import copy


def campaign_view(verified_snapshot, quarantine=None):
    view = copy.deepcopy(verified_snapshot)
    if quarantine is None:
        view["verification_notice"] = None
        return view
    view["verification_notice"] = {
        "status": "awaiting_verification",
        "title": "Result awaiting verification",
        "message": ("We've found conflicting match information and are checking "
                    "independent sources. Your campaign will update automatically "
                    "once the result is verified."),
        "fixture": {
            "home": quarantine["home"], "away": quarantine["away"],
            "date": quarantine.get("date"), "round": quarantine.get("round"),
        },
        "next_round": "Known conditional draw, if available; advancing club not confirmed",
    }
    # Verified history, current custodian and all statistics are intentionally
    # copied unchanged; UI must never treat a disputed winner as custodian.
    return view
