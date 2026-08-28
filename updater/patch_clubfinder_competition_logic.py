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

# One canonical club identity key for competition traversal and ground lookup.
identity_helper=r'''function canonicalClubKey(name){
  return String(name||'').toLowerCase()
    .replace(/&/g,' and ')
    .replace(/\b(association football club|football club)\b/g,' ')
    .replace(/\b(fc|afc|cfc)\b/g,' ')
    .replace(/[^a-z0-9]+/g,' ')
    .trim().replace(/\s+/g,' ');
}
function sameClubIdentity(a,b){return canonicalClubKey(a)===canonicalClubKey(b);}'''
if 'function canonicalClubKey(' not in text:
    marker='function clubByDisplayName(name){'
    pos=text.find(marker)
    if pos<0:raise SystemExit('ABORT: clubByDisplayName marker not found')
    text=text[:pos]+identity_helper+' '+text[pos:]

old_clubby="""function clubByDisplayName(name){   if(!name)return null;   const target=norm(name);   return ELIGIBLE.find(c=>norm(c.name)===target) ||          ELIGIBLE.find(c=>norm(String(c.name||'').replace(/\\s+(FC|AFC|CFC)$/,''))===target) ||          null; }"""
new_clubby="""function clubByDisplayName(name){   if(!name)return null;   const target=canonicalClubKey(name);   return ELIGIBLE.find(c=>canonicalClubKey(c.name)===target)||null; }"""
if old_clubby in text:text=text.replace(old_clubby,new_clubby,1)
elif new_clubby not in text:raise SystemExit('ABORT: unexpected clubByDisplayName implementation')

old_ground="""function groundByClubName(name){   if(!name)return {};   const target=norm(name);   return GROUNDS.find(g=>norm(g.name||g.club)===target) ||          GROUNDS.find(g=>norm(String(g.name||g.club||'').replace(/\\s+(FC|AFC|CFC)$/,''))===target) ||          {}; }"""
new_ground="""function groundByClubName(name){   if(!name)return {};   const target=canonicalClubKey(name);   return GROUNDS.find(g=>canonicalClubKey(g.name||g.club)===target)||{}; }"""
if old_ground in text:text=text.replace(old_ground,new_ground,1)
elif new_ground not in text:raise SystemExit('ABORT: unexpected groundByClubName implementation')

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
      if(participant&&r.winner&&!resultNeedsReplay(r))c=clubObjectForWinner(r.winner,c);
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
pat=re.compile(r'function buildJourney\(origin\)\{.*?\}\s*function previousRoundsHtml',re.S)
replacement=new_build+' function previousRoundsHtml'
text,n=pat.subn(lambda m:replacement,text,count=1)
if n!=1:raise SystemExit(f'ABORT: expected one buildJourney function, replaced {n}')

# Make won/eliminated state use the same identity rules as journey custody.
old_won="const won=r.winner&&norm(r.winner)===norm(club.name);"
new_won="const won=r.winner&&sameClubIdentity(r.winner,club.name);"
if old_won in text:text=text.replace(old_won,new_won,1)
elif new_won not in text:raise SystemExit('ABORT: competitionState winner comparison not found')

required=('function canonicalClubKey(','sameClubIdentity(r.home,c.name)','canonicalClubKey(g.name||g.club)','const won=r.winner&&sameClubIdentity(r.winner,club.name);')
for marker in required:
    if marker not in text:raise SystemExit(f'ABORT: required identity patch missing: {marker}')

P.write_text(text,encoding='utf-8')
print('CLUBFINDER COMPETITION PATCH: SUCCESS')
print('Known next fixture uses its canonical round.')
print('View Next Round uses fixturesUrl.')
print('Custody and winner state use canonical club identity across FC/AFC/CFC variants.')
print('Fixture venue lookup uses the same canonical club identity.')
print('Ground records themselves: UNTOUCHED')
