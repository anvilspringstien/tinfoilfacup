#!/usr/bin/env python3
"""Read-only inspect functions needed for season-scoped Holmesdale correction."""
from pathlib import Path
import re, json
s=Path("beta/clubfinder-beta.html").read_text()
begin="/* TIN_FOIL_EMBEDDED_COMPETITION_BEGIN */"
end="/* TIN_FOIL_EMBEDDED_COMPETITION_END */"
if s.count(begin)!=1 or s.count(end)!=1: raise SystemExit("Bad BETA snapshot boundaries")
sans=s.split(begin)[0]+"\n/* SNAPSHOT OMITTED */\n"+s.split(end)[1]
names=["historicalResultsForClub","candidateClubByName","clubByDisplayName","groundByClubName","resultSortValue","resultNeedsReplay","tinFoilPigeonCoords","canonicalClubKey","sameClubIdentity","liveLookup","resultFor","buildJourney",
       "currentDisplayFixture","nextRoundInfo","resolveLiveFixtureForCarrier",
       "completedResultVenue","tinFoilPigeonMilesForStats","journeyCertificate",
       "tinFoilCertificateWinner","tinFoilStatsDisplayClubKey","tinFoilBetaVerifiedThameNextFixture"]
def extract(source,n):
 m=re.search(r"\b(?:async\s+)?function\s+"+re.escape(n)+r"\s*\([^)]*\)\s*\{",source)
 if not m:return "(not found)"
 i=source.find("{",m.start(),m.end()); depth=0; q=""; escaped=False; line=False; block=False
 while i<len(source):
  ch=source[i]; nxt=source[i+1] if i+1<len(source) else ""
  if line:
   if ch=="\n":line=False
  elif block:
   if ch=="*" and nxt=="/":block=False;i+=1
  elif q:
   if escaped:escaped=False
   elif ch=="\\":escaped=True
   elif ch==q:q=""
  elif ch=="/" and nxt=="/":line=True;i+=1
  elif ch=="/" and nxt=="*":block=True;i+=1
  elif ch in ("'",'"',chr(96)):q=ch
  elif ch=="{":depth+=1
  elif ch=="}":
   depth-=1
   if depth==0:return source[m.start():i+1]
  i+=1
 return "(unclosed)"
for n in names:
 f=extract(sans,n)
 print("FUNCTION",n,"BYTES",len(f));print(f[:14000] if n in ("canonicalClubKey","sameClubIdentity","liveLookup","resultFor","buildJourney","currentDisplayFixture","nextRoundInfo","journeyCertificate","tinFoilPigeonMilesForStats","historicalResultsForClub","candidateClubByName","clubByDisplayName","groundByClubName") else f[:5000]);print("END_FUNCTION",n)
for term in ["Holmesdale FC","Petts Wood","const ELIGIBLE","function resultFor","LIVE_COMPETITION_DATA.result_history","function buildJourney","groundByClubName","campaignOrigin","function journeyCertificate"]:
 matches=list(re.finditer(re.escape(term),sans,re.I))
 print("OCCURRENCES",term,len(matches))
 for m in matches[:6]:
  print(sans[max(0,m.start()-420):m.end()+700].replace("\n"," ")[:1200])
data=json.loads(Path("competition.json").read_text())
print("CANONICAL_TIMESTAMP",data.get("updated_at"))
print("RESULT_KEY_HOLMESDALE",[k for k in data.get("results",{}) if "holmesdale" in k.lower()])
print("HISTORY_KEY_HOLMESDALE",[k for k in data.get("result_history",{}) if "holmesdale" in k.lower()])
