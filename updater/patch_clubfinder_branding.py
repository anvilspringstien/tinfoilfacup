#!/usr/bin/env python3
"""Apply presentation-only Tin Foil FA Cup branding to Clubfinder.

This patch deliberately does not alter club, ground, mileage, fixture, result,
custodian, or journey-progression data. It controls share-preview metadata and
replaces native browser confirm() prompts with a branded in-page confirmation
modal while preserving the same OK/Cancel behaviour.
"""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / 'clubfinder.html'
text = P.read_text(encoding='utf-8')

TITLE = 'Tin Foil FA Cup Clubfinder v7.6'
URL = 'https://anvilspringstien.github.io/tinfoilfacup/clubfinder.html'
DESCRIPTION = 'Find your three nearest eligible clubs and follow your Tin Foil FA Cup Journey.'

# ---- Share / social preview metadata -------------------------------------------------
text, n = re.subn(r'<title>.*?</title>', f'<title>{TITLE}</title>', text, count=1, flags=re.S)
if n != 1:
    raise SystemExit(f'ABORT: expected one <title>, replaced {n}')

meta_block = (
    f'<meta property="og:title" content="{TITLE}">'
    '<meta property="og:site_name" content="Tin Foil FA Cup">'
    '<meta property="og:type" content="website">'
    f'<meta property="og:url" content="{URL}">'
    f'<meta property="og:description" content="{DESCRIPTION}">'
    f'<meta name="description" content="{DESCRIPTION}">'
    f'<link rel="canonical" href="{URL}">'
)

# Remove only the metadata this patch owns, then reinsert one canonical block.
owned = [
    r'<meta\s+property="og:title"\s+content="[^"]*">',
    r'<meta\s+property="og:site_name"\s+content="[^"]*">',
    r'<meta\s+property="og:type"\s+content="[^"]*">',
    r'<meta\s+property="og:url"\s+content="[^"]*">',
    r'<meta\s+property="og:description"\s+content="[^"]*">',
    r'<meta\s+name="description"\s+content="[^"]*">',
    r'<link\s+rel="canonical"\s+href="[^"]*">',
]
for pat in owned:
    text = re.sub(pat, '', text, flags=re.I)
needle = f'<title>{TITLE}</title>'
if text.count(needle) != 1:
    raise SystemExit('ABORT: branded title boundary not unique')
text = text.replace(needle, needle + meta_block, 1)

# ---- Branded in-page confirmation modal ---------------------------------------------
css_marker = '.tin-foil-confirm-overlay{'
modal_css = r'''
.tin-foil-confirm-overlay{position:fixed;inset:0;z-index:99999;display:flex;align-items:center;justify-content:center;padding:20px;background:rgba(0,0,0,.48)}
.tin-foil-confirm-overlay[hidden]{display:none}
.tin-foil-confirm-box{width:min(420px,100%);background:#fff;border:1px solid #d7d7d7;border-radius:10px;box-shadow:0 12px 36px rgba(0,0,0,.28);padding:18px;font:300 13px/1.5 Poppins,Arial,sans-serif;color:#111}
.tin-foil-confirm-title{font-size:16px;font-weight:600;color:#084C61;margin:0 0 10px}
.tin-foil-confirm-message{white-space:pre-wrap;margin:0 0 16px}
.tin-foil-confirm-actions{display:flex;justify-content:flex-end;gap:8px}
.tin-foil-confirm-actions button{min-width:74px;height:36px;border:2px solid #084C61;border-radius:10px;padding:0 14px;font:400 13px Poppins,Arial,sans-serif;cursor:pointer}
#tinFoilConfirmCancel{background:#fff;color:#084C61}
#tinFoilConfirmOk{background:#084C61;color:#FAFAFA}
'''.strip()
if css_marker not in text:
    if '</style>' not in text:
        raise SystemExit('ABORT: page style boundary not found')
    text = text.replace('</style>', modal_css + '</style>', 1)

js_marker = 'function tinFoilConfirm(message){'
modal_js = r'''function tinFoilConfirm(message){
  return new Promise(resolve=>{
    let overlay=document.getElementById('tinFoilConfirmOverlay');
    if(!overlay){
      overlay=document.createElement('div');
      overlay.id='tinFoilConfirmOverlay';
      overlay.className='tin-foil-confirm-overlay';
      overlay.hidden=true;
      overlay.innerHTML='<div class="tin-foil-confirm-box" role="dialog" aria-modal="true" aria-labelledby="tinFoilConfirmTitle" aria-describedby="tinFoilConfirmMessage"><div id="tinFoilConfirmTitle" class="tin-foil-confirm-title">Tin Foil FA Cup says</div><div id="tinFoilConfirmMessage" class="tin-foil-confirm-message"></div><div class="tin-foil-confirm-actions"><button id="tinFoilConfirmCancel" type="button">Cancel</button><button id="tinFoilConfirmOk" type="button">OK</button></div></div>';
      document.body.appendChild(overlay);
    }
    const messageEl=document.getElementById('tinFoilConfirmMessage');
    const ok=document.getElementById('tinFoilConfirmOk');
    const cancel=document.getElementById('tinFoilConfirmCancel');
    const previous=document.activeElement;
    messageEl.textContent=String(message||'');
    overlay.hidden=false;
    function finish(value){
      document.removeEventListener('keydown',onKey);
      overlay.hidden=true;
      ok.onclick=null;cancel.onclick=null;overlay.onclick=null;
      if(previous&&typeof previous.focus==='function')previous.focus();
      resolve(value);
    }
    function onKey(e){if(e.key==='Escape'){e.preventDefault();finish(false)}}
    ok.onclick=()=>finish(true);
    cancel.onclick=()=>finish(false);
    overlay.onclick=e=>{if(e.target===overlay)finish(false)};
    document.addEventListener('keydown',onKey);
    ok.focus();
  });
}
'''
if js_marker not in text:
    boundary="const JOURNEY_STORAGE_KEY='tinFoilFACupJourney_v7';"
    if boundary not in text:
        raise SystemExit('ABORT: saved-journey JS boundary not found')
    text = text.replace(boundary, modal_js + boundary, 1)

old_choose="function chooseJourney(name,postcode){const o=ELIGIBLE.find(c=>norm(c.name)===norm(name));if(!o)return;const e=loadSavedJourney();if(e&&norm(e.originName)!==norm(o.name)&&!confirm('Replace your saved Tin Foil FA Cup Journey with '+o.name+'?'))return;saveJourney(o,postcode);window.__showOriginalTinFoilJourneys=false;go()}"
new_choose="async function chooseJourney(name,postcode){const o=ELIGIBLE.find(c=>norm(c.name)===norm(name));if(!o)return;const e=loadSavedJourney();if(e&&norm(e.originName)!==norm(o.name)&&!await tinFoilConfirm('Replace your saved Tin Foil FA Cup Journey with '+o.name+'?'))return;saveJourney(o,postcode);window.__showOriginalTinFoilJourneys=false;go()}"
if old_choose in text:
    text=text.replace(old_choose,new_choose,1)
elif new_choose not in text:
    raise SystemExit('ABORT: chooseJourney confirmation boundary not found')

old_end="function endMyJourney(){if(confirm('End your Tin Foil FA Cup Journey here? You can resume it later.')){updateSavedJourney({ended:true,endedAt:new Date().toISOString()});go()}}"
new_end="async function endMyJourney(){if(await tinFoilConfirm('End your Tin Foil FA Cup Journey here? You can resume it later.')){updateSavedJourney({ended:true,endedAt:new Date().toISOString()});go()}}"
if old_end in text:
    text=text.replace(old_end,new_end,1)
elif new_end not in text:
    raise SystemExit('ABORT: endMyJourney confirmation boundary not found')

old_hard="function hardResetFinder(){\n if(!confirm('Hard Reset will forget the saved Tin Foil FA Cup Journey in this browser and return the finder to a first-time-user state. Continue?'))return;"
new_hard="async function hardResetFinder(){\n if(!await tinFoilConfirm('Hard Reset will forget the saved Tin Foil FA Cup Journey in this browser and return the finder to a first-time-user state. Continue?'))return;"
if old_hard in text:
    text=text.replace(old_hard,new_hard,1)
elif new_hard not in text:
    raise SystemExit('ABORT: hardResetFinder confirmation boundary not found')

# No browser-native confirmation should remain. This prevents a future stray
# "anvilspringstien.github.io says" prompt from reappearing unnoticed.
if re.search(r'(?<![A-Za-z])confirm\s*\(', text):
    raise SystemExit('ABORT: native confirm() remains after branding patch')

required = (
    f'<title>{TITLE}</title>',
    f'<meta property="og:title" content="{TITLE}">',
    '<meta property="og:site_name" content="Tin Foil FA Cup">',
    f'<meta property="og:url" content="{URL}">',
    '<div id="tinFoilConfirmTitle" class="tin-foil-confirm-title">Tin Foil FA Cup says</div>',
    'async function chooseJourney(',
    'async function endMyJourney(',
    'async function hardResetFinder(',
)
for marker in required:
    if marker not in text:
        raise SystemExit(f'ABORT: required branding marker missing: {marker}')

P.write_text(text, encoding='utf-8')
print('CLUBFINDER BRANDING PATCH: SUCCESS')
print(f'Share title: {TITLE}')
print('Branded confirmation heading: Tin Foil FA Cup says')
print('Native confirm() prompts remaining: 0')
print('Club, ground, mileage, fixture, custodian and journey logic: UNTOUCHED')
