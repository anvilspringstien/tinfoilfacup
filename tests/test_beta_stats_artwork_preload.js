const fs=require('fs');
const html=fs.readFileSync('beta/clubfinder-beta.html','utf8');
function assert(cond,msg){if(!cond)throw new Error(msg);}

const assets=[
  'assets/stats-report/header-logo-f533fc07b55f.png',
  '../assets/stats/rounds-completed.svg',
  '../assets/stats/matches-played.svg',
  '../assets/stats/clubs-encountered.svg',
  '../assets/stats/goals-seen.svg',
  '../assets/stats/grounds-visited.svg',
  '../assets/stats/pigeon-miles-flown.svg'
];
const prepStart=html.indexOf("Preparing Your Stats");
assert(prepStart>=0,'Stats prep page missing');
const prepWindow=html.slice(Math.max(0,prepStart-7000),prepStart+4500);
assert(prepWindow.includes("journeyCertificate.toString()"),
  'Stats prep must derive preload assets from the existing renderer');
assert(prepWindow.includes("link.rel='preload';link.as='image';link.href=asset"),
  'Stats prep must create image preload links');
assert(prepWindow.includes("if(asset.includes('header-logo-'))link.fetchPriority='high'"),
  'Stats header logo preload must have high fetch priority');

const reportPngs=[...html.matchAll(/assets\/stats-report\/[^"'\\]+\.png/g)].map(m=>m[0]);
const reportSvgs=[...html.matchAll(/\.\.\/assets\/stats\/[^"'\\]+\.svg/g)].map(m=>m[0]);
assert(reportPngs.length===1&&reportPngs[0].includes('header-logo-'),
  'Stats renderer must retain only the header logo PNG');
assert(reportSvgs.length===6&&new Set(reportSvgs).size===6,
  'Stats renderer must use the six SVG roundel masters');

const statsDoc=html.indexOf('</style></head><body><main class="sheet"><div class="stats-return">');
assert(statsDoc>=0,'Stats return control must be inside the Stats sheet');
const top=html.indexOf('<section class="top">',statsDoc);
const ret=html.indexOf('<div class="stats-return">',statsDoc);
assert(ret>=statsDoc&&ret<top,'Stats return control must precede report header inside sheet');
assert(!html.includes('</style></head><body><div class="stats-return">'),
  'Stats return control must not remain outside the sheet');

console.log('BETA STATS ARTWORK PRELOAD + RETURN CONTROL: PASS');
