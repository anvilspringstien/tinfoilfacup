const fs=require('fs');
const html=fs.readFileSync('beta/challenges-beta.html','utf8');
function need(rx,msg){if(!rx.test(html)){console.error(msg);process.exit(1);}}
need(/\.beta-sim-panel\{[\s\S]*?padding:8px 14px 28px;/,'Desktop simulator top padding must stay at the collapsed 8px');
need(/@media\(max-width:560px\)[\s\S]*?\.beta-sim-panel\{width:calc\(100% - 20px\);padding:8px 10px 20px;/,'Mobile simulator top padding must stay at 8px');
if(/\.beta-sim-panel:has\(\.beta-sim-toggle\[aria-expanded="false"\]\)\{padding:/.test(html)){console.error('Collapsed-only panel padding would reintroduce title movement');process.exit(1);}
need(/\.beta-sim-toggle\[aria-expanded="true"\]\{margin-bottom:13px\}/,'Open-state spacing below the fixed title must remain');
need(/id="betaSimTools" hidden/,'Reveal mechanics must remain collapsed by default');
console.log('BETA simulator title position guard passed');
