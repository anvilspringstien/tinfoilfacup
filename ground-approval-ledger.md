# Tin Foil FA Cup — Ground Approval Ledger

Mode: **PUBLISH**

- 🟢 Exception-cleared candidates seen: **2**
- Eligible for promotion: **2**
- Skipped: **0**
- 🟡 Bishop's Cleeve corrected to human-decision queue: **Yes**

## Promotion candidates

- **AFC Mansfield** — Forest Town Welfare • NG19 0EE • `53.151566, -1.161345`
- **Heanor Town FC** — The Town Ground • DE75 7EN • `53.011586, -1.356027`

## Approval ledger

The ledger is intentionally conservative. It contains no invented groundshare approvals. Future explicit approvals can be stored in `known_groundshares` so Ground Health can stop repeatedly flagging known arrangements.

## Safety

- Existing canonical GROUNDS records are never overwritten.
- Only v7.6.8 green exception-cleared candidates can be promoted by this workflow.
- Bishop's Cleeve is reclassified only; it is not promoted.
- `competition.json` is untouched.
