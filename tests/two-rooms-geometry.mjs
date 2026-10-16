import {chromium} from 'playwright';
const browser=await chromium.launch();const sizes=[[1680,889],[1440,900],[1280,720],[1024,768],[390,844],[768,1024],[390,645]];
let failures=0;
for(const [width,height] of sizes){
 const values=[];
 for(const name of ['splash','clubfinder']){
  const page=await browser.newPage({viewport:{width,height}});
  await page.goto('http://127.0.0.1:8765/beta/two-rooms-'+name+'.html');
  const geometry=await page.evaluate(()=>Object.fromEntries(['.field','.crest'].map(s=>{const r=document.querySelector(s).getBoundingClientRect();return [s,['top','left','width','height'].map(k=>+r[k].toFixed(2))]})));
  values.push(geometry);await page.close();
 }
 for(const key of ['.field','.crest'])for(let i=0;i<4;i++)if(Math.abs(values[0][key][i]-values[1][key][i])>1)failures++;
 console.log(width+'x'+height,JSON.stringify(values),failures?'differences detected':'matched');
}

const mobile=await browser.newPage({viewport:{width:390,height:645},isMobile:true,hasTouch:true});
await mobile.goto('http://127.0.0.1:8765/beta/clubfinder-journey.html');
const master=mobile.frameLocator('iframe.tffc-exact-master-frame');
await master.locator('.clubfinder-search input').waitFor({timeout:15000});
await mobile.waitForFunction(()=>{
 const doc=document.querySelector('iframe.tffc-exact-master-frame')?.contentDocument;
 return !!doc?.getElementById('tffc-ios-postcode-nozoom');
},{timeout:15000});
const size=await master.locator('.clubfinder-search input').evaluate(el=>parseFloat(getComputedStyle(el).fontSize));
if(size<16){console.error('iOS postcode focus zoom risk:',size);failures++;}
await mobile.close();
await browser.close();if(failures)process.exitCode=1;
