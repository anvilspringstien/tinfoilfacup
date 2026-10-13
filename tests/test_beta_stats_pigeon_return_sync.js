#!/usr/bin/env node
'use strict';
const fs=require('node:fs');
const vm=require('node:vm');
const assert=require('node:assert/strict');
const source=fs.readFileSync('beta/clubfinder-beta.html','utf8');

// Execute the REAL lightweight snapshot and identity-refresh functions, while
// stubbing only browser storage and DOM. No network or Cloudflare counter calls.
function extract(name,next){
  const begin=source.indexOf('function '+name+'(');
  assert(begin>=0,name+' missing from BETA');
  const end=source.indexOf('\nfunction '+next+'(',begin);
  assert(end>begin,name+' boundary changed');
  return source.slice(begin,end);
}
const refresh=extract('tinFoilRefreshCampaignIdentityDisplay','tinFoilSetCurrentSearchNumber');
const restore=extract('tinFoilRestoreClubfinderReturnSnapshot','tinFoilStatsReturnPending');
assert(!/\btinFoilBeginSearchIdentity\b|\bgo\s*\(/.test(refresh+restore),
  'Repainting Pigeon identity must not start a postcode search');
const key='tffc.clubfinderReturnSnapshot.v1';
let writes=0, counterCalls=0;
const callSign='Tango Foxtrot 2 Alpha Charlie 01503';
const campaign={callSign,pigeonName:'Stats Named Me',searchNumber:1503,
 originName:'Heaton Stannington FC',postcode:'NE6 5NL'};
const snapshot={postcode:'NE6 5NL',status:'Campaign ready',
 resultsHtml:'<div class="result"><div class="campaign-identity">Stale Pigeon Name</div><div class="custodian">Atherton Collieries FC</div></div>'};
const nodes={
  results:{innerHTML:'',style:{display:'none'}},
  status:{textContent:''},
  postcode:{value:''},
  globalResetWrap:{style:{display:'none'}}
};
const pigeon={hidden:false,innerHTML:'Before Stats'};
const context={
  document:{
    getElementById:id=>nodes[id]||null,
    querySelectorAll:selector=>selector==='[data-tin-foil-campaign-identity]'?[pigeon]:[]
  },
  sessionStorage:{getItem:k=>k===key?JSON.stringify(snapshot):null},
  loadSavedJourney:()=>campaign,
  tinFoilSavedCallSign:s=>s.callSign,
  tinFoilCampaignIdentityInnerHtml:s=>'Pigeon Call Sign: '+s.callSign+
    ' | Pigeon Name: '+s.pigeonName,
  counterIncrement(){counterCalls++},
  localStorage:{setItem(){writes++}}
};
vm.createContext(context);
vm.runInContext(refresh+'\n'+restore,context,{timeout:2000});
const ok=vm.runInContext('tinFoilRestoreClubfinderReturnSnapshot()',context,{timeout:2000});
assert.equal(ok,true,'Saved Campaign snapshot was not restored');
assert.equal(nodes.results.innerHTML,snapshot.resultsHtml,'Fixture/Campaign HTML was changed');
assert.equal(nodes.results.style.display,'block');
assert.equal(nodes.status.textContent,'Campaign ready');
assert.equal(nodes.postcode.value,'NE6 5NL');
assert.equal(nodes.globalResetWrap.style.display,'block');
assert.equal(pigeon.hidden,false);
assert.match(pigeon.innerHTML,/Stats Named Me/,'The stale Pigeon Name was not refreshed');
assert.match(pigeon.innerHTML,/01503/,'The existing Call Sign was not preserved');
assert.equal(writes,0,'Repaint must not mutate saved Campaign');
assert.equal(counterCalls,0,'Repaint must not increment the counter');
assert.equal(campaign.pigeonName,'Stats Named Me');
campaign.pigeonName='Second Edit';
vm.runInContext('tinFoilRefreshCampaignIdentityDisplay()',context,{timeout:2000});
assert.match(pigeon.innerHTML,/Second Edit/,'Immediate Stats-to-Clubfinder redraw failed');
// A genuinely missing Call Sign still follows the existing fail-closed UI rule.
campaign.callSign='';
vm.runInContext('tinFoilRefreshCampaignIdentityDisplay()',context,{timeout:2000});
assert.equal(pigeon.hidden,true);
console.log('BETA Stats-to-Clubfinder Pigeon Name return and stale snapshot: PASS');
