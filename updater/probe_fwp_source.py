#!/usr/bin/env python3
import urllib.request
urls=['https://www.footballwebpages.co.uk/fa-cup/20260822','https://www.footballwebpages.co.uk/fa-cup/fixtures-results']
for url in urls:
    req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0','Accept':'text/html,application/xhtml+xml'})
    with urllib.request.urlopen(req,timeout=30) as r:
        raw=r.read(); print('URL',url); print('STATUS',r.status,'FINAL',r.geturl(),'TYPE',r.headers.get('content-type'),'BYTES',len(raw))
    text=raw.decode('utf-8','replace')
    print('TR',text.lower().count('<tr'),'TD',text.lower().count('<td'),'FT',text.count('Lower Breck'),'SCRIPT',text.lower().count('<script'))
    print('START',repr(text[:600]))
