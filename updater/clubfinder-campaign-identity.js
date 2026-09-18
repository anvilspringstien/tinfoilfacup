/* TIN_FOIL_CAMPAIGN_IDENTITY_BEGIN */
const TIN_FOIL_COUNTER_CONFIG_URL='./counter-config.json';
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
  let controller=null,timer=null;
  try{
    if(typeof AbortController==='function'){
      controller=new AbortController();
      timer=setTimeout(()=>controller.abort(),2500);
    }
    const opts={method:'POST',mode:'cors',cache:'no-store',keepalive:true};
    if(controller)opts.signal=controller.signal;
    const r=await fetch(endpoint,opts);
    if(!r.ok)return null;
    const j=await r.json();
    return tinFoilNormaliseSearchNumber(j&&j.number);
  }catch(e){
    return null;
  }finally{
    if(timer)clearTimeout(timer);
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
  if(!saved||saved.ended||saved.searchNumber)return;
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
    tinFoilSetCurrentSearchNumber(n);
    tinFoilBackfillChosenCampaignIdentity(n,sequence);
    tinFoilBackfillExistingCampaignIdentity(n,sequence);
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
  // Browsers may restore the previous form value on refresh. A saved Campaign is
  // authoritative here, so always repopulate it and redraw the Campaign.
  input.value=String(saved.postcode).toUpperCase();
  await go(false);
  return true;
}
/* TIN_FOIL_CAMPAIGN_IDENTITY_END */
