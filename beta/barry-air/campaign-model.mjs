import {campaignView} from './campaign-adapter.mjs';
export const JOURNEY_KEY='tinFoilFACupJourney_v7';
export function identityKey(saved){return [saved.originName,saved.postcode,saved.searchNumber,saved.selectedAt||''].join('|');}
export function roundCode(round){const r=String(round||'').replace(/ Replay$/i,'');const codes={'Extra Preliminary Round':'EP','Preliminary Round':'PRE','First Round Qualifying':'1RQ','Second Round Qualifying':'2RQ','Third Round Qualifying':'3RQ','Fourth Round Qualifying':'4RQ','First Round Proper':'FRP','Second Round Proper':'2RP','Third Round Proper':'3RP','Fourth Round Proper':'4RP','Fifth Round Proper':'5RP','Quarter Final':'QF','Semi Final':'SF','Final':'FINAL'};return (codes[r]||r.replace(/Round|Proper|Qualifying/g,'').trim().slice(0,8)) + (/ Replay$/i.test(round)?' R':'');}
export function dateLabel(date){if(!date)return 'Date to be confirmed';const d=new Date(date+'T12:00:00');return Number.isNaN(d.valueOf())?'Date to be confirmed':d.toLocaleDateString('en-GB',{weekday:'long',day:'numeric',month:'long',year:'numeric'});}
export async function buildCampaign(saved,competition,{fetcher=globalThis.fetch}={}){
 if(!saved?.originName||saved.ended)throw Error('Choose a Campaign in My Campaign, then come aboard Barry Air.');
 if(!competition?.updated_at||!competition.results||!competition.fixtures)throw Error('Your flight details are temporarily unavailable. Please try again.');
 const cache=new Map();const cachedFetch=async url=>{if(!cache.has(url))cache.set(url,Promise.resolve().then(()=>fetcher(url)));return (await cache.get(url)).clone();};
 const a=campaignView(competition,cachedFetch),origin=a.candidateClubByName(saved.originName);
 if(!origin)throw Error('Your saved Campaign could not be found. Return to My Campaign to check it.');
 const journey=a.buildJourney(origin),crumbs=journey.breadcrumbs||[],carrier=journey.carrier||origin;
 const state=a.competitionState(carrier),next=a.nextRoundInfo(carrier,true);
 let upcoming=state.type==='replay'&&state.replay?a.resolveLiveFixtureForCarrier(state.replay,carrier,true):next?.knownFixture||null;
 // Match the public Stats treatment: walkovers do not create a physical flight.
 const miles=await a.tinFoilPigeonMilesForStats(crumbs,saved.postcode,r=>a.completedResultVenue(r));
 const home=await a.tinFoilPigeonCoords(saved.postcode);
 const stops=[{name:'Home base',short:'Home base',ground:'Departure postcode',pc:saved.postcode||'Postcode not saved',...(home||{}),tag:'Your pigeon’s home base',result:origin.name,round:'Straight there and straight back.',status:'HOME BASE'}],flights=[];
 const known=new Map();
 async function stopFor(f,venue,status){
  const pc=String(venue?.postcode||'').trim();const venueKey=pc&&!/TBC/i.test(pc)?[venue?.ground,pc].join('|'):[f.home,f.date,f.round].join('|');
  if(known.has(venueKey)){const i=known.get(venueKey);stops[i].visits++;return i;}
  let coords=Number.isFinite(Number(venue?.lat))&&Number.isFinite(Number(venue?.lon))?{lat:Number(venue.lat),lon:Number(venue.lon)}:null;
  if(!coords&&pc&&!/TBC/i.test(pc)){const g=a.findGround({name:f.home});if(g&&String(g.postcode||'').replace(/\s/g,'').toUpperCase()===pc.replace(/\s/g,'').toUpperCase()&&Number.isFinite(Number(g.lat))&&Number.isFinite(Number(g.lon)))coords={lat:Number(g.lat),lon:Number(g.lon)};}
  if(!coords)coords=await a.tinFoilPigeonCoords(pc);
  const name=f.home||venue?.ground||'Venue to be confirmed';const i=stops.length;
  stops.push({name,short:name.replace(/\s+(FC|AFC|CFC)$/,''),ground:venue?.ground||'Venue to be confirmed',pc:pc||'Postcode to be confirmed',...(coords||{}),tag:f.round||'FA Cup',result:'',round:dateLabel(f.date)+(f.kickoff?' · '+f.kickoff:''),status,visits:1});known.set(venueKey,i);return i;
 }
 for(const cr of crumbs){const r=cr.result||{};if(String(r.decision||'').toLowerCase()==='walkover')continue;
  const venue=a.completedResultVenue(r),i=await stopFor({...r,round:cr.round||r.round},venue,'LANDED');
  const result=a.resultLinePlain(r);flights.push({round:roundCode(cr.round||r.round),destination:r.home||venue.ground,stop:i,status:'LANDED',result,date:r.date,fixture:r});
  const d=stops[i];d.result=d.result?d.result+' · '+result:result;d.tag=d.visits>1?d.visits+' flights · one ground':cr.round||r.round;d.round=dateLabel(r.date)+(r.kickoff?' · '+r.kickoff:'');
 }
 const lastLanded=flights.at(-1)?.stop??0;
 let nextStop=null;
 if(upcoming){const venue=upcoming.venue||{};nextStop=await stopFor(upcoming,venue,'NEXT FLIGHT');
  flights.push({round:roundCode(upcoming.round||next?.name),destination:upcoming.home||'Venue to be confirmed',stop:nextStop,status:'NEXT FLIGHT',result:upcoming.home+' v '+upcoming.away,date:upcoming.date,fixture:upcoming});
  // A return to an earlier ground is one map marker, with both historical and next flights.
  stops[nextStop].next=true;stops[nextStop].nextResult=upcoming.home+' v '+upcoming.away;stops[nextStop].nextRound=dateLabel(upcoming.date)+' · '+(upcoming.kickoff||'Kick-off to be confirmed');
 }
 return {saved,identity:identityKey(saved),origin:origin.name,carrier:carrier.name,updatedAt:competition.updated_at,callSign:a.tinFoilSavedCallSign(saved),digits:String(saved.searchNumber||'').padStart(5,'0'),name:a.tinFoilSavedPigeonName(saved)||'Your pigeon',miles,stops,flights,lastLanded,nextStop,upcoming,nextRound:upcoming?.round||next?.name||'Next flight to be confirmed',canCheckIn:!!(upcoming?.date&&upcoming?.home&&upcoming?.away&&!upcoming.conditional&&upcoming.venue?.postcode),flightKey:upcoming?identityKey(saved)+'|'+[upcoming.round,upcoming.date,upcoming.home,upcoming.away].join('|'):null};
}
