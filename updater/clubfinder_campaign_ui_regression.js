#!/usr/bin/env node
const fs=require('fs');
const html=fs.readFileSync('clubfinder.html','utf8');
function requireIt(ok,msg){if(!ok){console.error('CLUBFINDER CAMPAIGN UI REGRESSION: FAIL - '+msg);process.exit(1);}}
const pm=html.indexOf('/* TIN_FOIL_PIGEON_MILES_GLANCE */');
requireIt(pm>=0,'Pigeon Miles At-a-Glance marker missing');
const pmSlice=html.slice(pm,pm+180000);
requireIt(pmSlice.includes('alt="Pigeon Miles Flown"'),'approved Pigeon Miles artwork missing');
requireIt(pmSlice.includes('data:image/png;base64,'),'Pigeon Miles artwork is not embedded');
requireIt(!pmSlice.slice(0,1000).includes('🐦'),'emoji Pigeon Miles fallback still present');
requireIt(html.includes('.g-num{font-stretch:condensed;font-family:Arial Narrow,Arial,Helvetica,sans-serif;font-size:20pt;font-weight:700;line-height:1;white-space:nowrap}'),'Pigeon Miles value can wrap');
requireIt(html.includes("const TIN_FOIL_CHALLENGE_BRIDGE_KEY='tffc.clubfinderCampaign.v1';"),'Challenges bridge key missing');
requireIt(html.includes("window.open('beta/challenges-beta.html','_blank');"),'production Challenges path incorrect');
requireIt(html.includes("window.name='TFFC_CLUBFINDER'"),'Clubfinder window identity missing');
requireIt(html.includes('window.tffcOpenStatsFromChallenges='),'Challenges-to-Stats bridge missing');
requireIt(html.includes('async function openChallenges(origin)'),'Challenges launcher function missing');
requireIt(html.includes('async function journeyCertificate(origin, suppliedWindow=null, returnMode="clubfinder")'),'Stats return-mode integration missing');
requireIt(html.includes('Back to Challenges'),'Stats Challenges return button missing');
requireIt(html.includes('.challenges-launch{background:#e4bb26!important;color:#111!important}'),'yellow Challenges styling missing');
const launch=(html.match(/class="round challenges-launch"/g)||[]).length;
requireIt(launch===1,`expected exactly one Challenges launcher, found ${launch}`);
requireIt(html.includes("openChallenges(ELIGIBLE.find(c=>norm(c.name)===norm("),'Challenges launcher is not wired to selected Campaign origin');
console.log('CLUBFINDER CAMPAIGN UI REGRESSION: PASS');
console.log('Approved Pigeon Miles roundel, no-wrap value, yellow Challenges launcher and Candidate 13 bridge are present.');
