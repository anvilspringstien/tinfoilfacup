/* Isolated Shed-only runtime preview. Never imported by the approved Campaign.
 * Accepts only official-source pending evidence. A postcode is NOT a coordinate.
 */
import {entrantIdentityKey} from './entrant-ground-evidence.mjs';

const displayKey = v => String(v||'').toLowerCase().replace(/&/g,' and ')
  .replace(/\b(fc|afc|cfc)\b/g,' ').replace(/[^a-z0-9]+/g,' ')
  .trim().replace(/\s+/g,' ');

function readArray(source, name) {
 const rx = new RegExp('((?:let|const|var)\\s+'+name+'\\s*=\\s*)(\\[[\\s\\S]*?\\])(\\s*;)','g');
 const matches = [...source.matchAll(rx)];
 if(matches.length!==1) throw new Error('Original Shed location array changed: '+name);
 const values=JSON.parse(matches[0][2]);
 if(!Array.isArray(values)) throw new Error('Unexpected location array');
 return {match:matches[0],values};
}

export function buildEntrantGroundPreview(source, evidence) {
 if(typeof source!=='string'||!evidence||evidence.season!=='2026-27'
  ||evidence.safety?.automated_ground_promotion!==false
  ||evidence.safety?.verified_location_badge_authorized!==false
  ||evidence.safety?.coordinates_required_before_location_promotion!==true)
  throw new Error('Evidence safety policy failed');
 const original=readArray(source,'GROUNDS');
 const law2=readArray(source,'LAW2_ORIGIN_LOCATIONS');
 const existing=new Map();
 for(const record of [...original.values,...law2.values]){
  const d=displayKey(record.name);
  if(!d)continue;
  if(!existing.has(d))existing.set(d,new Set());
  existing.get(d).add(entrantIdentityKey(record.name));
 }
 const blocked=new Set((evidence.unresolved_conflicts||[]).map(r=>entrantIdentityKey(r.official_identity)));
 const encountered=new Set(), additions=[], skipped=[];
 for(const row of evidence.clubs||[]){
  const key=entrantIdentityKey(row.official_identity);
  if(!key||encountered.has(key))throw new Error('Duplicate or missing official identity');
  encountered.add(key);
  if(blocked.has(key))throw new Error('Unresolved official location conflict');
  if(!['awaiting-coordinates-and-human-promotion','awaiting-human-promotion'].includes(row.review_status)
    ||row.source_review!=='official-ground-and-postcode-confirmed'
    ||!row.ground||!row.postcode||!/^https:\/\//.test(row.official_home_ground_source||'')) {
   skipped.push({club:row.official_identity,reason:'incomplete evidence'});
   continue;
  }
  const d=displayKey(row.official_identity);
  if(existing.has(d)){
   skipped.push({club:row.official_identity,reason:'existing record or collision'});
   continue;
  }
  additions.push({
   name:row.official_identity,ground:row.ground,postcode:row.postcode,
   verification:'unverified',source:row.official_home_ground_source,
   ground_source:'Official club source — pending independent coordinate verification',
   preview_evidence_only:true
  });
  existing.set(d,new Set([key]));
 }
 if(additions.length!==31)throw new Error('Entrant evidence preview must match current 31-location audit');
 const updated=source.slice(0,original.match.index+original.match[1].length)
  +JSON.stringify([...original.values,...additions])
  +source.slice(original.match.index+original.match[0].length-original.match[3].length);
 const start='function findGround(c){', end='}function verification(c,g){';
 if(updated.split(start).length!==2||updated.split(end).length!==2)
  throw new Error('BETA lookup anchor changed');
 const [before,tail]=updated.split(start);
 const [lookup,after]=tail.split(end);
 if(lookup.split('if(g)return g;').length!==2||lookup.split('if(s)return s;').length!==2)
  throw new Error('BETA location return contract changed');
 const guard="  const previewAfcBoundary=(requested,record)=>/^\\s*afc\\b/i.test(requested||'')===/^\\s*afc\\b/i.test(record||'');\n";
 const bounded=guard+lookup.replace('if(g)return g;','if(g&&previewAfcBoundary(c.name,g.name))return g;')
  .replace('if(s)return s;','if(s&&previewAfcBoundary(c.name,s.name))return s;');
 return {html:before+start+bounded+end+after,additions,skipped};
}
