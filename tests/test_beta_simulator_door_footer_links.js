const fs=require('fs');
const html=fs.readFileSync('beta/challenges-beta.html','utf8');
function need(rx,msg){if(!rx.test(html)){console.error(msg);process.exit(1);}}
need(/\.beta-sim-panel:has\(\.beta-sim-toggle\[aria-expanded="false"\]\)\{padding:8px 14px\}/,'Collapsed desktop simulator door is not compact');
need(/\.beta-sim-panel:has\(\.beta-sim-toggle\[aria-expanded="false"\]\)\{padding:8px 10px\}/,'Collapsed mobile simulator door is not compact');
need(/id="betaSimTools" hidden/,'Simulator tools must remain collapsed by default');
need(/id="challengePrivacyLinkFooter"/,'Always-visible footer Privacy control missing');
need(/challengePrivacyLinkFooter\.onclick=.*tinFoilPrivacyNotice/,'Footer Privacy control is not wired to the existing notice');
const sales=html.indexOf('class="deck-sales-tease"');
const footer=html.indexOf('class="beta-help deck-footer-help"');
if(sales<0||footer<sales){console.error('Tester links are not below Like the Beer Mats');process.exit(1);}
for(const label of ['Feedback','Report an Issue','Privacy'])if(html.slice(footer,footer+1800).indexOf(label)<0){console.error('Footer tester link missing: '+label);process.exit(1);}
console.log('BETA simulator door/footer links guard passed');
