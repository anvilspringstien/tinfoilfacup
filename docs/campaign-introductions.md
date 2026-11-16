# Campaign navigation introductions

My Campaign, My Stats and My Challenges share a 420px-wide, viewport-capped
popup with the same Got It! control and “Don’t show this again this Campaign”
checkbox. Preferences live in the saved journey's introDismissed object, so the
existing Keep handover transfers them with the Campaign. Close/Escape/outside
cancels without saving a checkbox or navigating. Confirming saves only that
button's preference; replacing the Campaign starts fresh.

Stats prepares the canonical report and decoded artwork while its introduction
is visible. Got It! opens the existing Stats preparation window synchronously
within the user gesture and awaits that prepared document. Challenges prepares
the canonical bridge without writing it, and warms the Deck HTML and a bounded
set of relevant artwork. Confirming retains the existing preparation counter,
commits the bridge/snapshot and navigates. Failure does not commit partial
progress; another Campaign replacing the saved journey blocks stale confirmation.

A native browser-history return from Challenges leaves its origin marker in the
same tab. Clubfinder's pageshow handler consumes this marker and uses the shared
Frame 2 scroll owner, including BFCache restoration. Exit and Stats return routes
continue to use their deterministic snapshots. No Challenge Deck code, Splash
layout, competition data, mileage calculation or result-ingestion logic changes.

Tests run real preparation and navigation in Chromium and WebKit, including
controlled cold-load gates, cancellation, opt-outs, counters, new-Campaign
behaviour, history/BFCache restoration and popup geometry. Physical iPhone swipe
and first-visit popup acceptance remain the final device checks.
