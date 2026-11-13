import { chromium } from 'playwright';
import { mkdir, writeFile } from 'node:fs/promises';

const base='http://127.0.0.1:8765';
const viewport={width:1680,height:889};
const browser=await chromium.launch({headless:true});
const results={viewport,measuredAt:new Date().toISOString()};
await mkdir('geometry-evidence',{recursive:true});
async function measure(page,url,frameSelector,crestSelector,label){
 await page.goto(base+url,{waitUntil:'domcontentloaded'});
 await page.evaluate(()=>document.fonts?.ready);
 await page.waitForTimeout(1800);
 const data=await page.evaluate(({frameSelector,crestSelector})=>{
  const box=(selector)=>{
   const e=document.querySelector(selector);
   if(!e)throw Error('Missing geometry element: '+selector);
   const r=e.getBoundingClientRect();
   return Object.fromEntries(['top','left','width','height'].map(k=>[k,Number(r[k].toFixed(2))]));
  };
  return {frame:box(frameSelector),crest:box(crestSelector),classes:document.documentElement.className,zoom:getComputedStyle(document.body).zoom};
 },{frameSelector,crestSelector});
 await page.screenshot({path:'geometry-evidence/'+label+'.png',fullPage:true});
 return data;
}
let failed=false;
try{
 const page=await browser.newPage({viewport,deviceScaleFactor:1});
 results.splash=await measure(page,'/index.html','.stage .field','.stage .crest','splash');
 results.clubfinder=await measure(page,'/beta/clubfinder-beta.html?geometryProof=1','#tffcFourLaws .tffcOuter','#tffcFourLaws .tffcCrest','clubfinder');
 const tolerance=1;
 results.differences={};
 for(const part of ['frame','crest']){
  results.differences[part]={};
  for(const key of ['top','left','width','height']){
   const delta=Number((results.clubfinder[part][key]-results.splash[part][key]).toFixed(2));
   results.differences[part][key]=delta;
   if(Math.abs(delta)>tolerance)failed=true;
  }
 }
 if(!results.clubfinder.classes.includes('tffc-geometry-proof')){failed=true;results.activationError='Geometry proof class not activated';}
 console.log(JSON.stringify(results,null,2));
 await writeFile('geometry-evidence/measurements.json',JSON.stringify(results,null,2));
 if(failed){console.error('FAIL: Splash and Clubfinder frame/crest geometry differ by more than 1px.');process.exitCode=1;}
 else console.log('PASS: matching frame and crest geometry within 1px.');
 await page.close();
}catch(error){console.error(error);process.exitCode=1;}
finally{await browser.close();}
