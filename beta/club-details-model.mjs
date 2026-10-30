/* Read-only projection of published club identity and canonical fixtures. */
const key=value=>String(value||'').trim().toLocaleLowerCase('en-GB');
export function clubDetails(name,queue,competition){
 const query=key(name);
 if(!query)throw Error('Open the club-details link in your email to select your club.');
 const rows=(queue.rows||[]).filter(row=>[row.club,...(row.identities||[])].some(n=>key(n)===query));
 if(rows.length!==1)throw Error('We could not find a unique published listing for that club. Please reply to your email so we can check it.');
 const row=rows[0],names=new Set([row.club,...(row.identities||[])].map(key));
 const fixture=Object.values(competition.fixtures||{}).find(f=>names.has(key(f.home))||names.has(key(f.away)))||null;
 let website=null;
 try{const url=new URL(row.website);if(url.protocol==='https:'&&!url.username&&!url.password)website=url.href;}catch(_){}
 return {club:row.club,website,fixture,updatedAt:competition.updated_at||null};
}
