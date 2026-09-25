#!/usr/bin/env python3
from pathlib import Path
s=Path("beta/clubfinder-beta.html").read_text(encoding="utf-8")
start=s.find("async function journeyCertificate(")
end=s.find("</script>",start) if start>=0 else -1
print("CERTIFICATE_BEGIN",start,"CERTIFICATE_END",end)
if start>=0: print("CERTIFICATE SOURCE START",repr(s[start:start+5600]))
for needle in ["campaign-identity-band","campaign-identity-label","campaign-identity-value","<meta name=\\\"viewport","<meta name=\\\"viewport\\\"","text-size-adjust","Pigeon Name"]:
 print("\n=== NEEDLE",repr(needle),"COUNT",s.count(needle))
 off=0
 for i in range(min(4,s.count(needle))):
  p=s.find(needle,off)
  print("OFFSET",p,"SNIPPET",repr(s[max(start,p-250):p+490]))
  off=p+len(needle)
