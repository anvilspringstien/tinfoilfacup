#!/usr/bin/env python3
"""Generate a read-only Barry Air view from the exact public Campaign functions."""
from pathlib import Path
import re,sys,json
ROOT=Path(__file__).resolve().parents[1]
s=(ROOT/'beta/clubfinder-beta.html').read_text()
# The established inspect_beta_holmesdale extractor, unchanged except for errors.
def extract(source,n):
 m=re.search(r"\b(?:async\s+)?function\s+"+re.escape(n)+r"\s*\([^)]*\)\s*\{",source)
 if not m:raise ValueError('Missing function '+n)
 i=source.find('{',m.start(),m.end());depth=0;q='';escaped=False;line=False;block=False
 while i<len(source):
  ch=source[i];nxt=source[i+1] if i+1<len(source) else ''
  if line:
   if ch=='\n':line=False
  elif block:
   if ch=='*' and nxt=='/':block=False;i+=1
  elif q:
   if escaped:escaped=False
   elif ch=='\\':escaped=True
   elif ch==q:q=''
  elif ch=='/' and nxt=='/':line=True;i+=1
  elif ch=='/' and nxt=='*':block=True;i+=1
  elif ch in ("'",'"',chr(96)):q=ch
  elif ch=='{':depth+=1
  elif ch=='}':
   depth-=1
   if depth==0:return source[m.start():i+1]
  i+=1
 raise ValueError('Unclosed function '+n)
roots=['buildJourney','completedResultVenue','competitionState','nextRoundInfo','resolveLiveFixtureForCarrier','tinFoilPigeonCoords','tinFoilPigeonMilesForStats','tinFoilSavedCallSign','tinFoilSavedPigeonName','resultLinePlain','findGround','sameClubIdentity','candidateClubByName']
allnames=set(re.findall(r'\b(?:async\s+)?function\s+(\w+)\s*\(',s))
selected={};todo=roots.copy()
while todo:
 name=todo.pop()
 if name in selected:continue
 body=extract(s,name);selected[name]=body
 for dep in sorted(allnames):
  if dep not in selected and re.search(r'\b'+re.escape(dep)+r'\s*\(',body):todo.append(dep)
# Local function declarations stay inside their original enclosing functions.
# Including a local helper separately is unnecessary and may capture its closure.
locals_=set()
for name,body in selected.items():locals_.update(re.findall(r'\bfunction\s+(\w+)\s*\(',body)[1:])
for name in locals_:selected.pop(name,None)
joined='\n'.join(selected[n] for n in sorted(selected));constants=[]
tables=['ELIGIBLE','GROUNDS','LAW2_ORIGIN_LOCATIONS','EPR_RESULTS_BY_TIE','FA_FIXTURES_URL','PCAPI','aliases','NEXT_FIXTURE_OVERRIDES','PRELIM_FIXTURES_BY_CLUB','CURRENT_RESULT_OVERRIDES','REPLAY_FIXTURES_BY_CLUB','VERIFIED_MATCH_VENUE_OVERRIDES','ROUND_META','TIN_FOIL_PIGEON_COORD_CACHE']
for name in tables:
 m=re.search(r'\b(?:const|let|var)\s+'+name+r'\s*=',s)
 if not m:raise ValueError('Missing table '+name)
 i=m.end();q='';escaped=False
 while i<len(s):
  ch=s[i]
  if q:
   if escaped:escaped=False
   elif ch=='\\':escaped=True
   elif ch==q:q=''
  elif ch in ("'",'"',chr(96)):q=ch
  elif ch==';':break
  i+=1
 constants.append((name,'const '+name+'='+s[m.end():i]+';'))
text='/* Generated from public BETA; never hand-edit. No counter or Campaign-selection code. */\n'
text+='export function campaignView(LIVE_COMPETITION_DATA,fetcher=globalThis.fetch){\nconst fetch=fetcher;\n'
text+='\n'.join(d for _,d in constants)+'\n'+joined+'\nreturn {'+','.join(roots)+',origins:ELIGIBLE};\n}\n'
target=ROOT/'beta/barry-air/campaign-adapter.mjs'
if '--check' in sys.argv:
 if not target.exists() or target.read_text()!=text:sys.exit('Barry Air adapter differs from its public Campaign source; regenerate it.')
 print('PASS: Barry Air uses unchanged public Campaign functions and tables.')
else:
 target.write_text(text);print('Generated',len(selected),'functions;',len(text),'bytes; tables:',','.join(n for n,_ in constants))
