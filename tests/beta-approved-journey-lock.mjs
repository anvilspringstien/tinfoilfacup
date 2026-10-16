import assert from 'node:assert/strict';
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
const approved={
 'beta/two-rooms-splash-locked.html':'9d0565eda94ea221e2c6689865ae26da31fc8894',
 'beta/two-rooms-splash-locked.css':'309779e2751e316695365fbb67d5238b9624eb4b',
 'beta/two-rooms-clubfinder.html':'789a0de355ec93211767eb7fbb9ccd513c0f7c13',
 'beta/two-rooms.css':'1f982d6c3d70337234e0e43041eb6c77639e6706',
 'beta/two-rooms-shed-scrollbar.css':'a92c0386b383f4c701fa679c56e60d67597b34be',
 'beta/two-rooms-splash-iframe-proof.html':'243534419d8eff53e8858eec93fc7eb307979806',
 'beta/two-rooms-iframe-engine-proof.html':'cef56a18d00fefd7f4aa10647d7120f1240b5504',
 'beta/two-rooms-iframe-engine.css':'c5e57adc4d8950a4ab47f9ff348145910e6ec42e',
};
for(const [path,expected] of Object.entries(approved)){
 assert.equal(sha(path),expected,'Approved locked source changed: '+path);
}
const referenceSplash=read('beta/two-rooms-splash-iframe-proof.html');
const permanentSplash=read('beta/index.html');
assert.equal(permanentSplash,referenceSplash
 .replace('<title>Two rooms — Approved Master Splash</title>','<title>Tin Foil FA Cup — BETA</title>')
 .replace('href="two-rooms-iframe-engine-proof.html"','href="clubfinder-journey.html"'),
 'BETA entrance must remain exactly the accepted Splash');
const referenceEngine=read('beta/two-rooms-iframe-engine-proof.html');
const permanentEngine=read('beta/clubfinder-journey.html');
assert.equal(permanentEngine,referenceEngine
 .replace('<title>Shed — Splash to approved Four Laws to original BETA</title>','<title>Tin Foil FA Cup — BETA Clubfinder</title>')
 .replace("const response=await fetch('clubfinder-beta.html',{cache:'no-store'});",
 "try{sessionStorage.setItem('tffc.beta.approved-journey','1')}catch(_){}\n  const response=await fetch('clubfinder-beta.html',{cache:'no-store'});")
 .replace('two-rooms-iframe-engine.css','clubfinder-journey.css'),
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
const homepage=read('index.html');
assert.ok(homepage.includes('href="beta/clubfinder-beta.html"'),
 'Live homepage must retain its existing BETA target until separate production approval');
console.log('Approved visual sources frozen; BETA promoted snapshots exactly match. Existing production entry and legacy BETA route retained.');
