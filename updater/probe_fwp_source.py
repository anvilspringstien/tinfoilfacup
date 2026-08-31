#!/usr/bin/env python3
import re,urllib.request
from html import unescape
urls=['https://www.footballwebpages.co.uk/fa-cup/20260822','https://www.footballwebpages.co.uk/fa-cup/fixtures-results/first-qualifying-round']
for url in urls:
    req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0','Accept':'text/html,application/xhtml+xml'})
    with urllib.request.urlopen(req,timeout=30) as r: raw=r.read()
    text=raw.decode('utf-8','replace')
    print('URL',url,'BYTES',len(raw),'TR',text.lower().count('<tr'),'TD',text.lower().count('<td'))
    rows=re.findall(r'<tr\b[^>]*>.*?</tr>',text,re.I|re.S)
    shown=0
    for row in rows:
        plain=' '.join(unescape(re.sub(r'<[^>]+>',' ',row)).split())
        if ('Lower Breck' in plain or 'Cobham' in plain or 'Newton Aycliffe' in plain or shown<3):
            print('ROW',repr(plain[:500])); shown+=1
        if shown>=8: break
