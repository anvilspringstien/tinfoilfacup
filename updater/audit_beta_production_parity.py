#!/usr/bin/env python3
"""Read-only BETA/production semantic audit on a shared Git SHA."""
import hashlib,json,re
from pathlib import Path
R=Path(__file__).resolve().parents[1]
p=(R/"clubfinder.html").read_text();b=(R/"beta/clubfinder-beta.html").read_text()
data=json.loads((R/"competition.json").read_text())
def out(label,val):print(label+" "+json.dumps(val,ensure_ascii=False,sort_keys=True))
begin="/* TIN_FOIL_EMBEDDED_COMPETITION_BEGIN */"
end="/* TIN_FOIL_EMBEDDED_COMPETITION_END */"
def embedded(s):
 if s.count(begin)!=1 or s.count(end)!=1:return None
 block=s.split(begin)[1].split(end)[0]
 m=re.search(r'const EMBEDDED_COMPETITION_DATA\s*=\s*(\{.*\});?\s*$',block,re.S)
 try:return json.loads(m.group(1)) if m else None
 except Exception:return None
pe,be=embedded(p),embedded(b)
out("BASELINE",{"production_bytes":len(p),"beta_bytes":len(b),"competition_updated":data.get("updated_at"),
"prod_fallback_exact":pe==data,"beta_fallback_exact":be==data,
"prod_fallback_updated":pe.get("updated_at") if pe else None,"beta_fallback_updated":be.get("updated_at") if be else None})
names=["canonicalResultWinner","sameClubIdentity","verifiedConditionalWinner","resolveConditionalSide",
"resolveLiveFixtureForCarrier","nextRoundInfo","completedResultVenue","replayVenue",
"replayFixtureFor","currentDisplayFixture","resultTeamLine","resultLineFromResult","resultLinePlain",
"buildJourney","journeyCertificate","tinFoilCertificateWinner","tinFoilPigeonMilesForStats",
"tinFoilSavedPigeonName","tinFoilBetaCompletedKickoff","tinFoilStatsDisplayClubKey",
"tinFoilRepairStatsCustodyRows","tinFoilSaveClubfinderReturnSnapshot",
"tinFoilRestoreClubfinderReturnSnapshot"]
def func(s,n):
 m=re.search(r'\b(?:async\s+)?function\s+'+re.escape(n)+r'\s*\([^)]*\)\s*\{',s)
 if not m:return None
 i=s.find("{",m.start(),m.end());start=i;depth=0;quote="";esc=False;line=False;block=False
 while i<len(s) and i-start<700000:
  c=s[i];next=s[i+1] if i+1<len(s) else ""
  if line:
   if c=="\n":line=False
  elif block:
   if c=="*" and next=="/":block=False;i+=1
  elif quote:
   if esc:esc=False
   elif c=="\\":esc=True
   elif c==quote:quote=""
  elif c=="/" and next=="/":line=True;i+=1
  elif c=="/" and next=="*":block=True;i+=1
  elif c in ("'",'"',chr(96)):quote=c
  elif c=="{":depth+=1
  elif c=="}":
   depth-=1
   if depth==0:return s[m.start():i+1]
  i+=1
 return "PARSE INCOMPLETE"
table={}
for n in names:
 x,y=func(p,n),func(b,n)
 table[n]={"production":hashlib.sha256(x.encode()).hexdigest()[:10] if x else None,
           "beta":hashlib.sha256(y.encode()).hexdigest()[:10] if y else None,
           "same":x==y if x and y else False,
           "bytes":[len(x) if x else 0,len(y) if y else 0]}
out("FUNCTION_PARITY",table)
keys=["BR2 8HQ","Petts Wood","VERIFIED_MATCH_VENUE_OVERRIDES",
"Pigeon Miles Flown","tinFoilPigeonMilesForStats","tinFoilSavedPigeonName",
"preserveConditional","won 4–3 on penalties","function tinFoilBetaVerifiedWimborneReplay",
"function verifiedConditionalWinner","tffc.challengeOrigin"]
out("MARKERS",{k:{"production":p.count(k),"beta":b.count(k)} for k in keys})
def context(s,k,limit=2,pre=180,post=520):
 hits=list(re.finditer(re.escape(k),s,re.I))
 return [{"at":m.start(),"text":s[max(0,m.start()-pre):min(len(s),m.end()+post)].replace("\n"," ")} for m in hits[:limit]]
for k in ["BR2 8HQ","Petts Wood","window.location.href","window.open("]:
 out("CONTEXT "+k,{"production":context(p,k),"beta":context(b,k)})
for n in ["verifiedConditionalWinner","resolveLiveFixtureForCarrier","completedResultVenue",
"currentDisplayFixture","journeyCertificate","tinFoilCertificateWinner"]:
 if table[n]["same"]:continue
 x,y=func(p,n),func(b,n)
 out("DIFF "+n,{"production":x[:720].replace("\n"," ") if x else None,
              "beta":y[:720].replace("\n"," ") if y else None})
pat=r'.{0,80}(?:stats(?:\.html|=1)|challenges(?:-beta)?\.html).{0,120}'
for side,s in [("production",p),("beta",b)]:
 out("NAV "+side,[m.group(0).replace("\n"," ") for m in list(re.finditer(pat,s,re.I))[:15]])
print("READ ONLY AUDIT COMPLETED — source differences require behavioural verification.")
