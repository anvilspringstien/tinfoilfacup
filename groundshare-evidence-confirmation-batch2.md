# Tin Foil FA Cup — Groundshare Evidence Confirmation — Batch 2

Last checked: **27/08/2026, 13:04:44 UTC**

**CONFIRMATION ONLY / NO PUBLISH. No canonical ground record or approval ledger is changed.**

- 🟢 Confirmed relationships: **3**
- ➡️ Directed host/tenant relationships: **2**
- ↔️ Confirmed shared-venue relationships without direction: **1**
- 🔴 Rejected / not-current relationships: **2**
- Published canonical records: **0**

## 🟢 Human-confirmed relationships

### #6 — Walthamstow FC ↔ West Essex FC

- Status: **HUMAN_CONFIRMED**
- Relationship type: **CONFIRMED_SHARED_VENUE_UNDIRECTED**
- Ground: **Wadham Lodge Stadium / Wadham Lodge Sports Ground (Match Day Centres)**
- Postcode: **E17 4JP**
- Host/tenant direction: **UNRESOLVED / deliberately not inferred**
- Evidence: Current Essex Senior League club information says West Essex's Senior 1st XI groundshare at Wadham Lodge Stadium, while current FA county directory information places both Walthamstow and West Essex at Wadham Lodge, E17 4JP. West Essex's own ground announcement explicitly described sharing the stadium with Walthamstow. The shared venue is therefore supported, but because the venue is operated separately and the current evidence does not safely establish a landlord/tenant direction between the two clubs, direction remains unresolved.
- Source 1: https://www.essexseniorleague.co.uk/en_US/archive15032-club-info/92007845
- Source 2: https://www.thefa.com/-/media/cfa/essexfa/files/handbook/2025-26/section-3---club-and-competition-directory---men---senior-status.ashx
- Source 3: https://westessexfc.org.uk/news/club-statement-re--ground-announcement

### #7 — Broadfields United FC ↔ Rayners Lane FC

- Status: **HUMAN_CONFIRMED**
- Relationship type: **DIRECTED_HOST_TENANT**
- Ground: **Tithe Farm Sports & Social Club**
- Postcode: **HA2 0XH**
- Host: **Rayners Lane FC**
- Tenant: **Broadfields United FC**
- Evidence: Rayners Lane's current 2026/27 official site states that Broadfields United groundshare at Tithe Farm, and Broadfields United's own club history records the move into a groundshare agreement with Rayners Lane at Tithe Farm. Current venue information also lists both clubs there. This supports Rayners Lane as the host club and Broadfields United as tenant.
- Source 1: https://raynerslanefc.co.uk/
- Source 2: https://www.broadfieldsunitedfc.co.uk/a/club-history-64122.html
- Source 3: https://www.tithefarmclub.com/whats-on/

### #9 — Barwell FC ↔ Hinckley AFC

- Status: **HUMAN_CONFIRMED**
- Relationship type: **DIRECTED_HOST_TENANT**
- Ground: **Kirkby Road**
- Postcode: **LE9 8FQ**
- Host: **Barwell FC**
- Tenant: **Hinckley AFC**
- Evidence: Hinckley AFC's current official ground information says the club plays its home matches at Barwell FC, Kirkby Road, LE9 8FQ. A July 2026 FA Cup announcement explicitly calls Barwell the landlords when explaining a fixture move caused by Barwell also being at home. This establishes Barwell as host and Hinckley AFC as tenant for 2026/27.
- Source 1: https://hinckleyafc.co.uk/first-team/where-are-we/
- Source 2: https://hinckleyafc.co.uk/2026/07/19/friday-night-fa-cup-football-at-kirkby-road/

## 🔴 Human-confirmed not-current relationships

### #8 — Cobham FC ↔ Epsom & Ewell FC

- Status: **HUMAN_REJECTED_NOT_CURRENT**
- Queued postcode: **KT11 1AA**
- Current venue identified by research: **Chalky Lane, Chessington**
- Decision: **Do not approve or promote this queued groundshare relationship.**
- Evidence: The queued Cobham relationship is no longer current. Epsom & Ewell's own history says the club returned to Cobham for 2025/26 but moved again in October 2025 to Chessington & Hook United. Its August 2026 FA Cup match preview identifies Chalky Lane as its 2026/27 home venue. Cobham ↔ Epsom & Ewell must therefore not be approved from the stale shared-postcode candidate.
- Source 1: https://epsomandewellfc.co.uk/club/history/
- Source 2: https://epsomandewellfc.co.uk/2026/08/match-preview-epsom-ewell-vs-chipstead-emirates-f-a-cup-extra-preliminary-round/

### #10 — Belper United FC ↔ Eastwood Community FC

- Status: **HUMAN_REJECTED_NOT_CURRENT**
- Queued postcode: **NG16 3HB**
- Current venue identified by research: **Don Amott Arena, Mickleover**
- Decision: **Do not approve or promote this queued groundshare relationship.**
- Evidence: The queued Eastwood relationship is no longer current. Belper United announced in March 2026 that it would leave Eastwood CFC at the end of the 2025/26 season, ending a three-year groundshare. Belper United's current official site now gives the Don Amott Arena, home of Mickleover FC, as its ground. Eastwood's current site continues to identify Coronation Park as Eastwood's home. Belper United ↔ Eastwood Community must therefore not be approved for 2026/27.
- Source 1: https://belperunited.co.uk/
- Source 2: https://www.eastwoodcfc.co.uk/

## Safety

- Only v7.8.5 Batch 2 records are accepted; pair identity or postcode drift stops the run.
- Only research records classified `CONFIRMED` become `HUMAN_CONFIRMED`.
- Only research records classified `NOT_CURRENT` become `HUMAN_REJECTED_NOT_CURRENT`.
- A directed relationship requires both host and tenant to be explicitly present and to belong to the pair.
- A confirmed shared venue may remain undirected; no host is invented.
- Cobham FC ↔ Epsom & Ewell FC and Belper United FC ↔ Eastwood Community FC are explicitly excluded from later groundshare promotion.
- The replacement/current venues identified for Epsom & Ewell FC and Belper United FC are evidence for a separate current-venue correction/research stage; this confirmation does not publish them.
- This stage does not alter canonical `GROUNDS`, approval ledgers, `clubfinder.html`, or `competition.json`.
