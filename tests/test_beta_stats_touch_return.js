const fs=require('fs');
const html=fs.readFileSync('beta/clubfinder-beta.html','utf8');
function assert(cond,msg){if(!cond)throw new Error(msg);}

assert(html.includes('<meta name="viewport" content="width=980">'),
  'Stats report must retain its existing 980px printable/pinchable viewport');

const sticky="@media (hover:none) and (pointer:coarse){.stats-return{position:sticky;top:calc(env(safe-area-inset-top) + 56px);z-index:20}}";
assert(html.includes(sticky),
  'Touch Stats return control must remain sticky below browser chrome');

assert(html.includes('<main class="sheet"><div class="stats-return">'),
  'Stats return control must remain inside the Stats sheet');

console.log('BETA STATS TOUCH RETURN VISIBILITY: PASS');
