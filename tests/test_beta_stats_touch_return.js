const fs=require('fs');
const html=fs.readFileSync('beta/clubfinder-beta.html','utf8');
function assert(cond,msg){if(!cond)throw new Error(msg);}

assert(html.includes('<meta name="viewport" content="width=980">'),
  'Stats report must retain its existing 980px printable/pinchable viewport');

assert(html.includes('.stats-actions{position:fixed;'),
  'Stats actions must stay fixed while the report scrolls');
assert(html.includes('frame.getBoundingClientRect().width/frame.offsetWidth'),
  'The fixed bar must account for the report frame scale');
assert(html.includes("viewport?.addEventListener('scroll',fitBar)"),
  'The bar must follow the visual viewport when panning');
assert(html.includes('padding-bottom:var(--stats-bottom-space,84px)'),
  'The final report content must be able to scroll above the bar');

console.log('BETA STATS TOUCH RETURN VISIBILITY: PASS');
