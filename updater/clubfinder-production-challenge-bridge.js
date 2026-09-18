/* TIN_FOIL_PRODUCTION_CHALLENGE_BRIDGE_BEGIN */
const TIN_FOIL_CHALLENGE_BRIDGE_KEY='tffc.clubfinderCampaign.v1';
window.name='TFFC_CLUBFINDER'; window.TFFC_IS_CLUBFINDER=true;
function tinFoilChallengeRoundIndex(round){
 const s=String(round||'').toLowerCase();
 if(/extra preliminary/.test(s))return 0;if(/preliminary/.test(s)&&!/qualifying/.test(s))return 1;
 if(/first|1st/.test(s)&&/qualifying/.test(s))return 2;if(/second|2nd/.test(s)&&/qualifying/.test(s))return 3;
 if(/third|3rd/.test(s)&&/qualifying/.test(s))return 4;if(/fourth|4th/.test(s)&&/qualifying/.test(s))return 5;
 if(/first round/.test(s))return 6;if(/second round/.test(s))return 7;if(/third round/.test(s))return 8;if(/fourth round/.test(s))return 9;if(/fifth round/.test(s))return 10;
 if(/quarter/.test(s))return 11;if(/semi/.test(s))return 12;if(/final/.test(s))return 13;return 0;
}
window.tffcOpenStatsFromChallenges=function(originName,suppliedWindow){
  const origin=ELIGIBLE.find(c=>norm(c.name)===norm(originName));
  if(!origin){try{if(suppliedWindow&&!suppliedWindow.closed)suppliedWindow.close();}catch(e){} return false;}
  journeyCertificate(origin,suppliedWindow,"challenges");
  return true;
};

function tinFoilChallengeStatsSnapshot(origin,journey,crumbs,saved,pigeonMiles){
  function venueForStats(r){
    const v=completedResultVenue(r);
    return {ground:v.ground||'Venue TBC',postcode:v.postcode||'Postcode TBC'};
  }
  function dateLabel(v){if(!v)return 'Date TBC';const d=new Date(v+'T12:00:00');return Number.isNaN(d.getTime())?v:d.toLocaleDateString('en-GB',{day:'numeric',month:'short',year:'numeric'});}
  const carrier=journey.carrier||origin,clubs=[]; const addClub=n=>{if(n&&!clubs.some(x=>norm(x)===norm(n)))clubs.push(n)};
  addClub(origin.name); let goals=0,homeGames=0,awayGames=0,wins=0,draws=0,defeats=0,pathCarrier=origin.name; const venueKeys=new Set(),history=[];
  for(const cr of crumbs){const r=cr.result||{};addClub(r.home);addClub(r.away);const hs=Number(r.home_score),as=Number(r.away_score);if(Number.isFinite(hs))goals+=hs;if(Number.isFinite(as))goals+=as;const v=venueForStats(r);if(v.ground!=='Venue TBC'||v.postcode!=='Postcode TBC')venueKeys.add((v.ground||'')+'|'+(v.postcode||''));if(norm(r.home)===norm(pathCarrier))homeGames++;if(norm(r.away)===norm(pathCarrier))awayGames++;if(Number.isFinite(hs)&&Number.isFinite(as)&&hs===as)draws++;const canonicalWinner=tinFoilCertificateWinner(r);if(canonicalWinner){if(norm(canonicalWinner)===norm(pathCarrier))wins++;else if(norm(r.home)===norm(pathCarrier)||norm(r.away)===norm(pathCarrier))defeats++;pathCarrier=canonicalWinner;}history.push({round:cr.round||r.round||'FA Cup',fixture:resultLinePlain(r),date:dateLabel(r.date),ground:v.ground,postcode:v.postcode,winner:tinFoilCertificateWinner(r)});}
  addClub(carrier.name); const roundNames=new Set(crumbs.map(x=>String(x.round||((x.result||{}).round)||'FA Cup').replace(/\s+Replay$/i,'')));
  const currentState=competitionState(carrier),next=nextRoundInfo(carrier);let nextUp={round:'Upcoming Round TBC',fixture:'Next fixture TBC',meta:'Date TBC',venue:''};
  if(currentState&&currentState.type==='replay'&&currentState.replay){const rp=currentState.replay,rv=replayVenue(rp);nextUp={round:rp.round||'Replay',fixture:(rp.home||'')+' v '+(rp.away||''),meta:dateLabel(rp.date)+' • '+(rp.kickoff||'Kick-off TBC'),venue:(rv.ground&&rv.ground!=='Venue TBC')?rv.ground+(rv.postcode&&rv.postcode!=='Postcode TBC'?' • '+rv.postcode:''):''};}
  else if(next&&next.knownFixture){const k=next.knownFixture,v=k.venue||{};nextUp={round:next.name||k.round||'Next Round',fixture:(k.home||'')+' v '+(k.away||''),meta:dateLabel(k.date)+' • '+(k.kickoff||'Kick-off TBC'),venue:(v.ground&&v.ground!=='Venue TBC')?v.ground+(v.postcode&&v.postcode!=='Postcode TBC'?' • '+v.postcode:''):''};}
  else if(next){nextUp={round:next.name||'Next Round',fixture:'Draw / fixture TBC',meta:next.date||'Date TBC',venue:''};}
  return {season:'2026–27',origin:origin.name,currentCustodian:carrier.name,rounds:roundNames.size,matches:crumbs.length,clubs:clubs.length,goals,grounds:venueKeys.size,pigeonMiles:Math.round(Number(pigeonMiles)||0),homeGames,awayGames,wins,draws,defeats,history,nextUp};
}

async function openChallenges(origin){
 const journey=buildJourney(origin),crumbs=journey.breadcrumbs||[],saved=loadSavedJourney();
 let away=0,pathCarrier=origin.name;
 for(const cr of crumbs){const r=cr.result||{};if(norm(r.away||'')===norm(pathCarrier))away++;const hs=Number(r.home_score),as=Number(r.away_score);if(Number.isFinite(hs)&&Number.isFinite(as)&&hs!==as)pathCarrier=hs>as?r.home:r.away;}
 function venueForChallenge(r){return completedResultVenue(r);}
 const pm=await tinFoilPigeonMilesForStats(crumbs,saved&&saved.postcode,venueForChallenge);
 let ri=0;crumbs.forEach(cr=>ri=Math.max(ri,tinFoilChallengeRoundIndex((cr.result||{}).round)));
 const texts=[journey.round,journey.nextRound,journey.fixture&&journey.fixture.round,journey.next&&journey.next.round];texts.forEach(x=>ri=Math.max(ri,tinFoilChallengeRoundIndex(x)));
 const statsSnapshot=tinFoilChallengeStatsSnapshot(origin,journey,crumbs,saved,Number.isFinite(pm.miles)?pm.miles:0);
 const truth={source:'Clubfinder v7.6',originName:origin.name,currentCustodian:(journey.carrier||origin).name,postcode:saved&&saved.postcode||'',tiesPlayed:crumbs.length,awayTies:away,pigeonMiles:Number.isFinite(pm.miles)?pm.miles:0,campaignRound:ri,ended:!!(saved&&saved.ended),statsSnapshot,updatedAt:new Date().toISOString()};
 localStorage.setItem(TIN_FOIL_CHALLENGE_BRIDGE_KEY,JSON.stringify(truth));
 /* CANDIDATE 13 FIX — same-tab Challenges launch; Exit returns via browser history. */
 window.location.href='beta/challenges-beta.html';
}
/* TIN_FOIL_PRODUCTION_CHALLENGE_BRIDGE_END */
