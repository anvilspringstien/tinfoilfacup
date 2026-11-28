import assert from 'node:assert/strict';
import {acceptedSplash} from './beta-approved-journey-splash-reference.mjs';
import {createHash} from 'node:crypto';
import {readFileSync} from 'node:fs';

const read=path=>readFileSync(path,'utf8');
const sha=path=>{
 const data=readFileSync(path);
 return createHash('sha1').update('blob '+data.length+'\0').update(data).digest('hex');
};
/* Review-controlled acceptance hashes. Change them only after approving a
   new design, never just to make the workflow pass. This does NOT freeze
   competition data or original BETA, which must keep updating. */
// Bridge hash includes the wheel-boundary fix; all visual master hashes stay fixed.
const approved={
 'beta/two-rooms-splash-locked.html':'9d0565eda94ea221e2c6689865ae26da31fc8894',
 'beta/two-rooms-splash-locked.css':'309779e2751e316695365fbb67d5238b9624eb4b',
 'beta/two-rooms-clubfinder.html':'789a0de355ec93211767eb7fbb9ccd513c0f7c13',
 'beta/two-rooms.css':'1f982dfecd70337234e0e43041eb6c77639e6706',
 'beta/two-rooms-shed-scrollbar.css':'a92c0386b383f4c701fa679c56e60d67597b34be',
 'beta/two-rooms-splash-iframe-proof.html':'243534419d8eff53e8858eec93fc7eb307979806',
 'beta/two-rooms-iframe-engine-proof.html':'e1d945be8ade01adc59642ef7eee339682b63204',
 'beta/two-rooms-iframe-engine.css':'c5e57adc4d8950a4ab47f9ff348145910e6ec42e',
};
for(const [path,expected] of Object.entries(approved)){
 assert.equal(sha(path),expected,'Approved locked source changed: '+path);
}
const noindex='<meta name="robots" content="noindex">';
const paintedSplash=path=>read(path).replace(noindex,'')
 .replace('splash-campaign-label.js?v=journey-paint-20261128','splash-campaign-label.js');
const permanentSplash=paintedSplash('beta/shed-splash.html');
assert.equal(paintedSplash('beta/public-splash.html'),acceptedSplash);
assert.ok(read('beta/index.html').includes('data-tffc-entrance="shed"'));
assert.ok(read('beta/index.html').includes('phone-frame-launch.js?v=journey-paint-20261128'));
const crest=permanentSplash.match(/<img class="crest shed-astral-crest" decoding="sync" src="data:image\/webp;base64,([A-Za-z0-9+/=]+)"/);
assert.ok(crest,'Shed entrance must inline the accepted static Astral Portal');
assert.equal(createHash('sha256').update(Buffer.from(crest[1],'base64')).digest('hex'),
 '95fd53512b9879556d2fe81fdf65dabad4bec567977e9bcc273bf385d875de9d',
 'Static Astral Portal artwork must match the accepted neutral composition');
const integration='<link rel="stylesheet" href="astral-portal.css?v=shed-paint-20261128"><script defer src="astral-portal.js?v=shed-paint-20261128"></script>';
assert.ok(permanentSplash.includes(integration));
assert.equal(permanentSplash.replace(integration,'')
 .replace(crest[0],'<img class="crest" src="tffc-splash-logo-q80.webp"'),
 acceptedSplash,
 'Shed entrance may change only the accepted crest and its enhancement');
const referenceEngine=read('beta/two-rooms-iframe-engine-proof.html');
const permanentEngine=read('beta/clubfinder-journey.html')
 .replaceAll('<meta name="color-scheme" content="dark">','')
 .replace(String.raw` const ready=()=>requestAnimationFrame(()=>requestAnimationFrame(()=>{\n  if(parent!==window)parent.postMessage({type:'tffc-journey-painted'},location.origin);\n }));\n`,'')
 .replace(String.raw`\n  if(parent!==window)parent.postMessage({type:'tffc-journey-painted'},location.origin);\n  return;\n }`,String.raw`\n  return;\n }`)
 .replace("frame.title='Four Laws master unavailable';ready();return;", "frame.title='Four Laws master unavailable';return;")
 .replace(String.raw`if(page.URL!=='about:blank'){frame.title='Four Laws master controls unavailable';ready();}return;}\n  ready();`,
  "frame.title='Four Laws master controls unavailable';return;}")
 .replace("}catch(error){\n  document.body.textContent='Shed proof could not load: '+error.message;\n  if(parent!==window)parent.postMessage({type:'tffc-journey-painted'},location.origin);\n }",
  "}catch(error){document.body.textContent='Shed proof could not load: '+error.message;}");
assert.equal(permanentEngine,referenceEngine
 .replace('<title>Shed — Splash to approved Four Laws to original BETA</title>','<title>Tin Foil FA Cup — BETA Clubfinder</title>')
 .replace("const response=await fetch('clubfinder-beta.html',{cache:'no-store'});",
 "try{sessionStorage.setItem('tffc.beta.approved-journey','1')}catch(_){}\n  const response=await fetch('clubfinder-beta.html',{cache:'no-store'});")
 .replace('two-rooms-iframe-engine.css','clubfinder-journey.css')
 .replace("const html=await response.text();","// Apply the dark canvas before fonts, stylesheets or body content can paint.\n  const html=(await response.text()).replace('<head>','<head><style>html{background:#141210!important;color-scheme:dark}body{background:#141210}</style>');")
 .replace("frame.setAttribute('loading','eager');","frame.setAttribute('loading','eager');\\n frame.style.background='#141210';\\n frame.style.colorScheme='dark';")
 .replace('</head>','<link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">\n'
  + '<link rel="icon" type="image/png" sizes="192x192" href="/tffac-icon-192.png">\n'
  + '<link rel="manifest" href="/tffac.webmanifest">\n</head>'),
 'BETA engine bridge must match the approved integration exactly');
assert.equal(read('beta/clubfinder-journey.css'),read('beta/two-rooms-iframe-engine.css'),
 'BETA CSS must match approved three-frame CSS');
const beta=read('beta/clubfinder-beta.html');
assert.ok(beta.includes('function resetFinder(){'));
assert.ok(beta.includes('async function hardResetFinder(){'));
assert.ok(beta.includes('function tffcScrollToFinder(){'));
assert.ok(beta.includes('function chooseJourney('));
const challenges=read('beta/challenges-beta.html');
assert.match(challenges,/sessionStorage\.getItem\('tffc\.beta\.approved-journey'\)==='1'/);
assert.match(challenges,/window\.location\.replace\('clubfinder-journey\.html\?from=challenges-exit-v3'\)/);
assert.match(challenges,/window\.location\.replace\('clubfinder-beta\.html\?from=challenges-exit-v3'\)/);
/* The public front door was separately approved. It must now be exactly
   the locked BETA Splash body, adjusted only for root-relative navigation
   and image paths. SEO/sharing metadata belongs to the public URL. */
const homepage=read('index.html');
const afterHead=html=>html.slice(html.indexOf('</head>')+7);
assert.equal(afterHead(homepage)
 .replace('href="beta/clubfinder-journey.html"','href="clubfinder-journey.html"')
 .replace('src="beta/tffc-splash-logo-q80.webp"','src="tffc-splash-logo-q80.webp"'),
 afterHead(acceptedSplash),
 'Public Splash body must match the separately approved Splash (except paths)');
for(const fragment of [
 '<script defer src="beta/splash-campaign-label.js"></script>',
 '<link rel="stylesheet" href="beta/phone-frame-shed.css">',
 '<script defer src="beta/phone-frame-launch.js?v=journey-paint-20261128"></script>',
 'href="beta/clubfinder-journey.html"',
 'src="beta/tffc-splash-logo-q80.webp"',
 'href="beta/two-rooms-splash-locked.css"',
 'href="beta/two-rooms-shed-scrollbar.css"',
 '<link rel="canonical" href="https://tinfoilfacup.com/">',
 'property="og:image" content="https://tinfoilfacup.com/beta/tffc-share-preview.png.png"',
 'property="og:url" content="https://tinfoilfacup.com/"',
 'name="twitter:card" content="summary_large_image"'
 ])assert.ok(homepage.includes(fragment),'Missing public homepage contract: '+fragment);
assert.ok(!homepage.includes('href="beta/clubfinder-beta.html"'),
 'Public Start must not bypass the approved three-frame journey');
console.log('Approved layout, Astral Portal artwork and separate Public Splash contracts passed.');
