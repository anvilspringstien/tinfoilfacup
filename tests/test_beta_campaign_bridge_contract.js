#!/usr/bin/env node
'use strict';
// BETA-only contract test: execute the REAL standalone Challenge Deck script
// with independent persistent/session storage for each browsing scenario.
// This is a safety net for future refactors; it does not change app behaviour.
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');

const deckHtml=fs.readFileSync('beta/challenges-beta.html','utf8');
const scripts=[...deckHtml.matchAll(/<script[^>]*>([\s\S]*?)<\/script>/gi)]
  .map(m=>m[1]).join('\n');
assert(scripts.length>20000,'Actual BETA Deck script missing');
new vm.Script(scripts,{filename:'beta/challenges-beta.html'});

const DECK='tffc.challengeDeck.v1';
const BRIDGE='tffc.clubfinderCampaign.v1';
const IDENTITY='tffc.clubfinderCampaignIdentity.v1';
const SELECTED='2026-09-25T09:00:00.000Z';
const CALL='Tango Foxtrot 2 Alpha Charlie 01123';
const LONG_NAME='Pigeon McPigeonface';

function makeNode(){
  const classes=new Set();
  const node={
    style:{},dataset:{},children:[],textContent:'',_innerHTML:'',
    get innerHTML(){return this._innerHTML},
    set innerHTML(html){this._innerHTML=String(html);this.children=[]},
    value:'0',
    options:['Extra Preliminary Round','Preliminary Round','1st Qualifying Round',
      '2nd Qualifying Round','3rd Qualifying Round','4th Qualifying Round',
      'First Round Proper','Second Round Proper','Third Round Proper',
      'Fourth Round Proper','Fifth Round Proper','Quarter Finals',
      'Semi Finals','Final'].map(text=>({textContent:text,text})),
    selectedIndex:0,disabled:false,hidden:false,focus(){this.focused=true},
    classList:{
      add(k){classes.add(k)},remove(k){classes.delete(k)},
      contains(k){return classes.has(k)},
      toggle(k,on){if(on===undefined)on=!classes.has(k);
        if(on)classes.add(k);else classes.delete(k);return on}
    },
    setAttribute(){},removeAttribute(){},addEventListener(){},remove(){},
    querySelector(){return null},querySelectorAll(){return []},
    appendChild(child){this.children.push(child);return child},
    append(...children){this.children.push(...children)},
    replaceChildren(...children){this.children=children}
  };
  return node;
}
function boot(local,session={},query=''){
  const nodes=new Proxy({}, {get(o,k){return o[k]||(o[k]=makeNode())}});
  const listeners={};
  const document={
    body:makeNode(),readyState:'complete',activeElement:null,
    getElementById:id=>nodes[id],createElement:()=>makeNode(),
    querySelector:()=>null,querySelectorAll:()=>[],
    addEventListener(k,cb){(listeners[k]||=[]).push(cb)},
    removeEventListener(){}
  };
  const storage=data=>({
    getItem:k=>Object.hasOwn(data,k)?data[k]:null,
    setItem(k,v){data[k]=String(v)},removeItem:k=>{delete data[k]}
  });
  const location={
    href:'https://example.test/beta/challenges-beta.html'+query,
    pathname:'/beta/challenges-beta.html',hash:'',search:query,
    replace(url){this.href=url}
  };
  const ctx={
    console,document,location,history:{replaceState(_s,_t,path){location.search='';
      location.href=path}},
    localStorage:storage(local),sessionStorage:storage(session),
    navigator:{},URL,URLSearchParams,
    requestAnimationFrame:fn=>fn(),setTimeout:()=>0,clearTimeout(){},
    Image:class{set src(path){this._src=path}},MutationObserver:undefined
  };
  ctx.window=ctx;ctx.globalThis=ctx;
  vm.createContext(ctx);
  vm.runInContext(scripts,ctx,{filename:'beta/challenges-beta.html',timeout:25000});
  return {ctx,nodes,session,local,location,listeners,
    read:expression=>vm.runInContext(expression,ctx)};
}
function baseSave(overrides={}){
  return {version:1,accepted:{'01':true},completed:{'01':{at:'2026-09-19T15:00:00.000Z'}},
    records:{'04':{note:'retain existing trophy records'}},
    tiesPlayed:2,awayTies:1,pigeonMiles:40,campaignRound:0,
    giantKillAchieved:false,campaignStatus:'ACTIVE',...overrides};
}
function truth(overrides={}){
  return {source:'Clubfinder v7.6',originName:'Amersham Town FC',
    currentCustodian:'Eastbourne Borough FC',selectedAt:SELECTED,
    callSign:CALL,pigeonName:LONG_NAME,tiesPlayed:5,awayTies:2,
    pigeonMiles:314,campaignRound:4,ended:false,...overrides};
}
function backup(overrides={}){
  return {originName:'Amersham Town FC',selectedAt:SELECTED,
    searchNumber:1123,callSign:CALL,pigeonName:LONG_NAME,...overrides};
}
function store(deck,bridge,identity){
  return Object.fromEntries([
    [DECK,deck && JSON.stringify(deck)],
    [BRIDGE,bridge && JSON.stringify(bridge)],
    [IDENTITY,identity && JSON.stringify(identity)]
  ].filter(([,v])=>v));
}

// A saved challenge and verified campaign remain connected across Deck visits,
// actual Exit navigation, browser refresh, and a long Pigeon Name.
{
  const local=store(baseSave(),truth(),backup());
  const session={'tffc.challengeOrigin':'clubfinder-beta',otherSession:'preserve me'};
  const first=boot(local,session);
  assert(first.nodes.overlay.classList.contains('open'),'Deck must open directly');
  assert.equal(first.nodes.truthCallSign.textContent,CALL,'Call Sign not bridged');
  assert.equal(first.nodes.truthPigeonName.textContent,LONG_NAME,'Long name not bridged');
  assert.equal(first.nodes.truthPigeonMiles.textContent,'314','Verified miles not bridged');
  assert.equal(first.nodes.truthCampaignRound.textContent,'3rd Qualifying Round','Round not bridged');
  assert.equal(first.read('state.tiesPlayed'),5,'Verified ties must supersede simulator save');
  assert.equal(first.read('state.awayTies'),2,'Verified away ties not bridged');
  assert.equal(first.read('state.completed["01"].at'),'2026-09-19T15:00:00.000Z',
    'Historical earned Trophy completion changed');
  assert.equal(first.read('state.records["04"].note'),'retain existing trophy records',
    'Saved Honour Challenge record changed');
  assert.equal(first.read('Boolean(state.completed["02"])'),true,
    'Verified campaign milestone was not awarded');
  assert.equal(first.nodes.cabinetCount.textContent,'2 / 27',
    'Historical + verified milestone trophies must coexist');
  const savedAfterLaunch=JSON.parse(local[DECK]);
  assert(savedAfterLaunch.completed['01'],'Previously earned trophy was not persisted');
  assert(savedAfterLaunch.completed['02'],'Verified milestone not persisted');

  first.nodes.exitBtn.onclick({preventDefault(){},stopPropagation(){},stopImmediatePropagation(){}});
  assert.equal(first.location.href,'clubfinder-beta.html?from=challenges-exit-v3',
    'Exit must return to the originating BETA Clubfinder route');
  assert.equal(session['tffc.challengeOrigin'],undefined,
    'Exit must consume only the Challenges origin marker');
  assert.equal(session.otherSession,'preserve me','Exit cleared unrelated session data');
  assert.equal(JSON.parse(local[BRIDGE]).pigeonName,LONG_NAME,
    'Exit unexpectedly erased the Clubfinder campaign bridge');
  const refreshed=boot(local,session);
  assert.equal(refreshed.nodes.truthPigeonName.textContent,LONG_NAME,
    'Name lost across exit and Deck refresh');
  assert.equal(refreshed.nodes.truthPigeonMiles.textContent,'314',
    'Mileage lost across exit and Deck refresh');
  assert.equal(refreshed.read('Boolean(state.completed["01"])'),true,
    'Earned trophy lost across exit and Deck refresh');
  assert.equal(refreshed.read('Boolean(state.completed["02"])'),true,
    'Campaign milestone lost across exit and Deck refresh');
  assert.equal(refreshed.read('state.records["04"].note'),
    'retain existing trophy records','Existing records lost on refresh');
}

// A missing Pigeon Name may use the backup only for the SAME origin and
// selection date. The backup must never leak another campaign's identity.
{
  const matching=boot(store(baseSave(),truth({pigeonName:''}),backup()));
  assert.equal(matching.nodes.truthPigeonName.textContent,LONG_NAME,
    'Matching backup did not restore the full Pigeon Name');
  const wrongOrigin=boot(store(baseSave(),truth({pigeonName:''}),
    backup({originName:'Wimborne Town FC',pigeonName:'Wrong Origin'})));
  assert.equal(wrongOrigin.nodes.truthPigeonName.textContent,'—',
    'Different origin pigeon identity leaked into current campaign');
  assert.equal(wrongOrigin.nodes.truthCallSign.textContent,CALL,
    'Different-origin backup replaced current verified Call Sign');
  const wrongSelection=boot(store(baseSave(),truth({pigeonName:''}),
    backup({selectedAt:'2026-09-20T08:00:00.000Z',pigeonName:'Old Campaign'})));
  assert.equal(wrongSelection.nodes.truthPigeonName.textContent,'—',
    'Old selection pigeon identity leaked into new campaign');
  const bridgeWins=boot(store(baseSave(),truth(),
    backup({originName:'Wimborne Town FC',pigeonName:'Wrong Origin'})));
  assert.equal(bridgeWins.nodes.truthPigeonName.textContent,LONG_NAME,
    'Fresh bridge identity must take precedence over stale backup');
}

// Stage A guard: reject non-finite/negative progress while accepting historical
// numeric-string bridges; recover identity without copying an unrelated backup.
{
  const app=boot(store(baseSave(),truth({
    tiesPlayed:'Infinity',awayTies:'-3',pigeonMiles:'1e999',
    campaignRound:'not-a-round',giantKillAchieved:'true',
    callSign:'  Tango Foxtrot 2 Alpha Charlie 01123  ',
    pigeonName:'  Pigeon   McPigeonface  '
  }),backup()));
  for(const key of ['tiesPlayed','awayTies','pigeonMiles','campaignRound'])
    assert.equal(app.read('state.'+key),0,
      'Invalid or negative bridge progress must be normalized: '+key);
  assert.equal(app.read('state.giantKillAchieved'),false,
    'String true must not be trusted as a verified Giant Kill');
  assert.equal(app.nodes.truthCallSign.textContent,CALL,'Call Sign whitespace changed');
  assert.equal(app.nodes.truthPigeonName.textContent,LONG_NAME,
    'Name whitespace collapsed incorrectly or 20-character cap changed');
  assert.equal(app.nodes.truthCampaignRound.textContent,'Extra Preliminary Round',
    'Non-numeric campaign round must render the default');

  const numeric=boot(store(baseSave(),truth({
    tiesPlayed:'5',awayTies:'2',pigeonMiles:'314.4',campaignRound:'4'
  }),backup()));
  assert.equal(numeric.read('state.tiesPlayed'),5,'Numeric-string tie count not accepted');
  assert.equal(numeric.read('state.awayTies'),2,'Numeric-string away count not accepted');
  assert.equal(numeric.read('state.pigeonMiles'),314.4,
    'Finite decimal mileage must retain original verified precision');
  assert.equal(numeric.read('state.campaignRound'),4,
    'Numeric-string campaign round not accepted');

  const noBackup=boot(store(baseSave(),truth({pigeonName:'',callSign:''})));
  assert.equal(noBackup.nodes.truthPigeonName.textContent,'—',
    'Absent identity backup should not invent a Pigeon Name');
  assert.equal(noBackup.nodes.truthCallSign.textContent,'—',
    'Absent identity backup should not invent a Call Sign');
  const malformedBackup=store(baseSave(),truth({pigeonName:'',callSign:''}));
  malformedBackup[IDENTITY]='{malformed json';
  const bad=boot(malformedBackup);
  assert.equal(bad.nodes.truthPigeonName.textContent,'—',
    'Malformed identity backup should not crash or leak another Pigeon Name');

  const oldUndated=boot(store(baseSave(),
    truth({pigeonName:'',selectedAt:undefined}),backup()));
  assert.equal(oldUndated.nodes.truthPigeonName.textContent,LONG_NAME,
    'Previously supported undated matching-origin backup was rejected');
  const undatedMismatch=boot(store(baseSave(),
    truth({pigeonName:'',selectedAt:undefined}),
    backup({originName:'Wimborne Town FC',pigeonName:'Other Pigeon'})));
  assert.equal(undatedMismatch.nodes.truthPigeonName.textContent,'—',
    'Missing date must not allow a different-origin identity to leak');
}

// A legacy prototype save is MIGRATED in memory, not treated as an empty
// cabinet; new saves must use the current v1 tiesPlayed field.
{
  const old=baseSave({journeyTies:3});
  delete old.tiesPlayed;delete old.awayTies;delete old.pigeonMiles;
  delete old.campaignRound;delete old.records;delete old.campaignStatus;
  const local=store(old);
  const app=boot(local);
  assert.equal(app.read('state.tiesPlayed'),3,'Legacy journeyTies migration lost');
  assert.equal(app.read('state.journeyTies'),undefined,'Legacy counter was not retired');
  assert.equal(app.read('state.awayTies'),0,'Missing away ties must default to zero');
  assert.equal(app.read('state.pigeonMiles'),0,'Missing mileage must default to zero');
  assert.equal(app.read('state.campaignRound'),0,'Missing round must default to zero');
  assert.equal(app.read('state.campaignStatus'),'ACTIVE','Legacy campaign status not migrated');
  assert.equal(app.read('Boolean(state.completed["01"])'),true,'Legacy trophy erased');
  app.read('save()');
  const converted=JSON.parse(local[DECK]);
  assert.equal(converted.tiesPlayed,3,'Legacy tie count not saved in v1 format');
  assert(!Object.hasOwn(converted,'journeyTies'),'Obsolete field persisted after migration');
  assert(converted.completed['01'],'Legacy trophy erased during migration');
}

// Invalid, foreign or malformed bridge data cannot overwrite a saved campaign.
{
  const oldSave=baseSave({tiesPlayed:3,pigeonMiles:75});
  for(const invalid of [
    JSON.stringify({source:'unknown',tiesPlayed:999,pigeonMiles:9999}),
    '{this is not JSON'
  ]){
    const local=store(oldSave);
    local[BRIDGE]=invalid;
    const app=boot(local);
    assert.equal(app.read('state.tiesPlayed'),3,'Invalid bridge overwrote saved ties');
    assert.equal(app.read('state.pigeonMiles'),75,'Invalid bridge overwrote saved mileage');
    assert.equal(app.read('Boolean(state.completed["01"])'),true,
      'Invalid bridge erased earned trophy');
    assert.equal(app.nodes.truthPigeonName.textContent,'—',
      'Invalid bridge invented a campaign identity');
  }
}

// Ended campaign truth disables the prototype simulator without losing awards.
{
  const local=store(baseSave(),truth({ended:true}),backup());
  const app=boot(local);
  assert.equal(app.read('state.campaignStatus'),'ENDED','Ended campaign not applied');
  assert.equal(app.nodes.addTie.disabled,true,'Ended campaign can still play a tie');
  assert.equal(app.nodes.addPigeonMiles.disabled,true,'Ended campaign can still simulate mileage');
  const ties=app.read('state.tiesPlayed');
  app.nodes.addTie.onclick();
  assert.equal(app.read('state.tiesPlayed'),ties,'Ended campaign progressed through simulator');
  assert.equal(app.read('Boolean(state.completed["01"])'),true,
    'Ending a campaign wiped its earned trophy');
}

// Old already-open Stats tabs remain usable, without new Challenges Stats.
{
  const local=store(baseSave(),truth(),backup());
  const session={'tffc.challengeReturnIndex':'4',unrelated:'keep'};
  const app=boot(local,session,'?from=stats-return-v2');
  assert.equal(app.read('index'),4,'Old Stats-tab selected Deck mat was not restored');
  assert.equal(session['tffc.challengeReturnIndex'],undefined,
    'Stats return token was not consumed');
  assert.equal(session.unrelated,'keep','Stats return erased unrelated session state');
  assert.equal(app.location.search,'','Obsolete Stats query should be cleared');
  const escape=app.listeners.keydown.find(fn=>fn.toString().includes('Escape'));
  assert(escape,'Escape navigation handler missing');
  escape({key:'Escape',preventDefault(){}});
  assert.equal(app.location.href,'clubfinder-beta.html?from=challenges-exit-v3',
    'Legacy Stats-return Escape must return to BETA Clubfinder');
  const outOfRange=boot(store(baseSave()),{'tffc.challengeReturnIndex':'999'},
    '?from=stats-return-v2');
  assert.equal(outOfRange.read('index'),outOfRange.read('CHALLENGES.length-1'),
    'Out-of-range old Stats index was not bounded');
  const normal=boot(store(baseSave()),{'tffc.challengeReturnIndex':'4'});
  assert.equal(normal.read('index'),0,
    'Ordinary direct entry must not consume an unrelated stale Stats token');
}

// Stage B display contract: the active renderer keeps three independent views
// in sync (campaign truth, BETA simulator and the live earned Trophy Cabinet).
// Run against the original renderer BEFORE changing its implementation.
async function testDisplayAndReset(){
  for(const id of ['tieCount','awayTieCount','campaignRound','truthCallSign',
    'truthPigeonName','truthPigeonMiles','truthCampaignRound','campaignStatus',
    'deckCabinet','cabinetCount','addTie','addAwayTie','addPigeonMiles',
    'simulateGiantKill','reset']){
    assert(deckHtml.includes('id="'+id+'"'),
      'Stage B must retain existing Deck DOM control '+id);
  }
  const local=store(baseSave(),truth(),backup());
  const app=boot(local);
  const n=app.nodes;
  assert.equal(n.tieCount.innerHTML,'<span>0</span><span>5</span>',
    'Simulator total tie odometer drifted');
  assert.equal(n.awayTieCount.innerHTML,'<span>0</span><span>2</span>',
    'Simulator away tie odometer drifted');
  assert.equal(n.campaignRound.value,'4','Simulator round selection drifted');
  assert.equal(n.truthCallSign.textContent,CALL,'Truth Call Sign missing');
  assert.equal(n.truthPigeonName.textContent,LONG_NAME,'Truth Pigeon Name missing');
  assert.equal(n.truthPigeonMiles.textContent,'314','Truth Pigeon Miles missing');
  assert.equal(n.truthCampaignRound.textContent,'3rd Qualifying Round',
    'Truth round label drifted');
  assert.equal(n.campaignStatus.textContent,'IN PROGRESS',
    'Active campaign status not rendered');
  for(const key of ['addTie','addAwayTie','addPigeonMiles','simulateGiantKill',
    'campaignRound'])assert.equal(n[key].disabled,false,
      'Active simulator control unexpectedly disabled: '+key);
  assert.equal(n.cabinetCount.textContent,'2 / 27','Earned cabinet count drifted');
  assert.equal(n.deckCabinet.children.length,27,'Trophy Cabinet row order changed');
  const earned=n.deckCabinet.children.filter(slot=>slot.className.includes('completed'));
  assert.equal(earned.length,2,'Existing and verified trophies not both shown');
  assert(earned.every(slot=>typeof slot.onclick==='function'),
    'Completed trophies must remain inspectable');

  const persisted=local[DECK];
  app.read('renderStats()');
  assert.equal(local[DECK],persisted,'A display-only refresh wrote saved state');
  assert.equal(n.deckCabinet.children.length,27,
    'Display-only refresh duplicated or lost Trophy Cabinet slots');

  app.read('campaignIdentity.pigeonName="Percy"; state.pigeonMiles=1234.6; state.campaignRound=5; save()');
  assert.equal(n.truthPigeonName.textContent,'Percy','Save failed to refresh truth name');
  assert.equal(n.truthPigeonMiles.textContent,'1,235','Miles rounding/grouping changed');
  assert.equal(n.truthCampaignRound.textContent,'4th Qualifying Round',
    'Save failed to refresh round label');
  assert.equal(n.campaignRound.value,'5','Save failed to refresh simulator round');
  assert.equal(n.cabinetCount.textContent,'2 / 27',
    'Plain save unexpectedly awarded a new trophy');

  const simulated=boot(store(baseSave(),truth(),backup()));
  simulated.nodes.addAwayTie.onclick();
  assert.equal(simulated.nodes.tieCount.innerHTML,'<span>0</span><span>6</span>',
    'Away-tie simulation did not refresh total odometer');
  assert.equal(simulated.nodes.awayTieCount.innerHTML,'<span>0</span><span>3</span>',
    'Away-tie simulation did not refresh away odometer');
  assert.equal(simulated.nodes.cabinetCount.textContent,'3 / 27',
    'Qualifying away-tie simulator must award the correct third trophy');
  const newTrophy=simulated.nodes.deckCabinet.children.filter(
    slot=>slot.className.includes('completed'));
  assert.equal(newTrophy.length,3,'Campaign trophy did not join existing trophies');
  newTrophy[2].onclick();
  assert.equal(simulated.nodes.trophyViewer.hidden,false,
    'Newly earned trophy must still open its independent viewer');

  const ended=boot(store(baseSave(),truth({
    ended:true,giantKillAchieved:true
  }),backup()));
  assert.equal(ended.nodes.campaignStatus.textContent,'IT’S OVER',
    'Ended status rendering changed');
  for(const key of ['addTie','addAwayTie','addPigeonMiles','simulateGiantKill',
    'campaignRound'])assert.equal(ended.nodes[key].disabled,true,
      'Ended campaign control must remain disabled: '+key);
  assert.equal(ended.nodes.truthPigeonName.textContent,LONG_NAME,
    'Ended campaign lost its verified identity');
  assert.equal(ended.nodes.cabinetCount.textContent,'3 / 27',
    'Ended campaign must retain historical and verified Giant Kill trophies');

  // Exercise the actual confirmation-dependent Hard Reset click handler.
  // It resets only the Deck's local awards and then reapplies verified
  // Clubfinder truth; it must not erase the bridge or backup.
  const resetLocal=store(baseSave(),truth(),backup());
  const reset=boot(resetLocal);
  reset.read('tinFoilConfirm=async()=>true');
  await reset.nodes.reset.onclick();
  assert.equal(reset.read('Boolean(state.completed["01"])'),false,
    'Hard Reset must clear only earlier Honour awards');
  assert.equal(reset.read('Boolean(state.completed["02"])'),true,
    'Hard Reset must immediately restore verified Campaign milestone');
  assert.equal(reset.nodes.cabinetCount.textContent,'1 / 27',
    'Hard Reset cabinet count did not reflect verified-only awards');
  assert.equal(reset.nodes.truthPigeonName.textContent,LONG_NAME,
    'Hard Reset lost verified Pigeon Name');
  assert.equal(reset.nodes.truthPigeonMiles.textContent,'314',
    'Hard Reset lost verified Pigeon Miles');
  assert.equal(reset.nodes.tieCount.innerHTML,'<span>0</span><span>5</span>',
    'Hard Reset failed to re-render current verified simulator counters');
  assert.equal(JSON.parse(resetLocal[BRIDGE]).pigeonName,LONG_NAME,
    'Hard Reset must not delete Clubfinder campaign bridge');
  assert.equal(JSON.parse(resetLocal[IDENTITY]).pigeonName,LONG_NAME,
    'Hard Reset must not delete Clubfinder identity backup');
}

testDisplayAndReset().then(()=>{
  console.log('BETA SAVED CAMPAIGN / CHALLENGES BRIDGE CONTRACT: PASS');
  console.log('Verified bridge, long name, trophy persistence, legacy migration, campaign isolation, ended state and return routes: PASS');
  console.log('BETA RENDER STAGE B: truth frame, simulator, Trophy Cabinet, save, progress, ended state and actual Hard Reset: PASS');
}).catch(error=>{console.error(error);process.exitCode=1;});
