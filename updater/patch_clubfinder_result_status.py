#!/usr/bin/env python3
"""Embed Competition Health result-waiting state into Clubfinder presentation.

This is deliberately presentation-only. Competition Health remains the source of
truth for grace-period / overdue classification; this patch exposes that same
classification to users whose rendered Journey currently shows the affected tie.
"""
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / 'clubfinder.html'
HEALTH = ROOT / 'updater' / 'competition-health.json'

text = HTML.read_text(encoding='utf-8')
health = json.loads(HEALTH.read_text(encoding='utf-8'))

payload = {
    'checked_at': health.get('checked_at'),
    'grace_hours': health.get('grace_hours', 3),
    'awaiting_grace': health.get('awaiting_grace') or [],
    'overdue': health.get('overdue') or [],
}
payload_json = json.dumps(payload, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')

css = r'''
.tin-foil-result-health{margin:10px 0 14px;padding:11px 13px;border-radius:8px;font:300 13px/1.5 Poppins,Arial,sans-serif}
.tin-foil-result-health[hidden]{display:none}
.tin-foil-result-health-item+ .tin-foil-result-health-item{margin-top:9px;padding-top:9px;border-top:1px solid rgba(0,0,0,.12)}
.tin-foil-result-health-title{font-weight:600;margin-bottom:2px}
.tin-foil-result-health--grace{background:#fff7d6;border:1px solid #d5b84b;color:#3d3300}
.tin-foil-result-health--overdue{background:#fff0d8;border:1px solid #cf8128;color:#4d2a00}
'''.strip()

if '.tin-foil-result-health{' not in text:
    if '</style>' not in text:
        raise SystemExit('ABORT: page style boundary not found')
    text = text.replace('</style>', css + '</style>', 1)

begin = '/* TIN_FOIL_RESULT_HEALTH_BEGIN */'
end = '/* TIN_FOIL_RESULT_HEALTH_END */'
js = r'''/* TIN_FOIL_RESULT_HEALTH_BEGIN */
const TIN_FOIL_RESULT_HEALTH=__PAYLOAD__;
function tinFoilHealthKey(s){return String(s||'').toLowerCase().replace(/&/g,' and ').replace(/\b(association football club|football club|fc|afc|cfc)\b/g,' ').replace(/[^a-z0-9]+/g,' ').trim().replace(/\s+/g,' ')}
function tinFoilHealthTextHasClub(text,name){
  const hay=' '+tinFoilHealthKey(text)+' ',needle=' '+tinFoilHealthKey(name)+' ';
  return needle.trim()&&hay.includes(needle);
}
function tinFoilResultHealthMatches(renderedText,health){
  const h=health||TIN_FOIL_RESULT_HEALTH;
  const out=[];
  for(const phase of ['awaiting_grace','overdue']){
    for(const tie of (h[phase]||[])){
      if(tinFoilHealthTextHasClub(renderedText,tie.home)&&tinFoilHealthTextHasClub(renderedText,tie.away))out.push({phase,tie});
    }
  }
  return out;
}
function tinFoilResultHealthRenderedText(){
  const ids=['results','wrap','journeyCurrentClub','journeyPath','campaignSummary','currentStatus'];
  return ids.map(id=>{const e=document.getElementById(id);return e&&!e.hidden?e.textContent||'':''}).join(' ');
}
function tinFoilResultHealthTarget(){
  return document.getElementById('liveDataTools')||document.getElementById('status')||document.getElementById('results');
}
function tinFoilRenderResultHealthNotice(){
  const matches=tinFoilResultHealthMatches(tinFoilResultHealthRenderedText());
  let box=document.getElementById('tinFoilResultHealthNotice');
  if(!matches.length){if(box)box.remove();return;}
  const mode=matches.some(x=>x.phase==='overdue')?'overdue':'grace';
  const key=mode+'|'+matches.map(x=>x.phase+':'+x.tie.home+'|'+x.tie.away).join(';');
  if(box&&box.dataset.healthKey===key)return;
  if(!box){box=document.createElement('div');box.id='tinFoilResultHealthNotice';const target=tinFoilResultHealthTarget();if(!target||typeof target.insertAdjacentElement!=='function')return;target.insertAdjacentElement('afterend',box)}
  box.dataset.healthKey=key;
  box.className='tin-foil-result-health tin-foil-result-health--'+mode;
  box.setAttribute('role','status');
  box.innerHTML=matches.map(x=>{
    const t=x.tie||{},fixture='<strong>'+esc(t.home)+' v '+esc(t.away)+'</strong>';
    if(x.phase==='overdue')return '<div class="tin-foil-result-health-item"><div class="tin-foil-result-health-title">🟠 Result awaiting confirmation</div>'+fixture+' has been played, but we haven\'t yet confirmed the result. Your Tin Foil FA Cup Campaign will update automatically once the result is verified.</div>';
    return '<div class="tin-foil-result-health-item"><div class="tin-foil-result-health-title">🟡 Checking the result…</div>'+fixture+' has been played and is still inside our '+esc(String(TIN_FOIL_RESULT_HEALTH.grace_hours||3))+'-hour checking period. Your Tin Foil FA Cup Campaign will update automatically once the result is verified.</div>';
  }).join('');
}
function tinFoilStartResultHealthNotice(){
  tinFoilRenderResultHealthNotice();
  const roots=[document.getElementById('results'),document.getElementById('wrap')].filter(Boolean);
  if(typeof MutationObserver==='function'){
    let queued=false;
    const observer=new MutationObserver(()=>{if(queued)return;queued=true;setTimeout(()=>{queued=false;tinFoilRenderResultHealthNotice()},0)});
    roots.forEach(root=>observer.observe(root,{subtree:true,childList:true,characterData:true,attributes:true,attributeFilter:['hidden','style','class']}));
  }
  if(document&&typeof document.addEventListener==='function')document.addEventListener('click',()=>setTimeout(tinFoilRenderResultHealthNotice,0));
}
if(document.readyState==='loading'&&typeof document.addEventListener==='function')document.addEventListener('DOMContentLoaded',tinFoilStartResultHealthNotice);else setTimeout(tinFoilStartResultHealthNotice,0);
/* TIN_FOIL_RESULT_HEALTH_END */'''.replace('__PAYLOAD__', payload_json)

if begin in text or end in text:
    pat = re.compile(re.escape(begin) + r'.*?' + re.escape(end), re.S)
    text, n = pat.subn(lambda m: js, text, count=1)
    if n != 1:
        raise SystemExit(f'ABORT: expected one existing result-health block, replaced {n}')
else:
    boundary = "const JOURNEY_STORAGE_KEY='tinFoilFACupJourney_v7';"
    if boundary not in text:
        raise SystemExit('ABORT: saved-journey JS boundary not found')
    text = text.replace(boundary, js + boundary, 1)

required = (
    'const TIN_FOIL_RESULT_HEALTH=',
    'function tinFoilResultHealthMatches(',
    '🟠 Result awaiting confirmation',
    '🟡 Checking the result…',
    'Your Tin Foil FA Cup Campaign will update automatically once the result is verified.',
)
for marker in required:
    if marker not in text:
        raise SystemExit(f'ABORT: required result-health marker missing: {marker}')

if '🔴 Result awaiting confirmation' in text:
    raise SystemExit('ABORT: public outstanding-result state must not be red')

HTML.write_text(text, encoding='utf-8')
print('CLUBFINDER RESULT-STATUS PATCH: SUCCESS')
print('Competition Health checked_at:', payload.get('checked_at'))
print('Grace-period ties embedded:', len(payload['awaiting_grace']))
print('Awaiting-confirmation ties embedded:', len(payload['overdue']))
for tie in payload['overdue']:
    print('AWAITING CONFIRMATION:', tie.get('home'), 'v', tie.get('away'))
print('Competition result/custodian logic: UNTOUCHED')
