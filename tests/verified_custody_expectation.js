// Test oracle over canonical source records. Frozen renderer scenarios separately
// prove the historical milestones and reject premature/unsourced advancement.
module.exports=function verifiedCustodianAfter(data,club,after){
  const key=name=>String(name||'').toLowerCase().replace(/&/g,' and ')
    .replace(/\b(fc|afc|cfc|football club)\b/g,' ').replace(/[^a-z0-9]+/g,' ').trim();
  const history=Object.values(data.result_history||{}).flat().filter(r=>r&&r.date>after)
    .sort((a,b)=>String(a.date).localeCompare(String(b.date)));
  for(const row of history){
    if(key(row.home)!==key(club)&&key(row.away)!==key(club))continue;
    if(!row.source_url||!/^(FT(?:\b|$)|AET$|AWARDED$|WALKOVER$|W\/O$)/i.test(row.status||''))continue;
    if(Number.isInteger(row.home_score)&&Number.isInteger(row.away_score)&&row.home_score!==row.away_score)
      club=row.home_score>row.away_score?row.home:row.away;
    else if(row.winner&&row.decision!=='draw-replay')club=row.winner;
  }
  return club;
};
