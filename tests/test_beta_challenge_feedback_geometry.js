const fs=require('fs');
const html=fs.readFileSync('beta/challenges-beta.html','utf8');
const match=html.match(/\.deck-feedback\s*\{([\s\S]*?)\}/);
if(!match)throw new Error('Challenge deck feedback style missing');
const css=match[1];
const min=css.match(/min-height\s*:\s*(\d+)px/);
if(!min || Number(min[1])<39)throw new Error('Challenge feedback must reserve a two-line footprint (>=39px)');
if(!/display\s*:\s*flex/.test(css) || !/align-items\s*:\s*center/.test(css))throw new Error('Challenge feedback must remain vertically centred inside its reserved footprint');
console.log('BETA CHALLENGE FEEDBACK GEOMETRY: PASS');
