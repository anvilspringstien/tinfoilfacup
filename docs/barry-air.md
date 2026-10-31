# Barry Air

The public Campaign badge opens `beta/barry-air/` in the same origin. It shares
`tinFoilFACupJourney_v7`; no identity or counter request is made. Direct entry
without an active saved Campaign asks the visitor to choose one.

The approved four-frame design is retained. The boarding pass, split-flap board,
map and display panel are projections of the published Campaign, not example
fixtures. The map traces the Campaign in match order from home base through
each ground, with a dashed leg to the next venue. Replays retain separate
flights and repeat visits follow their chronological place in the route. Missing
locations break the line rather than inventing a connection. Walkovers have no physical flight or mileage. Miles Flown uses the exact
public My Stats function, including its fail-closed unknown-location behaviour.

`campaign-adapter.mjs` is generated from the public BETA functions and static
venue tables. No source Campaign function, result, fixture, winner or ground is
patched by Barry Air. After a relevant source-function or venue-table change run:

```
python3 updater/build_barry_air_adapter.py
python3 updater/build_barry_air_adapter.py --check
node tests/barry-air-model.mjs
```

The generated adapter has no Campaign selector or counter mutation functions.
Its source functions and tables are copied, not reimplemented. The model suite
checks all 651 current origins against those unchanged public journeys.

Competition data is fetched canonical-first, with the existing BETA published
fallback. Missing data never falls back to a demonstration Campaign. Venue
geocoding follows the same public Postcodes.io route as My Stats. Missing map
coordinates do not create fictional points or a zero-mile success.

The browser suite checks phone/tablet fits, an Amersham boarding pass, routing,
name edits, navigation and empty/offline states. It intercepts geocoding and
rejects counter requests; synthetic identities are test fixtures only.

Check-in is browser-local and scoped to Campaign identity plus the actual next
fixture. A changed Campaign or fixture does not inherit check-in. Wallet issuance
remains parked. Pigeon-name edits preserve the saved identity and its matching
backup. Another tab changing the saved Campaign reloads the flight view.

Brand artwork is copied from the approved Barry Air design. The static Natural
Earth SVG retains only its basemap; all markers and flight lines are rendered
from the current model. There are no external map scripts or paid services.

## Arrival and mobile zoom

Barry Air uses the same Campaign-scoped introduction dialog as My Campaign,
My Stats and My Challenges. The opt-out is `introDismissed.barry` on the saved
Campaign; only Got It! saves it. Closing leaves both the Campaign and preference
unchanged. A subsequent Campaign gets its own introduction.

The welcome and crest remain anchored while flight data loads. Loading status
is outside the spacing calculation. The visual-viewport resize handler ignores
native pinch zoom, preserving the scrolling room and tablet composition. The
page retains browser zoom; its background has no fixed paint layer.

The map controls zoom around the selected ground. Selecting another ground while
zoomed recentres it; subsequent zoom steps preserve a manually panned view. Drag
the enlarged map with a mouse or one finger, or focus it and use the arrow keys.
Native browser pinch remains available. Fit whole route resets both zoom and pan.
The camera uses SVG screen-coordinate conversion, including the iPad frame scale.
