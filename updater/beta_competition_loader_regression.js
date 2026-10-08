#!/usr/bin/env node
// BETA competition precedence contract. Run: node updater/beta_competition_loader_regression.js
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const html = fs.readFileSync('beta/clubfinder-beta.html', 'utf8');
const start = html.indexOf('async function refreshCompetitionData(force=false){');
const end = html.indexOf('function updateLiveDataBadge(){', start);
assert(start !== -1 && end > start, 'loader boundaries must remain recognizable');
const loader = html.slice(start, end);
const canonical = {schema_version:1,updated_at:'2026-10-08T12:00:00Z',results:{A:1},fixtures:{B:1}};
const snapshot = {schema_version:1,updated_at:'2026-10-01T12:00:00Z',results:{A:2},fixtures:{B:2}};
async function scenario(name, responses, expectedOrder, expectedState, expectedData) {
  const requested = [];
  const context = {
    BETA_COMPETITION_DATA_URL:'./competition-fallback.json',
    PRODUCTION_COMPETITION_DATA_URL:'../competition.json',
    LIVE_COMPETITION_DATA:null,
    LIVE_DATA_STATUS:null,
    Date, Error, Number,
    applyLiveRoundDates(){},
    updateLiveDataBadge(){},
    async fetch(url,opts) {
      const path=url.split('?')[0]; requested.push(path);
      assert.equal(opts.cache,'no-store');
      const response=responses[path];
      if(response instanceof Error)throw response;
      if(response===undefined)return {ok:false,status:503};
      return {ok:true,async json(){return response}};
    }
  };
  vm.createContext(context);
  vm.runInContext(loader,context);
  const success=await context.refreshCompetitionData();
  assert.deepEqual(requested,expectedOrder,name+' request precedence');
  assert.equal(context.LIVE_DATA_STATUS.state,expectedState,name+' state');
  assert.equal(success,expectedState==='live',name+' return value');
  assert.equal(context.LIVE_COMPETITION_DATA?.updated_at,expectedData?.updated_at,name+' data');
  if(expectedState==='fallback')assert.match(context.LIVE_DATA_STATUS.message,/fallback/i);
  if(expectedState==='unavailable')assert.match(context.LIVE_DATA_STATUS.message,/unavailable/i);
  console.log('PASS:',name);
}
(async()=>{
  const prod='../competition.json',beta='./competition-fallback.json';
  await scenario('canonical wins even when snapshot exists',{[prod]:canonical,[beta]:snapshot},[prod],'live',canonical);
  await scenario('canonical wins over outdated snapshot',{[prod]:canonical,[beta]:snapshot},[prod],'live',canonical);
  await scenario('network failure falls back to snapshot',{[prod]:new Error('offline'),[beta]:snapshot},[prod,beta],'fallback',snapshot);
  await scenario('invalid canonical schema falls back',{[prod]:{schema_version:2},[beta]:snapshot},[prod,beta],'fallback',snapshot);
  await scenario('missing canonical fields falls back',{[prod]:{schema_version:1},[beta]:snapshot},[prod,beta],'fallback',snapshot);
  await scenario('both sources fail closed',{[prod]:new Error('offline'),[beta]:new Error('offline')},[prod,beta],'unavailable',null);
  await scenario('invalid fallback fails closed',{[prod]:new Error('offline'),[beta]:{schema_version:1}},[prod,beta],'unavailable',null);
  assert(html.includes('if(!tinFoilCompetitionReady)tinFoilCompetitionReady=refreshCompetitionData(false);'),'startup loader promise preserved');
  assert(html.includes('await tinFoilEnsureCompetitionReady();'),'Stats loader promise preserved');
  console.log('PASS: saved Campaign and Stats startup promise wiring retained');
})().catch(err=>{console.error(err);process.exitCode=1});
