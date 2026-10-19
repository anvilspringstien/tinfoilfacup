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
 console.log(path+': announcement, London time, ball alias, elapsed draw and fixture precedence PASS');
}
