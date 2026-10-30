import {clubDetails} from './club-details-model.mjs';
const $=id=>document.getElementById(id);
try{
 const read=async url=>{const response=await fetch(url,{cache:'no-store'});if(!response.ok)throw Error('The published details could not be loaded. Please try again, or reply to your email.');return response.json();};
 const [queue,competition,reviewed]=await Promise.all([read('../updater/club_website_audit_queue.json'),read('../competition.json'),read('../updater/club_website_verified_batch_04.json')]);
 const data=clubDetails(new URLSearchParams(location.search).get('club'),queue,competition,reviewed);
 $('club-name').textContent=data.club;$('club-value').textContent=data.club;document.title=data.club+' — Tin Foil FA Cup';
 if(data.website){const link=document.createElement('a');link.href=data.website;link.target='_blank';link.rel='noopener noreferrer';link.textContent=data.website;$('website').append(link);}else $('website').textContent='No verified website is currently published.';
 if(data.fixture){
  const f=data.fixture;$('round').textContent=f.round||'Upcoming match';$('tie').textContent=f.home+' v '+f.away;
  const date=/^\d{4}-\d{2}-\d{2}$/.test(f.date||'')?new Date(f.date+'T12:00:00Z').toLocaleDateString('en-GB',{weekday:'long',day:'numeric',month:'long',year:'numeric',timeZone:'Europe/London'}):'Date to be confirmed';
  $('when').textContent=date+(f.kickoff?' · '+f.kickoff:' · Kick-off to be confirmed');
  $('venue').textContent=f.venue?.ground||'To be confirmed';$('postcode').textContent=f.venue?.postcode||'To be confirmed';
 }else{$('details').querySelector('.fixture').hidden=true;$('no-fixture').hidden=false;}
 $('updated').textContent=data.updatedAt?'Competition data updated: '+data.updatedAt.replace('T',' ').replace(/\.\d+.*$/,' UTC'):'';
 $('details').hidden=false;$('status').hidden=true;
 showCampaignStory(data,competition);
}catch(error){$('status').textContent=error.message;}

function showCampaignStory(data,competition){
 const worker=new Worker(new URL('./club-details-worker.mjs',import.meta.url),{type:'module'});
 const fail=()=>{$('story-status').textContent='The Campaign journey could not be loaded. Your club details are available below.';worker.terminate();};
 worker.onerror=fail;
 worker.onmessage=({data:reply})=>{
  worker.terminate();if(!reply.ok||!reply.value.journeys.length){fail();return;}
  const result=reply.value,club=data.club;
  const copy={
   custodian:['Your club is carrying the Cup',club+' is already custodian of '+result.count+' qualifying Campaign'+(result.count===1?'':'s')+'. Each started with an original qualifying club and followed the winners to '+club+'.',club+' is part of the journey','Win, and the Cup stays with '+club+'. Lose, and it travels on with the winning club. The Campaign continues all the way to Wembley.'],
   next:['A Tin Foil Cup is heading your way',result.count+' qualifying Campaign'+(result.count===1?' has':'s have')+' reached a custodian whose next confirmed fixture is against '+club+'.',club+' could be the next custodian','If '+club+' wins this confirmed tie, it takes custody of the Cup shown here. If the current custodian wins, the Cup stays with them.'],
   previous:['Your club is already in the story',result.count+' qualifying Campaign'+(result.count===1?' has':'s have')+' included '+club+'. Follow one below to see where its Cup has travelled since.',club+' helped carry the story forward','The Cup follows the winners. Whether a club carries the Cup or faces its custodian, it becomes part of that Campaign’s story. The journey continues after a club leaves the FA Cup.'],
   example:['How a Tin Foil Cup could reach '+club,'Every Tin Foil Cup starts with a qualifying club and follows the winners towards Wembley. Here is a real Campaign—and how '+club+' could become part of its story.', club+' could become a custodian','Win a future tie against a club carrying this Cup, and '+club+' takes custody. The Cup would then stay with '+club+' until another club beats them. No qualifying Campaign has reached '+club+' or its next opponent yet: this example is not a confirmed route or a prediction.']
  }[result.category];
  if(result.category==='example'&&result.eliminated){
   copy[0]='How a Tin Foil Cup travels';copy[1]=club+' has left this season’s FA Cup. Here is a real qualifying Campaign to show how a Cup travels with the winners.';copy[2]='A Cup’s journey carries on';copy[3]='A club can become custodian by beating the club carrying a Cup. Once a club leaves the FA Cup, that Cup continues with the winners. This example does not show a confirmed connection to '+club+'.';
  }
  $('story-heading').textContent=copy[0];$('story-intro').textContent=copy[1];$('club-role-heading').textContent=copy[2];$('club-role-copy').textContent=copy[3];
  $('example-label').hidden=result.category!=='example';
  const choice=$('origin-choice');
  result.journeys.forEach((j,i)=>{const option=document.createElement('option');option.value=String(i);option.textContent=j.origin;choice.append(option);});
  choice.hidden=$('origin-label').hidden=result.journeys.length<2;
  function render(j){
   $('campaign-origin').textContent=j.origin;$('campaign-custodian').textContent=j.carrier;
   $('campaign-next').textContent=j.next?'Next: '+j.next.home+' v '+j.next.away+' · '+j.next.round+' · '+j.next.date:'The next fixture is not currently confirmed.';
   $('campaign-history').replaceChildren();
   j.history.forEach(r=>{
    const li=document.createElement('li'),round=document.createElement('span'),tie=document.createElement('strong'),note=document.createElement('span');
    round.className='history-round';round.textContent=(r.round||'FA Cup')+' · '+(r.date||'Date TBC');
    const scored=Number.isInteger(r.home_score)&&Number.isInteger(r.away_score);
    tie.textContent=scored?r.home+' ('+r.home_score+') v ('+r.away_score+') '+r.away:r.home+' v '+r.away;
    note.textContent=/^VOID/i.test(r.status||'')||r.decision==='voided-replay-ordered'?'Result voided; no custody transfer.':r.custodian?'Cup custodian: '+r.custodian+(r.decision?' · '+r.decision:''):'No custody transfer confirmed'+(r.decision?' · '+r.decision:'');
    li.append(round,tie,note);$('campaign-history').append(li);
   });
  }
  choice.onchange=()=>render(result.journeys[Number(choice.value)]);render(result.journeys[0]);
  $('story-content').hidden=false;$('story-status').hidden=true;
 };
 worker.postMessage({club:data.club,competition});
}
