#!/usr/bin/env python3
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[1]
P=ROOT/'clubfinder.html'
text=P.read_text(encoding='utf-8')

old_round="+'</strong> • '+esc(next.name)+"
new_round="+'</strong> • '+esc(k.round||next.name)+"
old_link='s.next.drawUrl'
new_link='s.next.fixturesUrl'

rc_old=text.count(old_round); rc_new=text.count(new_round)
lc_old=text.count(old_link); lc_new=text.count(new_link)
if rc_old==1 and rc_new==0:text=text.replace(old_round,new_round,1)
elif not (rc_old==0 and rc_new>=1):raise SystemExit(f'ABORT: unexpected round renderer state old={rc_old} new={rc_new}')
if lc_old==1:text=text.replace(old_link,new_link,1)
elif lc_old!=0:raise SystemExit(f'ABORT: unexpected drawUrl reference count {lc_old}')
if 's.next.drawUrl' in text:raise SystemExit('ABORT: drawUrl reference remains')
if "esc(k.round||next.name)" not in text:raise SystemExit('ABORT: live fixture round patch missing')

new_build=r'''function buildJourney(origin){
  let carrier=origin;
  const breadcrumbs=[];
  const cn=n=>norm(String(n||'').replace(/\s+(FC|AFC|CFC)$/i,''));
  function clubObjectForWinner(name,prior){
    return candidateClubByName(name)||{name:name,entry_round:(prior&&prior.entry_round)||'',fixture:{}};
  }
  function appendHistory(club){
    const history=historicalResultsForClub(club);
    for(const item of history){
      if(!breadcrumbs.some(x=>sameMatchResult(x.result,item.result)))breadcrumbs.push(item);
    }
  }
  function resolveCarrier(){
    let c=origin;
    const ordered=[...breadcrumbs].sort((a,b)=>resultSortValue(a.result)-resultSortValue(b.result));
    for(const item of ordered){
      const r=item.result||{};
      const participant=cn(r.home)===cn(c.name)||cn(r.away)===cn(c.name);
      if(participant&&r.winner&&!resultNeedsReplay(r))c=clubObjectForWinner(r.winner,c);
    }
    return c;
  }

  const seen=new Set();
  for(let hop=0;hop<20;hop++){
    appendHistory(carrier);
    const next=resolveCarrier();
    const key=cn(next.name);
    if(key===cn(carrier.name)&&seen.has(key)){carrier=next;break;}
    carrier=next;
    if(seen.has(key)){appendHistory(carrier);carrier=resolveCarrier();break;}
    seen.add(key);
  }
  appendHistory(carrier);
  carrier=resolveCarrier();

  const unique=[];
  for(const item of breadcrumbs){
    if(!unique.some(x=>sameMatchResult(x.result,item.result)))unique.push(item);
  }
  unique.sort((a,b)=>resultSortValue(a.result)-resultSortValue(b.result));
  return {origin,carrier,breadcrumbs:unique};
}'''

pat=re.compile(r'function buildJourney\(origin\)\{.*?\}\s*function previousRoundsHtml',re.S)
if 'clubObjectForWinner' not in text:
    replacement=new_build+' function previousRoundsHtml'
    text,n=pat.subn(lambda m:replacement,text,count=1)
    if n!=1:raise SystemExit(f'ABORT: expected one buildJourney function, replaced {n}')

if 'clubObjectForWinner' not in text or 'for(let hop=0;hop<20;hop++)' not in text:
    raise SystemExit('ABORT: canonical custody traversal patch missing')

P.write_text(text,encoding='utf-8')
print('CLUBFINDER COMPETITION PATCH: SUCCESS')
print('Known next fixture uses its canonical round.')
print('View Next Round uses fixturesUrl.')
print('Custody now follows canonical winners across multiple hand-offs/replays.')
print('Ground/location logic: UNTOUCHED')
