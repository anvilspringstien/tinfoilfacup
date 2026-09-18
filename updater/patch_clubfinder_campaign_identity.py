#!/usr/bin/env python3
"""Restore and guard Campaign search-number / Pigeon Call Sign identity."""
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[1]
HTML=ROOT/'clubfinder.html'
IDENTITY=ROOT/'updater'/'clubfinder-campaign-identity.js'

text=HTML.read_text(encoding='utf-8')
identity=IDENTITY.read_text(encoding='utf-8').strip()+"\n"
if 'TIN_FOIL_CAMPAIGN_IDENTITY_BEGIN' not in identity or 'Tango Foxtrot 2 Alpha Charlie' not in identity:
    raise SystemExit('ABORT: canonical Campaign identity source invalid')

identity_pat=re.compile(r'/\* TIN_FOIL_CAMPAIGN_IDENTITY_BEGIN \*/.*?/\* TIN_FOIL_CAMPAIGN_IDENTITY_END \*/\n?',re.S)
if identity_pat.search(text):
    text=identity_pat.sub(lambda m:identity,text,count=1)
else:
    boundary="const JOURNEY_STORAGE_KEY='tinFoilFACupJourney_v7';"
    if boundary not in text: raise SystemExit('ABORT: Campaign storage boundary missing')
    text=text.replace(boundary,identity+boundary,1)

identity_css='.campaign-identity{margin:0 0 10px;padding:7px 10px;border-radius:5px;background:#f5f5f5;border-left:4px solid #084c61;color:#084c61;font-size:12px;font-weight:600}.campaign-identity[hidden]{display:none}'
if identity_css not in text:
    if '</style></head>' not in text: raise SystemExit('ABORT: main-page style boundary missing')
    text=text.replace('</style></head>',identity_css+'</style></head>',1)

old_badge="""function updateLiveDataBadge(){
  const e=document.getElementById('liveDataBadge');if(!e)return;
  if(LIVE_DATA_STATUS.state==='live'){
    let w=LIVE_DATA_STATUS.updated_at||'';try{w=new Date(w).toLocaleString('en-GB');}catch(x){}
    e.textContent='Clubfinder v7.6 — Competition data updated: '+w;
  }else e.textContent='Clubfinder v7.6 — '+LIVE_DATA_STATUS.message;
}"""
new_badge="""function updateLiveDataBadge(){
  const e=document.getElementById('liveDataBadge');if(!e)return;
  const searchLabel=typeof tinFoilSearchNumberLabel==='function'?tinFoilSearchNumberLabel(tinFoilCurrentSearchNumber()):'';
  const suffix=searchLabel?'  '+searchLabel:'';
  if(LIVE_DATA_STATUS.state==='live'){
    let w=LIVE_DATA_STATUS.updated_at||'';try{w=new Date(w).toLocaleString('en-GB');}catch(x){}
    e.textContent='Clubfinder v7.6 — Competition data updated: '+w+suffix;
  }else e.textContent='Clubfinder v7.6 — '+LIVE_DATA_STATUS.message+suffix;
}"""
if old_badge in text: text=text.replace(old_badge,new_badge,1)
elif new_badge not in text: raise SystemExit('ABORT: live-data badge boundary drifted')

old_save="function saveJourney(origin,postcode){const s={originName:origin.name,postcode,ended:false,selectedAt:new Date().toISOString()};localStorage.setItem(JOURNEY_STORAGE_KEY,JSON.stringify(s));return s}"
new_save="function saveJourney(origin,postcode){const existing=loadSavedJourney(),same=existing&&norm(existing.originName)===norm(origin.name),identity=tinFoilCampaignIdentityForSave(origin,existing);const s={originName:origin.name,postcode,ended:false,selectedAt:same&&existing.selectedAt?existing.selectedAt:new Date().toISOString()};if(identity.searchNumber){s.searchNumber=identity.searchNumber;s.callSign=identity.callSign}localStorage.setItem(JOURNEY_STORAGE_KEY,JSON.stringify(s));tinFoilRegisterPendingCampaignIdentity(s);return s}"
if old_save in text: text=text.replace(old_save,new_save,1)
elif new_save not in text: raise SystemExit('ABORT: saved Campaign identity boundary drifted')

if 'async function go(){' in text: text=text.replace('async function go(){','async function go(userInitiated=false){',1)
elif 'async function go(userInitiated=false){' not in text: raise SystemExit('ABORT: Clubfinder go() signature boundary drifted')

top_line="  const top=rows.slice(0,3);if(!top.length)throw Error('No eligible clubs could be returned.');"
top_new=top_line+"\n  if(userInitiated)tinFoilBeginSearchIdentity();"
if top_new not in text:
    if text.count(top_line)!=1: raise SystemExit('ABORT: successful-search identity boundary drifted')
    text=text.replace(top_line,top_new,1)

old_events="document.getElementById('postcode').addEventListener('input',function(){this.value=this.value.toUpperCase();});document.getElementById('findBtn').addEventListener('click',go);document.getElementById('postcode').addEventListener('keydown',e=>{if(e.key==='Enter')go()});"
new_events="document.getElementById('postcode').addEventListener('input',function(){this.value=this.value.toUpperCase();});document.getElementById('findBtn').addEventListener('click',()=>go(true));document.getElementById('postcode').addEventListener('keydown',e=>{if(e.key==='Enter')go(true)});"
if old_events in text: text=text.replace(old_events,new_events,1)
elif new_events not in text: raise SystemExit('ABORT: user-search event boundary drifted')

tick=chr(96); dollar='$'
old_return='return '+tick+'<div class="result">'+dollar+'{heading}'+dollar+'{tools}<h2>'
new_return='return '+tick+'<div class="result">'+dollar+'{heading}'+dollar+'{tools}'+dollar+"{mine?tinFoilCampaignIdentityHtml(saved):''}"+'<h2>'
if old_return in text: text=text.replace(old_return,new_return,1)
elif new_return not in text: raise SystemExit('ABORT: Campaign identity display boundary drifted')

hard_line=" localStorage.removeItem(JOURNEY_STORAGE_KEY);"
hard_new=hard_line+"\n if(typeof tinFoilClearCurrentSearchIdentity==='function')tinFoilClearCurrentSearchIdentity();"
if hard_new not in text:
    if text.count(hard_line)!=1: raise SystemExit('ABORT: Hard Reset identity boundary drifted')
    text=text.replace(hard_line,hard_new,1)

stats_saved="  const savedJourneyForStats=loadSavedJourney();\n  const pigeonStats=await tinFoilPigeonMilesForStats(crumbs,savedJourneyForStats&&savedJourneyForStats.postcode,venueForResult);"
stats_new="  const savedJourneyForStats=loadSavedJourney();\n  const campaignCallSign=tinFoilSavedCallSign(savedJourneyForStats);\n  const pigeonStats=await tinFoilPigeonMilesForStats(crumbs,savedJourneyForStats&&savedJourneyForStats.postcode,venueForResult);"
if stats_saved in text: text=text.replace(stats_saved,stats_new,1)
elif stats_new not in text: raise SystemExit('ABORT: Stats Campaign identity data boundary drifted')

call_css='.call-sign{font-stretch:condensed;font-family:Arial Narrow,Arial,Helvetica,sans-serif;font-size:11pt;font-weight:700;letter-spacing:.35px;line-height:1.25;margin-top:4px}'
if call_css not in text:
    anchor=".club{font-stretch:condensed;font-family:Arial Narrow,Arial,Helvetica,sans-serif;font-size:18pt;font-weight:700;letter-spacing:.5px;line-height:1.08;margin-top:5pxtext-transform:uppercase;}.tiny-rule"
    if text.count(anchor)!=1: raise SystemExit('ABORT: Stats Call Sign CSS boundary drifted')
    replacement=".club{font-stretch:condensed;font-family:Arial Narrow,Arial,Helvetica,sans-serif;font-size:18pt;font-weight:700;letter-spacing:.5px;line-height:1.08;margin-top:5pxtext-transform:uppercase;}"+call_css+".tiny-rule"
    text=text.replace(anchor,replacement,1)

old_header="'<section class=\"top\"><div class=\"top-left\"><div class=\"stats-title\">STATS</div><div class=\"sub\">YOUR TIN FOIL FA CUP CAMPAIGN</div><div class=\"red-star\">★</div><div class=\"minor\">STARTED WITH:</div><div class=\"club\">'+certEsc(origin.name)+'</div><div class=\"tiny-rule\"></div><div class=\"minor\">CURRENT CUSTODIAN:</div><div class=\"club\">'+certEsc(carrier.name)+'</div></div>'+"
new_header="'<section class=\"top\"><div class=\"top-left\"><div class=\"stats-title\">STATS</div><div class=\"sub\">YOUR TIN FOIL FA CUP CAMPAIGN</div><div class=\"red-star\">★</div><div class=\"minor\">STARTED WITH:</div><div class=\"club\">'+certEsc(origin.name)+'</div><div class=\"tiny-rule\"></div><div class=\"minor\">CURRENT CUSTODIAN:</div><div class=\"club\">'+certEsc(carrier.name)+'</div>'+(campaignCallSign?'<div class=\"tiny-rule\"></div><div class=\"minor\">PIGEON CALL SIGN:</div><div class=\"call-sign\">'+certEsc(campaignCallSign)+'</div>':'')+'</div>'+"
if old_header in text: text=text.replace(old_header,new_header,1)
elif new_header not in text: raise SystemExit('ABORT: Stats Call Sign presentation boundary drifted')

required=('TIN_FOIL_CAMPAIGN_IDENTITY_BEGIN',"TIN_FOIL_COUNTER_CONFIG_URL='./counter-config.json'",'Tango Foxtrot 2 Alpha Charlie','async function go(userInitiated=false)','if(userInitiated)tinFoilBeginSearchIdentity();',"addEventListener('click',()=>go(true))",'searchNumber=identity.searchNumber','data-tin-foil-campaign-identity','PIGEON CALL SIGN:','campaignCallSign=tinFoilSavedCallSign')
for marker in required:
    if marker not in text: raise SystemExit('ABORT: Campaign identity marker missing: '+marker)
if text.count('TIN_FOIL_CAMPAIGN_IDENTITY_BEGIN')!=1: raise SystemExit('ABORT: Campaign identity source must appear exactly once')

HTML.write_text(text,encoding='utf-8')
print('CLUBFINDER CAMPAIGN IDENTITY PATCH: SUCCESS')
print('Successful user searches: issue one sequential search number')
print('Internal redraws: do not increment')
print('Campaign choice: adopts search number + Pigeon Call Sign')
print('Existing Campaign identity: preserved')
print('Counter failure: non-blocking and harmless')
