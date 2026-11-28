import assert from 'node:assert/strict';
import {chromium} from 'playwright';

const browser=await chromium.launch();
const host=process.env.TFFC_PREVIEW_BASE || 'http://127.0.0.1:8765';
try {
  for(const [entry,source] of [['/','live'],['/beta/phone-frame.html','fallback'],['/beta/','unavailable']]){
    const context=await browser.newContext();
    await context.route('https://**/*',route=>route.abort());
    await context.route('https://api.postcodes.io/**',route=>route.fulfill({
      json:route.request().method()==='POST'?{result:[]}:
        {result:{postcode:'DL5 4RQ',latitude:54.618,longitude:-1.571}}
    }));
    let requests=0,unblock;
    const held=new Promise(resolve=>{unblock=resolve;});
    await context.route(/\/competition\.json\?t=/,async route=>{
      requests++;
      await held;
      return source==='live'?route.continue():route.abort();
    });
    if(source==='unavailable')await context.route(/\/competition-fallback\.json\?t=/,route=>route.abort());
    const page=await context.newPage();
    await page.goto(host+entry);
    const app=page.frameLocator('#phoneApp');
    await app.getByRole('link',{name:'Start Campaign',exact:true}).click();
    const laws=app.frameLocator('.tffc-exact-master-frame');
    const status=laws.locator('#clubfinder-status');
    assert.equal(await status.innerText(),'Competition data not yet requested');
    assert.equal(requests,0);
    await laws.locator('#postcode').fill('DL5 4RQ');
    await laws.getByRole('button',{name:'Find My Club'}).click();
    await laws.getByText('Loading competition data',{exact:false}).waitFor();
    unblock();
    if(source==='unavailable'){
      await laws.getByText('Competition data unavailable.',{exact:false}).waitFor();
    }else {
      const signal=source==='live'?/Live · Data (?:updated|last checked):/:/Using embedded competition snapshot — canonical data unavailable/;
      await laws.getByText(signal).waitFor();
      assert.match(await app.locator('#liveDataBadge').textContent(),signal);
    }
    assert.equal(requests,1);
    await context.close();
  }
} finally {
  await browser.close();
}
console.log('Public, installed and Shed status distinguish idle, canonical, fallback and unavailable data.');
