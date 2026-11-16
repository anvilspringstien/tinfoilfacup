const fs=require('fs');
const html=fs.readFileSync('beta/clubfinder-beta.html','utf8');
const p=html.indexOf('Preparing Your Stats…');
if(p<0){console.error('Stats Preparing document not found');process.exit(1);}
const prep=html.slice(Math.max(0,p-2600),p+300);
if(!/html,body\{min-height:100%;min-height:100vh\}/.test(prep)){console.error('Stats Preparing must establish viewport height');process.exit(1);}
if(!/@supports\(height:100dvh\)\{html,body\{min-height:100dvh\}\}/.test(prep)){console.error('Stats Preparing must use dynamic viewport height when supported');process.exit(1);}
if(!/body\{margin:0;display:grid;place-items:center;/.test(prep)){console.error('Stats Preparing must centre its card');process.exit(1);}
console.log('BETA Stats Preparing centring guard passed');
