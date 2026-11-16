const fs=require('fs');
const html=fs.readFileSync('beta/challenges-beta.html','utf8');

const rules=[...html.matchAll(/\.deck-feedback\s*\{([\s\S]*?)\}/g)];
if(rules.length<2)throw new Error('Expected base and mobile Challenge feedback styles');

const heights=rules.map((rule,i)=>{
  const min=rule[1].match(/min-height\s*:\s*(\d+)px/);
  if(!min)throw new Error('Challenge feedback rule '+(i+1)+' has no min-height');
  return Number(min[1]);
});

if(heights[0]<39)throw new Error('Base Challenge feedback must reserve a two-line footprint (>=39px)');
if(heights.slice(1).some(h=>h<35))throw new Error('Mobile Challenge feedback override must reserve a two-line footprint (>=35px)');

if(!/display\s*:\s*flex/.test(rules[0][1]) || !/align-items\s*:\s*center/.test(rules[0][1]))
  throw new Error('Challenge feedback must remain vertically centred inside its reserved footprint');

console.log('BETA CHALLENGE FEEDBACK GEOMETRY: PASS', heights.join(','));
