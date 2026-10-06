const fs=require('fs');
const html=fs.readFileSync('beta/clubfinder-beta.html','utf8');
function assert(cond,msg){if(!cond)throw new Error(msg);}

const assets=[
  'assets/stats-report/header-logo-q80.webp',
  'assets/stats-report/rounds-completed-q80.webp',
  'assets/stats-report/matches-played-q80.webp',
  'assets/stats-report/clubs-encountered-q80.webp',
  'assets/stats-report/goals-seen-q80.webp',
  'assets/stats-report/grounds-visited-q80.webp',
  'assets/stats-report/pigeon-miles-flown-q80.webp'
];
const prepStart=html.indexOf("Preparing Your Stats");
assert(prepStart>=0,'Stats prep page missing');
const prepWindow=html.slice(Math.max(0,prepStart-7000),prepStart+4500);
assert(prepWindow.includes("journeyCertificate.toString()"),
  'Stats prep must derive preload assets from the existing renderer');
assert(prepWindow.includes("link.rel='preload';link.as='image';link.href=asset"),
  'Stats prep must create image preload links');
assert(prepWindow.includes("\\.(?:png|webp)/g"),
  'Stats prep asset discovery must include q80 WebP artwork');
assert(prepWindow.includes("if(asset.includes('header-logo-'))link.fetchPriority='high'"),
  'Stats header logo preload must have high fetch priority');

const writeStart=html.indexOf("if(w){",prepStart);
const writeEnd=html.indexOf("async function tinFoilRenderStatsFromOpener",writeStart);
const writeBlock=html.slice(writeStart,writeEnd);
assert(writeBlock.includes("await Promise.all(assets.map(asset=>new Promise(resolve=>"),
  'Stats report must keep Preparing visible while report artwork loads');
assert(writeBlock.includes("if(typeof img.decode==='function')await img.decode()"),
  'Stats report must wait for image decode before revealing the report');
assert(writeBlock.includes("img.onerror=finish"),
  'Stats artwork failure must fail open instead of trapping the Preparing screen');
assert(writeBlock.indexOf("await Promise.all(assets.map(asset=>new Promise(resolve=>")<writeBlock.indexOf("w.document.open();"),
  'Stats artwork readiness must complete before replacing the Preparing document');

const reportImages=[...html.matchAll(/assets\/stats-report\/[^"'\\]+\.(?:png|webp)/g)].map(m=>m[0]);
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
