#!/usr/bin/env node
const fs=require('fs'), path=require('path'), Module=require('module');
const root=path.resolve(__dirname,'..');
const source=fs.readFileSync(path.join(root,'beta/clubfinder-beta.html'),'utf8');
const start=source.indexOf('async function journeyCertificate(');
if(start<0)throw new Error('Expected Stats source missing');
for(const token of ['const w=suppliedWindow || window.open','const doc=', 'w.document.open(', 'w.document.write(', 'w.document.close(', 'w.location', 'return w']){
 let startAt=start, count=0;
 while(count++<4){
  const p=source.indexOf(token,startAt);
  if(p<0)break;
  const excerpt=source.slice(Math.max(start,p-160),Math.min(source.length,p+520));
  console.log('SOURCE_ANCHOR',JSON.stringify({token,offset:p,excerpt}));
  startAt=p+token.length;
 }
}
for(const token of ['journeyCertificate(', 'tinFoilMaybeOpenCanonicalStatsRoute(', 'stats=1', 'window.open(', 'window.location.href=']){
 let at=source.indexOf('async function journeyCertificate('),num=0;
 while(num++<10){let p=source.indexOf(token,at);if(p<0)break;
 console.log('STATS_CALLSITE',JSON.stringify({token,offset:p,excerpt:source.slice(Math.max(0,p-240),Math.min(source.length,p+580))}));
 at=p+token.length;
 }
}
const regressionFile=path.join(__dirname,'beta_campaign_identity_regression.js');
const regression=fs.readFileSync(regressionFile,'utf8');
const marker='  // Execute the real Clubfinder -> Challenges producer path';
if(regression.split(marker).length!==2)throw new Error('Regression splice anchor drift');
const injected=`  await journeyCertificate(origin);
  console.log('STATS_RENDER_PROBE',JSON.stringify({
    characters:getCertificateHtml().length,
    bytes:new TextEncoder().encode(getCertificateHtml()).length,
    base64Tags:(getCertificateHtml().match(/src="data:image[^"]*/g)||[]).map(x=>x.length),
    url:window.location.href,
    start:getCertificateHtml().slice(0,160),
    end:getCertificateHtml().slice(-600)
  }));
`;
const patched=regression.replace(marker,injected+marker);
const m=new Module(regressionFile,module);m.filename=regressionFile;m.paths=Module._nodeModulePaths(__dirname);m._compile(patched,regressionFile);
