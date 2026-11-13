// The Trophy Cabinet contains Beer Mats 01–27. Mat 00 is the Four Laws reference.
export const trophyMatIds=Array.from({length:27},(_,index)=>String(index+1).padStart(2,'0'));

export function validateTrophyCabinet(ids){
 if(!Array.isArray(ids)||ids.length>trophyMatIds.length)return null;
 const earned=new Set(ids);
 const cabinet=trophyMatIds.filter(id=>earned.has(id));
 return cabinet.length===ids.length?cabinet:null;
}
