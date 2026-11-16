  // Frozen chronological states exercise the real renderer independently of
  // whichever later round the live competition has reached.
  const published=LIVE_COMPETITION_DATA;
  const clone=value=>JSON.parse(JSON.stringify(value));
  const atDate=cutoff=>{
    const d=clone(published);d.results={};
    for(const [name,rows] of Object.entries(d.result_history||{})){
      d.result_history[name]=rows.filter(r=>r.date&&r.date<=cutoff);
      const ordered=[...d.result_history[name]].sort((a,b)=>a.date.localeCompare(b.date));
      if(ordered.length)d.results[name]=ordered[ordered.length-1];
    }
    return d;
  };
  const insert=(d,row)=>{
    const names=new Set([row.home,row.away]);
    for(const name of Object.keys(d.result_history))
      if(same(name,row.home)||same(name,row.away))names.add(name);
    for(const name of names){
      const rows=d.result_history[name]||[];
      d.result_history[name]=rows.filter(r=>!(r.round===row.round&&r.date===row.date&&same(r.home,row.home)&&same(r.away,row.away)));
      d.result_history[name].push(clone(row));d.results[name]=clone(row);
    }
  };
  const check=(data,expected,label)=>{
    LIVE_COMPETITION_DATA=data;
    for(const journey of [buildJourney(origin),tinFoilJourneyForRender(origin)]){
      if(!same(journey.carrier.name,expected))throw new Error('DL5 chronology '+label+': expected '+expected+', got '+journey.carrier.name);
    }
    return buildJourney(origin);
  };
  try{
    const pending=atDate('2026-10-03');
    check(pending,'Trafford','draw and next-round fixture cannot settle replay');
    const replay=clone(verifiedJourneyMilestones.replay);
    const resolved=atDate('2026-10-03');insert(resolved,replay);
    check(resolved,'Atherton Collieries','verified replay victory');
    for(const status of ['HT','LIVE','POSTPONED','VOID','']){
      const d=clone(pending);insert(d,{...replay,status});
      check(d,'Trafford','replay not final: '+status);
    }
    const unverified=clone(pending);insert(unverified,{...replay,source_url:''});
    check(unverified,'Trafford','replay without provenance');
    const fylde=clone(verifiedJourneyMilestones.fylde);
    const beforeReplay=clone(pending);insert(beforeReplay,fylde);
    check(beforeReplay,'Trafford','Fylde result cannot bypass unresolved replay');
    const incomplete=clone(resolved);insert(incomplete,{...fylde,away_score:null});
    check(incomplete,'Atherton Collieries','incomplete full-time score');
    for(const status of ['HT','LIVE','POSTPONED','VOID','']){
      const d=clone(resolved);insert(d,{...fylde,status});
      check(d,'Atherton Collieries','Fylde not final: '+status);
    }
    const unsourced=clone(resolved);insert(unsourced,{...fylde,source_url:''});
    check(unsourced,'Atherton Collieries','Fylde without provenance');
    const final=clone(resolved);insert(final,fylde);
    const journey=check(final,'AFC Fylde','verified 5-0 full-time victory');
    const matches=journey.breadcrumbs.map(b=>b.result);
    const originals=matches.filter(r=>same(r.home,'Trafford')&&same(r.away,'Atherton Collieries')&&r.date==='2026-10-03');
    const replays=matches.filter(r=>same(r.home,'Atherton Collieries')&&same(r.away,'Trafford')&&r.date==='2026-10-06');
    if(originals.length!==1||replays.length!==1)throw new Error('DL5 chronology: original/replay duplicated or lost');
    const original=originals[0],originalVenue=completedResultVenue(original);
    if(original.home_score!==2||original.away_score!==2||originalVenue.postcode!=='M41 5DL'||originalVenue.ground!=='Shawe View')
      throw new Error('DL5 chronology: original drawn tie result or venue lost');
    const historical=replays[0];
    if(historical.kickoff!=='19:45'||historical.home_score!==3||historical.away_score!==0||historical.status!=='FT')
      throw new Error('DL5 chronology: historical replay metadata or result lost');
    if(!completedResultDateLabel(historical).includes('6 October 2026'))throw new Error('DL5 chronology: historical date lost');
    const venue=completedResultVenue(historical);
    if(venue.postcode!=='M46 9EY'||venue.ground!=='Dreams2Remember Stadium')throw new Error('DL5 chronology: historical replay venue lost');
    if(!resultLineFromResult(historical).includes('(3) v (0)'))throw new Error('DL5 chronology: rendered historical score lost');
    if(matches.indexOf(originals[0])>=matches.indexOf(historical)||matches.indexOf(historical)>=matches.findIndex(r=>same(r.home,'AFC Fylde')&&r.date==='2026-10-17'))
      throw new Error('DL5 chronology: matches not ordered original, replay, Fourth Qualifying');
    console.log('DL5 chronological custody, premature advancement and historical metadata: PASS');
  }finally{LIVE_COMPETITION_DATA=published;}
