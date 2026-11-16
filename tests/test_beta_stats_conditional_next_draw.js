const fs=require('fs');
const html=fs.readFileSync('beta/clubfinder-beta.html','utf8');
const statsAnchor="const currentState=competitionState(carrier);\n  // Stats is a permanent record:";
const start=html.indexOf(statsAnchor);
if(start<0){console.error('Stats current-state block not found');process.exit(1);}
const block=html.slice(start,start+2400);
if(!/const next=nextRoundInfo\(carrier,true\);/.test(block)){console.error('Stats must preserve unresolved conditional next-round sides');process.exit(1);}
if(!/after-label">NEXT ROUND DRAW<\/div>/.test(block)){console.error('Stats conditional replay follow-on must remain labelled NEXT ROUND DRAW');process.exit(1);}
if(!/certEsc\(\(k\.home\|\|''\)\+' v '\+\(k\.away\|\|''\)\)/.test(block)){console.error('Stats must render the preserved canonical fixture sides');process.exit(1);}
console.log('BETA Stats conditional next-round draw guard passed');
