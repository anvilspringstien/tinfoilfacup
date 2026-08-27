# Tin Foil FA Cup — Geography Review Resolver

Last checked: **27/08/2026, 10:11:59 UTC**

**PROPOSAL ONLY — no canonical ground record is changed by this workflow.**

- 🟢 Current ground/postcode confirmed: **3**
- 🟡 Current source indicates postcode correction: **3**
- 🔴 Conflicting current evidence / manual research: **1**
- ⚪ Geography-review cases checked: **7**

## 🟢 Confirmed current ground/postcode

- **Frickley Athletic FC** — queued: Westfield Lane • WF9 2EQ → current: Westfield Lane • WF9 2EQ — Current club contact information and current NCEL club data agree on Westfield Lane, WF9 2EQ.
  - Evidence: https://www.pitchero.com/clubs/frickleyathletic/contact
  - Evidence: https://ncefl.org.uk/teams/frickleyathletic/
- **Heybridge Swifts FC** — queued: First Call Community Stadium • CM9 8JA → current: Scraley Road Stadium • CM9 8JA — Current/local-authority and 2026 fixture evidence place Heybridge Swifts at Scraley Road, CM9 8JA. Sponsor naming may vary.
  - Evidence: https://www.maldon.gov.uk/publications/uniform/pages/PublicRegister.html
  - Evidence: https://www.halsteadtownfc.com/fixtures/1025
- **Sutton Athletic FC** — queued: Lower Road Ground • BR8 7RZ → current: Lower Road Ground • BR8 7RZ — Current club and SCEFL sources agree on Lower Road, Hextable, BR8 7RZ; sponsor naming varies.
  - Evidence: https://www.suttonathletic.co.uk/contact/
  - Evidence: https://scefl.com/sceflclub-sutton

## 🟡 Correction proposed — do not publish automatically

- **Beaconsfield Town FC** — queued: Holloways Park • HP9 2SF → current: Holloways Park • HP9 2SE — Current club/venue sources consistently use HP9 2SE; the queued HP9 2SF is stale/incorrect.
  - Evidence: https://www.beaconsfieldtownfc.co.uk/a/about-beaconsfield-town-fc-69433.html
  - Evidence: https://www.hollowayspark.co.uk/contact-bookings
- **Bradford (Park Avenue) FC** — queued: Horsfall Community Stadium • BD6 1JQ → current: Horsfall Community Stadium • BD6 2NG — Current Bradford (Park Avenue) material and the associated sports foundation use Cemetery Road, BD6 2NG.
  - Evidence: https://bpafc.com/
  - Evidence: https://register-of-charities.charitycommission.gov.uk/en/charity-search/-/charity-details/5117786/contact-information
- **Wormley Rovers FC** — queued: Wormley Sports Club • EN10 7QF → current: Wormley Sports Club • EN10 7QE — Current Wormley Sports Club pages use Church Lane, EN10 7QE; the queued EN10 7QF is stale/incorrect.
  - Evidence: https://wormleysports.club/
  - Evidence: https://www.broxbourne.gov.uk/downloads/file/4612/indoor-and-outdoor-sports-facilities-strategy-2023-2033

## 🔴 Conflicting evidence — stop and investigate

- **Corby Town FC** — queued: Steel Park • NN17 2AE → current: Steel Park • UNRESOLVED — Current club pages conflict: the stadium information page gives NN17 2AE while the club contact page gives NN17 2FB. Do not promote until resolved.
  - Evidence: https://www.corbytown.co.uk/a/steel-park-49382.html?page=2
  - Evidence: https://www.corbytown.co.uk/contact

## Safety

- This workflow writes only its JSON/report outputs.
- It does not modify `clubfinder.html`, `competition.json`, canonical `GROUNDS`, or the approval ledger.
- A changed postcode is never allowed to inherit old coordinates automatically.
- Any proposed postcode correction must be independently geocoded/validated before later promotion.
- Conflicting evidence remains red rather than being guessed.
