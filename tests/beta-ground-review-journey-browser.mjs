import {chromium} from 'playwright';
import assert from 'node:assert/strict';
import {readFileSync, mkdirSync} from 'node:fs';

const preview=readFileSync('/tmp/tffc-ground-review/beta/clubfinder-beta.html','utf8');
const base='http://127.0.0.1:8765';
const browser=await chromium.launch({headless:true});
const cases=[
 {club:'Leyton Orient FC',ground:'BetWright Stadium',postcode:'E10 5NF'},
 {club:'Port Vale FC',ground:'Vale Park',postcode:'ST6 1AW'},
 {club:'Rotherham United FC',ground:'AESSEAL New York Stadium',postcode:'S60 1FJ'}
];
mkdirSync('/tmp/tffc-ground-journey',{recursive:true});
try {
 for(const [device,width,height] of [['big-boy',1365,860],['iphone',390,844],['ipad-portrait',820,1180]]) {
  const context=await browser.newContext({viewport:{width,height}});
  const page=await context.newPage();
  let injected=0;
  const pageErrors=[];
  page.on('pageerror',e=>pageErrors.push(String(e)));
  await page.route('**/beta/clubfinder-beta.html',async route=>{
   injected++;
   await route.fulfill({status:200,contentType:'text/html; charset=utf-8',body:preview});
  });
  await page.route('https://tffac-clubfinder-counter.anvilspringstien.workers.dev/**',route=>route.abort());
  await page.goto(base+'/beta/clubfinder-journey.html',{waitUntil:'domcontentloaded',timeout:30000});
  await page.waitForFunction(()=>typeof findGround==='function',{timeout:25000});
  assert.equal(injected,1,'approved Shed wrapper must fetch exactly one preview engine');
  await page.locator('iframe.tffc-exact-master-frame').waitFor({timeout:25000});
  const actual=await page.evaluate(rows=>rows.map(row=>{
   const found=findGround({name:row.club});
   return {requested:row.club,found:found&&{
    name:found.name,ground:found.ground,postcode:found.postcode,
    verification:found.verification,lat:found.lat,lon:found.lon
   }};
  }),cases);
  for(const [i,row] of actual.entries()){
   assert.ok(row.found,'missing '+row.requested);
   assert.equal(row.found.ground,cases[i].ground);
   assert.equal(row.found.postcode,cases[i].postcode);
   assert.equal(row.found.verification,'unverified');
   assert.ok(!Number.isFinite(row.found.lat)&&!Number.isFinite(row.found.lon));
  }
  const afc=await page.evaluate(()=>findGround({name:'AFC Liverpool'}));
  const liverpool=await page.evaluate(()=>findGround({name:'Liverpool FC'}));
  assert.equal(afc?.name,'AFC Liverpool');
  assert.notEqual(liverpool?.name,'AFC Liverpool');
  assert.deepEqual(pageErrors,[],device+' script exceptions');
  const interfaces=await page.evaluate(()=>({
   functions:['chooseJourney','renderResults','render','buildJourney','findGround','verification','saveCampaign'].filter(k=>typeof window[k]==='function'),
   controls:[...document.querySelectorAll('#postcode,#findBtn,#results,#clubfinderField')].map(x=>x.id)
  }));
  if(device==='big-boy'){
   const contracts=await page.evaluate(()=>({
     choose:chooseJourney.toString().slice(0,1700),
     find:findGround.toString().slice(0,800),
     campaignKeys:Object.keys(localStorage).filter(k=>/tin|campaign|pigeon|tffc/i.test(k)).slice(0,12)
   }));
   console.log('Shed Campaign review contract',JSON.stringify(contracts));
  }
  console.log('PASS approved three-frame Shed',device,'custodian ground evidence, identity and 0 coords',JSON.stringify(interfaces));
  await page.screenshot({path:'/tmp/tffc-ground-journey/'+device+'.png',fullPage:true});
  await context.close();
 }
} finally {await browser.close()}
