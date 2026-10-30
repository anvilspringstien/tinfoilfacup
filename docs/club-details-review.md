# Club details for outreach

A direct public link `/?view=club&club=York%20City` opens a read-only club
review in the same phone frame. It consumes the existing published website
audit queue and live canonical competition JSON. Explicit club names/aliases
must identify one row. The existing reviewed First Round Proper website ledger
retains identity/website access after a club leaves the active queue; no fixture
is invented when it has no upcoming match. ambiguous or unknown names show an error.

The page distinguishes club/website from upcoming match venue/postcode, which
can belong to the opponent. It does not infer an entry round from a fixture.
It never creates a Campaign, issues a counter, or reads/writes saved progress.
The qualifying-round starting list and all competition data remain unchanged.

30 October review: today's15 later-club introductions need this direct link.
Already-sent batches04 and05 include21 later clubs (8+13) lacking an accessible
review destination. They are flagged for a short follow-up, not automatically
resent or sent a second introduction.


## Campaign story pass

The same stable club URL now traces original qualifying origins using a generated,
read-only adapter of the production journey engine. The generator copies the
origin list and journey functions verbatim; `--check` detects divergence. It has
no write, storage, counter or Campaign-selection operations. The established
Campaign masters remain unchanged.

A reverse graph of confirmed transfers shortlists candidate origins, then the
unchanged journey engine verifies every one. Computation runs in a module Worker
so details remain usable while the journey loads. The page reads canonical
competition.json afresh, with no fixed First Round Proper assumption.

- Current custodian: show connected origins and their real histories.
- Next opponent: show Campaigns arriving through an actual, definite fixture.
- Previous custodian: retain the club's place in the journey after elimination.
- No connection: show the real Newton Aycliffe example and explicitly conditional
  copy about future draws/results. Never manufacture a fixture or custody.

A club can be connected to several Cups. The current-custodian category takes
precedence, followed by arriving and previous Campaigns. The origin selector
browses the featured category. Unknown clubs retain the existing error state;
journey load failure leaves published club details available.

Tests compare the shortlist against a full authoritative traversal and simulate a
later-round draw, live score, unresolved replay and verified custody transfer.
Browser checks cover York's illustration, a custodian's origin selector, phone
and desktop geometry, preserved saved data and zero counter requests.
