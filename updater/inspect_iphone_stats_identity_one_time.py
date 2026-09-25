from pathlib import Path
s=Path("beta/clubfinder-beta.html").read_text(encoding="utf-8")
start=s.index("async function journeyCertificate(")
segment=s[start:start+26000]
for needle in ["<head","<meta","viewport","<style","const html","const css","width:","@media","w.document.write","document.write"]:
 print("\nTOKEN",repr(needle),"COUNT",segment.count(needle))
 off=0
 for i in range(min(5,segment.count(needle))):
  p=segment.find(needle,off)
  print("OFFSET",start+p,"SNIP",repr(segment[max(0,p-220):p+600]))
  off=p+len(needle)
