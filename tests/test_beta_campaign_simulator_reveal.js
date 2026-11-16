const fs=require('fs');
const html=fs.readFileSync('beta/challenges-beta.html','utf8');
function need(rx,msg){if(!rx.test(html)){console.error(msg);process.exit(1);}}
need(/id="betaSimToggle"[^>]*aria-expanded="false"[^>]*aria-controls="betaSimTools"[^>]*>BETA – Campaign Progress Simulator – BETA<\/button>/,'Simulator reveal control missing or not collapsed');
need(/class="beta-sim-tools" id="betaSimTools" hidden/,'Simulator tools must start hidden');
need(/betaSimTools\.hidden=!opening/,'Simulator reveal must toggle existing tools');
need(/betaSimToggle\.setAttribute\("aria-expanded",String\(opening\)\)/,'Simulator reveal must expose expanded state');
for(const id of ['addTie','addAwayTie','campaignRound','addPigeonMiles','simulateGiantKill','reset']){
 need(new RegExp('id="'+id+'"'),'Existing simulator control missing: '+id);
}
console.log('BETA Campaign simulator reveal guard passed');
