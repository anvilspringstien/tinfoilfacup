const fs=require('fs');
const html=fs.readFileSync('beta/challenges-beta.html','utf8');
function need(rx,msg){if(!rx.test(html)){console.error(msg);process.exit(1);}}
need(/\.beta-sim-panel\{[\s\S]*?padding:8px 14px;/,'Collapsed desktop door must have balanced 8px vertical padding');
need(/\.beta-sim-panel:has\(\.beta-sim-toggle\[aria-expanded="true"\]\)\{padding-bottom:28px\}/,'Desktop open depth must be restored only when expanded');
need(/\.beta-sim-tools:not\(\[hidden\]\)\{margin-top:13px\}/,'Open tools gap must live below the stationary header');
if(/\.beta-sim-toggle\[aria-expanded="true"\]\{margin-bottom:/.test(html)){console.error('Title must not carry open-state spacing');process.exit(1);}
need(/@media\(max-width:560px\)[\s\S]*?\.beta-sim-panel\{width:calc\(100% - 20px\);padding:8px 10px;margin-bottom:34px\}/,'Collapsed mobile door must have balanced 8px vertical padding');
need(/@media\(max-width:560px\)[\s\S]*?\.beta-sim-panel:has\(\.beta-sim-toggle\[aria-expanded="true"\]\)\{padding-bottom:20px\}/,'Mobile open depth must be restored only when expanded');
need(/id="betaSimTools" hidden/,'Reveal must remain collapsed by default');
console.log('BETA balanced simulator door guard passed');
