#!/usr/bin/env node
'use strict';
// Bulk website candidate triage. Read-only. Does NOT approve or publish websites.
// node updater/club_website_bulk_audit.js --source directory.csv --out /tmp/club-websites
const fs=require('node:fs'),path=require('node:path');
const args=process.argv.slice(2);
function opt(k){const i=args.indexOf(k);return i<0?null:args[i+1]}
const source=opt('--source'),out=opt('--out');
if(!source||!out){console.error('Usage: node updater/club_website_bulk_audit.js --source directory.csv --out output-prefix');process.exit(2)}
function csv(text){
 const rows=[];let row=[],field='',quoted=false;
 for(let i=0;i<text.length;i++){const c=text[i];
  if(quoted){if(c==='"'&&text[i+1]==='"'){field+='"';i++}else if(c==='"')quoted=false;else field+=c}
  else if(c==='"')quoted=true;else if(c===','){row.push(field);field=''}else if(c==='\n'){row.push(field.replace(/\r$/,''));rows.push(row);row=[];field=''}else field+=c;
 }
 if(quoted)throw Error('Unterminated CSV quote');
 if(field||row.length){row.push(field);rows.push(row)}
 const headers=rows.shift().map(x=>x.trim().toLowerCase().replace(/[^a-z0-9]+/g,'_'));
 return rows.filter(r=>r.some(Boolean)).map(r=>Object.fromEntries(headers.map((h,i)=>[h,(r[i]||'').trim()])));
}
function literal(html,name,open,close){
 const prefix='const '+name+'=',start=html.indexOf(prefix);
 if(start<0)throw Error('Missing '+name);
 const i0=start+prefix.length;if(html[i0]!==open)throw Error('Unexpected '+name+' syntax');
 let depth=0,quoted=false,escaped=false;
 for(let i=i0;i<html.length;i++){const c=html[i];
  if(quoted){if(escaped)escaped=false;else if(c==='\\')escaped=true;else if(c==='"')quoted=false;continue}
  if(c==='"'){quoted=true;continue}
  if(c===open)depth++;else if(c===close&&!--depth)return JSON.parse(html.slice(i0,i+1));
 }
 throw Error('Unterminated '+name);
}
const html=fs.readFileSync(path.join(__dirname,'../beta/clubfinder-beta.html'),'utf8');
const eligible=literal(html,'ELIGIBLE','[',']'),existing=literal(html,'CLUB_WEBSITES','{','}');
const directory=csv(fs.readFileSync(source,'utf8'));
if(!directory.length)throw Error('Source CSV has no records');
if(!('club_name' in directory[0])||!('website' in directory[0]))throw Error('CSV requires Club Name and Website columns');
const normal=s=>String(s||'').normalize('NFKD').toLowerCase().replace(/&/g,'and').replace(/\b(?:football club|f\.?c\.?)\b/g,'').replace(/[^a-z0-9]/g,'');
const postcode=s=>String(s||'').toUpperCase().replace(/\s/g,'');
const safe=url=>{try{const u=new URL(url);return ['http:','https:'].includes(u.protocol)&&!/(^|\.)facebook\.com$|(^|\.)instagram\.com$|(^|\.)x\.com$|(^|\.)twitter\.com$|(^|\.)wikipedia\.org$|(^|\.)pitchero\.com$/i.test(u.hostname)}catch{return false}};
const index=new Map();
for(const d of directory){const k=normal(d.club_name);if(!index.has(k))index.set(k,[]);index.get(k).push(d)}
const result=[],stats={eligible:eligible.length,already_linked:0,high_confidence_candidate:0,needs_review:0,no_candidate:0};
for(const club of eligible){
 if(existing[club.name]){stats.already_linked++;continue}
 const matches=index.get(normal(club.name))||[];
 const candidates=matches.filter(x=>safe(x.website));
 const groundPostcode=postcode(club.fixture?.postcode||club.postcode||'');
 const samePostcode=groundPostcode?candidates.filter(x=>postcode(x.postcode)===groundPostcode):[];
 let status='no_candidate',chosen=null,reason='No exact-normalised club name with acceptable website URL';
 if(candidates.length){chosen=candidates[0];status='needs_review';reason='Name match alone does not verify official club identity';
  if(candidates.length===1&&groundPostcode&&samePostcode.length===1){status='high_confidence_candidate';reason='Exact-normalised name and postcode match; independent official-site verification still required'}
  else if(candidates.length>1)reason='Multiple directory candidates: possible club identity collision';
 }
 stats[status]++;
 result.push({club:club.name,status,candidate_url:chosen?.website||'',source_name:chosen?.club_name||'',source_postcode:chosen?.postcode||'',club_postcode:groundPostcode,reason,source:'Non-League Network candidate export; not independently verified'});
}
const columns=['club','status','candidate_url','source_name','source_postcode','club_postcode','reason','source'];
const quote=x=>'"'+String(x??'').replace(/"/g,'""')+'"';
fs.writeFileSync(out+'.csv',columns.join(',')+'\n'+result.map(r=>columns.map(k=>quote(r[k])).join(',')).join('\n')+'\n');
fs.writeFileSync(out+'.json',JSON.stringify({schema_version:1,source_file:path.basename(source),stats,records:result},null,2)+'\n');
console.log(JSON.stringify(stats,null,2));
