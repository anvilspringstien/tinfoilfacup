# Match decision policy

Active results and archived qualifying replays use `updater/match_decisions.py`.
The sporting requirement for a winner never supplies a club identity.

A completed decisive score supplies its winner. A completed level score with an
explicit, participating penalty winner from an accepted competition source is
sufficient. If shoot-out scores are present they must be complete, non-level and
consistent with the named winner. Match scores and shoot-out scores remain
separate. A non-level match score labelled as a penalty decision is quarantined.

Accepted penalty publishers are HTTPS Football Web Pages FA Cup pages and HTTPS
FA Cup competition pages on the FA's site. The current structural result parser
reads FWP replay/round/live pages; this policy also recognises explicit FA
observations supplied to the classifier. Merely recognising an accepted publisher
does not invent a parser for a different page layout. Source URLs are retained.
Different pages of FWP are one publisher, not independent corroboration.
An explicit FA observation can resolve a conflicting secondary report. Otherwise
contradictory observations stay held until a later scan supplies consistent or
independently corroborated evidence. Existing reviewed exceptional dispositions
and historical results are preserved; source corrections do not overwrite them.

Only a verified terminal result clears a pending decision. Missing winner notes,
conflicts and missing due replay coverage retain the affected fixture unchanged.
Other fixtures can publish. Ambiguous fixture mappings, missing canonical
ancestry, invalid source-round pages and downstream candidate integrity failures
still prevent publication.

`pending_match_decisions` in canonical competition data retains fixture identity,
observation date, source URLs, hold reason and first-seen time. Draw promotion
preserves this queue. Subsequent Results scans retry the original round source,
including after later draws have advanced, and clear the hold after a verified
result or already-recorded equivalent. An unavailable archived source leaves its
hold in place and is recorded in diagnostics. Publication remains through the
normal Results/Health CLI workflows and their complete candidate guards.

Every unresolved decision emits a workflow warning on each scan. Competition
Health includes the pending list and shows an amber data-completeness state;
tracked fixture holds do not become a batch-wide publication veto. This does not
claim that GitHub will launch scheduled workflows on time, and does not introduce
an email delivery channel.
