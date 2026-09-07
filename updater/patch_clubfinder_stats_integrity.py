#!/usr/bin/env python3
"""Keep the Clubfinder Stats chronology aligned with canonical scorelines.

Presentation-only guard. A decisive displayed scoreline determines the winner / next
custodian; a stale legacy winner field must never override the score. This version
also patches the generated Stats certificate HTML at its source, so the saved/printed
journey cannot bypass canonical custody via r.winner.
"""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / 'clubfinder.html'
text = HTML.read_text(encoding='utf-8')

begin = '/* TIN_FOIL_STATS_INTEGRITY_BEGIN */'
end = '/* TIN_FOIL_STATS_INTEGRITY_END */'
js = r'''/* TIN_FOIL_STATS_INTEGRITY_BEGIN */
function tinFoilStatsFixtureParts(text){
  const s=String(text||'').replace(/\s+/g,' ').trim();
  const m=s.match(/^(.+?)\s*\((\d+)\)\s*v\s*\((\d+)\)\s*(.+)$/i);
  if(!m)return null;
  return {home:m[1].trim(),homeScore:Number(m[2]),awayScore:Number(m[3]),away:m[4].trim()};
}
function tinFoilStatsWinnerFromFixture(text){
  const p=tinFoilStatsFixtureParts(text);
  if(!p||!Number.isFinite(p.homeScore)||!Number.isFinite(p.awayScore)||p.homeScore===p.awayScore)return '';
  return p.homeScore>p.awayScore?p.home:p.away;
}
function tinFoilCertificateWinner(r){
  if(r){
    const hs=Number(r.home_score),as=Number(r.away_score);
    if(Number.isFinite(hs)&&Number.isFinite(as)){
      if(hs===as)return '';
      return (hs>as?String(r.home||''):String(r.away||'')).trim();
    }
  }
  if(typeof canonicalResultWinner==='function')return canonicalResultWinner(r)||'';
  return r&&r.winner?r.winner:'';
}
function tinFoilStatsDisplayClubKey(name){
  return String(name||'').toLowerCase().replace(/&/g,' and ').replace(/\b(association football club|football club|fc|afc|cfc)\b/g,' ').replace(/[^a-z0-9]+/g,' ').trim().replace(/\s+/g,' ');
}
function tinFoilStatsFixtureCount(text){
  const s=String(text||'').replace(/\s+/g,' ');
  const re=/(?:^|\s)([^|]{1,100}?)\s*\(\d+\)\s*v\s*\(\d+\)\s*([^|]{1,100}?)(?=$|\s{2,}|\n)/ig;
  let n=0; while(re.exec(s)&&n<3)n++; return n;
}
function tinFoilStatsLeafElements(root){
  if(!root||typeof root.querySelectorAll!=='function')return [];
  return [...root.querySelectorAll('*')].filter(e=>!e.children||e.children.length===0);
}
function tinFoilStatsRepairRenderedRow(row){
  if(!row)return false;
  const leaves=tinFoilStatsLeafElements(row);
  let fixtureLeaf=null,parts=null;
  for(const leaf of leaves){
    const p=tinFoilStatsFixtureParts(leaf.textContent||'');
    if(p){fixtureLeaf=leaf;parts=p;break;}
  }
  if(!fixtureLeaf||!parts||parts.homeScore===parts.awayScore)return false;
  const winner=parts.homeScore>parts.awayScore?parts.home:parts.away;
  const homeKey=tinFoilStatsDisplayClubKey(parts.home),awayKey=tinFoilStatsDisplayClubKey(parts.away);
  const candidates=leaves.filter(leaf=>{
    if(leaf===fixtureLeaf)return false;
    const k=tinFoilStatsDisplayClubKey(leaf.textContent||'');
    return k&&(k===homeKey||k===awayKey);
  });
  if(!candidates.length)return false;
  const target=candidates[candidates.length-1];
  if(tinFoilStatsDisplayClubKey(target.textContent||'')===tinFoilStatsDisplayClubKey(winner))return false;
  target.textContent=winner;
  return true;
}
function tinFoilStatsFindRenderedRow(fixtureLeaf){
  let node=fixtureLeaf;
  let best=null;
  for(let depth=0;node&&depth<8;depth++,node=node.parentElement){
    const count=tinFoilStatsFixtureCount(node.textContent||'');
    if(count===1)best=node;
    else if(count>1)break;
  }
  return best;
}
function tinFoilRepairStatsCustodyRows(){
  if(!document||typeof document.querySelectorAll!=='function')return 0;
  let repaired=0;
  const leaves=[...document.querySelectorAll('*')].filter(e=>!e.children||e.children.length===0);
  const seen=new Set();
  for(const leaf of leaves){
    if(!tinFoilStatsFixtureParts(leaf.textContent||''))continue;
    const row=tinFoilStatsFindRenderedRow(leaf);
    if(!row||seen.has(row))continue;
    seen.add(row);
    if(tinFoilStatsRepairRenderedRow(row))repaired++;
  }
  return repaired;
}
function tinFoilStartStatsIntegrity(){
  tinFoilRepairStatsCustodyRows();
  if(typeof MutationObserver==='function'){
    let queued=false;
    const observer=new MutationObserver(()=>{if(queued)return;queued=true;setTimeout(()=>{queued=false;tinFoilRepairStatsCustodyRows()},0)});
    const root=document.getElementById('wrap')||document.body;
    if(root)observer.observe(root,{subtree:true,childList:true,characterData:true});
  }
  if(document&&typeof document.addEventListener==='function')document.addEventListener('click',()=>setTimeout(tinFoilRepairStatsCustodyRows,0));
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

# The Stats/Print certificate is generated as an HTML string. Patch that source
# expression itself so it cannot bypass canonical custody with the legacy r.winner.
old_cert = "certEsc(r.winner||'')"
new_cert = "certEsc(tinFoilCertificateWinner(r))"
if new_cert not in text:
    count = text.count(old_cert)
    if count != 1:
        raise SystemExit(f'ABORT: expected exactly one legacy certificate winner expression, found {count}')
    text = text.replace(old_cert, new_cert, 1)

for marker in (
    'function tinFoilStatsFixtureParts(',
    'function tinFoilCertificateWinner(',
    'function tinFoilStatsRepairRenderedRow(',
    'function tinFoilRepairStatsCustodyRows(',
    'target.textContent=winner;',
    new_cert,
):
    if marker not in text:
        raise SystemExit(f'ABORT: required Stats integrity marker missing: {marker}')
if old_cert in text:
    raise SystemExit('ABORT: legacy certificate r.winner renderer still present')

HTML.write_text(text, encoding='utf-8')
print('CLUBFINDER STATS INTEGRITY PATCH: SUCCESS')
print('Generated Stats certificate now derives Winner / Next Custodian from the decisive scoreline.')
print('Rendered-page reconciliation remains as defence in depth.')
print('Draw rows remain unresolved until replay/result resolution.')
print('Competition data and canonical custody logic: UNTOUCHED')
