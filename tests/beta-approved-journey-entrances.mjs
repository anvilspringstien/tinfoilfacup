import assert from 'node:assert/strict';
import {chromium, devices} from 'playwright';

const origin = 'http://127.0.0.1:8765';
const browser = await chromium.launch();
const journeyKey = 'tinFoilFACupJourney_v7';
const publicArt = '6bb8ae591609e95f220b22ecf684beba56e05e369d1b5c803b09429fa1ae04ef';
const shedArt = '95fd53512b9879556d2fe81fdf65dabad4bec567977e9bcc273bf385d875de9d';
const fixture = {originName:'Newton Aycliffe FC',postcode:'DL5 4RQ',searchNumber:18765,
  callSign:'Tango Foxtrot 2 Alpha Charlie 18765',pigeonName:'Boundary Pigeon',ended:false};

async function newContext(options) {
  const context = await browser.newContext(options);
  let counters = 0;
  await context.route('https://**/*', route => route.abort());
  await context.route('https://api.postcodes.io/**', route => {
    const path = decodeURIComponent(new URL(route.request().url()).pathname).toUpperCase();
    if (path !== '/POSTCODES/DL5 4RQ') return route.abort();
    return route.fulfill({headers:{'access-control-allow-origin':'*'},
      json:{status:200,result:{postcode:'DL5 4RQ',latitude:54.618,longitude:-1.571}}});
  });
  await context.route('https://tffac-clubfinder-counter.anvilspringstien.workers.dev/**', route => {
    assert.equal(route.request().method(),'POST');
    counters++;
    return route.fulfill({headers:{'access-control-allow-origin':'*'},json:{number:fixture.searchNumber}});
  });
  return {context, allocations:()=>counters};
}

const app = page => page.frameLocator('#phoneApp');
const saved = page => page.evaluate(key=>JSON.parse(localStorage.getItem(key)),journeyKey);
const shell = page => new URL(page.url()).pathname;
const myStats = page => app(page).getByRole('button',{name:'My Stats',exact:true});

async function checkSplash(page, entry, isShed, label) {
  await page.goto(origin+entry);
  const crest = app(page).getByRole('img',{name:'Tin Foil FA Cup crest'});
  const image = await crest.evaluate(async img=>{
    await img.decode();
    const response = await fetch(img.currentSrc);
    const digest = await crypto.subtle.digest('SHA-256',await response.arrayBuffer());
    return {hash:Array.from(new Uint8Array(digest), n=>n.toString(16).padStart(2,'0')).join(''),
      path:location.pathname, opacity:getComputedStyle(img).opacity, width:img.naturalWidth};
  });
  assert.equal(image.hash,isShed?shedArt:publicArt,entry+' must render the correct crest');
  assert.equal(image.path,isShed?'/beta/shed-splash.html':'/beta/public-splash.html');
  assert.equal(image.opacity,'1');
  assert.equal(image.width,isShed?507:900);
  assert.equal(await app(page).locator('#phoneApp').count(),0);
  await app(page).getByRole('link',{name:label,exact:true}).waitFor();
}

async function checkCampaign(page, entry) {
  const inside = app(page);
  await inside.locator('.chosen-campaign-current').waitFor();
  const nav = inside.locator('.phone-frame-nav');
  await nav.getByRole('button',{name:'Barry Air',exact:true}).waitFor();
  assert.equal(await nav.locator('.campaign-primary-nav button').first().evaluate(el=>getComputedStyle(el).boxShadow.includes('inset')),true);
  assert.equal(await inside.locator('.campaign-origin-name').textContent(),fixture.originName);
  assert.equal(await inside.locator('html').evaluate(()=>location.pathname),'/beta/clubfinder-journey.html');
  assert.equal(shell(page),entry);
}

try {
  for(const [entry,isShed] of [['/',false],['/beta/',true],['/beta/phone-frame.html',false]]){
    const {context,allocations}=await newContext({viewport:{width:1890,height:919},reducedMotion:'reduce'});
    context.setDefaultTimeout(18000);
    const page=await context.newPage();
    await checkSplash(page,entry,isShed,'Start Campaign');
    await app(page).getByRole('link',{name:'Start Campaign',exact:true}).click();
    const laws=app(page).frameLocator('iframe.tffc-exact-master-frame');
    await laws.getByRole('heading',{name:'The Four Laws',exact:true}).waitFor();
    await laws.locator('#postcode').fill(fixture.postcode);
    await laws.getByRole('button',{name:'Find My Club'}).click();
    await app(page).getByRole('button',{name:'Make Tin Foil FA Cup Campaign 1 my Campaign'}).click();
    await checkCampaign(page,entry);
    await page.waitForFunction(({key,number})=>JSON.parse(localStorage.getItem(key))?.searchNumber===number,{key:journeyKey,number:fixture.searchNumber});
    assert.equal(allocations(),1);
    const pigeon=app(page).getByRole('textbox',{name:'Pigeon name',exact:true});
    await pigeon.fill(fixture.pigeonName);
    await pigeon.press('Tab');
    await page.waitForFunction(({key,name})=>JSON.parse(localStorage.getItem(key))?.pigeonName===name,{key:journeyKey,name:fixture.pigeonName});

    await checkSplash(page,entry,isShed,'My Campaign');
    await app(page).getByRole('link',{name:'My Campaign',exact:true}).click();
    await checkCampaign(page,entry);
    assert.equal(await pigeon.inputValue(),fixture.pigeonName);

    if(entry==='/beta/'){
      await app(page).getByRole('button',{name:'Refresh TFFAC',exact:true}).click();
      await page.waitForURL(url=>url.pathname===entry&&url.searchParams.has('tffc-refresh'));
      await checkCampaign(page,entry);
      await myStats(page).click();
      const popupPromise=page.waitForEvent('popup');
      await app(page).getByRole('button',{name:'Got It!',exact:true}).click();
      const stats=await popupPromise;
      await app(stats).getByRole('button',{name:'← My Campaign',exact:true}).waitFor();
      await stats.waitForURL(url=>url.pathname===entry&&url.searchParams.get('view')==='stats');
      const closed=stats.waitForEvent('close');
      await app(stats).getByRole('button',{name:'← My Campaign',exact:true}).click().catch(error=>{
        if(!stats.isClosed())throw error;
      });
      await closed;
      await checkCampaign(page,entry);
    }

    await app(page).getByRole('button',{name:'Share the Magic',exact:true}).click();
    const share=app(page).frameLocator('iframe[title="Share Tin Foil FA Cup"]');
    await share.getByRole('heading',{name:'Share the Magic',exact:true}).waitFor();
    await share.getByRole('button',{name:'Keep the Magic',exact:true}).click();
    await share.getByRole('heading',{name:'Keep the Magic',exact:true}).waitFor();
    await share.getByRole('button',{name:'Back to Share',exact:true}).click();
    await share.getByRole('button',{name:'Close',exact:true}).click();
    await checkCampaign(page,entry);
    const record=await saved(page);
    for(const key of ['originName','postcode','searchNumber','callSign','pigeonName'])assert.equal(record[key],fixture[key]);
    assert.equal(allocations(),1,'returning, refreshing and closing auxiliary views must not allocate');
    await context.close();
  }

  // Simulate a cached shell renderer that still asks for beta/index.html.
  const {context:cached}=await newContext({reducedMotion:'reduce'});
  await cached.route('**/beta/phone-frame-shed.js*',async route=>{
    const response=await route.fetch();
    const body=(await response.text()).replace("splash:shed?'shed-splash.html':'public-splash.html'","splash:'index.html'");
    await route.fulfill({response,body});
  });
  const cachedPage=await cached.newPage();
  await checkSplash(cachedPage,'/',false,'Start Campaign');
  await checkSplash(cachedPage,'/beta/phone-frame-shed.html',true,'Start Campaign');
  await cached.close();

  const {context,allocations}=await newContext({...devices['iPhone 14'],reducedMotion:'reduce'});
  await context.addInitScript(({key,value})=>{
    if(!localStorage.getItem(key))localStorage.setItem(key,JSON.stringify(value));
  },{key:journeyKey,value:fixture});
  const page=await context.newPage();
  for(const [entry,environment] of [['/','public'],['/beta/','shed'],['/beta/phone-frame.html',null]]){
    await page.goto(origin+entry+'?view=campaign');
    await myStats(page).click();
    await app(page).getByRole('button',{name:'Got It!',exact:true}).click();
    await page.waitForURL(url=>url.pathname==='/beta/clubfinder-beta.html'&&url.searchParams.get('stats')==='1');
    assert.equal(new URL(page.url()).searchParams.get('shell'),environment);
    await page.getByRole('button',{name:'← My Campaign',exact:true}).click();
    await checkCampaign(page,entry);
  }
  assert.equal(allocations(),0);
  await context.close();
} finally {
  await browser.close();
}
console.log('Public, installed and Shed routes render distinct approved Splash artwork and retain the framed Campaign identity.');
