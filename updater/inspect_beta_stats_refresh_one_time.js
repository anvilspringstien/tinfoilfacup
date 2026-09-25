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
const regressionFile=path.join(__dirname,'beta_campaign_identity_regression.js');
const regression=fs.readFileSync(regressionFile,'utf8');
const marker='  // Execute the real Clubfinder -> Challenges producer path';
if(regression.split(marker).length!==2)throw new Error('Regression splice anchor drift');
const injected=`  await journeyCertificate(origin);
  console.log('STATS_RENDER_PROBE',JSON.stringify({
    characters:certificateHtml.length,
    bytes:Buffer.byteLength(certificateHtml,'utf8'),
    base64Tags:(certificateHtml.match(/src="data:image[^"]*/g)||[]).map(x=>x.length),
    url:window.location.href,
    start:certificateHtml.slice(0,160),
    end:certificateHtml.slice(-600)
  }));
`;
const patched=regression.replace(marker,injected+marker);
const m=new Module(regressionFile,module);m.filename=regressionFile;m.paths=Module._nodeModulePaths(__dirname);m._compile(patched,regressionFile);
