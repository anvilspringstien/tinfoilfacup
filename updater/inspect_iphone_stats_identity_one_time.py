#!/usr/bin/env python3
from pathlib import Path
s=Path("beta/clubfinder-beta.html").read_text(encoding="utf-8")
for needle in [".campaign-identity-band{",".campaign-identity-label{",".campaign-identity-value{","Pigeon Call Sign:","Pigeon Name:","<span class=\\\"campaign-identity-value"]:
 print("\n=== NEEDLE",repr(needle),"count",s.count(needle))
 start=0
 for i in range(min(3,s.count(needle))):
  p=s.find(needle,start)
  if p<0: break
  print("OFFSET",p,"EXCERPT",repr(s[max(0,p-380):min(len(s),p+850)]))
  start=p+len(needle)
