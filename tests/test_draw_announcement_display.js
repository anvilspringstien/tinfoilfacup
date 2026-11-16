const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const announcement=JSON.parse(fs.readFileSync('tests/fixtures/draw-announcement-first-proper.json','utf8'));
for(const path of (process.argv.length>2?process.argv.slice(2):['clubfinder.html','beta/clubfinder-beta.html'])){
 const html=fs.readFileSync(path,'utf8');
 const a=html.indexOf('function nextProgressHtml('),b=html.indexOf('function stateHtml(',a);
 let now=Date.parse('2026-10-19T16:00:00Z');
 class Clock extends Date {static now(){return now;}}
 const ctx={Date:Clock,esc:String,formatDateGB:String,drawAlternatives:s=>s.split(/\s+or\s+/i),canonicalClubKey:s=>s.toLowerCase().replace(/\s+FC$/i,'')};
 vm.createContext(ctx);vm.runInContext(html.slice(a,b),ctx);
 const next={name:'First Round Proper',date:'2026-11-07',drawAnnouncement:announcement,drawClub:'AFC Fylde FC'};
 let shown=ctx.nextProgressHtml({},next);
 assert.match(shown,/Monday,? 19 October 2026/);
 assert.match(shown,/approximately 18:35 BST/);
 assert.match(shown,/ball 64/);
 assert.doesNotMatch(shown,/TBC|awaiting confirmed draw/);
 now=Date.parse('2026-10-19T18:00:00Z');
 assert.match(ctx.nextProgressHtml({},next),/awaiting confirmed draw/);
 next.knownFixture={home:'AFC Fylde',away:'Test Club',round:next.name,date:'2026-11-07',kickoff:'15:00'};
 shown=ctx.nextProgressHtml({},next);
 assert.match(shown,/AFC Fylde v Test Club/);
 assert.doesNotMatch(shown,/ball 64|awaiting confirmed draw/);
 delete next.knownFixture;delete next.drawAnnouncement;
 assert.match(ctx.nextProgressHtml({},next),/Draw: TBC/);
 const start=html.indexOf('function nextRoundInfo(');
 const end=html.indexOf('\nfunction canonicalClubKey(',start);
 const guard=html.slice(html.indexOf('/* TIN_FOIL_NEXT_ROUND_INTEGRITY_BEGIN */'),html.indexOf('/* TIN_FOIL_NEXT_ROUND_INTEGRITY_END */'));
 const club={name:'AFC Fylde'};
 let result,fixture;
 Object.assign(ctx,{resultFor:()=>result,liveLookup:()=>fixture,liveConditionalFixtureForClub:()=>null,
  resolveLiveFixtureForCarrier:f=>f,ROUND_META:{},LIVE_COMPETITION_DATA:{},FA_FIXTURES_URL:'',
  tinFoilVerifiedThameNextFixture:()=>null,tinFoilBetaVerifiedThameNextFixture:()=>null});
 vm.runInContext(html.slice(start,end)+guard,ctx);
 const proper=['First Round Proper','Second Round Proper','Third Round Proper','Fourth Round Proper',
  'Fifth Round Proper','Quarter Final','Semi Final','Final'];
 for(let i=0;i<proper.length-1;i++){
  result={round:proper[i]};
  fixture={home:'AFC Fylde',away:'Luton Town',round:proper[i+1],date:'2026-12-05'};
  const progress=ctx.nextRoundInfo(club);
  assert.equal(progress.name,proper[i+1]);
  assert.match(ctx.nextProgressHtml(club,progress),/AFC Fylde v Luton Town/);
  fixture={...fixture,round:proper[i]};
  assert.equal(ctx.nextRoundInfo(club).knownFixture,null);
 }
 if(path==='clubfinder.html'){
  result={round:'First Round Proper'};
  fixture=null;
  const preview={outgoing_round:'First Round Proper',target_round:'Second Round Proper',
   at:'2026-11-09T18:45:00+00:00',draw_schedule:{date_text:'Monday 9 November',time_text:'approximately 6.45pm GMT'},
   entries:[{number:19,clubs:['AFC Fylde FC']}]};
  ctx.LIVE_COMPETITION_DATA={source_round:'First Round Proper',draw_preview:preview};
  now=Date.parse('2026-11-09T18:40:00Z');
  assert.match(ctx.nextProgressHtml(club,ctx.nextRoundInfo(club)),/Monday 9 November.*approximately 6.45pm GMT.*ball 19/);
  assert.doesNotMatch(ctx.nextProgressHtml(club,ctx.nextRoundInfo(club)),/awaiting confirmed draw/);
  now=Date.parse('2026-11-09T18:45:00Z');
  assert.match(ctx.nextProgressHtml(club,ctx.nextRoundInfo(club)),/awaiting confirmed draw.*ball 19/);
  fixture={home:'AFC Fylde',away:'Luton Town',round:'Second Round Proper',date:'2026-12-05'};
  assert.doesNotMatch(ctx.nextProgressHtml(club,ctx.nextRoundInfo(club)),/ball 19|awaiting confirmed draw/);
  fixture=null;
  ctx.LIVE_COMPETITION_DATA.source_round='Second Round Proper';
  assert.equal(ctx.nextRoundInfo(club).drawPreview,null);
  ctx.LIVE_COMPETITION_DATA.source_round='First Round Proper';
  preview.target_round='Third Round Proper';
  assert.equal(ctx.nextRoundInfo(club).drawPreview,null);
 }
 console.log(path+': announcement, London time, ball alias, elapsed draw and fixture precedence PASS');
}
