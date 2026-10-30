import {campaignEngine} from './club-details-engine.mjs';
/* A read-only view: no Campaign selection, storage, pigeon or counter operations. */
export function clubCampaigns(club,competition){
 const engine=campaignEngine(competition),same=engine.sameClubIdentity;
 const results=Object.values(competition.results||{});
 const fixtures=[...new Map(Object.values(competition.fixtures||{}).filter(f=>f?.home&&f?.away&&!/\sor\s/i.test(f.home+' '+f.away)).map(f=>[[f.round,f.date,f.home,f.away].join('|'),f])).values()];
 function nextFixture(journey){
  const last=(journey.breadcrumbs||[]).at(-1)?.result;
  return fixtures.filter(f=>(same(f.home,journey.carrier.name)||same(f.away,journey.carrier.name))&&(!last?.date||f.date>=last.date)&&!results.some(r=>r.round===f.round&&r.date===f.date&&same(r.home,f.home)&&same(r.away,f.away)&&engine.canonicalResultWinner(r))).sort((a,b)=>String(a.date).localeCompare(String(b.date)))[0]||null;
 }
 // Reverse only confirmed custody transfers to shortlist origins. The unchanged
 // journey engine verifies every candidate; the graph never manufactures a journey.
 const reachable=new Set(),seeds=[club];
 const key=name=>String(name||'').toLowerCase().replace(/&/g,' and ').replace(/\b(association football club|football club|fc|afc|cfc)\b/g,' ').replace(/[^a-z0-9]+/g,' ').trim().replace(/\s+/g,' ');
 for(const f of fixtures)if(same(f.home,club)||same(f.away,club))seeds.push(f.home,f.away);
 for(const r of engine.resultCandidates)if(same(r.home,club)||same(r.away,club))seeds.push(r.home,r.away);
 const incoming=new Map();
 for(const r of engine.resultCandidates){
  const winner=engine.canonicalResultWinner(r);if(!winner||engine.resultNeedsReplay(r))continue;
  const k=key(winner);if(!incoming.has(k))incoming.set(k,new Set());
  incoming.get(k).add(key(r.home));incoming.get(k).add(key(r.away));
 }
 const pending=seeds.map(key);
 while(pending.length){const name=pending.pop();if(reachable.has(name))continue;reachable.add(name);for(const prior of incoming.get(name)||[])pending.push(prior);}
 const possible=engine.origins.filter(o=>reachable.has(key(o.name)));
 const example=engine.origins.find(o=>same(o.name,'Newton Aycliffe FC'));
 if(example&&!possible.includes(example))possible.push(example);
 const journeys=possible.map(origin=>{
  const j=engine.buildJourney(origin);
  return {origin:origin.name,entryRound:origin.entry_round,carrier:j.carrier.name,history:j.breadcrumbs.map(x=>({...x.result,custodian:engine.canonicalResultWinner(x.result)||null})),next:nextFixture(j)};
 });
 const held=journeys.filter(j=>same(j.carrier,club));
 const arriving=journeys.filter(j=>!same(j.carrier,club)&&j.next&&(same(j.next.home,club)||same(j.next.away,club)));
 const past=journeys.filter(j=>!held.includes(j)&&!arriving.includes(j)&&(j.history.some(r=>same(r.home,club)||same(r.away,club))||same(j.origin,club)));
 const category=held.length?'custodian':arriving.length?'next':past.length?'previous':'example';
 // A familiar, real qualifying Campaign is an illustration only, never an inferred route.
 const candidates=category==='custodian'?held:category==='next'?arriving:category==='previous'?past:[journeys.find(j=>same(j.origin,'Newton Aycliffe FC')&&j.history.length)||journeys.find(j=>j.history.length)];
 const lastClubResult=engine.resultCandidates.filter(r=>(same(r.home,club)||same(r.away,club))&&engine.canonicalResultWinner(r)).sort((a,b)=>String(b.date).localeCompare(String(a.date)))[0];
 const eliminated=!!lastClubResult&&!same(engine.canonicalResultWinner(lastClubResult),club);
 return {category,eliminated,count:category==='example'?0:candidates.length,journeys:candidates.filter(Boolean),updatedAt:competition.updated_at};
}
