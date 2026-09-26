#!/usr/bin/env python3
"""One-time fail-closed patch: BETA lightweight Stats first-open route."""
from pathlib import Path
import subprocess

root=Path(__file__).resolve().parents[1]
target=root/"beta/clubfinder-beta.html"
test_file=root/"updater/beta_campaign_identity_regression.js"
expected_blob="a353194f2e3c678ae3f5182db5076192ecb61095"
actual=subprocess.check_output(["git","hash-object",str(target)],cwd=root,text=True).strip()
if actual!=expected_blob:
    raise SystemExit(f"ABORT: BETA Clubfinder changed since review: expected {expected_blob}, got {actual}")
source=target.read_text()
start=source.index("async function journeyCertificate(")
end=source.index("\nasync function go(",start)
cert=source[start:end]
assert cert.startswith('async function journeyCertificate(origin, suppliedWindow=null, returnMode="clubfinder", reloadablePreview=false){')
cert=cert.replace(
    'async function journeyCertificate(origin, suppliedWindow=null, returnMode="clubfinder", reloadablePreview=false){',
    'async function journeyCertificate(origin, suppliedWindow=null, returnMode="clubfinder"){',1)
begin=cert.index("  // Reuse the already loaded Clubfinder for fast Stats;")
finish=cert.index("  const w=suppliedWindow;",begin)
cert=cert[:begin]+'''  // Open a tiny same-origin page synchronously while still in the click.
  // It asks its already-loaded Clubfinder opener to produce the certificate.
  if(!suppliedWindow){
    window.open("stats-beta.html","_blank");
    return;
  }
'''+cert[finish:]
old_tail='''    if(reloadablePreview){
      // The new blank popup inherits our origin: use a real reloadable URL
      // without fetching and booting the entire Clubfinder on first open.
      try{
        w.history.replaceState(null,"",new URL("clubfinder-beta.html?stats=1",window.location.href).href);
      }catch(_){
        // Restricted history APIs must not reintroduce blank-on-refresh.
        w.location.replace("clubfinder-beta.html?stats=1");
      }
    }
'''
assert cert.count(old_tail)==1,"Unexpected Stats popup tail"
cert=cert.replace(old_tail,"",1)
helper='''
async function tinFoilRenderStatsFromOpener(target){
  if(!target || target.closed)return false;
  await tinFoilCompetitionReady;
  const saved=loadSavedJourney();
  const origin=saved&&ELIGIBLE.find(c=>norm(c.name)===norm(saved.originName));
  if(!origin)return false;
  await journeyCertificate(origin,target,"clubfinder");
  return true;
}
'''
assert "tinFoilRenderStatsFromOpener" not in source
source=source[:start]+cert+helper+source[end:]
assert "reloadablePreview" not in source
target.write_text(source)

test=test_file.read_text()
needle="const competition=JSON.parse(fs.readFileSync(path.join(ROOT,'competition.json'),'utf8'));"
assert test.count(needle)==1
test=test.replace(needle,needle+'''
const liteRoute=fs.readFileSync(path.join(ROOT,'beta','stats-beta.html'),'utf8');
const liteScriptMatch=liteRoute.match(/<script>([\\s\\S]*?)<\\/script>/i);
if(!liteScriptMatch)throw new Error('BETA fast Stats: tiny route script missing');
if(!liteRoute.includes('content="width=980"')||
   !liteRoute.includes('source.tinFoilRenderStatsFromOpener(window)')||
   !liteRoute.includes('source.location.origin===window.location.origin')||
   !liteRoute.includes('sessionStorage.removeItem(marker)')||
   !liteRoute.includes('window.location.replace(canonical)'))
  throw new Error('BETA fast Stats: opener, wide page, refresh or fallback guard missing');
''',1)
test_start=test.index("  // First opening must immediately reuse the already loaded Clubfinder,")
test_end=test.index("  // Execute the real Clubfinder -> Challenges producer path",test_start)
new_test='''  // First opening loads only a tiny local page, not another 4.6 MB Clubfinder.
  // That page asks the existing opener to render into the new tab.
  const statsSavedBefore=JSON.stringify(loadSavedJourney());
  const statsCounterBefore=getCounterIncrementCalls();
  const competitionBeforeStats=getCompetitionFetchCalls();
  const originalPageHref=window.location.href;
  await journeyCertificate(origin);
  const openedUrls=JSON.parse(getPopupRoutes());
  if(openedUrls.length!==1||openedUrls[0]!=='stats-beta.html')
    throw new Error('BETA Stats fast-open: did not open the tiny same-origin route: '+JSON.stringify(openedUrls));
  if(getCertificateHtml())throw new Error('BETA Stats fast-open: opener unexpectedly rendered into itself');
  if(!await tinFoilRenderStatsFromOpener(window.open('')))
    throw new Error('BETA Stats fast-open: ready Clubfinder did not render the pop-up');
  const instantPage=getCertificateHtml();
  if(instantPage.length<10000||!instantPage.includes('Pigeon McPigeonface')||
     !instantPage.includes('Tango Foxtrot 2 Alpha Charlie 09842')||
     !instantPage.includes('Thame United')||
     !instantPage.includes('<meta name="viewport" content="width=980">'))
    throw new Error('BETA Stats fast-open: original report, identity or wide viewport lost');
  if(getCompetitionFetchCalls()!==competitionBeforeStats)
    throw new Error('BETA Stats fast-open: opening triggered a redundant competition fetch');
  if(window.location.href!==originalPageHref)
    throw new Error('BETA Stats fast-open: opening navigated away from Clubfinder');
  // Genuine refresh retains the existing canonical route and fetches fresh data.
  const originalSearch=window.location.search;
  window.location.search='?stats=1';
  await tinFoilMaybeOpenCanonicalStatsRoute();
  const statsPage=getCertificateHtml();
  if(!statsPage.includes('<meta name="viewport" content="width=980">')||
     !statsPage.includes('grid-template-columns:repeat(6,minmax(0,1fr))')||
     !statsPage.includes('Pigeon McPigeonface')||
     !statsPage.includes('Tango Foxtrot 2 Alpha Charlie 09842')||
     !statsPage.includes('Thame United'))
    throw new Error('BETA Stats refresh: original zoomable report or campaign missing');
  document.open();
  await tinFoilMaybeOpenCanonicalStatsRoute();
  const refreshedStats=getCertificateHtml();
  if(!refreshedStats.includes('<meta name="viewport" content="width=980">')||
     !refreshedStats.includes('Pigeon McPigeonface')||
     !refreshedStats.includes('Tango Foxtrot 2 Alpha Charlie 09842')||
     !refreshedStats.includes('Thame United'))
    throw new Error('BETA Stats refresh: blank page or stale campaign');
  window.location.search=originalSearch;
  if(getCounterIncrementCalls()!==statsCounterBefore||
     JSON.stringify(loadSavedJourney())!==statsSavedBefore)
    throw new Error('BETA Stats: navigation altered campaign or allocated a call sign');
  console.log('BETA STATS LIGHT FIRST OPEN + CANONICAL REFRESH: PASS');

'''
test=test[:test_start]+new_test+test[test_end:]
# Test the actual small-page script as a browser would, including real reload
# and a closed/unavailable opener. This catches errors a static source check misses.
test+='''
(async()=>{
  const script=liteScriptMatch[1], storage={}, redirects=[];
  let renders=0;
  const origin='https://anvilspringstien.github.io';
  const source={
    closed:false,location:{origin},
    async tinFoilRenderStatsFromOpener(){renders++;return true}
  };
  const page={
    opener:source,
    location:{origin,replace:url=>redirects.push(String(url))}
  };
  const session={
    getItem:k=>storage[k]??null,
    setItem:(k,v)=>{storage[k]=String(v)},
    removeItem:k=>{delete storage[k]}
  };
  const ctx={window:page,sessionStorage:session,console};
  await vm.runInNewContext(script,ctx,{filename:'beta/stats-beta.html'});
  if(renders!==1||redirects.length||storage['tffc.stats-fast-open.v1']!=='1')
    throw new Error('BETA lite Stats: first load failed to use available opener');
  await vm.runInNewContext(script,ctx,{filename:'beta/stats-beta.html'});
  if(renders!==1||redirects.length!==1||redirects[0]!=='clubfinder-beta.html?stats=1')
    throw new Error('BETA lite Stats: browser refresh did not fetch canonical fresh route');
  page.opener=null;
  redirects.length=0;
  await vm.runInNewContext(script,ctx,{filename:'beta/stats-beta.html'});
  if(redirects.length!==1||redirects[0]!=='clubfinder-beta.html?stats=1')
    throw new Error('BETA lite Stats: missing opener failed to use canonical fallback');
  console.log('BETA STATS LIGHT ROUTE: first open, real refresh, missing opener — PASS');
})().catch(e=>{console.error(e.stack||e);process.exitCode=1});
'''
test_file.write_text(test)
print("Patched BETA Clubfinder and Stats regression; production and canonical data untouched")

# Rerun isolated workflow after draft PR opened.
