# Stage C — full-file BETA Clubfinder producer audit

**Historical, source-scoped, read-only inventory.** Generated inside the repository with `python3 updater/audit_beta_clubfinder_stage_c.py` from the **complete** BETA Clubfinder, with the large embedded competition-data literal masked while keeping source line numbers. No application file is changed by this audit. Static references and source windows are evidence pointers, **not** a complete JavaScript call graph.

## Exact audited sources

| File | Bytes | SHA-256 |
|---|---:|---|
| `beta/clubfinder-beta.html` | 4,616,151 | `aef5737e7a54e66b9754c11c2796ea2586f5f70c2d4239cba9d8767d70dfb858` |
| `beta/challenges-beta.html` | 82,344 | `061dea095343da1380e71b3a517b0930af1c25035b123e71bf608566163e8d0a` |

The Deck side already contains the Stage A `applyClubfinderCampaignTruth()` reader, Stage B `renderTrophyCabinet()` helper and their regression tests.

## Producer and downstream function declarations

| Function or expression | First source line | Detected declaration | Source token occurrences |
|---|---:|---|---:|
| `openChallenges` | 1520 | function | 2 |
| `tinFoilChallengeStatsSnapshot` | 1503 | function | 2 |
| `tinFoilCampaignIdentityForSave` | 1330 | function | 2 |
| `tinFoilPersistCampaignIdentityBackup` | 1190 | function | 5 |
| `tinFoilRecoverCampaignIdentity` | 1204 | function | 3 |
| `tinFoilSavePigeonName` | 1165 | function | 2 |
| `tinFoilRestoreClubfinderReturnSnapshot` | 1367 | function | 2 |
| `completedResultVenue` | 485 | reference only | 5 |
| `tinFoilPigeonMilesForStats` | 1471 | function | 3 |
| `buildJourney` | 725 | reference only | 4 |
| `journeyCertificate` | 1539 | function | 4 |
| `loadSavedJourney` | 1406 | function | 16 |
| `saveJourney` | 1407 | function | 2 |
| `tinFoilSavedPigeonName` | 1152 | function | 8 |
| `tinFoilPigeonNameInputHtml` | 1156 | function | 2 |
| `tinFoilPigeonNameBandHtml` | — | not found | 0 |
| `tinFoilSaveClubfinderReturnSnapshot` | 1352 | function | 2 |

The seven required rows form the existing BETA Clubfinder producer/saved-identity/return-snapshot boundary. Optional support names marked as references are not claimed to have a standalone function.

## Shared browser-storage identifiers

| Storage key | Source occurrences (excluding offline JSON) | First six source lines |
|---|---:|---|
| `tffc.clubfinderCampaign.v1` | 2 | 1126, 1486 |
| `tffc.clubfinderCampaignIdentity.v1` | 1 | 1125 |
| `tffc.clubfinderReturnSnapshot.v1` | 1 | 1351 |
| `tffc.challengeOrigin` | 1 | 1535 |
| `tffc.challengeReturnIndex` | 0 | None |
| `tffc.openStatsOnReturn` | 2 | 1385, 1776 |
| `tffc.challengeDeck.v1` | 0 | None |

### Direct storage operations (filtered to relevant keys/aliases)

| Source line | Operation | Source expression | Resolved literal if simple alias |
|---|---|---|---|
| 1194 | `localStorage.setItem` | `TIN_FOIL_CAMPAIGN_IDENTITY_BACKUP_KEY` | `tffc.clubfinderCampaignIdentity.v1` |
| 1228 | `localStorage.removeItem` | `TIN_FOIL_CAMPAIGN_IDENTITY_BACKUP_KEY` | `tffc.clubfinderCampaignIdentity.v1` |
| 1229 | `localStorage.removeItem` | `TIN_FOIL_CHALLENGE_BRIDGE_IDENTITY_KEY` | `tffc.clubfinderCampaign.v1` |
| 1363 | `sessionStorage.setItem` | `TIN_FOIL_CLUBFINDER_RETURN_SNAPSHOT_KEY` | `tffc.clubfinderReturnSnapshot.v1` |
| 1369 | `sessionStorage.getItem` | `TIN_FOIL_CLUBFINDER_RETURN_SNAPSHOT_KEY` | `tffc.clubfinderReturnSnapshot.v1` |
| 1385 | `sessionStorage.getItem` | `tffc.openStatsOnReturn` | `tffc.openStatsOnReturn` |
| 1530 | `localStorage.setItem` | `TIN_FOIL_CHALLENGE_BRIDGE_KEY` | `tffc.clubfinderCampaign.v1` |
| 1535 | `sessionStorage.setItem` | `tffc.challengeOrigin` | `tffc.challengeOrigin` |
| 1776 | `sessionStorage.removeItem` | `tffc.openStatsOnReturn` | `tffc.openStatsOnReturn` |

## Critical producer evidence

These are **bounded opening excerpts**, not whole function bodies; inspect the file itself before editing any function.

### `openChallenges` — source line 1520

~~~js
async function openChallenges(origin){
 const journey=buildJourney(origin),crumbs=journey.breadcrumbs||[],saved=loadSavedJourney();
 let away=0,pathCarrier=origin.name;
 for(const cr of crumbs){const r=cr.result||{};if(norm(r.away||'')===norm(pathCarrier))away++;const hs=Number(r.home_score),as=Number(r.away_score);if(Number.isFinite(hs)&&Number.isFinite(as)&&hs!==as)pathCarrier=hs>as?r.home:r.away;}
 function venueForChallenge(r){return completedResultVenue(r);}
 const pm=await tinFoilPigeonMilesForStats(crumbs,saved&&saved.postcode,venueForChallenge);
 let ri=0;crumbs.forEach(cr=>ri=Math.max(ri,tinFoilChallengeRoundIndex((cr.result||{}).round)));
 const texts=[journey.round,journey.nextRound,journey.fixture&&journey.fixture.round,journey.next&&journey.next.round];texts.forEach(x=>ri=Math.max(ri,tinFoilChallengeRoundIndex(x)));
 const statsSnapshot=tinFoilChallengeStatsSnapshot(origin,journey,crumbs,saved,Number.isFinite(pm.miles)?pm.miles:0);
 const truth={source:'Clubfinder v7.6',originName:origin.name,currentCustodian:(journey.carrier||origin).name,postcode:saved&&saved.postcode||'',selectedAt:saved&&saved.selectedAt||null,searchNumber:saved&&saved.searchNumber||null,callSign: ...
 localStorage.setItem(TIN_FOIL_CHALLENGE_BRIDGE_KEY,JSON.stringify(truth));
 /* Preserve the fully rendered BETA Campaign before leaving Clubfinder.
    Challenge Stats may replace the current document, but Exit can restore this
    exact Campaign view without another postcode lookup. */
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
| `pigeonName:` | Yes |
| `selectedAt:` | Yes |
| `originName:` | Yes |
| `statsSnapshot:` | Not within window |
| `pigeonMiles:` | Yes |
| `tiesPlayed:` | Yes |


### `tinFoilChallengeStatsSnapshot` — source line 1503

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


### `tinFoilCampaignIdentityForSave` — source line 1330

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


### `tinFoilPersistCampaignIdentityBackup` — source line 1190

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


### `tinFoilRecoverCampaignIdentity` — source line 1204

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


### `tinFoilSavePigeonName` — source line 1165

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


### `tinFoilRestoreClubfinderReturnSnapshot` — source line 1367

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
