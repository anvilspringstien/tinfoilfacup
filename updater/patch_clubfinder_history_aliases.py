#!/usr/bin/env python3
"""Harden Clubfinder historical Campaign lookup against fragmented alias buckets.

Canonical result_history can legitimately contain repeated club-name variants.
Clubfinder must collect semantic rows involving the club across the whole history
section rather than trusting one exact-name bucket. Extra Preliminary origins are
also merged from the embedded tie table when available, then deduplicated.
"""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / 'clubfinder.html'
text = HTML.read_text(encoding='utf-8')

history_fn = r'''function historicalResultsForClub(club){
  const out=[];
  function add(r,round){
    if(!r||typeof r!=='object')return;
    if(!sameClubIdentity(r.home,club.name)&&!sameClubIdentity(r.away,club.name))return;
    if(!out.some(x=>sameSemanticResult(x.result,r)))out.push({round:round||r.round||club.entry_round||'FA Cup',result:r});
  }
  const f=club.fixture||{};
  /* TIN_FOIL_HISTORY_ALIAS_HARDENING:
     Preserve an available Extra Preliminary origin even when a partial live
     bucket already contains a later replay/result. */
  if(club.entry_round==='Extra Preliminary Round'&&f.number!=null){
    add(EPR_RESULTS_BY_TIE[String(f.number)]||null,club.entry_round);
  }
  const hist=liveLookup('result_history',club.name);
  if(Array.isArray(hist))for(const r of hist)add(r,r&&r.round);
  /* Canonical history can contain uneven alias buckets. Scan every bucket for
     semantic participation so an exact-name bucket cannot hide earlier ties. */
  const allHistory=(LIVE_COMPETITION_DATA&&LIVE_COMPETITION_DATA.result_history)||{};
  for(const arr of Object.values(allHistory)){
    if(!Array.isArray(arr))continue;
    for(const r of arr)add(r,r&&r.round);
  }
  add(liveLookup('results',club.name));
  if(!out.length){
    if(f.result&&typeof f.result==='object')add(f.result,club.entry_round||f.result.round);
    const key=String(club.name||'').replace(/\s+(FC|AFC|CFC)$/,'');
    add(CURRENT_RESULT_OVERRIDES[club.name]||CURRENT_RESULT_OVERRIDES[key]||null);
    add(liveLookup('results',club.name));
  }
  out.sort((a,b)=>resultSortValue(a.result)-resultSortValue(b.result));
  return out;
}'''

pat = re.compile(r'function historicalResultsForClub\(club\)\{.*?\}\s*(?=function buildJourney)', re.S)
text, n = pat.subn(lambda m: history_fn + ' ', text, count=1)
if n != 1:
    raise SystemExit(f'ABORT: expected one historicalResultsForClub function, replaced {n}')

required = (
    'TIN_FOIL_HISTORY_ALIAS_HARDENING',
    "const allHistory=(LIVE_COMPETITION_DATA&&LIVE_COMPETITION_DATA.result_history)||{};",
    'for(const arr of Object.values(allHistory))',
    "add(EPR_RESULTS_BY_TIE[String(f.number)]||null,club.entry_round);",
)
for marker in required:
    if marker not in text:
        raise SystemExit(f'ABORT: history alias hardening marker missing: {marker}')

HTML.write_text(text, encoding='utf-8')
print('CLUBFINDER HISTORY ALIAS PATCH: SUCCESS')
print('Historical rows: collected across all canonical alias buckets')
print('Extra Preliminary origin: merged when embedded tie result is available')
print('Semantic duplicates: suppressed')
print('Competition data: UNTOUCHED')
