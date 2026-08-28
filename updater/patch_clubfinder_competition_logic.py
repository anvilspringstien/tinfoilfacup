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

identity_block=r'''function canonicalClubKey(name){
  return String(name||'').toLowerCase()
    .replace(/&/g,' and ')
    .replace(/\b(association football club|football club)\b/g,' ')
    .replace(/\b(fc|afc|cfc)\b/g,' ')
    .replace(/[^a-z0-9]+/g,' ')
    .trim().replace(/\s+/g,' ');
}
function sameClubIdentity(a,b){return canonicalClubKey(a)===canonicalClubKey(b);}
function canonicalResultWinner(r){
  if(!r)return '';
  if(r.decision==='draw-replay')return '';
  const hs=Number(r.home_score),as=Number(r.away_score);
  if(Number.isFinite(hs)&&Number.isFinite(as)&&hs!==as)return hs>as?r.home:r.away;
  return r.winner||'';
}
function clubByDisplayName(name){
  if(!name)return null;
  const target=canonicalClubKey(name);
  return ELIGIBLE.find(c=>canonicalClubKey(c.name)===target)||null;
}
function groundByClubName(name){
  if(!name)return {};
  const target=canonicalClubKey(name);
  return GROUNDS.find(g=>canonicalClubKey(g.name||g.club)===target)||{};
}'''
lookup_pat=re.compile(r'(?:function canonicalClubKey\(name\)\{.*?\}\s*function sameClubIdentity\(a,b\)\{.*?\}\s*(?:function canonicalResultWinner\(r\)\{.*?\}\s*)?)?function clubByDisplayName\(name\)\{.*?\}\s*function groundByClubName\(name\)\{.*?\}\s*(?=function completedResultVenue)',re.S)
text,n=lookup_pat.subn(lambda m:identity_block+' ',text,count=1)
if n!=1:raise SystemExit(f'ABORT: expected one club/ground lookup block, replaced {n}')

history_fn=r'''function historicalResultsForClub(club){
  const out=[];
  function add(r,round){
    if(!r||typeof r!=='object')return;
    if(!sameClubIdentity(r.home,club.name)&&!sameClubIdentity(r.away,club.name))return;
    if(!out.some(x=>sameMatchResult(x.result,r)))out.push({round:round||r.round||club.entry_round||'FA Cup',result:r});
  }
  const hist=liveLookup('result_history',club.name);
  if(Array.isArray(hist))for(const r of hist)add(r,r&&r.round);
  add(liveLookup('results',club.name));
  if(!out.length){
    const f=club.fixture||{};
    if(club.entry_round==='Extra Preliminary Round'&&f.number!=null)add(EPR_RESULTS_BY_TIE[String(f.number)]||null,club.entry_round);
    else if(f.result&&typeof f.result==='object')add(f.result,club.entry_round||f.result.round);
    const key=String(club.name||'').replace(/\s+(FC|AFC|CFC)$/,'');
    add(CURRENT_RESULT_OVERRIDES[club.name]||CURRENT_RESULT_OVERRIDES[key]||null);
    add(liveLookup('results',club.name));
  }
  out.sort((a,b)=>resultSortValue(a.result)-resultSortValue(b.result));
  return out;
}'''
history_pat=re.compile(r'function historicalResultsForClub\(club\)\{.*?\}\s*(?=function buildJourney)',re.S)
text,n=history_pat.subn(lambda m:history_fn+' ',text,count=1)
if n!=1:raise SystemExit(f'ABORT: expected one historicalResultsForClub function, replaced {n}')

new_build=r'''function buildJourney(origin){
  let carrier=origin;
  const breadcrumbs=[];
  function clubObjectForWinner(name,prior){
    return clubByDisplayName(name)||candidateClubByName(name)||{name:name,entry_round:(prior&&prior.entry_round)||'',fixture:{}};
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
      const participant=sameClubIdentity(r.home,c.name)||sameClubIdentity(r.away,c.name);
      const winner=canonicalResultWinner(r);
      if(participant&&winner&&!resultNeedsReplay(r))c=clubObjectForWinner(winner,c);
    }
    return c;
  }
  const seen=new Set();
  for(let hop=0;hop<20;hop++){
    appendHistory(carrier);
    const next=resolveCarrier();
    const key=canonicalClubKey(next.name);
    if(key===canonicalClubKey(carrier.name)&&seen.has(key)){carrier=next;break;}
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
journey_pat=re.compile(r'function buildJourney\(origin\)\{.*?\}\s*function previousRoundsHtml',re.S)
text,n=journey_pat.subn(lambda m:new_build+' function previousRoundsHtml',text,count=1)
if n!=1:raise SystemExit(f'ABORT: expected one buildJourney function, replaced {n}')

old_won="const won=r.winner&&sameClubIdentity(r.winner,club.name);"
new_won="const won=canonicalResultWinner(r)&&sameClubIdentity(canonicalResultWinner(r),club.name);"
if old_won in text:text=text.replace(old_won,new_won,1)
elif new_won not in text:raise SystemExit('ABORT: competitionState winner comparison not found')

required=('function canonicalClubKey(','function canonicalResultWinner(',"liveLookup('result_history',club.name)",'const winner=canonicalResultWinner(r);','const won=canonicalResultWinner(r)&&sameClubIdentity(canonicalResultWinner(r),club.name);')
for marker in required:
    if marker not in text:raise SystemExit(f'ABORT: required competition patch missing: {marker}')

P.write_text(text,encoding='utf-8')
print('CLUBFINDER COMPETITION PATCH: SUCCESS')
print('Decisive scorelines override contradictory legacy winner fields.')
print('Canonical result_history is included in journey traversal.')
print('Custody and winner state use canonical club identity.')
print('Fixture venue lookup uses canonical club identity.')
print('Ground records themselves: UNTOUCHED')
