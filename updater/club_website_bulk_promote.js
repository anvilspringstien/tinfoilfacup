#!/usr/bin/env node
'use strict';
// Reviewed evidence -> reproducible website map. Competition/search eligibility is read-only.
const fs=require('node:fs'),path=require('node:path');
function literalRange(html,name,open,close){
 const tag='const '+name+'=',at=html.indexOf(tag);if(at<0)throw Error('Missing '+name);
 const begin=at+tag.length;let depth=0,quoted=false,escaped=false;
 if(html[begin]!==open)throw Error('Unexpected '+name);
 for(let i=begin;i<html.length;i++){const c=html[i];if(quoted){if(escaped)escaped=false;else if(c==='\\')escaped=true;else if(c==='"')quoted=false;continue}
 if(c==='"'){quoted=true;continue}if(c===open)depth++;else if(c===close&&!--depth)return {begin,end:i+1,value:JSON.parse(html.slice(begin,i+1))}}
 throw Error('Unclosed '+name);
}
const normal=s=>String(s).toLowerCase().replace(/&/g,' and ').replace(/\b(fc|cfc)\b/g,' ').replace(/\bafc\s*$/g,' ').replace(/[^a-z0-9]+/g,' ').replace(/\s+/g,' ').trim();
function registry(eligible,competition){
 const names=new Set(eligible.map(c=>c.name));
 function visit(value){if(!value||typeof value!=='object')return;
  if(typeof value.home==='string'&&typeof value.away==='string')for(const club of [value.home,value.away])if(club.trim()&&!/\s\/\s|\b(?:winner|loser|tbc|tbd)\b/i.test(club))names.add(club);
  for(const child of Object.values(value))if(child&&typeof child==='object')visit(child);
 }
 visit(competition);return names;
}
function promote(html,competition,ledger){
 const eligible=literalRange(html,'ELIGIBLE','[',']').value,existing=literalRange(html,'CLUB_WEBSITES','{','}').value;
 if(new Set(eligible.map(c=>c.name)).size!==eligible.length)throw Error('Duplicate eligible club identities');
 const names=registry(eligible,competition),approved={...existing},seen=new Set(),accepted=[],errors=[];
 if(ledger.schema_version!==1||!Array.isArray(ledger.verified))throw Error('Expected schema_version=1 and verified array');
 for(const item of ledger.verified){
  const {club,url,evidence_url,status}=item,verified_on=item.verified_on||ledger.verified_on;
  if(!Array.isArray(item.aliases||[])){errors.push('Invalid aliases: '+club);continue}
  const identities=[club,...(item.aliases||[])];
  if(identities.some(n=>typeof n!=='string'||!names.has(n))){errors.push('Unknown competition club: '+club);continue}
  if(identities.some(n=>normal(n)!==normal(club))){errors.push('Alias identity mismatch: '+club);continue}
  if(identities.some(n=>seen.has(n))||new Set(identities).size!==identities.length){errors.push('Duplicate approval: '+club);continue}
  identities.forEach(n=>seen.add(n));
  if(status!=='verified_official_club_site'){errors.push('Not independently verified: '+club);continue}
  if(!/^\d{4}-\d{2}-\d{2}$/.test(verified_on||'')||!evidence_url){errors.push('Missing evidence/date: '+club);continue}
  try{const u=new URL(url),e=new URL(evidence_url);
   if(u.protocol!=='https:'||e.protocol!=='https:'||u.username||u.password||e.username||e.password)throw Error('HTTPS required');
   if(/(^|\.)(facebook\.com|instagram\.com|twitter\.com|x\.com|wikipedia\.org)$/i.test(u.hostname))throw Error('Social/directory URL');
  }catch(err){errors.push('Invalid URL for '+club+': '+err.message);continue}
  if(identities.some(n=>existing[n]&&existing[n]!==url)){errors.push('Existing mapping conflict: '+club);continue}
  for(const name of identities)if(!existing[name]){approved[name]=url;accepted.push(name)}
 }
 if(errors.length)throw Error(errors.join('\n'));
 return {schema_version:1,eligible:eligible.length,known_competition_identities:names.size,accepted,website_count:Object.keys(approved).length,websites:Object.fromEntries(Object.entries(approved).sort(([a],[b])=>a.localeCompare(b,'en-GB')))};
}
function applyMapping(html,websites){const r=literalRange(html,'CLUB_WEBSITES','{','}');return html.slice(0,r.begin)+JSON.stringify(websites)+html.slice(r.end)}
function main(){
 const args=process.argv.slice(2),option=k=>{const i=args.indexOf(k);return i<0?null:args[i+1]},ledgerFile=option('--ledger'),output=option('--out');
 if(!ledgerFile||!output)throw Error('Usage: node updater/club_website_bulk_promote.js --ledger reviewed.json --out mapping.json [--apply-beta]');
 const root=path.join(__dirname,'..'),beta=path.join(root,'beta/clubfinder-beta.html'),canonical=path.join(root,'competition.json');
 if([beta,canonical,path.join(root,'clubfinder.html')].includes(path.resolve(output)))throw Error('Output cannot replace an application or competition input');
 const html=fs.readFileSync(beta,'utf8'),result=promote(html,JSON.parse(fs.readFileSync(canonical,'utf8')),JSON.parse(fs.readFileSync(ledgerFile,'utf8')));
 fs.writeFileSync(output,JSON.stringify(result,null,2)+'\n');
 if(args.includes('--apply-beta'))fs.writeFileSync(beta,applyMapping(html,result.websites));
 console.log(JSON.stringify({eligible:result.eligible,known_competition_identities:result.known_competition_identities,accepted:result.accepted.length,website_count:result.website_count,beta_applied:args.includes('--apply-beta')},null,2));
}
module.exports={literalRange,normal,registry,promote,applyMapping};
if(require.main===module){try{main()}catch(error){console.error(error.message);process.exitCode=1}}
