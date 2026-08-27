#!/usr/bin/env python3
import json,re
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]; LEDGER=ROOT/'updater/ground-approval-ledger.json'; HTML=ROOT/'clubfinder.html'; OUT=ROOT/'updater/kingstonian-groundshare-approval.json'; REPORT=ROOT/'kingstonian-groundshare-approval.md'
def norm(s):
 s=(s or '').lower().replace('&',' and ').replace('’',"'"); s=re.sub(r'\b(fc|afc|cfc|football club)\b',' ',s); return re.sub(r'[^a-z0-9]+',' ',s).strip()
def arr(text,name):
 m=re.search(r'\b(?:const|let|var)\s+'+re.escape(name)+r'\s*=\s*\[',text); s=text.find('[',m.start()); d=0; ins=False; esc=False; q=''
 for i in range(s,len(text)):
  c=text[i]
  if ins:
   if esc: esc=False
   elif c=='\\': esc=True
   elif c==q: ins=False
  else:
   if c in ("'",'"'): ins=True;q=c
   elif c=='[': d+=1
   elif c==']':
    d-=1
    if d==0:return json.loads(text[s:i+1])
R={"tenant":"Kingstonian FC","host":"Ashford Town (Middx) FC","ground":"Robert Parker Stadium","postcode":"TW19 7BH","season":"2026-27","evidence":"Kingstonian's official March 2026 announcement says its Raynes Park Vale groundshare ends after 2025/26 and it signed a two-season groundshare at the Robert Parker Stadium, home of Ashford Town (Middlesex). Kingstonian's current official general information confirms Robert Parker Stadium as its 2026/27 home.","source_url":"https://www.kingstonianfc.com/news/k-s-to-groundshare-at-ashford-town-middlesex"}
text=HTML.read_text(encoding='utf8'); grounds=arr(text,'GROUNDS'); by={}
for g in grounds: by.setdefault(norm(g.get('name') or g.get('club')),[]).append(g)
tr=by.get(norm(R['tenant']),[]); hr=by.get(norm(R['host']),[])
if len(tr)!=1 or len(hr)!=1: raise SystemExit('Safety stop: canonical resolution failed.')
if (tr[0].get('postcode') or '').upper()!=R['postcode'] or (hr[0].get('postcode') or '').upper()!=R['postcode']: raise SystemExit('Safety stop: postcode mismatch.')
ledger=json.loads(LEDGER.read_text(encoding='utf8')); now=datetime.now(timezone.utc).isoformat(); known=ledger.get('known_groundshares') or []
known=[x for x in known if norm(x.get('tenant'))!=norm(R['tenant'])]+[{**R,"approved_at":now,"status":"current","approval_source":"v7.9.16 post-correction current groundshare approval"}]
ledger['known_groundshares']=known; ledger['version']='7.9.16'; ledger['updated_at']=now; LEDGER.write_text(json.dumps(ledger,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
OUT.write_text(json.dumps({"approved_at":now,"version":"7.9.16","relationship":R,"canonical_ground_records_changed":0,"competition_json_changed":False},indent=2,ensure_ascii=False)+'\n',encoding='utf8')
REPORT.write_text(f"# Tin Foil FA Cup — Kingstonian Groundshare Approval\n\nApproved: **{datetime.now(timezone.utc).strftime('%d/%m/%Y, %H:%M:%S UTC')}**\n\n- **Kingstonian FC** → Ashford Town (Middx) FC • Robert Parker Stadium • TW19 7BH • 2026-27\n- Canonical ground records changed: **0**\n- `competition.json` changed: **NO**\n",encoding='utf8')
print('KINGSTONIAN GROUNDSHARE APPROVAL v7.9.16'); print('Approved: Kingstonian FC -> Ashford Town (Middx) FC'); print('Canonical records changed: 0')
