import { chromium } from 'playwright';
import { mkdir, writeFile } from 'node:fs/promises';
const origin='http://127.0.0.1:8765';
const sizes=[[1680,889],[1440,900],[1280,720],[1024,768],[390,844]];
await mkdir('geometry-evidence',{recursive:true});
const browser=await chromium.launch({headless:true});
let failed=false;const report=[];
for(const [width,height] of sizes){
 const results=[];
 for(const kind of ['splash','clubfinder']){
  const page=await browser.newPage({viewport:{width,height},deviceScaleFactor:1});
  await page.goto(origin+'/beta/shared-frame-'+kind+'-proof.html',{waitUntil:'load'});
  await page.evaluate(()=>document.fonts.ready);
  await page.waitForTimeout(400);
  const measure=await page.evaluate(()=>{
   const rect=selector=>{const r=document.querySelector(selector).getBoundingClientRect();return Object.fromEntries(['top','left','width','height'].map(k=>[k,Number(r[k].toFixed(2))]));};
   return {frame:rect('.stage .field'),crest:rect('.stage .crest'),fit:document.documentElement.classList.contains('tffc-viewport-fit')};
  });
  await page.screenshot({path:'geometry-evidence/'+kind+'-'+width+'x'+height+'.png',fullPage:true});
  results.push(measure);await page.close();
 }
 const diffs={};
 for(const element of ['frame','crest'])for(const dimension of ['top','left','width','height']){
  const delta=Number((results[1][element][dimension]-results[0][element][dimension]).toFixed(2));
  diffs[element+'.'+dimension]=delta;if(Math.abs(delta)>1)failed=true;
 }
 report.push({viewport:{width,height},splash:results[0],clubfinder:results[1],differences:diffs});
}
await browser.close();
await writeFile('geometry-evidence/report.json',JSON.stringify(report,null,2));
console.log(JSON.stringify(report,null,2));
if(failed){console.error('FAIL: shared frame proof geometry differs by more than 1px');process.exitCode=1;}
else console.log('PASS: both proof pages match within 1px across all viewports');
