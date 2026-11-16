const fs=require('fs');
const html=fs.readFileSync('beta/clubfinder-beta.html','utf8');
for(const token of [
  'CHALLENGE HONOURS',
  'challengeHonoursHtml',
  'finalChallengeHonours.length',
  "certEsc(h.verification.toUpperCase())",
  "tinFoilChallengeCampaignKey(bridge)===tinFoilChallengeCampaignKey(challengeTruth)"
]) if(!html.includes(token)) throw new Error('Missing Stats Challenge honours contract: '+token);
if(/challenge-honours[^\n]*<img/i.test(html)) throw new Error('Challenge honours must not add an artwork payload to Stats');
const campaignPos=html.indexOf('THE CAMPAIGN SO FAR');
const honoursPos=html.indexOf('challengeHonoursHtml+');
const statsPos=html.indexOf('<section class="bottom">');
if(!(campaignPos>=0&&honoursPos>campaignPos&&statsPos>honoursPos)) throw new Error('Challenge Honours must sit between Campaign history and the bottom Stats block');
console.log('BETA CHALLENGE HONOURS STATS PRESENTATION: PASS');
