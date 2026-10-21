#!/usr/bin/env node
'use strict';
// Read-only queue: current fixtures first; every existing link still needs evidence.
const fs=require('node:fs'),path=require('node:path');
const {literalRange}=require('./club_website_bulk_promote');
const root=path.join(__dirname,'..'),html=fs.readFileSync(path.join(root,'beta/clubfinder-beta.html'),'utf8');
const eligible=literalRange(html,'ELIGIBLE','[',']').value,websites=literalRange(html,'CLUB_WEBSITES','{','}').value;
const competition=JSON.parse(fs.readFileSync(path.join(root,'competition.json'),'utf8'));
const active=new Set();for(const f of Object.values(competition.fixtures||{}))for(const n of [f.home,f.away])if(typeof n==='string'&&!/\s\/\s|\b(tbc|tbd|winner)\b/i.test(n))active.add(n);
const evidence=new Map(),reviewedAliases=[];for(const file of fs.readdirSync(__dirname).filter(n=>/^club_website_verified_batch_.*\.json$/.test(n))){
 const ledger=JSON.parse(fs.readFileSync(path.join(__dirname,file),'utf8'));for(const row of ledger.verified||[])if(row.status==='verified_official_club_site')reviewedAliases.push([row.club,...(row.aliases||[])]);for(const row of ledger.verified||[])for(const name of [row.club,...(row.aliases||[])])if(row.status==='verified_official_club_site')evidence.set(name,{url:row.url,evidence_url:row.evidence_url,verified_on:row.verified_on||ledger.verified_on,ledger:file});
}
const allNames=new Set([...active,...eligible.map(c=>c.name)]),parents=new Map([...allNames].map(n=>[n,n]));
const leader=name=>{let n=name;while(parents.get(n)!==n)n=parents.get(n);return n};
for(const aliases of reviewedAliases){const known=aliases.filter(n=>allNames.has(n));for(const n of known.slice(1))parents.set(leader(n),leader(known[0]))}
const groups=new Map();for(const name of allNames){const key=leader(name);if(!groups.has(key))groups.set(key,new Set());groups.get(key).add(name)}
const rows=[...groups.values()].map(set=>{
 const identities=[...set].sort(),current=identities.filter(n=>active.has(n)),links=[...new Set(identities.map(n=>websites[n]).filter(Boolean))];
 const records=identities.map(n=>evidence.get(n)).filter(Boolean),verified=links.length===1&&records.some(r=>r.url===links[0]);
 return {club:current[0]||identities[0],identities,current_competition:!!current.length,website:links.length===1?links[0]:null,status:links.length>1?'conflict':verified?'verified':links.length?'needs_verification':'missing',priority:current.length?0:verified?3:links.length?1:2,evidence:records};
}).sort((a,b)=>a.priority-b.priority||a.club.localeCompare(b.club,'en-GB'));
const report={schema_version:1,competition_updated_at:competition.updated_at,eligible:eligible.length,current_clubs:active.size,current_verified:rows.filter(r=>r.current_competition&&r.status==='verified').length,current_linked:rows.filter(r=>r.current_competition&&r.website).length,eligible_linked:eligible.filter(c=>websites[c.name]).length,rows};
const i=process.argv.indexOf('--out');if(i>=0){if(!process.argv[i+1])throw Error('--out requires a path');if(['competition.json','clubfinder.html','beta/clubfinder-beta.html'].some(n=>path.join(root,n)===path.resolve(process.argv[i+1])))throw Error('Queue output cannot overwrite application or competition input');fs.writeFileSync(process.argv[i+1],JSON.stringify(report,null,2)+'\n')}
console.log(JSON.stringify({...report,rows:undefined,status_counts:rows.reduce((a,r)=>(a[r.status]=(a[r.status]||0)+1,a),{})},null,2));
