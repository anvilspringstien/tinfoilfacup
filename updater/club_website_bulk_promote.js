#!/usr/bin/env node
'use strict';
// Review-gated bulk website mapping generator. Never modifies live Clubfinder.
const fs=require('node:fs'),path=require('node:path');
const args=process.argv.slice(2);const option=k=>{const i=args.indexOf(k);return i<0?null:args[i+1]};
const ledgerFile=option('--ledger'),output=option('--out');
if(!ledgerFile||!output){console.error('Usage: node updater/club_website_bulk_promote.js --ledger reviewed.json --out /tmp/website-mapping.json');process.exit(2)}
const html=fs.readFileSync(path.join(__dirname,'../beta/clubfinder-beta.html'),'utf8');
function literal(name,opening,closing){
 const tag='const '+name+'=',at=html.indexOf(tag);if(at<0)throw Error('Missing '+name);
 const begin=at+tag.length;let depth=0,quoted=false,escaped=false;
 if(html[begin]!==opening)throw Error('Unexpected '+name);
 for(let i=begin;i<html.length;i++){const c=html[i];if(quoted){if(escaped)escaped=false;else if(c==='\\')escaped=true;else if(c==='"')quoted=false;continue}
 if(c==='"'){quoted=true;continue}if(c===opening)depth++;else if(c===closing&&!--depth)return JSON.parse(html.slice(begin,i+1))}
 throw Error('Unclosed '+name);
}
const eligible=literal('ELIGIBLE','[',']'),existing=literal('CLUB_WEBSITES','{','}');
const names=new Set(eligible.map(x=>x.name));if(names.size!==eligible.length)throw Error('Duplicate eligible club identities');
const ledger=JSON.parse(fs.readFileSync(ledgerFile,'utf8'));
if(ledger.schema_version!==1||!Array.isArray(ledger.verified))throw Error('Expected schema_version=1 and verified array');
const approved={...existing},seen=new Set(),errors=[],accepted=[];
for(const item of ledger.verified){
 const {club,url,evidence_url,verified_on,status}=item;
 if(typeof club!=='string'||!names.has(club)){errors.push('Unknown eligible club: '+club);continue}
 if(seen.has(club)){errors.push('Duplicate approval: '+club);continue}seen.add(club);
 if(status!=='verified_official_club_site'){errors.push('Not independently verified: '+club);continue}
 if(!verified_on||!/^\d{4}-\d{2}-\d{2}$/.test(verified_on)||!evidence_url){errors.push('Missing evidence/date: '+club);continue}
 try{const u=new URL(url),e=new URL(evidence_url);
  if(u.protocol!=='https:'||e.protocol!=='https:'||u.username||u.password||e.username||e.password)throw Error('HTTPS required');
  if(/(^|\.)facebook\.com$|(^|\.)instagram\.com$|(^|\.)twitter\.com$|(^|\.)x\.com$|(^|\.)wikipedia\.org$/i.test(u.hostname))throw Error('Social/directory URL');
 }catch(err){errors.push('Invalid URL for '+club+': '+err.message);continue}
 if(existing[club]&&existing[club]!==url){errors.push('Existing mapping conflict: '+club);continue}
 if(!existing[club]){approved[club]=url;accepted.push(club)}
}
if(errors.length){console.error(errors.join('\n'));process.exit(1)}
const sorted=Object.fromEntries(Object.entries(approved).sort(([a],[b])=>a.localeCompare(b,'en-GB')));
fs.writeFileSync(output,JSON.stringify({schema_version:1,accepted,website_count:Object.keys(sorted).length,websites:sorted},null,2)+'\n');
console.log(JSON.stringify({eligible:eligible.length,accepted:accepted.length,website_count:Object.keys(sorted).length},null,2));
