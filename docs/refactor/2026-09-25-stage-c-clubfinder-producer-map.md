# Stage C — full-file BETA Clubfinder producer audit

**Historical, source-scoped, read-only inventory.** Generated inside the repository with `python3 updater/audit_beta_clubfinder_stage_c.py` from the **complete** BETA Clubfinder, with the large embedded competition-data literal masked while keeping source line numbers. No application file is changed by this audit. Static references and source windows are evidence pointers, **not** a complete JavaScript call graph.

## Exact audited sources

| File | Bytes | SHA-256 |
|---|---:|---|
| `beta/clubfinder-beta.html` | 631,423 | `50d5804cfaef1d0c570579e0e432f0c81d396935ff5b40aab8199e4d1a701a24` |
| `beta/challenges-beta.html` | 116,345 | `7cd1041530213fdf6d97cf5ceed644a4baf8ce8775c854a31636c5c7a58c4087` |

The Deck side already contains the Stage A `applyClubfinderCampaignTruth()` reader, Stage B `renderTrophyCabinet()` helper and their regression tests.

## Producer and downstream function declarations

| Function or expression | First source line | Detected declaration | Source token occurrences |
|---|---:|---|---:|
| `openChallenges` | 2075 | function | 2 |
| `tinFoilChallengeStatsSnapshot` | 1964 | function | 2 |
| `tinFoilCampaignIdentityForSave` | 1758 | function | 2 |
| `tinFoilPersistCampaignIdentityBackup` | 1618 | function | 5 |
| `tinFoilRecoverCampaignIdentity` | 1632 | function | 3 |
| `tinFoilSavePigeonName` | 1593 | function | 2 |
| `tinFoilRestoreClubfinderReturnSnapshot` | 1795 | function | 3 |
| `completedResultVenue` | 839 | reference only | 5 |
| `tinFoilPigeonMilesForStats` | 1932 | function | 3 |
| `buildJourney` | 1095 | reference only | 4 |
| `journeyCertificate` | 2094 | function | 5 |
| `loadSavedJourney` | 1839 | function | 19 |
| `saveJourney` | 1840 | function | 2 |
| `tinFoilSavedPigeonName` | 1580 | function | 8 |
| `tinFoilPigeonNameInputHtml` | 1584 | function | 2 |
| `tinFoilPigeonNameBandHtml` | — | not found | 0 |
| `tinFoilSaveClubfinderReturnSnapshot` | 1780 | function | 2 |

The seven required rows form the existing BETA Clubfinder producer/saved-identity/return-snapshot boundary. Optional support names marked as references are not claimed to have a standalone function.

## Shared browser-storage identifiers

| Storage key | Source occurrences (excluding offline JSON) | First six source lines |
|---|---:|---|
| `tffc.clubfinderCampaign.v1` | 2 | 1554, 1947 |
| `tffc.clubfinderCampaignIdentity.v1` | 2 | 1553, 2313 |
| `tffc.clubfinderReturnSnapshot.v1` | 1 | 1779 |
| `tffc.challengeOrigin` | 3 | 2058, 2058, 2085 |
| `tffc.challengeReturnIndex` | 0 | None |
| `tffc.openStatsOnReturn` | 2 | 1816, 2451 |
| `tffc.challengeDeck.v1` | 1 | 1999 |

### Direct storage operations (filtered to relevant keys/aliases)

| Source line | Operation | Source expression | Resolved literal if simple alias |
|---|---|---|---|
| 1622 | `localStorage.setItem` | `TIN_FOIL_CAMPAIGN_IDENTITY_BACKUP_KEY` | `tffc.clubfinderCampaignIdentity.v1` |
| 1656 | `localStorage.removeItem` | `TIN_FOIL_CAMPAIGN_IDENTITY_BACKUP_KEY` | `tffc.clubfinderCampaignIdentity.v1` |
| 1657 | `localStorage.removeItem` | `TIN_FOIL_CHALLENGE_BRIDGE_IDENTITY_KEY` | `tffc.clubfinderCampaign.v1` |
| 1791 | `sessionStorage.setItem` | `TIN_FOIL_CLUBFINDER_RETURN_SNAPSHOT_KEY` | `tffc.clubfinderReturnSnapshot.v1` |
| 1797 | `sessionStorage.getItem` | `TIN_FOIL_CLUBFINDER_RETURN_SNAPSHOT_KEY` | `tffc.clubfinderReturnSnapshot.v1` |
| 1816 | `sessionStorage.getItem` | `tffc.openStatsOnReturn` | `tffc.openStatsOnReturn` |
| 1999 | `localStorage.getItem` | `tffc.challengeDeck.v1` | `tffc.challengeDeck.v1` |
| 2058 | `sessionStorage.getItem` | `tffc.challengeOrigin` | `tffc.challengeOrigin` |
| 2058 | `sessionStorage.removeItem` | `tffc.challengeOrigin` | `tffc.challengeOrigin` |
| 2080 | `localStorage.setItem` | `TIN_FOIL_CHALLENGE_BRIDGE_KEY` | `tffc.clubfinderCampaign.v1` |
| 2085 | `sessionStorage.setItem` | `tffc.challengeOrigin` | `tffc.challengeOrigin` |
| 2211 | `localStorage.getItem` | `TIN_FOIL_CHALLENGE_BRIDGE_KEY` | `tffc.clubfinderCampaign.v1` |
| 2451 | `sessionStorage.removeItem` | `tffc.openStatsOnReturn` | `tffc.openStatsOnReturn` |

## Critical producer evidence

These are **bounded opening excerpts**, not whole function bodies; inspect the file itself before editing any function.

### `openChallenges` — source line 2075

~~~js
async function openChallenges(origin,prepared=null){
 await tinFoilPaintChallengesPrep();
 let truth;
 try{truth=await (prepared||tinFoilPrepareChallenges(origin));}
 catch(_){tinFoilRemoveChallengesPrep();await tinFoilConfirm('We couldn’t prepare your Challenges. Please try again.');return;}
 localStorage.setItem(TIN_FOIL_CHALLENGE_BRIDGE_KEY,JSON.stringify(truth));
 /* Preserve the fully rendered BETA Campaign before leaving Clubfinder.
    Challenge Stats may replace the current document, but Exit can restore this
    exact Campaign view without another postcode lookup. */
 tinFoilSaveClubfinderReturnSnapshot();
 try{sessionStorage.setItem('tffc.challengeOrigin','clubfinder-beta');}catch(_){}
 // Leave a clean Clubfinder document for browser Back / page-cache restoration.
 // The preparation screen has served its purpose once the bridge is ready.
 tinFoilRemoveChallengesPrep();
~~~

Within the first bounded source window (not a parser-grade AST):

| Evidence string | Present in bounded window? |
|---|---|
| `completedResultVenue` | Not within window |
| `tinFoilPigeonMilesForStats` | Not within window |
| `TIN_FOIL_CHALLENGE_BRIDGE_KEY` | Yes |
| `TIN_FOIL_CLUBFINDER_RETURN_SNAPSHOT_KEY` | Not within window |
| `TIN_FOIL_CAMPAIGN_IDENTITY_BACKUP_KEY` | Not within window |
| `localStorage.setItem` | Yes |
| `sessionStorage.setItem` | Yes |
| `challenges-beta.html` | Yes |
| `pigeonName:` | Not within window |
| `selectedAt:` | Not within window |
| `originName:` | Not within window |
| `statsSnapshot:` | Not within window |
| `pigeonMiles:` | Not within window |
| `tiesPlayed:` | Not within window |


### `tinFoilChallengeStatsSnapshot` — source line 1964

~~~js
function tinFoilChallengeStatsSnapshot(origin,journey,crumbs,saved,pigeonMiles){
  function venueForStats(r){
    const v=completedResultVenue(r);
    return {ground:v.ground||'Venue TBC',postcode:v.postcode||'Postcode TBC'};
  }
  function dateLabel(v){if(!v)return 'Date TBC';const d=new Date(v+'T12:00:00');return Number.isNaN(d.getTime())?v:d.toLocaleDateString('en-GB',{day:'numeric',month:'short',year:'numeric'});}
  const carrier=journey.carrier||origin,clubs=[]; const addClub=n=>{if(n&&!clubs.some(x=>norm(x)===norm(n)))clubs.push(n)};
  addClub(origin.name); let goals=0,homeGames=0,awayGames=0,wins=0,draws=0,defeats=0,pathCarrier=origin.name; const venueKeys=new Set(),history=[];
  for(const cr of crumbs){const r=cr.result||{};addClub(r.home);addClub(r.away);const hs=Number(r.home_score),as=Number(r.away_score);if(Number.isFinite(hs))goals+=hs;if(Number.isFinite(as))goals+=as;const v=venueForStats(r);if(v.ground!==' ...
  addClub(carrier.name); const roundNames=new Set(crumbs.map(x=>String(x.round||((x.result||{}).round)||'FA Cup').replace(/\s+Replay$/i,'')));
  const currentState=competitionState(carrier),next=nextRoundInfo(carrier);let nextUp={round:'Upcoming Round TBC',fixture:'Next fixture TBC',meta:'Date TBC',venue:''};
  if(currentState&&currentState.type==='replay'&&currentState.replay){const rp=currentState.replay,rv=replayVenue(rp);nextUp={round:rp.round||'Replay',fixture:(rp.home||'')+' v '+(rp.away||''),meta:dateLabel(rp.date)+' • '+(rp.kickoff||'Kic ...
  else if(next&&next.knownFixture){const k=next.knownFixture,v=k.venue||{};nextUp={round:next.name||k.round||'Next Round',fixture:(k.home||'')+' v '+(k.away||''),meta:dateLabel(k.date)+' • '+(k.kickoff||'Kick-off TBC'),venue:(v.ground&&v.gr ...
  else if(next){nextUp={round:next.name||'Next Round',fixture:'Draw / fixture TBC',meta:next.date||'Date TBC',venue:''};}
~~~


### `tinFoilCampaignIdentityForSave` — source line 1758

~~~js
function tinFoilCampaignIdentityForSave(origin,existing){
  const same=existing&&origin&&sameClubIdentity(existing.originName,origin.name);
  const existingNumber=same?tinFoilNormaliseSearchNumber(existing.searchNumber):null;
  if(existingNumber)return {searchNumber:existingNumber,callSign:tinFoilSavedCallSign(existing)};
  const current=tinFoilCurrentSearchNumber();
  if(current)return {searchNumber:current,callSign:tinFoilCallSignFromSearchNumber(current)};
  return {searchNumber:null,callSign:''};
}
function tinFoilRegisterPendingCampaignIdentity(saved){
  if(!saved||saved.searchNumber||!TIN_FOIL_SEARCH_NUMBER_PROMISE)return;
  window.__tinFoilPendingCampaignIdentity={
    sequence:TIN_FOIL_SEARCH_SEQUENCE,
    originName:saved.originName,
    selectedAt:saved.selectedAt
~~~


### `tinFoilPersistCampaignIdentityBackup` — source line 1618

~~~js
function tinFoilPersistCampaignIdentityBackup(saved){
  const n=saved&&tinFoilNormaliseSearchNumber(saved.searchNumber);
  if(!saved||!n)return;
  try{
    localStorage.setItem(TIN_FOIL_CAMPAIGN_IDENTITY_BACKUP_KEY,JSON.stringify({
      originName:saved.originName||'',
      postcode:saved.postcode||'',
      selectedAt:saved.selectedAt||null,
      searchNumber:n,
      callSign:tinFoilSavedCallSign(saved),
      pigeonName:tinFoilSavedPigeonName(saved)
    }));
  }catch(e){}
}
~~~


### `tinFoilRecoverCampaignIdentity` — source line 1632

~~~js
function tinFoilRecoverCampaignIdentity(saved){
  if(!saved)return saved;
  const current=tinFoilNormaliseSearchNumber(saved.searchNumber);
  if(current){
    tinFoilPersistCampaignIdentityBackup(saved);
    return saved;
  }
  const candidates=[
    [tinFoilIdentityStorageSnapshot(TIN_FOIL_CAMPAIGN_IDENTITY_BACKUP_KEY),'backup'],
    [tinFoilIdentityStorageSnapshot(TIN_FOIL_CHALLENGE_BRIDGE_IDENTITY_KEY),'bridge']
  ];
  for(const [candidate,source] of candidates){
    if(source==='bridge'&&candidate&&candidate.source!=='Clubfinder v7.6')continue;
    const n=candidate&&tinFoilNormaliseSearchNumber(candidate.searchNumber);
~~~


### `tinFoilSavePigeonName` — source line 1593

~~~js
function tinFoilSavePigeonName(value){
  const saved=loadSavedJourney();
  if(!saved)return '';
  const name=String(value||'').replace(/\s+/g,' ').trim().slice(0,20);
  updateSavedJourney({pigeonName:name});
  tinFoilRefreshCampaignIdentityDisplay();
  return name;
}
function tinFoilCampaignPostcodeKey(value){
  return String(value||'').toUpperCase().replace(/\s+/g,'');
}
function tinFoilIdentityStorageSnapshot(key){
  try{return JSON.parse(localStorage.getItem(key)||'null')}catch(e){return null}
}
~~~


### `tinFoilRestoreClubfinderReturnSnapshot` — source line 1795

~~~js
function tinFoilRestoreClubfinderReturnSnapshot(){
  try{
    const raw=sessionStorage.getItem(TIN_FOIL_CLUBFINDER_RETURN_SNAPSHOT_KEY);
    if(!raw)return false;
    const snapshot=JSON.parse(raw);
    if(!snapshot||!snapshot.resultsHtml)return false;
    const results=document.getElementById('results'),status=document.getElementById('status'),input=document.getElementById('postcode');
    if(!results)return false;
    if(input&&snapshot.postcode)input.value=String(snapshot.postcode).toUpperCase();
    if(status)status.textContent=snapshot.status||'Your Tin Foil FA Cup Campaign. Dates & times may change. Always check before travelling';
    results.innerHTML=snapshot.resultsHtml;
    // Saved identity wins over an older HTML snapshot after a Stats/Challenges edit.
    // Refresh just the pigeon rows; never re-run a postcode search or counter.
    tinFoilRefreshCampaignIdentityDisplay();
~~~

## Cross-page contract and safeguards

- **Producer:** `openChallenges(origin)` owns the direct Deck launch and v1 campaign bridge. The independent actual-Clubfinder VM regression verifies Call Sign, the full 19-character Pigeon Name, stable origin/selection timestamp and search number, canonical calculated mileage, a retained rendered-return snapshot and no additional counter allocation.
- **Consumer:** the Deck's Stage A reader validates the existing Clubfinder source marker, normalises finite progress and falls back to the saved identity only when the current bridge lacks a name and the existing origin/selection rule permits it.
- **Mileage trust:** `completedResultVenue()` and `tinFoilPigeonMilesForStats()` are existing calculation dependencies. Recalculate from resolved historical venues rather than trusting a stale cached counter; continue to include the Petts Wood BR2 8HQ override.
- **Navigation:** preserve the snapshot restoration route and its exact previously rendered campaign. Legacy Stats-tab return belongs to the Deck and remains a regression requirement.
- **Scope:** the audit does not refresh embedded competition JSON, change the simulator, alter v1 localStorage fields, modify production or enable the forthcoming BETA Clubfinder code change.

## Next controlled step

Inspect the bounded `openChallenges` producer code and actual Clubfinder VM assertions together. Extract only duplicated **pure** bridge-field assembly if the full source proves it useful; retain function entry points and the original v1 shape. Make that change in a separate BETA Clubfinder PR behind the independently guarded Stage C workflow. Require the Clubfinder VM/mobile/Petts Wood/Holmesdale/Exmouth/Weston/Thame/conditional-draw tests plus the Deck bridge/Trophy suite and a protected-production/competition diff gate.
