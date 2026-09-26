#!/usr/bin/env python3
"""One-time, fail-closed BETA Stats first-open acceleration. Delete after patch."""
from pathlib import Path

club=Path("beta/clubfinder-beta.html")
test=Path("updater/beta_campaign_identity_regression.js")

def replace_exact(path, old, new):
    src=path.read_text(encoding="utf-8")
    found=src.count(old)
    if found!=1:
        raise SystemExit(f"FAIL CLOSED: {path}: expected 1 matching anchor, got {found}: {old[:95]!r}")
    path.write_text(src.replace(old,new,1),encoding="utf-8")
    print(f"PATCHED {path}: {len(new)-len(old):+d} chars")

replace_exact(club,
'''async function journeyCertificate(origin, suppliedWindow=null, returnMode="clubfinder"){
  // Open the existing reloadable Stats route while still in the user click.
  if(!suppliedWindow){
    window.open("clubfinder-beta.html?stats=1","_blank");
    return;
  }
  const w=suppliedWindow || window.open("","_blank");''',
'''async function journeyCertificate(origin, suppliedWindow=null, returnMode="clubfinder", reloadablePreview=false){
  // Reuse the already loaded Clubfinder for fast Stats; open synchronously in
  // the click before venue-derived mileage's asynchronous work.
  if(!suppliedWindow){
    const popup=window.open("","_blank");
    if(!popup)return;
    return journeyCertificate(origin,popup,returnMode,true);
  }
  const w=suppliedWindow;''')

replace_exact(club,
'''    w.document.close();
  }
}

async function go(explicitPostcodeSearch=false){''',
'''    w.document.close();
    if(reloadablePreview){
      // The new blank popup inherits our origin: use a real reloadable URL
      // without fetching and booting the entire Clubfinder on first open.
      try{
        w.history.replaceState(null,"",new URL("clubfinder-beta.html?stats=1",window.location.href).href);
      }catch(_){
        // Restricted history APIs must not reintroduce blank-on-refresh.
        w.location.replace("clubfinder-beta.html?stats=1");
      }
    }
  }
}

async function go(explicitPostcodeSearch=false){''')

replace_exact(test,
'''const popupRoutes=[];
function popupStub(){''',
'''const popupRoutes=[];
const popupHistory=[];
const popupFallbacks=[];
let competitionFetchCalls=0;
function popupStub(){''')

replace_exact(test,
'''  return {document:doc,closed:false,focus(){},print(){},close(){this.closed=true}};
}''',
'''  return {
    document:doc,closed:false,focus(){},print(){},close(){this.closed=true},
    history:{replaceState(_state,_title,url){popupHistory.push(String(url))}},
    location:{replace(url){popupFallbacks.push(String(url))}}
  };
}''')

replace_exact(test,
'''  getPopupRoutes:()=>JSON.stringify(popupRoutes),
  getCounterIncrementCalls:()=>counterIncrementCalls,''',
'''  getPopupRoutes:()=>JSON.stringify(popupRoutes),
  getPopupHistory:()=>JSON.stringify(popupHistory),
  getPopupFallbacks:()=>JSON.stringify(popupFallbacks),
  getCompetitionFetchCalls:()=>competitionFetchCalls,
  getCounterIncrementCalls:()=>counterIncrementCalls,''')

replace_exact(test,
'''    if(s.includes('competition.json'))return {ok:true,status:200,json:async()=>JSON.parse(JSON.stringify(competition)),text:async()=>JSON.stringify(competition)};''',
'''    if(s.includes('competition.json')){competitionFetchCalls++;return {ok:true,status:200,json:async()=>JSON.parse(JSON.stringify(competition)),text:async()=>JSON.stringify(competition)};}''')

replace_exact(test,
'''  // iPhone pull-to-refresh regression: the Stats button must open a real
  // reloadable URL, never a document written into a blank about:blank tab.
  const statsSavedBefore=JSON.stringify(loadSavedJourney());
  const statsCounterBefore=getCounterIncrementCalls();
  const originalPageHref=window.location.href;
  await journeyCertificate(origin);
  const openedUrls=JSON.parse(getPopupRoutes());
  if(openedUrls.length!==1||openedUrls[0]!=='clubfinder-beta.html?stats=1')
    throw new Error('BETA Stats refresh: button did not open its canonical reloadable route: '+JSON.stringify(openedUrls));
  if(getCertificateHtml())throw new Error('BETA Stats refresh: popup is still filled with an ephemeral document');
  if(window.location.href!==originalPageHref)throw new Error('BETA Stats refresh: opening Stats navigated away from the original Clubfinder');''',
'''  // First opening must immediately reuse the already loaded Clubfinder, not
  // refetch competition.json. The popup's rendered document receives a proper
  // URL via same-origin history replacement, so refresh still regenerates it.
  const statsSavedBefore=JSON.stringify(loadSavedJourney());
  const statsCounterBefore=getCounterIncrementCalls();
  const competitionBeforeStats=getCompetitionFetchCalls();
  const originalPageHref=window.location.href;
  await journeyCertificate(origin);
  const openedUrls=JSON.parse(getPopupRoutes());
  if(openedUrls.length!==1||openedUrls[0]!=='')
    throw new Error('BETA Stats fast-open: popup was not created synchronously as a blank same-origin document');
  const historyUrls=JSON.parse(getPopupHistory());
  if(historyUrls.length!==1||
     historyUrls[0]!==new URL('clubfinder-beta.html?stats=1',originalPageHref).href||
     JSON.parse(getPopupFallbacks()).length!==0)
    throw new Error('BETA Stats fast-open: rendered popup did not acquire its reloadable URL: '+JSON.stringify(historyUrls));
  const instantPage=getCertificateHtml();
  if(instantPage.length<10000||!instantPage.includes('Pigeon McPigeonface')||
     !instantPage.includes('Tango Foxtrot 2 Alpha Charlie 09842')||
     !instantPage.includes('Thame United')||
     !instantPage.includes('<meta name="viewport" content="width=980">'))
    throw new Error('BETA Stats fast-open: accepted pinch-to-zoom report or campaign identity missing');
  if(getCompetitionFetchCalls()!==competitionBeforeStats)
    throw new Error('BETA Stats fast-open: redundant competition-data fetch on opening Stats');
  if(window.location.href!==originalPageHref)
    throw new Error('BETA Stats fast-open: opening Stats navigated away from Clubfinder');''')

replace_exact(test,
'''  console.log('BETA IPHONE STATS PULL-TO-REFRESH: canonical route, full identity, restored report, no extra counter — PASS');''',
'''  console.log('BETA IPHONE STATS FAST OPEN + PULL-TO-REFRESH: reused competition, canonical URL, wide report, restored identity, no extra counter — PASS');''')

print("Fail-closed, isolated Stats fast-open patch complete.")
