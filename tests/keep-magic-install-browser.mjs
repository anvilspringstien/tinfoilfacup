import assert from 'node:assert/strict';
import { createRequire } from 'node:module';
import { pathToFileURL } from 'node:url';
export async function checkInstalledHandover(browser,base){
 // Model the actual iOS boundary: only cookies cross into a brand-new app.
 // Do not supply storageState.origins or localStorage to the installed context.
 const sourceContext=await browser.newContext({viewport:{width:390,height:669}});
 await sourceContext.route('https://tffac-clubfinder-counter.anvilspringstien.workers.dev/**',route=>route.abort());
 const postcodeRoute=route=>{const u=new URL(route.request().url());return decodeURIComponent(u.pathname).toUpperCase()==='/POSTCODES/NE6 5NL'?route.fulfill({json:{status:200,result:{postcode:'NE6 5NL',latitude:54.99,longitude:-1.56}}}):route.abort()};
 await sourceContext.route('https://api.postcodes.io/**',postcodeRoute);
 const sourcePage=await sourceContext.newPage();
 await sourcePage.goto(base+'/beta/keep-the-magic-shed.html');
 const checky={originName:'Heaton Stannington FC',postcode:'NE6 5NL',ended:false,selectedAt:'2026-10-20T11:30:00.000Z',searchNumber:1755,callSign:'Tango Foxtrot 2 Alpha Charlie [01755]',pigeonName:'Checky',introDismissed:{stats:true,challenges:true}};
 await sourcePage.evaluate(value=>localStorage.setItem('tinFoilFACupJourney_v7',JSON.stringify(value)),checky);
 await sourcePage.goto(base+'/beta/clubfinder-journey.html');
 await sourcePage.locator('.pigeon-name-input').waitFor({timeout:30000});
 await sourcePage.getByRole('button',{name:'My Challenges',exact:true}).click();
 await sourcePage.waitForURL('**/beta/challenges-beta.html');
 await sourcePage.waitForFunction(()=>JSON.parse(localStorage.getItem('tffc.challengeDeck.v1')||'null')?.version===1);
 await sourcePage.goto(base+'/beta/clubfinder-journey.html');
 await sourcePage.getByRole('button',{name:'Share the Magic',exact:true}).click();
 const magic=sourcePage.frameLocator('iframe[title="Share Tin Foil FA Cup"]');
 await magic.locator('#keep').click();
 await magic.locator('#magic').evaluate(()=>new Promise(resolve=>{const check=()=>document.cookie.includes('tffc_keep_v1=')&&!document.getElementById('install-status').textContent?resolve():setTimeout(check,20);check()}));
 const beforeInstall=await magic.locator('#magic').evaluate(()=>Object.fromEntries(TffcMagicBackup.KEYS.map(k=>[k,localStorage.getItem(k)]).filter(([,v])=>v!==null)));
 assert.equal(Object.keys(beforeInstall).length,4,'real Campaign/Challenges flow populated all four progress keys');
 const cookieCopy=await sourceContext.cookies(base+'/beta/keep-the-magic-shed.html');
 const installed=await browser.newContext({viewport:{width:390,height:669}});
 assert.deepEqual((await installed.storageState()).origins,[],'installed app begins with empty localStorage');
 await installed.addCookies(cookieCopy);
 await installed.addInitScript(()=>Object.defineProperty(navigator,'standalone',{value:true}));
 let newNumbers=0;
 await installed.route('https://tffac-clubfinder-counter.anvilspringstien.workers.dev/**',route=>{newNumbers++;return route.abort()});
 await installed.route('https://api.postcodes.io/**',postcodeRoute);
 const installedPage=await installed.newPage();
 await installedPage.goto(base+'/beta/keep-the-magic-shed.html');await installedPage.waitForURL(base+'/beta/');
 const afterInstall=await installedPage.evaluate(keys=>Object.fromEntries(keys.map(k=>[k,localStorage.getItem(k)])),Object.keys(beforeInstall));
 assert.deepEqual(afterInstall,beforeInstall,'all Campaign, Pigeon and Challenge bytes transfer before Splash');
 assert.equal((await installed.cookies()).filter(c=>c.name.startsWith('tffc_keep_v1')).length,0,'handover cookies consumed');
 await installedPage.locator('.splash-start').click();
 await installedPage.locator('.pigeon-name-input').waitFor({timeout:30000});
 await installedPage.waitForFunction(()=>Math.abs(document.getElementById('tffc-results-summary').getBoundingClientRect().top-14)<3,null,{timeout:10000});
 assert.equal(await installedPage.locator('.pigeon-name-input').inputValue(),'Checky');
 assert.equal(await installedPage.evaluate(()=>JSON.parse(localStorage.getItem('tinFoilFACupJourney_v7')).searchNumber),1755);
 assert.match(await installedPage.locator('#results').innerText(),/Heaton Stannington/);
 await installedPage.getByRole('button',{name:'My Challenges',exact:true}).click();
 await installedPage.waitForURL('**/beta/challenges-beta.html');
 const challenge=await installedPage.evaluate(()=>JSON.parse(localStorage.getItem('tffc.challengeDeck.v1')));
 const oldChallenge=JSON.parse(beforeInstall['tffc.challengeDeck.v1']);
 assert.deepEqual(challenge.completed,oldChallenge.completed,'Trophy Cabinet awards survive the install');
 assert.equal(challenge.pigeonMiles,oldChallenge.pigeonMiles,'flown mileage survives the install');
 await installedPage.goto(base+'/beta/keep-the-magic-shed.html');await installedPage.waitForURL(base+'/beta/');
 assert.equal(await installedPage.evaluate(()=>JSON.parse(localStorage.getItem('tinFoilFACupJourney_v7')).pigeonName),'Checky');
 assert.equal(newNumbers,0,'fresh installed storage must not issue 01756');
 await installed.close();await sourceContext.close();
}
if(process.argv[1]&&import.meta.url===pathToFileURL(process.argv[1]).href){
 const {webkit}=createRequire(import.meta.url)('playwright');
 const browser=await webkit.launch({headless:true});
 try{await checkInstalledHandover(browser,process.env.TFFC_PREVIEW_BASE||'http://127.0.0.1:8765');console.log('WEBKIT INSTALL HANDOVER: PASS — empty app storage restores Checky, #01755, Cabinet and miles with no fresh counter.');}
 finally{await browser.close();}
}
