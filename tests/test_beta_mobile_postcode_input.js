const fs=require('fs');
const html=fs.readFileSync('beta/clubfinder-beta.html','utf8');
function assert(cond,msg){if(!cond)throw new Error(msg);}

assert(html.includes('@media(max-width:480px){#searchPanel{padding:20px 8px;gap:6px}#findBtn{padding:0 9px;font-size:13px}#postcode{font-size:16px;padding:0 8px}}'),
  'Mobile postcode input must remain 16px to prevent iOS focus zoom');

assert(html.includes('id="postcode"')&&html.includes('enterkeyhint="search"'),
  'Postcode field should expose a search/return keyboard hint');

const handler="document.getElementById('postcode').addEventListener('keydown',e=>{if(e.key==='Enter'){e.preventDefault();e.currentTarget.blur();go(true)}});";
assert(html.includes(handler),
  'Return key must blur the postcode field before running Find My Club');

console.log('BETA MOBILE POSTCODE INPUT: PASS');
