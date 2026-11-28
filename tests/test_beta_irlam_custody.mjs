import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {campaignView} from '../beta/barry-air/campaign-adapter.mjs';

for(const source of ['competition.json','beta/competition-fallback.json']){
  const data=JSON.parse(readFileSync(new URL('../'+source,import.meta.url)));
  const view=campaignView(data);
  const origin=view.origins.find(club=>club.name==='Irlam FC');
  assert.ok(origin);
  assert.equal(origin.fixture.date,'2026-08-08','the listed default does not have to match the published completion date');
  const journey=view.buildJourney(origin);
  const results=journey.breadcrumbs.map(({result})=>result);
  assert.deepEqual(results.slice(0,2).map(r=>[r.home,r.date,r.home_score,r.away_score]),[
    ['Hallam','2026-08-09',0,3], ['Atherton Collieries','2026-08-22',3,0],
  ]);
  assert.equal(results.filter(r=>r.home==='Hallam').length,1);
  assert.ok(!view.sameClubIdentity(journey.carrier.name,origin.name),'custody leaves after the Preliminary Round loss');
  const decisive=results.filter(result=>result.winner&&result.decision!=='voided-replay-ordered').at(-1);
  assert.ok(view.sameClubIdentity(journey.carrier.name,decisive.winner),
    'the final decisive result identifies the current custodian');
  assert.notEqual(view.competitionState(journey.carrier).type,'played');
  assert.equal(campaignView({...data,season:'2027-28'}).sameClubIdentity('Irlam','Irlam Town'),false);
}
console.log('Irlam rescheduled entry result, subsequent loss and Cup custody agree in live and offline data.');
