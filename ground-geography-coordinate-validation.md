# Tin Foil FA Cup — Geography Coordinate Validation

Last checked: **27/08/2026, 10:19:11 UTC**

**VALIDATION ONLY. No canonical ground data is changed.**

- 🟢 Existing candidate coordinates validated: **3**
- 🟢 Corrected postcode coordinates validated: **3**
- 🔴 Held for genuine research: **1**
- 🟡 Lookup/review failures: **0**
- ⚪ Cases processed: **7**

- 🟢 **Beaconsfield Town FC** — Holloways Park • HP9 2SE • postcode centroid `51.587894, -0.628189` — Corrected postcode independently resolves. Fresh postcode coordinates proposed; old coordinates are not inherited.
- 🟢 **Bradford (Park Avenue) FC** — Horsfall Community Stadium • BD6 2NG • postcode centroid `53.758419, -1.777899` — Corrected postcode independently resolves. Fresh postcode coordinates proposed; old coordinates are not inherited.
- 🔴 **Corby Town FC** — Steel Park • UNRESOLVED — Conflicting current postcode evidence remains unresolved; no postcode selected and no coordinates promoted.
- 🟢 **Frickley Athletic FC** — Westfield Lane • WF9 2EQ • postcode centroid `53.590463, -1.294087` — Current postcode independently resolves and the existing candidate was already within the <=2 km review envelope.
- 🟢 **Heybridge Swifts FC** — Scraley Road Stadium • CM9 8JA • postcode centroid `51.749012, 0.708251` — Current postcode independently resolves and the existing candidate was already within the <=2 km review envelope.
- 🟢 **Sutton Athletic FC** — Lower Road Ground • BR8 7RZ • postcode centroid `51.412151, 0.186822` — Current postcode independently resolves and the existing candidate was already within the <=2 km review envelope.
- 🟢 **Wormley Rovers FC** — Wormley Sports Club • EN10 7QE • postcode centroid `51.734387, -0.03781` — Corrected postcode independently resolves. Fresh postcode coordinates proposed; old coordinates are not inherited.

## Safety

- `clubfinder.html`, `competition.json`, canonical `GROUNDS`, and approval ledgers are untouched.
- Corrected postcodes never inherit coordinates from the superseded postcode.
- Postcodes are independently resolved at runtime through Postcodes.io.
- Corby Town remains held: this validator cannot choose between conflicting current postcodes.
- Any API failure remains yellow/red; it is never converted into an approval.
