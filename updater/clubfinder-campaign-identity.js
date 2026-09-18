/* TIN_FOIL_CAMPAIGN_IDENTITY_BEGIN */
const TIN_FOIL_COUNTER_CONFIG_URL='./counter-config.json';
const TIN_FOIL_COUNTER_INCREMENT_URL='https://tffac-clubfinder-counter.anvilspringstien.workers.dev/increment';
const TIN_FOIL_CAMPAIGN_IDENTITY_BACKUP_KEY='tffc.clubfinderCampaignIdentity.v1';
const TIN_FOIL_CHALLENGE_BRIDGE_IDENTITY_KEY='tffc.clubfinderCampaign.v1';
let TIN_FOIL_CURRENT_SEARCH_NUMBER=null;
let TIN_FOIL_SEARCH_NUMBER_PROMISE=null;
let TIN_FOIL_SEARCH_SEQUENCE=0;
let TIN_FOIL_COUNTER_ENDPOINT_PROMISE=null;

function tinFoilNormaliseSearchNumber(value){
  const n=Number(value);
  return Number.isSafeInteger(n)&&n>0?n:null;
}
function tinFoilSearchNumberDigits(value){
  const n=tinFoilNormaliseSearchNumber(value);
  return n?String(n).padStart(5,'0'):'';
}
function tinFoilSearchNumberLabel(value){
  const d=tinFoilSearchNumberDigits(value);
  return d?'#'+d:'';
}
function tinFoilCallSignFromSearchNumber(value){
  const d=tinFoilSearchNumberDigits(value);
  return d?'Tango Foxtrot 2 Alpha Charlie '+d:'';
}
function tinFoilSavedCallSign(saved){
  if(!saved)return '';
  return String(saved.callSign||tinFoilCallSignFromSearchNumber(saved.searchNumber)||'');
}
function tinFoilCampaignPostcodeKey(value){
  return String(value||'').toUpperCase().replace(/\s+/g,'');
}
function tinFoilIdentityStorageSnapshot(key){
  try{return JSON.parse(localStorage.getItem(key)||'null')}catch(e){return null}
}
function tinFoilCampaignIdentityCandidateMatches(saved,candidate,source){
  if(!saved||!candidate||norm(saved.originName)!==norm(candidate.originName))return false;
  const a=tinFoilCampaignPostcodeKey(saved.postcode),b=tinFoilCampaignPostcodeKey(candidate.postcode);
  if(a&&b&&a!==b)return false;
  if(source==='backup'&&saved.selectedAt&&candidate.selectedAt&&saved.selectedAt!==candidate.selectedAt)return false;
  if(source==='bridge'&&saved.selectedAt&&candidate.updatedAt){
    const selected=Date.parse(saved.selectedAt),updated=Date.parse(candidate.updatedAt);
    if(Number.isFinite(selected)&&Number.isFinite(updated)&&updated<selected)return false;
  }
  return true;
}
function tinFoilPersistCampaignIdentityBackup(saved){
  const n=saved&&tinFoilNormaliseSearchNumber(saved.searchNumber);
  if(!saved||!n)return;
  try{
    localStorage.setItem(TIN_FOIL_CAMPAIGN_IDENTITY_BACKUP_KEY,JSON.stringify({
      originName:saved.originName||'',
      postcode:saved.postcode||'',
      selectedAt:saved.selectedAt||null,
      searchNumber:n,
      callSign:tinFoilSavedCallSign(saved)
    }));
  }catch(e){}
}
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
    if(!n||!tinFoilCampaignIdentityCandidateMatches(saved,candidate,source))continue;
    const repaired=Object.assign({},saved,{searchNumber:n,callSign:String(candidate.callSign||tinFoilCallSignFromSearchNumber(n))});
    try{localStorage.setItem(JOURNEY_STORAGE_KEY,JSON.stringify(repaired))}catch(e){}
    tinFoilPersistCampaignIdentityBackup(repaired);
    return repaired;
  }
  return saved;
}
function tinFoilClearCampaignIdentityBackup(){
  try{
    localStorage.removeItem(TIN_FOIL_CAMPAIGN_IDENTITY_BACKUP_KEY);
    localStorage.removeItem(TIN_FOIL_CHALLENGE_BRIDGE_IDENTITY_KEY);
  }catch(e){}
}
async function tinFoilCounterIncrementUrl(){
  if(TIN_FOIL_COUNTER_ENDPOINT_PROMISE)return TIN_FOIL_COUNTER_ENDPOINT_PROMISE;
  TIN_FOIL_COUNTER_ENDPOINT_PROMISE=(async()=>{
    // Production has one public, non-secret counter endpoint. Use it directly so
    // search identity issuance cannot be lost to a separate config fetch.
    const direct=String(TIN_FOIL_COUNTER_INCREMENT_URL||'').trim();
    if(direct)return direct;
    try{
      const r=await fetch(TIN_FOIL_COUNTER_CONFIG_URL,{cache:'no-store'});
      if(!r.ok)return '';
      const j=await r.json();
      return String(j&&j.increment_url||'').trim();
    }catch(e){return '';}
  })();
  return TIN_FOIL_COUNTER_ENDPOINT_PROMISE;
}
async function tinFoilIssueSearchNumber(){
  const endpoint=await tinFoilCounterIncrementUrl();
  if(!endpoint)return null;
  try{
    // This is deliberately non-blocking from the user's point of view. Do not
    // impose an arbitrary client timeout: a valid issued number is more useful
    // than abandoning a slow Worker cold start.
    const r=await fetch(endpoint,{method:'POST',mode:'cors',cache:'no-store',keepalive:true});
    if(!r.ok)return null;
    const j=await r.json();
    return tinFoilNormaliseSearchNumber(j&&j.number);
  }catch(e){
    return null;
  }
}
function tinFoilRefreshCampaignIdentityDisplay(){
  if(!document||typeof document.querySelectorAll!=='function')return;
  const saved=loadSavedJourney(),callSign=tinFoilSavedCallSign(saved);
  document.querySelectorAll('[data-tin-foil-campaign-identity]').forEach(el=>{
    el.hidden=!callSign;
    el.textContent=callSign?'Pigeon Call Sign: '+callSign:'';
  });
}
function tinFoilSetCurrentSearchNumber(value){
  TIN_FOIL_CURRENT_SEARCH_NUMBER=tinFoilNormaliseSearchNumber(value);
  if(typeof updateLiveDataBadge==='function')updateLiveDataBadge();
  tinFoilRefreshCampaignIdentityDisplay();
  return TIN_FOIL_CURRENT_SEARCH_NUMBER;
}
function tinFoilCurrentSearchNumber(){
  return tinFoilNormaliseSearchNumber(TIN_FOIL_CURRENT_SEARCH_NUMBER);
}
function tinFoilClearCurrentSearchIdentity(){
  TIN_FOIL_SEARCH_SEQUENCE++;
  TIN_FOIL_CURRENT_SEARCH_NUMBER=null;
  TIN_FOIL_SEARCH_NUMBER_PROMISE=null;
  window.__tinFoilPendingCampaignIdentity=null;
  if(typeof updateLiveDataBadge==='function')updateLiveDataBadge();
}
function tinFoilBackfillChosenCampaignIdentity(number,sequence){
  const n=tinFoilNormaliseSearchNumber(number);
  const pending=window.__tinFoilPendingCampaignIdentity;
  if(!n||!pending||pending.sequence!==sequence||sequence!==TIN_FOIL_SEARCH_SEQUENCE)return;
  const saved=loadSavedJourney();
  if(!saved||norm(saved.originName)!==norm(pending.originName)||saved.selectedAt!==pending.selectedAt||saved.searchNumber)return;
  updateSavedJourney({searchNumber:n,callSign:tinFoilCallSignFromSearchNumber(n)});
  window.__tinFoilPendingCampaignIdentity=null;
  tinFoilRefreshCampaignIdentityDisplay();
}
function tinFoilBackfillExistingCampaignIdentity(number,sequence){
  const n=tinFoilNormaliseSearchNumber(number);
  if(!n||sequence!==TIN_FOIL_SEARCH_SEQUENCE)return;
  const saved=loadSavedJourney();
  // Only a real positive counter value means this Campaign already has an
  // identity. Legacy/null/string placeholders must not block repair.
  if(!saved||saved.ended||tinFoilNormaliseSearchNumber(saved.searchNumber))return;
  const input=document.getElementById('postcode');
  const currentPostcode=tinFoilCampaignPostcodeKey(input&&input.value);
  const savedPostcode=tinFoilCampaignPostcodeKey(saved.postcode);
  // A search may be exploring another postcode while a Campaign remains saved.
  // Only repair the existing Campaign from a search for that Campaign postcode.
  if(currentPostcode&&savedPostcode&&currentPostcode!==savedPostcode)return;
  updateSavedJourney({searchNumber:n,callSign:tinFoilCallSignFromSearchNumber(n)});
  tinFoilRefreshCampaignIdentityDisplay();
}
function tinFoilBeginSearchIdentity(){
  const sequence=++TIN_FOIL_SEARCH_SEQUENCE;
  TIN_FOIL_CURRENT_SEARCH_NUMBER=null;
  window.__tinFoilPendingCampaignIdentity=null;
  if(typeof updateLiveDataBadge==='function')updateLiveDataBadge();
  const p=tinFoilIssueSearchNumber().then(n=>{
    if(sequence!==TIN_FOIL_SEARCH_SEQUENCE)return null;
    // Bind/persist first, then make the number current. The final display
    // refresh therefore reads the repaired Campaign identity, not stale state.
    tinFoilBackfillChosenCampaignIdentity(n,sequence);
    tinFoilBackfillExistingCampaignIdentity(n,sequence);
    tinFoilSetCurrentSearchNumber(n);
    return n;
  }).catch(()=>null);
  TIN_FOIL_SEARCH_NUMBER_PROMISE=p;
  return p;
}
function tinFoilCampaignIdentityForSave(origin,existing){
  const same=existing&&origin&&norm(existing.originName)===norm(origin.name);
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
  };
}
function tinFoilCampaignIdentityHtml(saved){
  if(!saved)return '';
  const callSign=tinFoilSavedCallSign(saved);
  return '<div class="campaign-identity" data-tin-foil-campaign-identity'+(callSign?'':' hidden')+'>'+(callSign?'Pigeon Call Sign: '+esc(callSign):'')+'</div>';
}
async function tinFoilRestoreSavedCampaignOnLoad(){
  const q=new URLSearchParams(window.location.search||'');
  if(q.get('stats')==='1')return false;
  const saved=loadSavedJourney();
  if(!saved||!saved.postcode)return false;
  const input=document.getElementById('postcode');
  if(!input)return false;
  // A refresh is not a new search: restore the Campaign's existing number into
  // the housekeeping badge without touching the counter service.
  const savedNumber=tinFoilNormaliseSearchNumber(saved.searchNumber);
  if(savedNumber)tinFoilSetCurrentSearchNumber(savedNumber);
  // Browsers may restore or clear the form value on refresh. The saved Campaign
  // is authoritative here, so always repopulate it and redraw.
  input.value=String(saved.postcode).toUpperCase();
  await go(false);
  return true;
}
/* TIN_FOIL_CAMPAIGN_IDENTITY_END */
