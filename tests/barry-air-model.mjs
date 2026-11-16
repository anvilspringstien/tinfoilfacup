import assert from 'node:assert/strict';import fs from 'node:fs';import {buildCampaign} from '../beta/barry-air/campaign-model.mjs';import {campaignView} from '../beta/barry-air/campaign-adapter.mjs';
const data=JSON.parse(fs.readFileSync('competition.json'));
const geocoder=async url=>{const pc=decodeURIComponent(String(url).split('/').at(-1)).replace(/\s/g,'');const n=[...pc].reduce((n,c)=>n*17+c.charCodeAt(0),1)%1000;return new Response(JSON.stringify({result:{latitude:50+n/200,longitude:-5+n/170}}));};
const oracle=campaignView(data,geocoder);
const eastwood=oracle.origins.find(club=>club.name==='Eastwood Community FC');
assert(eastwood,'Eastwood Community must remain a selectable origin');
const eastwoodJourney=oracle.buildJourney(eastwood);
const eastwoodOpening=eastwoodJourney.breadcrumbs[0].result;
assert.equal(eastwoodOpening.home,'Loughborough Students');
assert.equal(eastwoodOpening.away_score,2);
const eastwoodPreliminary=eastwoodJourney.breadcrumbs.filter(({result})=>result.round==='Preliminary Round');
assert.equal(eastwoodPreliminary.length,1,'The Barton Town tie should appear once across the Eastwood aliases');
const eastwoodBarton=eastwoodPreliminary[0].result;
assert.match(eastwoodBarton.winner,/^Barton Town/);
assert.deepEqual([eastwoodBarton.home_score,eastwoodBarton.away_score],[0,2]);
assert.equal(oracle.completedResultVenue(eastwoodBarton).postcode,'NG16 3HB');
assert(eastwoodJourney.breadcrumbs.some(({result})=>result.round==='First Round Qualifying'&&
  result.away==='Barton Town'),'Eastwood’s Campaign must follow Barton Town into the next round');

let count=0;for(const origin of oracle.origins){const saved={originName:origin.name,postcode:'DL5 4RQ',searchNumber:12345,pigeonName:'Test pigeon'},journey=oracle.buildJourney(origin),m=await buildCampaign(saved,data,{fetcher:geocoder});assert.equal(m.carrier,journey.carrier.name);assert.equal(m.flights.filter(f=>f.status==='LANDED').length,journey.breadcrumbs.filter(x=>x.result.decision!=='walkover').length,origin.name);assert.equal(m.saved.searchNumber,12345);for(const f of m.flights)assert.ok(m.stops[f.stop],origin.name);count++;}
const saved={originName:'Newton Aycliffe FC',postcode:'DL5 4RQ',searchNumber:12345,pigeonName:'Cheeky'},m=await buildCampaign(saved,data,{fetcher:geocoder});const journey=oracle.buildJourney(oracle.candidateClubByName(saved.originName));const miles=await oracle.tinFoilPigeonMilesForStats(journey.breadcrumbs,saved.postcode,r=>oracle.completedResultVenue(r));assert.equal(m.miles.display,miles.display);assert.ok(m.miles.miles>0);assert.equal(m.name,'Cheeky');const carrier=journey.carrier;
const state=oracle.competitionState(carrier);
const upcoming=state.type==='replay'&&state.replay?oracle.resolveLiveFixtureForCarrier(state.replay,carrier,true):oracle.nextRoundInfo(carrier,true)?.knownFixture||null;
assert.deepEqual(m.upcoming,upcoming);
assert.equal(m.canCheckIn,!!(upcoming?.date&&upcoming?.home&&upcoming?.away&&!upcoming.conditional&&upcoming.venue?.postcode));
const other=await buildCampaign({...saved,searchNumber:12346},data,{fetcher:geocoder});
assert.notEqual(m.identity,other.identity);
if(upcoming)assert.notEqual(m.flightKey,other.flightKey);
else assert.equal(m.flightKey,null);
const unavailable=await buildCampaign(saved,data,{fetcher:async()=>{throw Error('offline')}});assert.equal(unavailable.miles.miles,null);assert.match(unavailable.miles.display,/Awaiting/);await assert.rejects(buildCampaign(null,data),/Choose a Campaign/);await assert.rejects(buildCampaign({...saved,ended:true},data),/Choose a Campaign/);await assert.rejects(buildCampaign({...saved,originName:'Not a real club'},data),/could not be found/);
console.log('PASS: all '+count+' origins project the unchanged public journeys; replay flights, same-as-Stats mileage, unknown locations, identities and empty/ended Campaigns.');
