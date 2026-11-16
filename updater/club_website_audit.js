#!/usr/bin/env node
// Read-only audit of explicit club website identities in the BETA Clubfinder.
// Usage: node updater/club_website_audit.js [--csv]
// No network access, no guessed domains, no competition data writes.
const fs=require('fs');
const path=require('path');
const html=fs.readFileSync(path.join(__dirname,'../beta/clubfinder-beta.html'),'utf8');
function literal(name,opening,closing){
  const token='const '+name+'=';
  const at=html.indexOf(token);
  if(at<0)throw Error('Missing '+name);
  const start=at+token.length;
  if(html[start]!==opening)throw Error('Unexpected '+name+' format');
  let depth=0,quote=false,escape=false;
  for(let i=start;i<html.length;i++){
    const ch=html[i];
    if(quote){if(escape)escape=false;else if(ch==='\\')escape=true;else if(ch==='"')quote=false;continue;}
    if(ch==='"'){quote=true;continue;}
    if(ch===opening)depth++;
    if(ch===closing&&!--depth)return JSON.parse(html.slice(start,i+1));
  }
  throw Error('Unclosed '+name);
}
const eligible=literal('ELIGIBLE','[',']');
const websites=literal('CLUB_WEBSITES','{','}');
const counts=new Map();
for(const c of eligible)counts.set(c.name,(counts.get(c.name)||0)+1);
const names=[...counts.keys()].sort((a,b)=>a.localeCompare(b,'en-GB'));
const rows=names.map(name=>({club:name,website:websites[name]||'',status:websites[name]?'existing_unverified':'missing',evidence:'',notes:''}));
const unmatched=Object.keys(websites).filter(name=>!counts.has(name)).sort();
const report={
  eligible_rows:eligible.length,unique_eligible_names:names.length,
  explicit_website_identities:Object.keys(websites).length,
  matched_eligible_names:rows.filter(r=>r.website).length,
  missing_eligible_names:rows.filter(r=>!r.website).length,
  unmatched_website_keys:unmatched,
  duplicate_eligible_names:[...counts].filter(([,n])=>n>1).map(([name,n])=>({name,count:n})),
  status_note:'Existing URLs are not independently verified by this inventory. No candidate URL is guessed.'
};
if(process.argv.includes('--csv')){
  const fields=['club','website','status','evidence','notes'];
  const esc=v=>'"'+String(v??'').replace(/"/g,'""')+'"';
  process.stdout.write(fields.join(',')+'\n'+rows.map(r=>fields.map(k=>esc(r[k])).join(',')).join('\n')+'\n');
}else{
  process.stdout.write(JSON.stringify(report,null,2)+'\n');
}
