# Stage C — full-file BETA Clubfinder producer audit

**Historical, source-scoped, read-only inventory.** Generated inside the repository with `python3 updater/audit_beta_clubfinder_stage_c.py` from the **complete** BETA Clubfinder, with the large embedded competition-data literal masked while keeping source line numbers. No application file is changed by this audit. Static references and source windows are evidence pointers, **not** a complete JavaScript call graph.

## Exact audited sources

| File | Bytes | SHA-256 |
|---|---:|---|
| `beta/clubfinder-beta.html` | 581,770 | `6b8e7e4956322c71cb9b571d050d5c130e7c76f868b312bc5d94f87bf9be16cb` |
| `beta/challenges-beta.html` | 96,406 | `3546154e64c15d93c9eb164018e0ea29efda03b4c23e248c0d27e289a15fdb0b` |

The Deck side already contains the Stage A `applyClubfinderCampaignTruth()` reader, Stage B `renderTrophyCabinet()` helper and their regression tests.

## Producer and downstream function declarations

| Function or expression | First source line | Detected declaration | Source token occurrences |
|---|---:|---|---:|
| `openChallenges` | 1668 | function | 3 |
| `tinFoilChallengeStatsSnapshot` | 1574 | function | 2 |
| `tinFoilCampaignIdentityForSave` | 1401 | function | 2 |
| `tinFoilPersistCampaignIdentityBackup` | 1261 | function | 5 |
| `tinFoilRecoverCampaignIdentity` | 1275 | function | 3 |
| `tinFoilSavePigeonName` | 1236 | function | 2 |
| `tinFoilRestoreClubfinderReturnSnapshot` | 1438 | function | 2 |
| `completedResultVenue` | 513 | reference only | 5 |
| `tinFoilPigeonMilesForStats` | 1542 | function | 3 |
| `buildJourney` | 769 | reference only | 4 |
| `journeyCertificate` | 1689 | function | 7 |
| `loadSavedJourney` | 1477 | function | 18 |
| `saveJourney` | 1478 | function | 2 |
| `tinFoilSavedPigeonName` | 1223 | function | 8 |
| `tinFoilPigeonNameInputHtml` | 1227 | function | 2 |
| `tinFoilPigeonNameBandHtml` | — | not found | 0 |
| `tinFoilSaveClubfinderReturnSnapshot` | 1423 | function | 2 |

The seven required rows form the existing BETA Clubfinder producer/saved-identity/return-snapshot boundary. Optional support names marked as references are not claimed to have a standalone function.

## Shared browser-storage identifiers

| Storage key | Source occurrences (excluding offline JSON) | First six source lines |
|---|---:|---|
| `tffc.clubfinderCampaign.v1` | 2 | 1197, 1557 |
| `tffc.clubfinderCampaignIdentity.v1` | 1 | 1196 |
| `tffc.clubfinderReturnSnapshot.v1` | 1 | 1422 |
| `tffc.challengeOrigin` | 1 | 1685 |
| `tffc.challengeReturnIndex` | 0 | None |
| `tffc.openStatsOnReturn` | 2 | 1456, 2004 |
| `tffc.challengeDeck.v1` | 1 | 1609 |

### Direct storage operations (filtered to relevant keys/aliases)

| Source line | Operation | Source expression | Resolved literal if simple alias |
|---|---|---|---|
| 1265 | `localStorage.setItem` | `TIN_FOIL_CAMPAIGN_IDENTITY_BACKUP_KEY` | `tffc.clubfinderCampaignIdentity.v1` |
| 1299 | `localStorage.removeItem` | `TIN_FOIL_CAMPAIGN_IDENTITY_BACKUP_KEY` | `tffc.clubfinderCampaignIdentity.v1` |
| 1300 | `localStorage.removeItem` | `TIN_FOIL_CHALLENGE_BRIDGE_IDENTITY_KEY` | `tffc.clubfinderCampaign.v1` |
| 1434 | `sessionStorage.setItem` | `TIN_FOIL_CLUBFINDER_RETURN_SNAPSHOT_KEY` | `tffc.clubfinderReturnSnapshot.v1` |
| 1440 | `sessionStorage.getItem` | `TIN_FOIL_CLUBFINDER_RETURN_SNAPSHOT_KEY` | `tffc.clubfinderReturnSnapshot.v1` |
| 1456 | `sessionStorage.getItem` | `tffc.openStatsOnReturn` | `tffc.openStatsOnReturn` |
| 1609 | `localStorage.getItem` | `tffc.challengeDeck.v1` | `tffc.challengeDeck.v1` |
| 1680 | `localStorage.setItem` | `TIN_FOIL_CHALLENGE_BRIDGE_KEY` | `tffc.clubfinderCampaign.v1` |
| 1685 | `sessionStorage.setItem` | `tffc.challengeOrigin` | `tffc.challengeOrigin` |
| 1799 | `localStorage.getItem` | `TIN_FOIL_CHALLENGE_BRIDGE_KEY` | `tffc.clubfinderCampaign.v1` |
| 2004 | `sessionStorage.removeItem` | `tffc.openStatsOnReturn` | `tffc.openStatsOnReturn` |

## Critical producer evidence

These are **bounded opening excerpts**, not whole function bodies; inspect the file itself before editing any function.

### `openChallenges` — source line 1668

~~~js
async function openChallenges(origin){
 await tinFoilPaintChallengesPrep();
 const journey=buildJourney(origin),crumbs=journey.breadcrumbs||[],saved=loadSavedJourney();
 let away=0,pathCarrier=origin.name;
 for(const cr of crumbs){const r=cr.result||{};if(norm(r.away||'')===norm(pathCarrier))away++;const hs=Number(r.home_score),as=Number(r.away_score);if(Number.isFinite(hs)&&Number.isFinite(as)&&hs!==as)pathCarrier=hs>as?r.home:r.away;}
 function venueForChallenge(r){return completedResultVenue(r);}
 const pm=await tinFoilPigeonMilesForStats(crumbs,saved&&saved.postcode,venueForChallenge);
 let ri=0;crumbs.forEach(cr=>ri=Math.max(ri,tinFoilChallengeRoundIndex((cr.result||{}).round)));
 const texts=[journey.round,journey.nextRound,journey.fixture&&journey.fixture.round,journey.next&&journey.next.round];texts.forEach(x=>ri=Math.max(ri,tinFoilChallengeRoundIndex(x)));
 const verifiedMiles=Number.isFinite(pm.miles)?pm.miles:0;
 const statsSnapshot=tinFoilChallengeStatsSnapshot(origin,journey,crumbs,saved,verifiedMiles);
 const truth=tinFoilBuildChallengeBridgeRecord(origin,journey,crumbs,saved,{awayTies:away,pigeonMiles:verifiedMiles,campaignRound:ri},statsSnapshot,new Date().toISOString());
 localStorage.setItem(TIN_FOIL_CHALLENGE_BRIDGE_KEY,JSON.stringify(truth));
 /* Preserve the fully rendered BETA Campaign before leaving Clubfinder.
~~~

Within the first bounded source window (not a parser-grade AST):

| Evidence string | Present in bounded window? |
|---|---|
| `completedResultVenue` | Yes |
| `tinFoilPigeonMilesForStats` | Yes |
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
| `pigeonMiles:` | Yes |
| `tiesPlayed:` | Not within window |


### `tinFoilChallengeStatsSnapshot` — source line 1574

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


### `tinFoilCampaignIdentityForSave` — source line 1401

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


### `tinFoilPersistCampaignIdentityBackup` — source line 1261

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


### `tinFoilRecoverCampaignIdentity` — source line 1275

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


### `tinFoilSavePigeonName` — source line 1236

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


### `tinFoilRestoreClubfinderReturnSnapshot` — source line 1438

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
    results.style.display='block';
    const gr=document.getElementById('globalResetWrap');if(gr)gr.style.display='block';
    requestAnimationFrame(()=>{try{window.scrollTo(0,Math.max(0,Number(snapshot.scrollY)||0))}catch(e){}});
~~~

## Cross-page contract and safeguards

- **Producer:** `openChallenges(origin)` owns the direct Deck launch and v1 campaign bridge. The independent actual-Clubfinder VM regression verifies Call Sign, the full 19-character Pigeon Name, stable origin/selection timestamp and search number, canonical calculated mileage, a retained rendered-return snapshot and no additional counter allocation.
- **Consumer:** the Deck's Stage A reader validates the existing Clubfinder source marker, normalises finite progress and falls back to the saved identity only when the current bridge lacks a name and the existing origin/selection rule permits it.
- **Mileage trust:** `completedResultVenue()` and `tinFoilPigeonMilesForStats()` are existing calculation dependencies. Recalculate from resolved historical venues rather than trusting a stale cached counter; continue to include the Petts Wood BR2 8HQ override.
- **Navigation:** preserve the snapshot restoration route and its exact previously rendered campaign. Legacy Stats-tab return belongs to the Deck and remains a regression requirement.
- **Scope:** the audit does not refresh embedded competition JSON, change the simulator, alter v1 localStorage fields, modify production or enable the forthcoming BETA Clubfinder code change.

## Next controlled step

Inspect the bounded `openChallenges` producer code and actual Clubfinder VM assertions together. Extract only duplicated **pure** bridge-field assembly if the full source proves it useful; retain function entry points and the original v1 shape. Make that change in a separate BETA Clubfinder PR behind the independently guarded Stage C workflow. Require the Clubfinder VM/mobile/Petts Wood/Holmesdale/Exmouth/Weston/Thame/conditional-draw tests plus the Deck bridge/Trophy suite and a protected-production/competition diff gate.
