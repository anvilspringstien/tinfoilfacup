import {clubDetails} from './club-details-model.mjs';
const $=id=>document.getElementById(id);
try{
 const read=async url=>{const response=await fetch(url,{cache:'no-store'});if(!response.ok)throw Error('The published details could not be loaded. Please try again, or reply to your email.');return response.json();};
 const [queue,competition]=await Promise.all([read('../updater/club_website_audit_queue.json'),read('../competition.json')]);
 const data=clubDetails(new URLSearchParams(location.search).get('club'),queue,competition);
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
}catch(error){$('status').textContent=error.message;}
