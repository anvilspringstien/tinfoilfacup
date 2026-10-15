import {chromium} from 'playwright';
import {mkdir,writeFile} from 'node:fs/promises';
const base='http://127.0.0.1:8765';
const sizes=[[1680,889],[1440,900],[1280,720],[1024,768],[390,844]];
await mkdir('splash-parity-evidence',{recursive:true});
const browser=await chromium.launch();
const results=[];
for(const [width,height] of sizes){
 const records=[];
 for(const [name,path] of [['approved','/index.html'],['proof','/beta/shared-frame-splash-proof.html']]){
  const page=await browser.newPage({viewport:{width,height},deviceScaleFactor:1});
  await page.goto(base+path,{waitUntil:'load'});
  await page.evaluate(()=>document.fonts.ready);
  await page.waitForTimeout(600);
  const rects=await page.evaluate(()=>{
   const box=selector=>{const el=document.querySelector(selector);if(!el)throw Error('Missing '+selector);const r=el.getBoundingClientRect();return Object.fromEntries(['top','left','width','height'].map(k=>[k,+r[k].toFixed(2)]));};
   return {frame:box('.field'),crest:box('.crest')};
  });
  await page.screenshot({path:'splash-parity-evidence/'+name+'-'+width+'x'+height+'.png',fullPage:true});
  records.push(rects);await page.close();
 }
 const differences={};
 for(const element of ['frame','crest'])for(const dim of ['top','left','width','height'])differences[element+'.'+dim]=+(records[1][element][dim]-records[0][element][dim]).toFixed(2);
 results.push({viewport:width+'x'+height,approved:records[0],proof:records[1],differences});
}
await browser.close();
await writeFile('splash-parity-evidence/report.json',JSON.stringify(results,null,2));
console.log(JSON.stringify(results,null,2));
const mismatches=results.flatMap(r=>Object.entries(r.differences).filter(([,delta])=>Math.abs(delta)>1).map(([key,delta])=>r.viewport+' '+key+' '+delta));
if(mismatches.length){console.error('FAIL: approved Splash parity differs beyond 1px:',mismatches);process.exitCode=1;}else console.log('PASS: approved Splash geometry parity within 1px');
