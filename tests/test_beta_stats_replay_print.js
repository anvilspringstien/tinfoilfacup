const fs=require('fs');
const html=fs.readFileSync('beta/clubfinder-beta.html','utf8');
function must(re,msg){if(!re.test(html)){console.error(msg);process.exit(1);}}
must(/const homeUnresolved=\/\\s\+or\\s\+\/i\.test\(home\);[\s\S]{0,260}if\(!homeUnresolved&&home\)/,'venue must depend on home-side certainty only');
must(/after-label">NEXT ROUND DRAW<\/div>/,'known post-replay fixture must use neutral NEXT ROUND DRAW label');
if(/after-label">IF THROUGH<\/div>/.test(html)){console.error('presumptive IF THROUGH label remains');process.exit(1);}
must(/\.stats-return,\.print\{display:none!important\}/,'print navigation must be forcibly removed');
must(/@media print[\s\S]*?\.bottom>div\{min-height:0;padding:10px 12px\}/,'print bottom panels must compact safely');
console.log('BETA replay/print presentation guards passed');
