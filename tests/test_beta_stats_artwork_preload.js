const fs=require('fs');
const html=fs.readFileSync('beta/clubfinder-beta.html','utf8');
function assert(cond,msg){if(!cond)throw new Error(msg);}

const assets=[
  'assets/stats-report/header-logo-f533fc07b55f.png',
  'assets/stats-report/rounds-completed-b2fef60a225c.png',
  'assets/stats-report/matches-played-298ff9e75570.png',
  'assets/stats-report/clubs-encountered-ef3c16d79856.png',
  'assets/stats-report/goals-seen-7de1249b67bf.png',
  'assets/stats-report/grounds-visited-6848e3eb51f9.png',
  'assets/stats-report/pigeon-miles-flown-143c833d4cdf.png'
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

const reportImages=[...html.matchAll(/assets\/stats-report\/[^"'\\]+\.png/g)].map(m=>m[0]);
assert(reportImages.length===7&&new Set(reportImages).size===7,
  'Stats renderer must retain exactly seven literal artwork references');

const statsDoc=html.indexOf('</style></head><body><main class="sheet"><div class="stats-return">');
assert(statsDoc>=0,'Stats return control must be inside the Stats sheet');
const top=html.indexOf('<section class="top">',statsDoc);
const ret=html.indexOf('<div class="stats-return">',statsDoc);
assert(ret>=statsDoc&&ret<top,'Stats return control must precede report header inside sheet');
assert(!html.includes('</style></head><body><div class="stats-return">'),
  'Stats return control must not remain outside the sheet');

console.log('BETA STATS ARTWORK PRELOAD + RETURN CONTROL: PASS');
