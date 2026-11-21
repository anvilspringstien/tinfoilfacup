import {chromium} from 'playwright';
import assert from 'node:assert/strict';
const base='http://127.0.0.1:8765';
const browser=await chromium.launch({headless:true});
const cases=[
  ['Leyton Orient FC','E10 5NF','BetWright Stadium'],
  ['Port Vale FC','ST6 1AW','Vale Park'],
  ['Rotherham United FC','S60 1FJ','AESSEAL New York Stadium']
];
try {
  for(const [name,width,height] of [['big-boy',1365,860],['iphone',390,844],['ipad-portrait',820,1180]]) {
    const ctx=await browser.newContext({viewport:{width,height}});
    const page=await ctx.newPage();
    await page.route('https://tffac-clubfinder-counter.anvilspringstien.workers.dev/**', route=>route.abort());
    await page.goto(base+'/beta/clubfinder-ground-review.html',{waitUntil:'domcontentloaded',timeout:30000});
    await page.waitForFunction(()=>typeof findGround==='function',{timeout:20000});
    for (const [club,postcode,ground] of cases) {
      const row=await page.evaluate(name=>findGround({name}),club);
      assert.ok(row,club+' missing from actual BETA findGround');
      assert.equal(row.postcode,postcode);
      assert.equal(row.ground,ground);
      assert.equal(row.verification,'unverified');
      assert.ok(!Number.isFinite(row.lat) && !Number.isFinite(row.lon),
        club+' must not get map coordinates or mileage');
    }
    const afc=await page.evaluate(()=>findGround({name:'AFC Liverpool'}));
    assert.equal(afc?.name,'AFC Liverpool','Existing AFC Liverpool own-ground record must remain intact');
    const other=await page.evaluate(()=>findGround({name:'Liverpool FC'}));
    assert.notEqual(other?.name,'AFC Liverpool','Liverpool FC must NOT inherit AFC Liverpool ground');
    console.log('PASS guarded BETA preview lookup:',name);
    await ctx.close();
  }
} finally {
  await browser.close();
}
