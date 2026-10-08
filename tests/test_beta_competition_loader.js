'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const html=fs.readFileSync('beta/clubfinder-beta.html','utf8');
const live=JSON.parse(fs.readFileSync('competition.json','utf8'));
const fallback=JSON.parse(fs.readFileSync('beta/competition-fallback.json','utf8'));
const source=html.slice(html.indexOf("const BETA_COMPETITION_DATA_URL="),html.indexOf('function liveLookup('))+
  html.slice(html.indexOf('function applyLiveRoundDates(){'),html.indexOf('\nconst ROUND_META={'));
assert(source.includes('async function refreshCompetitionData(force=false)'));
assert(html.includes('if(!LIVE_COMPETITION_DATA){status.textContent=LIVE_DATA_STATUS.message;return}'));
async function scenario(liveOK,fallbackOK){
  const calls=[], badge={textContent:''};
  const ctx={Date,console,document:{getElementById:()=>badge},
    tinFoilSearchNumberLabel:()=>'',tinFoilCurrentSearchNumber:()=>null,
    ROUND_META:{'Third Round Qualifying':{date:'old'}},
    fetch:async(url,options)=>{
      calls.push({url:String(url),options});
      if(String(url).startsWith('../competition.json')){
        if(!liveOK)throw Error('live unavailable');
        return {ok:true,json:async()=>live};
      }
      assert.match(String(url),/^\.\/competition-fallback\.json\?t=\d+$/);
      if(!fallbackOK)throw Error('fallback unavailable');
      return {ok:true,json:async()=>fallback};
    }};
  vm.createContext(ctx);vm.runInContext(source,ctx);
  const result=await vm.runInContext('refreshCompetitionData()',ctx);
  return {calls,badge,result,state:vm.runInContext('LIVE_DATA_STATUS.state',ctx),
    data:vm.runInContext('LIVE_COMPETITION_DATA',ctx),
    date:vm.runInContext("ROUND_META['Third Round Qualifying'].date",ctx)};
}
(async()=>{
  const success=await scenario(true,true);
  assert.equal(success.result,true);assert.equal(success.state,'live');
  assert.equal(success.calls.length,1);assert.match(success.calls[0].url,/^\.\.\/competition\.json\?t=\d+$/);
  assert.equal(success.calls[0].options.cache,'no-store');assert.equal(success.data.updated_at,live.updated_at);
  const offline=await scenario(false,true);
  assert.equal(offline.result,false);assert.equal(offline.state,'fallback');
  assert.equal(offline.calls.length,2);assert.match(offline.calls[1].url,/^\.\/competition-fallback\.json\?t=\d+$/);
  assert.equal(offline.calls[1].options.cache,'no-store');assert.equal(offline.data.updated_at,fallback.updated_at);
  assert.equal(offline.date,fallback.round_dates['Third Round Qualifying']);
  const unavailable=await scenario(false,false);
  assert.equal(unavailable.result,false);assert.equal(unavailable.state,'unavailable');
  assert.equal(unavailable.data,null);assert.match(unavailable.badge.textContent,/Competition data unavailable/);
  console.log('BETA competition live/fallback/unavailable loader: PASS');
})().catch(e=>{console.error(e);process.exitCode=1});
