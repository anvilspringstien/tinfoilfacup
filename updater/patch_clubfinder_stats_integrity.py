#!/usr/bin/env python3
"""Keep the Clubfinder Stats chronology aligned with canonical scorelines.

Presentation-only guard. A decisive displayed scoreline determines the winner / next
custodian; a stale legacy winner field must never override the score. Draw rows are
left alone because custody remains with the incoming custodian until a replay/result
resolves it.
"""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / 'clubfinder.html'
text = HTML.read_text(encoding='utf-8')

begin = '/* TIN_FOIL_STATS_INTEGRITY_BEGIN */'
end = '/* TIN_FOIL_STATS_INTEGRITY_END */'
js = r'''/* TIN_FOIL_STATS_INTEGRITY_BEGIN */
function tinFoilStatsWinnerFromFixture(text){
  const s=String(text||'').replace(/\s+/g,' ').trim();
  const m=s.match(/^(.+?)\s*\((\d+)\)\s*v\s*\((\d+)\)\s*(.+)$/i);
  if(!m)return '';
  const hs=Number(m[2]),as=Number(m[3]);
  if(!Number.isFinite(hs)||!Number.isFinite(as)||hs===as)return '';
  return (hs>as?m[1]:m[4]).trim();
}
function tinFoilRepairStatsCustodyTable(){
  if(!document||typeof document.querySelectorAll!=='function')return;
  for(const table of document.querySelectorAll('table')){
    const heads=[...table.querySelectorAll('th')].map(x=>String(x.textContent||'').trim().toUpperCase());
    const fixtureCol=heads.findIndex(x=>x==='FIXTURE');
    const winnerCol=heads.findIndex(x=>x.includes('WINNER')&&x.includes('CUSTODIAN'));
    if(fixtureCol<0||winnerCol<0)continue;
    for(const row of table.querySelectorAll('tbody tr')){
      const cells=[...row.querySelectorAll('td')];
      if(!cells[fixtureCol]||!cells[winnerCol])continue;
      const winner=tinFoilStatsWinnerFromFixture(cells[fixtureCol].textContent||'');
      if(winner)cells[winnerCol].textContent=winner;
    }
  }
}
function tinFoilStartStatsIntegrity(){
  tinFoilRepairStatsCustodyTable();
  if(typeof MutationObserver==='function'){
    let queued=false;
    const observer=new MutationObserver(()=>{if(queued)return;queued=true;setTimeout(()=>{queued=false;tinFoilRepairStatsCustodyTable()},0)});
    const root=document.getElementById('wrap')||document.body;
    if(root)observer.observe(root,{subtree:true,childList:true,characterData:true});
  }
  if(document&&typeof document.addEventListener==='function')document.addEventListener('click',()=>setTimeout(tinFoilRepairStatsCustodyTable,0));
}
if(document.readyState==='loading'&&typeof document.addEventListener==='function')document.addEventListener('DOMContentLoaded',tinFoilStartStatsIntegrity);else setTimeout(tinFoilStartStatsIntegrity,0);
/* TIN_FOIL_STATS_INTEGRITY_END */'''

if begin in text or end in text:
    pat = re.compile(re.escape(begin) + r'.*?' + re.escape(end), re.S)
    text, n = pat.subn(lambda m: js, text, count=1)
    if n != 1:
        raise SystemExit(f'ABORT: expected one existing Stats integrity block, replaced {n}')
else:
    boundary = "const JOURNEY_STORAGE_KEY='tinFoilFACupJourney_v7';"
    if boundary not in text:
        raise SystemExit('ABORT: saved-journey JS boundary not found')
    text = text.replace(boundary, js + boundary, 1)

for marker in ('function tinFoilStatsWinnerFromFixture(', 'function tinFoilRepairStatsCustodyTable(', "x==='FIXTURE'", "x.includes('WINNER')&&x.includes('CUSTODIAN')"):
    if marker not in text:
        raise SystemExit(f'ABORT: required Stats integrity marker missing: {marker}')

HTML.write_text(text, encoding='utf-8')
print('CLUBFINDER STATS INTEGRITY PATCH: SUCCESS')
print('Decisive Stats scorelines now determine Winner / Next Custodian display.')
print('Draw rows remain unresolved until replay/result resolution.')
print('Competition data and custody logic: UNTOUCHED')
