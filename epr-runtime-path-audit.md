# Extra Preliminary runtime path audit

READ ONLY. Production data unchanged.

## `EPR_RESULTS_BY_TIE`
Matches: **3**

### 1
```js
rough Town FC":"https://www.guisboroughtown.co.uk/","Hartley Wintney FC":"https://www.hartleyfc.com/","Heaton Stannington FC":"https://heatonstan.co.uk/","Hendon FC":"https://hendonfc.com/","Hungerford Town FC":"https://www.hungerfordtown.com/","Kendal Town FC":"https://kendaltownfc.org/","Kingstonian FC":"https://www.kingstonianfc.com/","Newcastle Blue Star FC":"https://www.nbsfc2018.co.uk/","AFC Croydon Athletic FC":"https://croydonathletic.com/","AFC Portchester FC":"https://afcportchester.co.uk/","AFC Rushden & Diamonds FC":"https://afcdiamonds.com/","AFC Sudbury FC":"https://www.afcsudbury.co.uk/","AFC Varndeanians FC":"https://www.afcvs.com/","AFC Wolverhampton City FC":"https://www.afcwulfrunians.co.uk/","South Liverpool FC":"https://www.southliverpoolfc.com/","Vauxhall Motors FC":"https://www.vauxhallmotorsfc.co.uk/","Vauxhall Motors":"https://www.vauxhallmotorsfc.co.uk/"};const EPR_RESULTS_BY_TIE={"1":{"home":"West Auckland Town","away":"Yarm & Eaglescliffe","home_score":3,"away_score":2,"status":"FT","decision":"replay","date":"2026-08-08","winner":"West Auckland Town FC"},"2":{"home":"Carlisle City","away":"Northallerton Town","home_score":2,"away_score":0,"status":"FT","decision":"","date":"2026-08-08","winner":"Carlisle City FC"},"3":{"home":"North Shields","away":"Consett","home_score":1,"away_score":2,"status":"FT","decision":"replay","date":"2026-08-08","winner":"Consett AFC"},"4":{"home":"Easington Colliery","away":"Whitley Bay","home_score":3,"away_score":2,"status":"FT","decision":"replay","date":"2026-08-08","winner":"Easington Colliery FC"},"5":{"home":"Birtley Town","away":"Bishop Auckland","home_score":2,"away_score":3,"status":"FT","decision":"","date":"2026-08-08","winner":"Bishop Auckland FC"},"6":{"home":"Penrith","away":"Bridlington Town","home_score":1,"away_score":2,"status":"FT","decision":"","date":"2026-08-08","winner":"Bridlington Town AFC"},"7":{"home":"Shildon","away":"Blyth Town","home_score":4,"away_score":1,"status":"FT","decision":"","date":"2026-08-08","winner":"Shildon AFC"},"8":{"home":"Ashington","away":"Horden Community Welfare","home_score":2,"away_score":0,"status":"FT","decision":"","date":"2026-08-08","winner":"Ashington FC"},"9":{"home":"Marske United","away":"Boro Rangers","home_score":null,"away_score":null,"status":"FT","decision":"walkover","date":"2026-08-08","winner":"Marske United FC"},"10":{"home":"Ne
```

### 2
```js
 strings to Google Maps.
    destination=rf.home+' Football Club, UK';
  }else{
    destination=club.name+' Football Club, UK';
  }

  return 'https://www.google.com/maps/dir/?api=1&origin='+
    encodeURIComponent(origin)+'&destination='+encodeURIComponent(destination)+
    '&travelmode=driving';
}
function clubStillActive(club){
  if(club.active===false)return false;
  const r=resultFor(club);
  if(r&&r.winner)return norm(r.winner)===norm(club.name);
  return true;
}

function resultFor(club){
  const f=club.fixture||{},key=String(club.name||'').replace(/\s+(FC|AFC|CFC)$/,'');
  const live=liveLookup('results',club.name);
  if(live)return live;
  const cur=CURRENT_RESULT_OVERRIDES[club.name]||CURRENT_RESULT_OVERRIDES[key]||null;
  if(cur)return cur;
  if(f.result&&typeof f.result==='object')return f.result;
  if(club.entry_round==='Extra Preliminary Round'&&f.number!=null){
    return EPR_RESULTS_BY_TIE[String(f.number)]||null;
  }
  return null;
}
function resultTeamLine(club){
  const r=resultFor(club);
  if(!r)return '';
  if(r.decision==='walkover'){
    return esc(r.home)+' (W/O) v '+esc(r.away);
  }
  let line=esc(r.home)+' ('+esc(r.home_score)+') v ('+esc(r.away_score)+') '+esc(r.away);
  if(r.decision&&r.decision.startsWith('pens ')){
    line+=' • '+esc(r.winner)+' won '+esc(r.decision.replace('pens ','')+' on pens');
  }else if(r.decision==='a.e.t.'){
    line+=' • AET';
  }
  return line;
}

function resultLineFromResult(r){
  if(!r)return '';
  if(r.decision==='walkover'){
    return esc(r.home)+' (W/O) v '+esc(r.away);
  }
  let line=esc(r.home)+' ('+esc(r.home_score)+') v ('+esc(r.away_score)+') '+esc(r.away);
  if(r.decision&&r.decision.startsWith('pens ')){
    line+=' • '+esc(r.winner)+' won '+esc(r.decision.replace('pens ','')+' on pens');
  }else if(r.decision==='a.e.t.'){
    line+=' • AET';
  }
  return line;
}

function sameMatchResult(a,b){
 if(!a||!b)return false;
 const cn=n=>norm(String(n||'').replace(/\s+(FC|AFC|CFC)$/i,''));
 return cn(a.home)===cn(b.home)&&cn(a.away)===cn(b.away)&&String(a.date||'')===String(b.date||'')&&String(a.home_score??'')===String(b.home_score??'')&&String(a.away_score??'')===String(b.away_score??'');
}
function resultSortValue(r){
  if(!r||!r.date)return 0;
  const d=new Date(r.date+'T12:00:00');
  return Number.isNaN(d.getTime())?0:d.getTime();
}
function historicalResultsForClub(club){
  const out=[];
```

### 3
```js
te||'')===String(b.date||'')&&String(a.home_score??'')===String(b.home_score??'')&&String(a.away_score??'')===String(b.away_score??'');
}
function resultSortValue(r){
  if(!r||!r.date)return 0;
  const d=new Date(r.date+'T12:00:00');
  return Number.isNaN(d.getTime())?0:d.getTime();
}
function historicalResultsForClub(club){
  const out=[];
  function add(r,round){
    if(!r||typeof r!=='object')return;
    if(!sameClubIdentity(r.home,club.name)&&!sameClubIdentity(r.away,club.name))return;
    if(!out.some(x=>sameSemanticResult(x.result,r)))out.push({round:round||r.round||club.entry_round||'FA Cup',result:r});
  }
  const hist=liveLookup('result_history',club.name);
  if(Array.isArray(hist))for(const r of hist)add(r,r&&r.round);
  add(liveLookup('results',club.name));
  if(!out.length){
    const f=club.fixture||{};
    if(club.entry_round==='Extra Preliminary Round'&&f.number!=null)add(EPR_RESULTS_BY_TIE[String(f.number)]||null,club.entry_round);
    else if(f.result&&typeof f.result==='object')add(f.result,club.entry_round||f.result.round);
    const key=String(club.name||'').replace(/\s+(FC|AFC|CFC)$/,'');
    add(CURRENT_RESULT_OVERRIDES[club.name]||CURRENT_RESULT_OVERRIDES[key]||null);
    add(liveLookup('results',club.name));
  }
  out.sort((a,b)=>resultSortValue(a.result)-resultSortValue(b.result));
  return out;
} function buildJourney(origin){
  let carrier=origin;
  const candidates=[];
  function clubObjectForWinner(name,prior){
    return clubByDisplayName(name)||candidateClubByName(name)||{name:name,entry_round:(prior&&prior.entry_round)||'',fixture:{}};
  }
  function appendHistory(club){
    const history=historicalResultsForClub(club);
    for(const item of history){
      if(!candidates.some(x=>sameSemanticResult(x.result,item.result)))candidates.push(item);
    }
  }
  function resolveChain(){
    let c=origin;
    const chain=[];
    const ordered=[...candidates].sort((a,b)=>resultSortValue(a.result)-resultSortValue(b.result));
    for(const item of ordered){
      const r=item.result||{};
      const participant=sameClubIdentity(r.home,c.name)||sameClubIdentity(r.away,c.name);
      if(!participant)continue;
      chain.push(item);
      const winner=canonicalResultWinner(r);
      if(winner&&!resultNeedsReplay(r))c=clubObjectForWinner(winner,c);
    }
    return {carrier:c,breadcrumbs:chain};
  }
  const expanded=new Set();
  for(let hop
```

## `EMBEDDED_COMPETITION_DATA`
Matches: **5**

### 1
```js
ode":"NE7 7HP"},"Heaton Stannington":{"round":"Preliminary Round Replay","home":"Heaton Stannington","away":"Kendal Town","date":"2026-08-25","kickoff":"19:45","ground":"The Willow Park","postcode":"NE7 7HP"},"Kendal Town FC":{"round":"Preliminary Round Replay","home":"Heaton Stannington","away":"Kendal Town","date":"2026-08-25","kickoff":"19:45","ground":"The Willow Park","postcode":"NE7 7HP"},"Kendal Town":{"round":"Preliminary Round Replay","home":"Heaton Stannington","away":"Kendal Town","date":"2026-08-25","kickoff":"19:45","ground":"The Willow Park","postcode":"NE7 7HP"}};

const VERIFIED_MATCH_VENUE_OVERRIDES={
  "Heaton Stannington":{
    ground:"The Willow Park",
    postcode:"NE7 7HP"
  },
  "Heaton Stannington FC":{
    ground:"The Willow Park",
    postcode:"NE7 7HP"
  }
};

const LIVE_COMPETITION_DATA_URL='./competition.json';
/* TIN_FOIL_EMBEDDED_COMPETITION_BEGIN */
const EMBEDDED_COMPETITION_DATA={"schema_version":1,"season":"2026-27","updated_at":"2026-09-13T23:40:24.845593+00:00","round_dates":{"First Round Qualifying":"2026-09-05","Second Round Qualifying":"2026-09-19","Third Round Qualifying":"2026-10-03","Fourth Round Qualifying":"2026-10-17","First Round Proper":"2026-11-07","Preliminary Round":"2026-08-22"},"results":{"Blyth Spartans AFC":{"round":"First Round Qualifying","home":"Redcar Town","away":"Blyth Spartans","home_score":1,"away_score":0,"winner":"Redcar Town","status":"FT","decision":"","date":"2026-09-05","source_url":"https://www.footballwebpages.co.uk/fa-cup/fixtures-results/first-qualifying-round"},"Redcar Town FC":{"round":"First Round Qualifying","home":"Redcar Town","away":"Blyth Spartans","home_score":1,"away_score":0,"winner":"Redcar Town","status":"FT","decision":"","date":"2026-09-05","source_url":"https://www.footballwebpages.co.uk/fa-cup/fixtures-results/first-qualifying-round"},"Heaton Stannington FC":{"round":"First Round Qualifying","home":"Heaton Stannington","away":"Knaresborough Town","home_score":1,"away_score":0,"winner":"Heaton Stannington","status":"FT","decision":"","date":"2026-09-05","source_url":"https://www.footballwebpages.co.uk/fa-cup/fixtures-results/first-qualifying-round"},"Heaton Stannington AFC":{"round":"First Round Qualifying","home":"Heaton Stannington","away":"Knaresborough Town","home_score":1,"away_score":0,"winner":"Heaton Stannington","status":"FT","decision":"","date":"2026-09-05","s
```

### 2
```js
m","date":"2026-09-06","kickoff":"15:00","source_url":"https://www.footballwebpages.co.uk/fa-cup/fixtures-results/first-qualifying-round"},{"round":"First Round Qualifying","home":"Stourbridge","away":"Rushall Olympic","date":"2026-09-06","kickoff":"15:00","venue":{"ground":"War Memorial Athletic Ground","postcode":"DY8 4HN","source":"https://fchd.info/maps/GAZ.htm","verification":"fchd-gazetteer"},"source_url":"https://www.footballwebpages.co.uk/fa-cup/fixtures-results/first-qualifying-round"}]},"second_qualifying_sync":{"source":"Football Web Pages + retained pending replay slot","source_url":"https://www.footballwebpages.co.uk/fa-cup/fixtures-results","synced_at":"2026-09-13T23:40:21.496888+00:00","resolved_fixtures":79,"pending_replay_slots":1,"total_fixtures":80,"pending":"Hanwell Town v Burgess H or Jersey Bulls"}};
/* TIN_FOIL_EMBEDDED_COMPETITION_END */
let LIVE_COMPETITION_DATA=EMBEDDED_COMPETITION_DATA;
let LIVE_DATA_STATUS={state:'embedded',updated_at:EMBEDDED_COMPETITION_DATA.updated_at||null,message:'Using embedded competition snapshot'};
function liveLookup(section,name){
  if(!LIVE_COMPETITION_DATA||!LIVE_COMPETITION_DATA[section])return null;
  const obj=LIVE_COMPETITION_DATA[section],raw=String(name||''),short=raw.replace(/\s+(FC|AFC|CFC)$/,'');
  return obj[raw]||obj[short]||null;
}

function liveResultHistory(name){
  if(!LIVE_COMPETITION_DATA)return [];
  const section=LIVE_COMPETITION_DATA.result_history||{};
  const raw=String(name||''), short=raw.replace(/\s+(FC|AFC|CFC)$/,'');
  const arr=section[raw]||section[short]||[];
  return Array.isArray(arr)?arr:[];
}
function applyLiveRoundDates(){
  const d=LIVE_COMPETITION_DATA&&LIVE_COMPETITION_DATA.round_dates;if(!d)return;
  Object.keys(d).forEach(k=>{if(ROUND_META[k])ROUND_META[k].date=d[k];});
}
async function refreshCompetitionData(force=false){
  try{
    const u=LIVE_COMPETITION_DATA_URL+(LIVE_COMPETITION_DATA_URL.includes('?')?'&':'?')+'t='+Date.now();
    const r=await fetch(u,{cache:'no-store'});if(!r.ok)throw new Error('HTTP '+r.status);
    const d=await r.json();if(!d||Number(d.schema_version)!==1)throw new Error('Unsupported schema');
    LIVE_COMPETITION_DATA=d;applyLiveRoundDates();
    LIVE_DATA_STATUS={state:'live',updated_at:d.updated_at||null,message:'Competition data loaded'};
  }catch(e){LIVE_COMPETITION_DATA=EMBEDDED_COMPETITION_DATA;applyLiveRoundDates();LIVE_DATA_S
```

### 3
```js
bpages.co.uk/fa-cup/fixtures-results/first-qualifying-round"},{"round":"First Round Qualifying","home":"Stourbridge","away":"Rushall Olympic","date":"2026-09-06","kickoff":"15:00","venue":{"ground":"War Memorial Athletic Ground","postcode":"DY8 4HN","source":"https://fchd.info/maps/GAZ.htm","verification":"fchd-gazetteer"},"source_url":"https://www.footballwebpages.co.uk/fa-cup/fixtures-results/first-qualifying-round"}]},"second_qualifying_sync":{"source":"Football Web Pages + retained pending replay slot","source_url":"https://www.footballwebpages.co.uk/fa-cup/fixtures-results","synced_at":"2026-09-13T23:40:21.496888+00:00","resolved_fixtures":79,"pending_replay_slots":1,"total_fixtures":80,"pending":"Hanwell Town v Burgess H or Jersey Bulls"}};
/* TIN_FOIL_EMBEDDED_COMPETITION_END */
let LIVE_COMPETITION_DATA=EMBEDDED_COMPETITION_DATA;
let LIVE_DATA_STATUS={state:'embedded',updated_at:EMBEDDED_COMPETITION_DATA.updated_at||null,message:'Using embedded competition snapshot'};
function liveLookup(section,name){
  if(!LIVE_COMPETITION_DATA||!LIVE_COMPETITION_DATA[section])return null;
  const obj=LIVE_COMPETITION_DATA[section],raw=String(name||''),short=raw.replace(/\s+(FC|AFC|CFC)$/,'');
  return obj[raw]||obj[short]||null;
}

function liveResultHistory(name){
  if(!LIVE_COMPETITION_DATA)return [];
  const section=LIVE_COMPETITION_DATA.result_history||{};
  const raw=String(name||''), short=raw.replace(/\s+(FC|AFC|CFC)$/,'');
  const arr=section[raw]||section[short]||[];
  return Array.isArray(arr)?arr:[];
}
function applyLiveRoundDates(){
  const d=LIVE_COMPETITION_DATA&&LIVE_COMPETITION_DATA.round_dates;if(!d)return;
  Object.keys(d).forEach(k=>{if(ROUND_META[k])ROUND_META[k].date=d[k];});
}
async function refreshCompetitionData(force=false){
  try{
    const u=LIVE_COMPETITION_DATA_URL+(LIVE_COMPETITION_DATA_URL.includes('?')?'&':'?')+'t='+Date.now();
    const r=await fetch(u,{cache:'no-store'});if(!r.ok)throw new Error('HTTP '+r.status);
    const d=await r.json();if(!d||Number(d.schema_version)!==1)throw new Error('Unsupported schema');
    LIVE_COMPETITION_DATA=d;applyLiveRoundDates();
    LIVE_DATA_STATUS={state:'live',updated_at:d.updated_at||null,message:'Competition data loaded'};
  }catch(e){LIVE_COMPETITION_DATA=EMBEDDED_COMPETITION_DATA;applyLiveRoundDates();LIVE_DATA_STATUS={state:'embedded',updated_at:EMBEDDED_COMPETITION_DATA.updated_at||null
```

### 4
```js
history||{};
  const raw=String(name||''), short=raw.replace(/\s+(FC|AFC|CFC)$/,'');
  const arr=section[raw]||section[short]||[];
  return Array.isArray(arr)?arr:[];
}
function applyLiveRoundDates(){
  const d=LIVE_COMPETITION_DATA&&LIVE_COMPETITION_DATA.round_dates;if(!d)return;
  Object.keys(d).forEach(k=>{if(ROUND_META[k])ROUND_META[k].date=d[k];});
}
async function refreshCompetitionData(force=false){
  try{
    const u=LIVE_COMPETITION_DATA_URL+(LIVE_COMPETITION_DATA_URL.includes('?')?'&':'?')+'t='+Date.now();
    const r=await fetch(u,{cache:'no-store'});if(!r.ok)throw new Error('HTTP '+r.status);
    const d=await r.json();if(!d||Number(d.schema_version)!==1)throw new Error('Unsupported schema');
    LIVE_COMPETITION_DATA=d;applyLiveRoundDates();
    LIVE_DATA_STATUS={state:'live',updated_at:d.updated_at||null,message:'Competition data loaded'};
  }catch(e){LIVE_COMPETITION_DATA=EMBEDDED_COMPETITION_DATA;applyLiveRoundDates();LIVE_DATA_STATUS={state:'embedded',updated_at:EMBEDDED_COMPETITION_DATA.updated_at||null,message:'Embedded snapshot — live data unavailable'};}
  updateLiveDataBadge();return LIVE_DATA_STATUS.state==='live';
}
function updateLiveDataBadge(){
  const e=document.getElementById('liveDataBadge');if(!e)return;
  if(LIVE_DATA_STATUS.state==='live'){
    let w=LIVE_DATA_STATUS.updated_at||'';try{w=new Date(w).toLocaleString('en-GB');}catch(x){}
    e.textContent='Clubfinder v7.6 — Competition data updated: '+w;
  }else e.textContent='Clubfinder v7.6 — '+LIVE_DATA_STATUS.message;
}

const ROUND_META={
  'Preliminary Round':{
    date:'22 August 2026',
    drawDate:'Draw already made'
  },
  'First Round Qualifying':{
    date:'5 September 2026',
    drawDate:'TBC'
  },
  'Second Round Qualifying':{
    date:'19 September 2026',
    drawDate:'TBC'
  },
  'Third Round Qualifying':{
    date:'3 October 2026',
    drawDate:'TBC'
  },
  'Fourth Round Qualifying':{
    date:'17 October 2026',
    drawDate:'TBC'
  },
  'First Round Proper':{
    date:'7 November 2026',
    drawDate:'TBC'
  }
};

function drawAlternatives(side){return String(side||'').split(/\s+or\s+/i).map(x=>x.trim()).filter(Boolean)}
function resolveConditionalSide(side,carrier){
  const a=drawAlternatives(side);
  if(a.length<=1)return side;
  const n=carrier&&carrier.name?carrier.name:String(carrier||'');
  const carrierKey=canonicalClubKey(n);
  for(const x of a)if(canoni
```

### 5
```js
rr=section[raw]||section[short]||[];
  return Array.isArray(arr)?arr:[];
}
function applyLiveRoundDates(){
  const d=LIVE_COMPETITION_DATA&&LIVE_COMPETITION_DATA.round_dates;if(!d)return;
  Object.keys(d).forEach(k=>{if(ROUND_META[k])ROUND_META[k].date=d[k];});
}
async function refreshCompetitionData(force=false){
  try{
    const u=LIVE_COMPETITION_DATA_URL+(LIVE_COMPETITION_DATA_URL.includes('?')?'&':'?')+'t='+Date.now();
    const r=await fetch(u,{cache:'no-store'});if(!r.ok)throw new Error('HTTP '+r.status);
    const d=await r.json();if(!d||Number(d.schema_version)!==1)throw new Error('Unsupported schema');
    LIVE_COMPETITION_DATA=d;applyLiveRoundDates();
    LIVE_DATA_STATUS={state:'live',updated_at:d.updated_at||null,message:'Competition data loaded'};
  }catch(e){LIVE_COMPETITION_DATA=EMBEDDED_COMPETITION_DATA;applyLiveRoundDates();LIVE_DATA_STATUS={state:'embedded',updated_at:EMBEDDED_COMPETITION_DATA.updated_at||null,message:'Embedded snapshot — live data unavailable'};}
  updateLiveDataBadge();return LIVE_DATA_STATUS.state==='live';
}
function updateLiveDataBadge(){
  const e=document.getElementById('liveDataBadge');if(!e)return;
  if(LIVE_DATA_STATUS.state==='live'){
    let w=LIVE_DATA_STATUS.updated_at||'';try{w=new Date(w).toLocaleString('en-GB');}catch(x){}
    e.textContent='Clubfinder v7.6 — Competition data updated: '+w;
  }else e.textContent='Clubfinder v7.6 — '+LIVE_DATA_STATUS.message;
}

const ROUND_META={
  'Preliminary Round':{
    date:'22 August 2026',
    drawDate:'Draw already made'
  },
  'First Round Qualifying':{
    date:'5 September 2026',
    drawDate:'TBC'
  },
  'Second Round Qualifying':{
    date:'19 September 2026',
    drawDate:'TBC'
  },
  'Third Round Qualifying':{
    date:'3 October 2026',
    drawDate:'TBC'
  },
  'Fourth Round Qualifying':{
    date:'17 October 2026',
    drawDate:'TBC'
  },
  'First Round Proper':{
    date:'7 November 2026',
    drawDate:'TBC'
  }
};

function drawAlternatives(side){return String(side||'').split(/\s+or\s+/i).map(x=>x.trim()).filter(Boolean)}
function resolveConditionalSide(side,carrier){
  const a=drawAlternatives(side);
  if(a.length<=1)return side;
  const n=carrier&&carrier.name?carrier.name:String(carrier||'');
  const carrierKey=canonicalClubKey(n);
  for(const x of a)if(canonicalClubKey(x)===carrierKey)return x;
  const compatible=a.filter(x=>{
    const k=canonicalClu
```

## `competitionData`
Matches: **0**

## `COMPETITION`
Matches: **20**

### 1
```js
away":"Kendal Town","date":"2026-08-25","kickoff":"19:45","ground":"The Willow Park","postcode":"NE7 7HP"},"Heaton Stannington":{"round":"Preliminary Round Replay","home":"Heaton Stannington","away":"Kendal Town","date":"2026-08-25","kickoff":"19:45","ground":"The Willow Park","postcode":"NE7 7HP"},"Kendal Town FC":{"round":"Preliminary Round Replay","home":"Heaton Stannington","away":"Kendal Town","date":"2026-08-25","kickoff":"19:45","ground":"The Willow Park","postcode":"NE7 7HP"},"Kendal Town":{"round":"Preliminary Round Replay","home":"Heaton Stannington","away":"Kendal Town","date":"2026-08-25","kickoff":"19:45","ground":"The Willow Park","postcode":"NE7 7HP"}};

const VERIFIED_MATCH_VENUE_OVERRIDES={
  "Heaton Stannington":{
    ground:"The Willow Park",
    postcode:"NE7 7HP"
  },
  "Heaton Stannington FC":{
    ground:"The Willow Park",
    postcode:"NE7 7HP"
  }
};

const LIVE_COMPETITION_DATA_URL='./competition.json';
/* TIN_FOIL_EMBEDDED_COMPETITION_BEGIN */
const EMBEDDED_COMPETITION_DATA={"schema_version":1,"season":"2026-27","updated_at":"2026-09-13T23:40:24.845593+00:00","round_dates":{"First Round Qualifying":"2026-09-05","Second Round Qualifying":"2026-09-19","Third Round Qualifying":"2026-10-03","Fourth Round Qualifying":"2026-10-17","First Round Proper":"2026-11-07","Preliminary Round":"2026-08-22"},"results":{"Blyth Spartans AFC":{"round":"First Round Qualifying","home":"Redcar Town","away":"Blyth Spartans","home_score":1,"away_score":0,"winner":"Redcar Town","status":"FT","decision":"","date":"2026-09-05","source_url":"https://www.footballwebpages.co.uk/fa-cup/fixtures-results/first-qualifying-round"},"Redcar Town FC":{"round":"First Round Qualifying","home":"Redcar Town","away":"Blyth Spartans","home_score":1,"away_score":0,"winner":"Redcar Town","status":"FT","decision":"","date":"2026-09-05","source_url":"https://www.footballwebpages.co.uk/fa-cup/fixtures-results/first-qualifying-round"},"Heaton Stannington FC":{"round":"First Round Qualifying","home":"Heaton Stannington","away":"Knaresborough Town","home_score":1,"away_score":0,"winner":"Heaton Stannington","status":"FT","decision":"","date":"2026-09-05","source_url":"https://www.footballwebpages.co.uk/fa-cup/fixtures-results/first-qualifying-round"},"Heaton Stannington AFC":{"round":"First Round Qualifying","home":"Heaton Stannington","away":"Knaresborough Town","home_score":1,"awa
```

### 2
```js
d":"The Willow Park","postcode":"NE7 7HP"},"Heaton Stannington":{"round":"Preliminary Round Replay","home":"Heaton Stannington","away":"Kendal Town","date":"2026-08-25","kickoff":"19:45","ground":"The Willow Park","postcode":"NE7 7HP"},"Kendal Town FC":{"round":"Preliminary Round Replay","home":"Heaton Stannington","away":"Kendal Town","date":"2026-08-25","kickoff":"19:45","ground":"The Willow Park","postcode":"NE7 7HP"},"Kendal Town":{"round":"Preliminary Round Replay","home":"Heaton Stannington","away":"Kendal Town","date":"2026-08-25","kickoff":"19:45","ground":"The Willow Park","postcode":"NE7 7HP"}};

const VERIFIED_MATCH_VENUE_OVERRIDES={
  "Heaton Stannington":{
    ground:"The Willow Park",
    postcode:"NE7 7HP"
  },
  "Heaton Stannington FC":{
    ground:"The Willow Park",
    postcode:"NE7 7HP"
  }
};

const LIVE_COMPETITION_DATA_URL='./competition.json';
/* TIN_FOIL_EMBEDDED_COMPETITION_BEGIN */
const EMBEDDED_COMPETITION_DATA={"schema_version":1,"season":"2026-27","updated_at":"2026-09-13T23:40:24.845593+00:00","round_dates":{"First Round Qualifying":"2026-09-05","Second Round Qualifying":"2026-09-19","Third Round Qualifying":"2026-10-03","Fourth Round Qualifying":"2026-10-17","First Round Proper":"2026-11-07","Preliminary Round":"2026-08-22"},"results":{"Blyth Spartans AFC":{"round":"First Round Qualifying","home":"Redcar Town","away":"Blyth Spartans","home_score":1,"away_score":0,"winner":"Redcar Town","status":"FT","decision":"","date":"2026-09-05","source_url":"https://www.footballwebpages.co.uk/fa-cup/fixtures-results/first-qualifying-round"},"Redcar Town FC":{"round":"First Round Qualifying","home":"Redcar Town","away":"Blyth Spartans","home_score":1,"away_score":0,"winner":"Redcar Town","status":"FT","decision":"","date":"2026-09-05","source_url":"https://www.footballwebpages.co.uk/fa-cup/fixtures-results/first-qualifying-round"},"Heaton Stannington FC":{"round":"First Round Qualifying","home":"Heaton Stannington","away":"Knaresborough Town","home_score":1,"away_score":0,"winner":"Heaton Stannington","status":"FT","decision":"","date":"2026-09-05","source_url":"https://www.footballwebpages.co.uk/fa-cup/fixtures-results/first-qualifying-round"},"Heaton Stannington AFC":{"round":"First Round Qualifying","home":"Heaton Stannington","away":"Knaresborough Town","home_score":1,"away_score":0,"winner":"Heaton Stannington","status":"FT","decision
```

### 3
```js
 7HP"},"Heaton Stannington":{"round":"Preliminary Round Replay","home":"Heaton Stannington","away":"Kendal Town","date":"2026-08-25","kickoff":"19:45","ground":"The Willow Park","postcode":"NE7 7HP"},"Kendal Town FC":{"round":"Preliminary Round Replay","home":"Heaton Stannington","away":"Kendal Town","date":"2026-08-25","kickoff":"19:45","ground":"The Willow Park","postcode":"NE7 7HP"},"Kendal Town":{"round":"Preliminary Round Replay","home":"Heaton Stannington","away":"Kendal Town","date":"2026-08-25","kickoff":"19:45","ground":"The Willow Park","postcode":"NE7 7HP"}};

const VERIFIED_MATCH_VENUE_OVERRIDES={
  "Heaton Stannington":{
    ground:"The Willow Park",
    postcode:"NE7 7HP"
  },
  "Heaton Stannington FC":{
    ground:"The Willow Park",
    postcode:"NE7 7HP"
  }
};

const LIVE_COMPETITION_DATA_URL='./competition.json';
/* TIN_FOIL_EMBEDDED_COMPETITION_BEGIN */
const EMBEDDED_COMPETITION_DATA={"schema_version":1,"season":"2026-27","updated_at":"2026-09-13T23:40:24.845593+00:00","round_dates":{"First Round Qualifying":"2026-09-05","Second Round Qualifying":"2026-09-19","Third Round Qualifying":"2026-10-03","Fourth Round Qualifying":"2026-10-17","First Round Proper":"2026-11-07","Preliminary Round":"2026-08-22"},"results":{"Blyth Spartans AFC":{"round":"First Round Qualifying","home":"Redcar Town","away":"Blyth Spartans","home_score":1,"away_score":0,"winner":"Redcar Town","status":"FT","decision":"","date":"2026-09-05","source_url":"https://www.footballwebpages.co.uk/fa-cup/fixtures-results/first-qualifying-round"},"Redcar Town FC":{"round":"First Round Qualifying","home":"Redcar Town","away":"Blyth Spartans","home_score":1,"away_score":0,"winner":"Redcar Town","status":"FT","decision":"","date":"2026-09-05","source_url":"https://www.footballwebpages.co.uk/fa-cup/fixtures-results/first-qualifying-round"},"Heaton Stannington FC":{"round":"First Round Qualifying","home":"Heaton Stannington","away":"Knaresborough Town","home_score":1,"away_score":0,"winner":"Heaton Stannington","status":"FT","decision":"","date":"2026-09-05","source_url":"https://www.footballwebpages.co.uk/fa-cup/fixtures-results/first-qualifying-round"},"Heaton Stannington AFC":{"round":"First Round Qualifying","home":"Heaton Stannington","away":"Knaresborough Town","home_score":1,"away_score":0,"winner":"Heaton Stannington","status":"FT","decision":"","date":"2026-09-05","source_url
```

### 4
```js
d Qualifying","home":"Southall","away":"Cobham","date":"2026-09-06","kickoff":"15:00","source_url":"https://www.footballwebpages.co.uk/fa-cup/fixtures-results/first-qualifying-round"},{"round":"First Round Qualifying","home":"Stourbridge","away":"Rushall Olympic","date":"2026-09-06","kickoff":"15:00","venue":{"ground":"War Memorial Athletic Ground","postcode":"DY8 4HN","source":"https://fchd.info/maps/GAZ.htm","verification":"fchd-gazetteer"},"source_url":"https://www.footballwebpages.co.uk/fa-cup/fixtures-results/first-qualifying-round"}]},"second_qualifying_sync":{"source":"Football Web Pages + retained pending replay slot","source_url":"https://www.footballwebpages.co.uk/fa-cup/fixtures-results","synced_at":"2026-09-13T23:40:21.496888+00:00","resolved_fixtures":79,"pending_replay_slots":1,"total_fixtures":80,"pending":"Hanwell Town v Burgess H or Jersey Bulls"}};
/* TIN_FOIL_EMBEDDED_COMPETITION_END */
let LIVE_COMPETITION_DATA=EMBEDDED_COMPETITION_DATA;
let LIVE_DATA_STATUS={state:'embedded',updated_at:EMBEDDED_COMPETITION_DATA.updated_at||null,message:'Using embedded competition snapshot'};
function liveLookup(section,name){
  if(!LIVE_COMPETITION_DATA||!LIVE_COMPETITION_DATA[section])return null;
  const obj=LIVE_COMPETITION_DATA[section],raw=String(name||''),short=raw.replace(/\s+(FC|AFC|CFC)$/,'');
  return obj[raw]||obj[short]||null;
}

function liveResultHistory(name){
  if(!LIVE_COMPETITION_DATA)return [];
  const section=LIVE_COMPETITION_DATA.result_history||{};
  const raw=String(name||''), short=raw.replace(/\s+(FC|AFC|CFC)$/,'');
  const arr=section[raw]||section[short]||[];
  return Array.isArray(arr)?arr:[];
}
function applyLiveRoundDates(){
  const d=LIVE_COMPETITION_DATA&&LIVE_COMPETITION_DATA.round_dates;if(!d)return;
  Object.keys(d).forEach(k=>{if(ROUND_META[k])ROUND_META[k].date=d[k];});
}
async function refreshCompetitionData(force=false){
  try{
    const u=LIVE_COMPETITION_DATA_URL+(LIVE_COMPETITION_DATA_URL.includes('?')?'&':'?')+'t='+Date.now();
    const r=await fetch(u,{cache:'no-store'});if(!r.ok)throw new Error('HTTP '+r.status);
    const d=await r.json();if(!d||Number(d.schema_version)!==1)throw new Error('Unsupported schema');
    LIVE_COMPETITION_DATA=d;applyLiveRoundDates();
    LIVE_DATA_STATUS={state:'live',updated_at:d.updated_at||null,message:'Competition data loaded'};
  }catch(e){LIVE_COMPETITION_DATA=EMBEDDED_COMPE
```

### 5
```js
ll","away":"Cobham","date":"2026-09-06","kickoff":"15:00","source_url":"https://www.footballwebpages.co.uk/fa-cup/fixtures-results/first-qualifying-round"},{"round":"First Round Qualifying","home":"Stourbridge","away":"Rushall Olympic","date":"2026-09-06","kickoff":"15:00","venue":{"ground":"War Memorial Athletic Ground","postcode":"DY8 4HN","source":"https://fchd.info/maps/GAZ.htm","verification":"fchd-gazetteer"},"source_url":"https://www.footballwebpages.co.uk/fa-cup/fixtures-results/first-qualifying-round"}]},"second_qualifying_sync":{"source":"Football Web Pages + retained pending replay slot","source_url":"https://www.footballwebpages.co.uk/fa-cup/fixtures-results","synced_at":"2026-09-13T23:40:21.496888+00:00","resolved_fixtures":79,"pending_replay_slots":1,"total_fixtures":80,"pending":"Hanwell Town v Burgess H or Jersey Bulls"}};
/* TIN_FOIL_EMBEDDED_COMPETITION_END */
let LIVE_COMPETITION_DATA=EMBEDDED_COMPETITION_DATA;
let LIVE_DATA_STATUS={state:'embedded',updated_at:EMBEDDED_COMPETITION_DATA.updated_at||null,message:'Using embedded competition snapshot'};
function liveLookup(section,name){
  if(!LIVE_COMPETITION_DATA||!LIVE_COMPETITION_DATA[section])return null;
  const obj=LIVE_COMPETITION_DATA[section],raw=String(name||''),short=raw.replace(/\s+(FC|AFC|CFC)$/,'');
  return obj[raw]||obj[short]||null;
}

function liveResultHistory(name){
  if(!LIVE_COMPETITION_DATA)return [];
  const section=LIVE_COMPETITION_DATA.result_history||{};
  const raw=String(name||''), short=raw.replace(/\s+(FC|AFC|CFC)$/,'');
  const arr=section[raw]||section[short]||[];
  return Array.isArray(arr)?arr:[];
}
function applyLiveRoundDates(){
  const d=LIVE_COMPETITION_DATA&&LIVE_COMPETITION_DATA.round_dates;if(!d)return;
  Object.keys(d).forEach(k=>{if(ROUND_META[k])ROUND_META[k].date=d[k];});
}
async function refreshCompetitionData(force=false){
  try{
    const u=LIVE_COMPETITION_DATA_URL+(LIVE_COMPETITION_DATA_URL.includes('?')?'&':'?')+'t='+Date.now();
    const r=await fetch(u,{cache:'no-store'});if(!r.ok)throw new Error('HTTP '+r.status);
    const d=await r.json();if(!d||Number(d.schema_version)!==1)throw new Error('Unsupported schema');
    LIVE_COMPETITION_DATA=d;applyLiveRoundDates();
    LIVE_DATA_STATUS={state:'live',updated_at:d.updated_at||null,message:'Competition data loaded'};
  }catch(e){LIVE_COMPETITION_DATA=EMBEDDED_COMPETITION_DATA;applyLiveRoundDa
```

### 6
```js
:"2026-09-06","kickoff":"15:00","source_url":"https://www.footballwebpages.co.uk/fa-cup/fixtures-results/first-qualifying-round"},{"round":"First Round Qualifying","home":"Stourbridge","away":"Rushall Olympic","date":"2026-09-06","kickoff":"15:00","venue":{"ground":"War Memorial Athletic Ground","postcode":"DY8 4HN","source":"https://fchd.info/maps/GAZ.htm","verification":"fchd-gazetteer"},"source_url":"https://www.footballwebpages.co.uk/fa-cup/fixtures-results/first-qualifying-round"}]},"second_qualifying_sync":{"source":"Football Web Pages + retained pending replay slot","source_url":"https://www.footballwebpages.co.uk/fa-cup/fixtures-results","synced_at":"2026-09-13T23:40:21.496888+00:00","resolved_fixtures":79,"pending_replay_slots":1,"total_fixtures":80,"pending":"Hanwell Town v Burgess H or Jersey Bulls"}};
/* TIN_FOIL_EMBEDDED_COMPETITION_END */
let LIVE_COMPETITION_DATA=EMBEDDED_COMPETITION_DATA;
let LIVE_DATA_STATUS={state:'embedded',updated_at:EMBEDDED_COMPETITION_DATA.updated_at||null,message:'Using embedded competition snapshot'};
function liveLookup(section,name){
  if(!LIVE_COMPETITION_DATA||!LIVE_COMPETITION_DATA[section])return null;
  const obj=LIVE_COMPETITION_DATA[section],raw=String(name||''),short=raw.replace(/\s+(FC|AFC|CFC)$/,'');
  return obj[raw]||obj[short]||null;
}

function liveResultHistory(name){
  if(!LIVE_COMPETITION_DATA)return [];
  const section=LIVE_COMPETITION_DATA.result_history||{};
  const raw=String(name||''), short=raw.replace(/\s+(FC|AFC|CFC)$/,'');
  const arr=section[raw]||section[short]||[];
  return Array.isArray(arr)?arr:[];
}
function applyLiveRoundDates(){
  const d=LIVE_COMPETITION_DATA&&LIVE_COMPETITION_DATA.round_dates;if(!d)return;
  Object.keys(d).forEach(k=>{if(ROUND_META[k])ROUND_META[k].date=d[k];});
}
async function refreshCompetitionData(force=false){
  try{
    const u=LIVE_COMPETITION_DATA_URL+(LIVE_COMPETITION_DATA_URL.includes('?')?'&':'?')+'t='+Date.now();
    const r=await fetch(u,{cache:'no-store'});if(!r.ok)throw new Error('HTTP '+r.status);
    const d=await r.json();if(!d||Number(d.schema_version)!==1)throw new Error('Unsupported schema');
    LIVE_COMPETITION_DATA=d;applyLiveRoundDates();
    LIVE_DATA_STATUS={state:'live',updated_at:d.updated_at||null,message:'Competition data loaded'};
  }catch(e){LIVE_COMPETITION_DATA=EMBEDDED_COMPETITION_DATA;applyLiveRoundDates();LIVE_DATA_STATUS={st
```

### 7
```js
.uk/fa-cup/fixtures-results/first-qualifying-round"},{"round":"First Round Qualifying","home":"Stourbridge","away":"Rushall Olympic","date":"2026-09-06","kickoff":"15:00","venue":{"ground":"War Memorial Athletic Ground","postcode":"DY8 4HN","source":"https://fchd.info/maps/GAZ.htm","verification":"fchd-gazetteer"},"source_url":"https://www.footballwebpages.co.uk/fa-cup/fixtures-results/first-qualifying-round"}]},"second_qualifying_sync":{"source":"Football Web Pages + retained pending replay slot","source_url":"https://www.footballwebpages.co.uk/fa-cup/fixtures-results","synced_at":"2026-09-13T23:40:21.496888+00:00","resolved_fixtures":79,"pending_replay_slots":1,"total_fixtures":80,"pending":"Hanwell Town v Burgess H or Jersey Bulls"}};
/* TIN_FOIL_EMBEDDED_COMPETITION_END */
let LIVE_COMPETITION_DATA=EMBEDDED_COMPETITION_DATA;
let LIVE_DATA_STATUS={state:'embedded',updated_at:EMBEDDED_COMPETITION_DATA.updated_at||null,message:'Using embedded competition snapshot'};
function liveLookup(section,name){
  if(!LIVE_COMPETITION_DATA||!LIVE_COMPETITION_DATA[section])return null;
  const obj=LIVE_COMPETITION_DATA[section],raw=String(name||''),short=raw.replace(/\s+(FC|AFC|CFC)$/,'');
  return obj[raw]||obj[short]||null;
}

function liveResultHistory(name){
  if(!LIVE_COMPETITION_DATA)return [];
  const section=LIVE_COMPETITION_DATA.result_history||{};
  const raw=String(name||''), short=raw.replace(/\s+(FC|AFC|CFC)$/,'');
  const arr=section[raw]||section[short]||[];
  return Array.isArray(arr)?arr:[];
}
function applyLiveRoundDates(){
  const d=LIVE_COMPETITION_DATA&&LIVE_COMPETITION_DATA.round_dates;if(!d)return;
  Object.keys(d).forEach(k=>{if(ROUND_META[k])ROUND_META[k].date=d[k];});
}
async function refreshCompetitionData(force=false){
  try{
    const u=LIVE_COMPETITION_DATA_URL+(LIVE_COMPETITION_DATA_URL.includes('?')?'&':'?')+'t='+Date.now();
    const r=await fetch(u,{cache:'no-store'});if(!r.ok)throw new Error('HTTP '+r.status);
    const d=await r.json();if(!d||Number(d.schema_version)!==1)throw new Error('Unsupported schema');
    LIVE_COMPETITION_DATA=d;applyLiveRoundDates();
    LIVE_DATA_STATUS={state:'live',updated_at:d.updated_at||null,message:'Competition data loaded'};
  }catch(e){LIVE_COMPETITION_DATA=EMBEDDED_COMPETITION_DATA;applyLiveRoundDates();LIVE_DATA_STATUS={state:'embedded',updated_at:EMBEDDED_COMPETITION_DATA.updated_at||null,message:
```

### 8
```js
pic","date":"2026-09-06","kickoff":"15:00","venue":{"ground":"War Memorial Athletic Ground","postcode":"DY8 4HN","source":"https://fchd.info/maps/GAZ.htm","verification":"fchd-gazetteer"},"source_url":"https://www.footballwebpages.co.uk/fa-cup/fixtures-results/first-qualifying-round"}]},"second_qualifying_sync":{"source":"Football Web Pages + retained pending replay slot","source_url":"https://www.footballwebpages.co.uk/fa-cup/fixtures-results","synced_at":"2026-09-13T23:40:21.496888+00:00","resolved_fixtures":79,"pending_replay_slots":1,"total_fixtures":80,"pending":"Hanwell Town v Burgess H or Jersey Bulls"}};
/* TIN_FOIL_EMBEDDED_COMPETITION_END */
let LIVE_COMPETITION_DATA=EMBEDDED_COMPETITION_DATA;
let LIVE_DATA_STATUS={state:'embedded',updated_at:EMBEDDED_COMPETITION_DATA.updated_at||null,message:'Using embedded competition snapshot'};
function liveLookup(section,name){
  if(!LIVE_COMPETITION_DATA||!LIVE_COMPETITION_DATA[section])return null;
  const obj=LIVE_COMPETITION_DATA[section],raw=String(name||''),short=raw.replace(/\s+(FC|AFC|CFC)$/,'');
  return obj[raw]||obj[short]||null;
}

function liveResultHistory(name){
  if(!LIVE_COMPETITION_DATA)return [];
  const section=LIVE_COMPETITION_DATA.result_history||{};
  const raw=String(name||''), short=raw.replace(/\s+(FC|AFC|CFC)$/,'');
  const arr=section[raw]||section[short]||[];
  return Array.isArray(arr)?arr:[];
}
function applyLiveRoundDates(){
  const d=LIVE_COMPETITION_DATA&&LIVE_COMPETITION_DATA.round_dates;if(!d)return;
  Object.keys(d).forEach(k=>{if(ROUND_META[k])ROUND_META[k].date=d[k];});
}
async function refreshCompetitionData(force=false){
  try{
    const u=LIVE_COMPETITION_DATA_URL+(LIVE_COMPETITION_DATA_URL.includes('?')?'&':'?')+'t='+Date.now();
    const r=await fetch(u,{cache:'no-store'});if(!r.ok)throw new Error('HTTP '+r.status);
    const d=await r.json();if(!d||Number(d.schema_version)!==1)throw new Error('Unsupported schema');
    LIVE_COMPETITION_DATA=d;applyLiveRoundDates();
    LIVE_DATA_STATUS={state:'live',updated_at:d.updated_at||null,message:'Competition data loaded'};
  }catch(e){LIVE_COMPETITION_DATA=EMBEDDED_COMPETITION_DATA;applyLiveRoundDates();LIVE_DATA_STATUS={state:'embedded',updated_at:EMBEDDED_COMPETITION_DATA.updated_at||null,message:'Embedded snapshot — live data unavailable'};}
  updateLiveDataBadge();return LIVE_DATA_STATUS.state==='live';
}
function update
```

### 9
```js
,"kickoff":"15:00","venue":{"ground":"War Memorial Athletic Ground","postcode":"DY8 4HN","source":"https://fchd.info/maps/GAZ.htm","verification":"fchd-gazetteer"},"source_url":"https://www.footballwebpages.co.uk/fa-cup/fixtures-results/first-qualifying-round"}]},"second_qualifying_sync":{"source":"Football Web Pages + retained pending replay slot","source_url":"https://www.footballwebpages.co.uk/fa-cup/fixtures-results","synced_at":"2026-09-13T23:40:21.496888+00:00","resolved_fixtures":79,"pending_replay_slots":1,"total_fixtures":80,"pending":"Hanwell Town v Burgess H or Jersey Bulls"}};
/* TIN_FOIL_EMBEDDED_COMPETITION_END */
let LIVE_COMPETITION_DATA=EMBEDDED_COMPETITION_DATA;
let LIVE_DATA_STATUS={state:'embedded',updated_at:EMBEDDED_COMPETITION_DATA.updated_at||null,message:'Using embedded competition snapshot'};
function liveLookup(section,name){
  if(!LIVE_COMPETITION_DATA||!LIVE_COMPETITION_DATA[section])return null;
  const obj=LIVE_COMPETITION_DATA[section],raw=String(name||''),short=raw.replace(/\s+(FC|AFC|CFC)$/,'');
  return obj[raw]||obj[short]||null;
}

function liveResultHistory(name){
  if(!LIVE_COMPETITION_DATA)return [];
  const section=LIVE_COMPETITION_DATA.result_history||{};
  const raw=String(name||''), short=raw.replace(/\s+(FC|AFC|CFC)$/,'');
  const arr=section[raw]||section[short]||[];
  return Array.isArray(arr)?arr:[];
}
function applyLiveRoundDates(){
  const d=LIVE_COMPETITION_DATA&&LIVE_COMPETITION_DATA.round_dates;if(!d)return;
  Object.keys(d).forEach(k=>{if(ROUND_META[k])ROUND_META[k].date=d[k];});
}
async function refreshCompetitionData(force=false){
  try{
    const u=LIVE_COMPETITION_DATA_URL+(LIVE_COMPETITION_DATA_URL.includes('?')?'&':'?')+'t='+Date.now();
    const r=await fetch(u,{cache:'no-store'});if(!r.ok)throw new Error('HTTP '+r.status);
    const d=await r.json();if(!d||Number(d.schema_version)!==1)throw new Error('Unsupported schema');
    LIVE_COMPETITION_DATA=d;applyLiveRoundDates();
    LIVE_DATA_STATUS={state:'live',updated_at:d.updated_at||null,message:'Competition data loaded'};
  }catch(e){LIVE_COMPETITION_DATA=EMBEDDED_COMPETITION_DATA;applyLiveRoundDates();LIVE_DATA_STATUS={state:'embedded',updated_at:EMBEDDED_COMPETITION_DATA.updated_at||null,message:'Embedded snapshot — live data unavailable'};}
  updateLiveDataBadge();return LIVE_DATA_STATUS.state==='live';
}
function updateLiveDataBadge(){
  const
```

### 10
```js
tic Ground","postcode":"DY8 4HN","source":"https://fchd.info/maps/GAZ.htm","verification":"fchd-gazetteer"},"source_url":"https://www.footballwebpages.co.uk/fa-cup/fixtures-results/first-qualifying-round"}]},"second_qualifying_sync":{"source":"Football Web Pages + retained pending replay slot","source_url":"https://www.footballwebpages.co.uk/fa-cup/fixtures-results","synced_at":"2026-09-13T23:40:21.496888+00:00","resolved_fixtures":79,"pending_replay_slots":1,"total_fixtures":80,"pending":"Hanwell Town v Burgess H or Jersey Bulls"}};
/* TIN_FOIL_EMBEDDED_COMPETITION_END */
let LIVE_COMPETITION_DATA=EMBEDDED_COMPETITION_DATA;
let LIVE_DATA_STATUS={state:'embedded',updated_at:EMBEDDED_COMPETITION_DATA.updated_at||null,message:'Using embedded competition snapshot'};
function liveLookup(section,name){
  if(!LIVE_COMPETITION_DATA||!LIVE_COMPETITION_DATA[section])return null;
  const obj=LIVE_COMPETITION_DATA[section],raw=String(name||''),short=raw.replace(/\s+(FC|AFC|CFC)$/,'');
  return obj[raw]||obj[short]||null;
}

function liveResultHistory(name){
  if(!LIVE_COMPETITION_DATA)return [];
  const section=LIVE_COMPETITION_DATA.result_history||{};
  const raw=String(name||''), short=raw.replace(/\s+(FC|AFC|CFC)$/,'');
  const arr=section[raw]||section[short]||[];
  return Array.isArray(arr)?arr:[];
}
function applyLiveRoundDates(){
  const d=LIVE_COMPETITION_DATA&&LIVE_COMPETITION_DATA.round_dates;if(!d)return;
  Object.keys(d).forEach(k=>{if(ROUND_META[k])ROUND_META[k].date=d[k];});
}
async function refreshCompetitionData(force=false){
  try{
    const u=LIVE_COMPETITION_DATA_URL+(LIVE_COMPETITION_DATA_URL.includes('?')?'&':'?')+'t='+Date.now();
    const r=await fetch(u,{cache:'no-store'});if(!r.ok)throw new Error('HTTP '+r.status);
    const d=await r.json();if(!d||Number(d.schema_version)!==1)throw new Error('Unsupported schema');
    LIVE_COMPETITION_DATA=d;applyLiveRoundDates();
    LIVE_DATA_STATUS={state:'live',updated_at:d.updated_at||null,message:'Competition data loaded'};
  }catch(e){LIVE_COMPETITION_DATA=EMBEDDED_COMPETITION_DATA;applyLiveRoundDates();LIVE_DATA_STATUS={state:'embedded',updated_at:EMBEDDED_COMPETITION_DATA.updated_at||null,message:'Embedded snapshot — live data unavailable'};}
  updateLiveDataBadge();return LIVE_DATA_STATUS.state==='live';
}
function updateLiveDataBadge(){
  const e=document.getElementById('liveDataBadge');if(!e)return
```

### 11
```js
esults/first-qualifying-round"}]},"second_qualifying_sync":{"source":"Football Web Pages + retained pending replay slot","source_url":"https://www.footballwebpages.co.uk/fa-cup/fixtures-results","synced_at":"2026-09-13T23:40:21.496888+00:00","resolved_fixtures":79,"pending_replay_slots":1,"total_fixtures":80,"pending":"Hanwell Town v Burgess H or Jersey Bulls"}};
/* TIN_FOIL_EMBEDDED_COMPETITION_END */
let LIVE_COMPETITION_DATA=EMBEDDED_COMPETITION_DATA;
let LIVE_DATA_STATUS={state:'embedded',updated_at:EMBEDDED_COMPETITION_DATA.updated_at||null,message:'Using embedded competition snapshot'};
function liveLookup(section,name){
  if(!LIVE_COMPETITION_DATA||!LIVE_COMPETITION_DATA[section])return null;
  const obj=LIVE_COMPETITION_DATA[section],raw=String(name||''),short=raw.replace(/\s+(FC|AFC|CFC)$/,'');
  return obj[raw]||obj[short]||null;
}

function liveResultHistory(name){
  if(!LIVE_COMPETITION_DATA)return [];
  const section=LIVE_COMPETITION_DATA.result_history||{};
  const raw=String(name||''), short=raw.replace(/\s+(FC|AFC|CFC)$/,'');
  const arr=section[raw]||section[short]||[];
  return Array.isArray(arr)?arr:[];
}
function applyLiveRoundDates(){
  const d=LIVE_COMPETITION_DATA&&LIVE_COMPETITION_DATA.round_dates;if(!d)return;
  Object.keys(d).forEach(k=>{if(ROUND_META[k])ROUND_META[k].date=d[k];});
}
async function refreshCompetitionData(force=false){
  try{
    const u=LIVE_COMPETITION_DATA_URL+(LIVE_COMPETITION_DATA_URL.includes('?')?'&':'?')+'t='+Date.now();
    const r=await fetch(u,{cache:'no-store'});if(!r.ok)throw new Error('HTTP '+r.status);
    const d=await r.json();if(!d||Number(d.schema_version)!==1)throw new Error('Unsupported schema');
    LIVE_COMPETITION_DATA=d;applyLiveRoundDates();
    LIVE_DATA_STATUS={state:'live',updated_at:d.updated_at||null,message:'Competition data loaded'};
  }catch(e){LIVE_COMPETITION_DATA=EMBEDDED_COMPETITION_DATA;applyLiveRoundDates();LIVE_DATA_STATUS={state:'embedded',updated_at:EMBEDDED_COMPETITION_DATA.updated_at||null,message:'Embedded snapshot — live data unavailable'};}
  updateLiveDataBadge();return LIVE_DATA_STATUS.state==='live';
}
function updateLiveDataBadge(){
  const e=document.getElementById('liveDataBadge');if(!e)return;
  if(LIVE_DATA_STATUS.state==='live'){
    let w=LIVE_DATA_STATUS.updated_at||'';try{w=new Date(w).toLocaleString('en-GB');}catch(x){}
    e.textContent='Clubfinder v7.6 — 
```

### 12
```js
ing_sync":{"source":"Football Web Pages + retained pending replay slot","source_url":"https://www.footballwebpages.co.uk/fa-cup/fixtures-results","synced_at":"2026-09-13T23:40:21.496888+00:00","resolved_fixtures":79,"pending_replay_slots":1,"total_fixtures":80,"pending":"Hanwell Town v Burgess H or Jersey Bulls"}};
/* TIN_FOIL_EMBEDDED_COMPETITION_END */
let LIVE_COMPETITION_DATA=EMBEDDED_COMPETITION_DATA;
let LIVE_DATA_STATUS={state:'embedded',updated_at:EMBEDDED_COMPETITION_DATA.updated_at||null,message:'Using embedded competition snapshot'};
function liveLookup(section,name){
  if(!LIVE_COMPETITION_DATA||!LIVE_COMPETITION_DATA[section])return null;
  const obj=LIVE_COMPETITION_DATA[section],raw=String(name||''),short=raw.replace(/\s+(FC|AFC|CFC)$/,'');
  return obj[raw]||obj[short]||null;
}

function liveResultHistory(name){
  if(!LIVE_COMPETITION_DATA)return [];
  const section=LIVE_COMPETITION_DATA.result_history||{};
  const raw=String(name||''), short=raw.replace(/\s+(FC|AFC|CFC)$/,'');
  const arr=section[raw]||section[short]||[];
  return Array.isArray(arr)?arr:[];
}
function applyLiveRoundDates(){
  const d=LIVE_COMPETITION_DATA&&LIVE_COMPETITION_DATA.round_dates;if(!d)return;
  Object.keys(d).forEach(k=>{if(ROUND_META[k])ROUND_META[k].date=d[k];});
}
async function refreshCompetitionData(force=false){
  try{
    const u=LIVE_COMPETITION_DATA_URL+(LIVE_COMPETITION_DATA_URL.includes('?')?'&':'?')+'t='+Date.now();
    const r=await fetch(u,{cache:'no-store'});if(!r.ok)throw new Error('HTTP '+r.status);
    const d=await r.json();if(!d||Number(d.schema_version)!==1)throw new Error('Unsupported schema');
    LIVE_COMPETITION_DATA=d;applyLiveRoundDates();
    LIVE_DATA_STATUS={state:'live',updated_at:d.updated_at||null,message:'Competition data loaded'};
  }catch(e){LIVE_COMPETITION_DATA=EMBEDDED_COMPETITION_DATA;applyLiveRoundDates();LIVE_DATA_STATUS={state:'embedded',updated_at:EMBEDDED_COMPETITION_DATA.updated_at||null,message:'Embedded snapshot — live data unavailable'};}
  updateLiveDataBadge();return LIVE_DATA_STATUS.state==='live';
}
function updateLiveDataBadge(){
  const e=document.getElementById('liveDataBadge');if(!e)return;
  if(LIVE_DATA_STATUS.state==='live'){
    let w=LIVE_DATA_STATUS.updated_at||'';try{w=new Date(w).toLocaleString('en-GB');}catch(x){}
    e.textContent='Clubfinder v7.6 — Competition data updated: '+w;
  }else e.textCont
```

## `resultsBy`
Matches: **0**

## `buildJourney`
Matches: **3**

### 1
```js
ameClubIdentity(r.away,club.name))return;
    if(!out.some(x=>sameSemanticResult(x.result,r)))out.push({round:round||r.round||club.entry_round||'FA Cup',result:r});
  }
  const hist=liveLookup('result_history',club.name);
  if(Array.isArray(hist))for(const r of hist)add(r,r&&r.round);
  add(liveLookup('results',club.name));
  if(!out.length){
    const f=club.fixture||{};
    if(club.entry_round==='Extra Preliminary Round'&&f.number!=null)add(EPR_RESULTS_BY_TIE[String(f.number)]||null,club.entry_round);
    else if(f.result&&typeof f.result==='object')add(f.result,club.entry_round||f.result.round);
    const key=String(club.name||'').replace(/\s+(FC|AFC|CFC)$/,'');
    add(CURRENT_RESULT_OVERRIDES[club.name]||CURRENT_RESULT_OVERRIDES[key]||null);
    add(liveLookup('results',club.name));
  }
  out.sort((a,b)=>resultSortValue(a.result)-resultSortValue(b.result));
  return out;
} function buildJourney(origin){
  let carrier=origin;
  const candidates=[];
  function clubObjectForWinner(name,prior){
    return clubByDisplayName(name)||candidateClubByName(name)||{name:name,entry_round:(prior&&prior.entry_round)||'',fixture:{}};
  }
  function appendHistory(club){
    const history=historicalResultsForClub(club);
    for(const item of history){
      if(!candidates.some(x=>sameSemanticResult(x.result,item.result)))candidates.push(item);
    }
  }
  function resolveChain(){
    let c=origin;
    const chain=[];
    const ordered=[...candidates].sort((a,b)=>resultSortValue(a.result)-resultSortValue(b.result));
    for(const item of ordered){
      const r=item.result||{};
      const participant=sameClubIdentity(r.home,c.name)||sameClubIdentity(r.away,c.name);
      if(!participant)continue;
      chain.push(item);
      const winner=canonicalResultWinner(r);
      if(winner&&!resultNeedsReplay(r))c=clubObjectForWinner(winner,c);
    }
    return {carrier:c,breadcrumbs:chain};
  }
  const expanded=new Set();
  for(let hop=0;hop<20;hop++){
    const key=canonicalClubKey(carrier.name);
    if(expanded.has(key))break;
    expanded.add(key);
    appendHistory(carrier);
    const resolved=resolveChain();
    const next=resolved.carrier;
    if(canonicalClubKey(next.name)===key){carrier=next;break;}
    carrier=next;
  }
  appendHistory(carrier);
  const resolved=resolveChain();
  return {origin,carrier:resolved.carrier,breadcrumbs:resolved.breadcrumbs};
} /* TIN_FOIL_NEX
```

### 2
```js
mbs,startPostcode,venueForResult){
  const played=(crumbs||[]).filter(cr=>String(((cr||{}).result||{}).decision||'').toLowerCase()!=='walkover');
  if(!played.length)return {miles:0,display:'0',unresolved:0};
  const start=await tinFoilPigeonCoords(startPostcode);
  if(!start)return {miles:null,display:'Awaiting venue location',unresolved:played.length};
  const venues=await Promise.all(played.map(cr=>{
    const v=venueForResult(((cr||{}).result)||{});
    return tinFoilPigeonCoords(v&&v.postcode);
  }));
  if(venues.some(v=>!v))return {miles:null,display:'Awaiting venue location',unresolved:venues.filter(v=>!v).length};
  const miles=venues.reduce((sum,venue)=>sum+(2*hav(start,venue)),0);
  return {miles,display:String(Math.round(miles)),unresolved:0};
}
/* TIN_FOIL_PIGEON_MILES_STATS_END */
async function journeyCertificate(origin){
  const w=window.open("","_blank");
  const journey=buildJourney(origin);
  const carrier=journey.carrier||origin;
  const crumbs=journey.breadcrumbs||[];
  const season='2026–27';
  function venueForResult(r){
    if(!r)return {ground:'Venue TBC',postcode:'Postcode TBC'};
    if(/Replay/i.test(r.round||'')){
      const hn=r.home||'',ov=VERIFIED_MATCH_VENUE_OVERRIDES[hn]||VERIFIED_MATCH_VENUE_OVERRIDES[(candidateClubByName(hn)||{}).name]||null;
      if(ov)return {ground:ov.ground||'Venue TBC',postcode:ov.postcode||'Postcode TBC'};
    }
    const hc=candidateClubByName(r.home),g=groundByClubName(hc?hc.name:r.home);
    return {ground:(g&&g.ground)||'Venue TBC',postcode:(g&&g.postcode)||'Postcode TBC'};
  }

  const savedJourneyForStats=loadSavedJourney();
  const pigeonStats=await tinFoilPigeonMilesForStats(crumbs,savedJourneyForStats&&savedJourneyForStats.postcode,venueForResult);
  const pigeonMilesDisplay=pigeonStats.display;


  const clubs=[];
  function addClub(n){
    if(n && !clubs.some(x=>norm(x)===norm(n))) clubs.push(n);
  }
  addClub(origin.name);
  crumbs.forEach(cr=>{
    const r=cr.result||{};
    addClub(r.home);
    addClub(r.away);
  });
  addClub(carrier.name);

  let goals=0, homeGames=0, awayGames=0, custodianWins=0, draws=0, custodianDefeats=0;
  const venueKeys=new Set();

  let pathCarrier=origin.name;

  for(const cr of crumbs){
    const r=cr.result||{};
    const hs=Number(r.home_score), as=Number(r.away_score);

    if(Number.isFinite(hs))goals+=hs;
    if(Number.isFinite(as))goals+=as;

    const
```

### 3
```js
s=[];
  for(const c of ELIGIBLE){const g=findGround(c)||{},v=verification(c,g),hasCoords=Number.isFinite(Number(g.lat))&&Number.isFinite(Number(g.lon));rows.push({...c,...g,website:c.website||(typeof CLUB_WEBSITES!=='undefined'?CLUB_WEBSITES[c.name]:'')||'',verification:v,hasCoords,distance:Infinity})}
  await geocodeClubPostcodes(rows);for(const r of rows)if(r.hasCoords)r.distance=hav(u,{lat:Number(r.lat),lon:Number(r.lon)});
  rows.sort((a,b)=>a.hasCoords&&b.hasCoords?a.distance-b.distance:a.hasCoords?-1:b.hasCoords?1:0);
  const top=rows.slice(0,3);if(!top.length)throw Error('No eligible clubs could be returned.');
  saved=loadSavedJourney();const selected=savedOrigin(rows,saved),showOriginal=!!window.__showOriginalTinFoilJourneys,shown=selected&&!showOriginal?[selected]:top;
  results.innerHTML=shown.map((origin,di)=>{
   const oi=top.findIndex(x=>norm(x.name)===norm(origin.name)),j=buildJourney(origin),c=j.carrier||origin,f=fixture(c),hasLoc=!!(origin.ground||origin.postcode),verified=origin.hasCoords&&origin.verification==='verified';
   const loc=verified?'✅ Verified Location.':hasLoc?'⚠️ Unverified Location - Please check before travelling.':'❌ No location data available.',lc=verified?'#176b2c':hasLoc?'#8a5a00':'#a32626',dist=origin.hasCoords?` • ${origin.distance.toFixed(1)} miles`:'';
   const website=(typeof CLUB_WEBSITES!=='undefined'&&CLUB_WEBSITES[origin.name])?` • <a href="${esc(CLUB_WEBSITES[origin.name])}" target="_blank" rel="noopener noreferrer">Website</a>`:'',ground=`${esc(origin.ground||'Ground location unavailable')} • ${esc(origin.postcode||'Postcode unavailable')}${dist}${website}`;
   const df=currentDisplayFixture(c),scored=resultTeamLine(c),round=df.round,tie=scored||df.tie||'',tieLine=tie?`<div><strong>${scored?scored:esc(df.tie)}</strong> • ${esc(round)}</div>`:'';
   const mine=saved&&norm(saved.originName)===norm(origin.name),jn=oi>=0?oi+1:di+1;
   const heading=selected&&!showOriginal?'':`<div class="journey-choice"><button class="journey-lozenge" type="button" title="Make This My Tin Foil FA Cup Journey" aria-label="Make Tin Foil FA Cup Journey ${jn} my journey" onclick='chooseJourney(${JSON.stringify(origin.name)},${JSON.stringify(u.postcode)})'><span class="round"><span class="default-label">Tin Foil FA Cup Journey ${jn}</span><span class="hover-label">Make This My Tin Foil FA Cup Journey</span></span></button></div>`;
   
```

## `canonicalResultWinner`
Matches: **6**

### 1
```js
_FIXTURE_OVERRIDES[club.name]||NEXT_FIXTURE_OVERRIDES[String(club.name||'').replace(/\s+(FC|AFC|CFC)$/,'')]||null;
  }
  const knownFixture=nf?(()=>{const k=resolveLiveFixtureForCarrier({home:nf.home,away:nf.away,date:nf.date,kickoff:nf.kickoff||'15:00',round:nf.round||nextName,conditional:!!nf.conditional},club);if(nf.venue&&nf.venue.postcode&&!/TBC/i.test(String(nf.venue.postcode)))k.venue={...nf.venue};return k;})():null;
  return {name:nextName,date:meta.date,drawDate:meta.drawDate,knownFixture,fixturesUrl:FA_FIXTURES_URL};
}

function canonicalClubKey(name){
  return String(name||'').toLowerCase()
    .replace(/&/g,' and ')
    .replace(/\b(association football club|football club)\b/g,' ')
    .replace(/\b(fc|afc|cfc)\b/g,' ')
    .replace(/[^a-z0-9]+/g,' ')
    .trim().replace(/\s+/g,' ');
}
function sameClubIdentity(a,b){return canonicalClubKey(a)===canonicalClubKey(b);}
function canonicalResultWinner(r){
  if(!r)return '';
  const hs=Number(r.home_score),as=Number(r.away_score);
  if(Number.isFinite(hs)&&Number.isFinite(as)&&hs!==as)return hs>as?r.home:r.away;
  if(r.decision==='draw-replay')return '';
  return r.winner||'';
}
function sameSemanticResult(a,b){
  if(!a||!b)return false;
  return sameClubIdentity(a.home,b.home)&&sameClubIdentity(a.away,b.away)&&
    Number(a.home_score)===Number(b.home_score)&&Number(a.away_score)===Number(b.away_score)&&
    String(a.round||'')===String(b.round||'')&&String(a.decision||'')===String(b.decision||'');
}
function clubByDisplayName(name){
  if(!name)return null;
  const target=canonicalClubKey(name);
  return ELIGIBLE.find(c=>canonicalClubKey(c.name)===target)||null;
}
function groundByClubName(name){
  if(!name)return {};
  const target=canonicalClubKey(name);
  const g=GROUNDS.find(g=>canonicalClubKey(g.name||g.club)===target);
  if(g)return g;
  const s=LAW2_ORIGIN_LOCATIONS.find(g=>canonicalClubKey(g.name||g.club)===target);
  if(s)return s;
  const c=ELIGIBLE.find(c=>canonicalClubKey(c.name)===target);
  if(c&&(c.ground||c.postcode))return c;
  return {};
} function completedResultVenue(result){
  if(!result)return {ground:'Venue TBC',postcode:'Postcode TBC'};
  const homeClub=candidateClubByName(result.home);
  const hg=groundByClubName(homeClub?homeClub.name:result.home);
  return {
    ground:(hg&&hg.ground)||'Venue TBC',
    postcode:(hg&&hg.postcode)||'Postcode TBC',
    lat:hg&&hg.lat,lon:hg&&hg
```

### 2
```js
tValue(b.result));
  return out;
} function buildJourney(origin){
  let carrier=origin;
  const candidates=[];
  function clubObjectForWinner(name,prior){
    return clubByDisplayName(name)||candidateClubByName(name)||{name:name,entry_round:(prior&&prior.entry_round)||'',fixture:{}};
  }
  function appendHistory(club){
    const history=historicalResultsForClub(club);
    for(const item of history){
      if(!candidates.some(x=>sameSemanticResult(x.result,item.result)))candidates.push(item);
    }
  }
  function resolveChain(){
    let c=origin;
    const chain=[];
    const ordered=[...candidates].sort((a,b)=>resultSortValue(a.result)-resultSortValue(b.result));
    for(const item of ordered){
      const r=item.result||{};
      const participant=sameClubIdentity(r.home,c.name)||sameClubIdentity(r.away,c.name);
      if(!participant)continue;
      chain.push(item);
      const winner=canonicalResultWinner(r);
      if(winner&&!resultNeedsReplay(r))c=clubObjectForWinner(winner,c);
    }
    return {carrier:c,breadcrumbs:chain};
  }
  const expanded=new Set();
  for(let hop=0;hop<20;hop++){
    const key=canonicalClubKey(carrier.name);
    if(expanded.has(key))break;
    expanded.add(key);
    appendHistory(carrier);
    const resolved=resolveChain();
    const next=resolved.carrier;
    if(canonicalClubKey(next.name)===key){carrier=next;break;}
    carrier=next;
  }
  appendHistory(carrier);
  const resolved=resolveChain();
  return {origin,carrier:resolved.carrier,breadcrumbs:resolved.breadcrumbs};
} /* TIN_FOIL_NEXT_ROUND_INTEGRITY_BEGIN */
const tinFoilBaseNextRoundInfo=nextRoundInfo;
nextRoundInfo=function(club){
  const info=tinFoilBaseNextRoundInfo(club);
  if(!info||!info.knownFixture)return info;
  const fixture=info.knownFixture||{};
  const target=String(info.name||'').trim().toLowerCase();
  const actual=String(fixture.round||'').trim().toLowerCase();
  if(target&&actual&&target!==actual){
    return {...info,knownFixture:null};
  }
  return info;
};
/* TIN_FOIL_NEXT_ROUND_INTEGRITY_END */
function previousRoundsHtml(journey){
  const crumbs=journey.breadcrumbs||[];
  let body='<div class="history"><div class="history-title">Previous Rounds</div>'+
    '<div class="history-origin">Journey started with: '+esc(journey.origin.name)+'</div>';
  const entryRound=journey.origin.entry_round||'';
  if(entryRound&&entryRound!=='Extra Preliminary Round'){
```

### 3
```js
ground||'Venue TBC',
      postcode:override.postcode||'Postcode TBC',
      verification:'verified'
    };
  }

  const hc=candidateClubByName(homeName);
  const hg=groundByClubName(hc?hc.name:homeName);
  if(hg && ((hg.ground&&!/TBC/i.test(hg.ground)) || (hg.postcode&&!/TBC/i.test(hg.postcode)))){
    return {
      ground:hg.ground||rf.ground||'Venue TBC',
      postcode:hg.postcode||rf.postcode||'Postcode TBC',
      lat:hg.lat,lon:hg.lon,
      verification:hg.verification||'verified'
    };
  }

  return {
    ground:rf.ground||'Venue TBC',
    postcode:rf.postcode||'Postcode TBC',
    verification:'unverified'
  };
}
function competitionState(club){
  const f=club.fixture||{},r=resultFor(club),kickoff=parseKickoff(f),now=new Date();
  if(r){
    if(resultNeedsReplay(r))return {type:'replay',title:'↻ Replay required',result:r,replay:replayFixtureFor(club),next:null};
    const won=canonicalResultWinner(r)&&sameClubIdentity(canonicalResultWinner(r),club.name);
    return {type:won?'won':'eliminated',title:won?'✅ Through to the next round':'❌ Eliminated from the FA Cup',result:r,next:nextRoundInfo(club)};
  }
  if(kickoff&&now<kickoff)return {type:'upcoming',title:'Upcoming FA Cup tie',next:null};
  if(kickoff&&now>=kickoff)return {type:'played',title:'This tie has been played',result:null,next:nextRoundInfo(club)};
  return {type:'pending',title:'Fixture details pending',next:nextRoundInfo(club)};
}

function formatDateGB(value){
  if(!value)return 'Date TBC';
  const d=new Date(value+'T12:00:00');
  if(Number.isNaN(d.getTime()))return value;
  return d.toLocaleDateString('en-GB',{weekday:'long',day:'numeric',month:'long',year:'numeric'});
}
function nextProgressHtml(club,next){
  if(!next)return '';

  if(next.knownFixture){
    const k=next.knownFixture;
    const v=k.venue||{};
    return '<br><strong>Next: '+esc(k.home)+' v '+esc(k.away)+'</strong> • '+esc(k.round||next.name)+
      '<br>'+esc(formatDateGB(k.date))+' • '+esc(k.kickoff)+
      ' • '+esc(v.ground||'Venue TBC')+' • '+esc(v.postcode||'Postcode TBC');
  }

  let drawLine='';
  if(next.knownFixture){ drawLine=''; } else if(next.drawDate==='Draw already made'){
    drawLine='Draw already made';
  }else if(next.drawDate&&next.drawDate!=='TBC'){
    drawLine='Draw to be made on '+next.drawDate;
  }else{
    drawLine='Draw: TBC';
  }

  return '<br><strong>Next: '+esc(next.name)+'</strong>'+

```

### 4
```js
e.postcode||'Postcode TBC',
      verification:'verified'
    };
  }

  const hc=candidateClubByName(homeName);
  const hg=groundByClubName(hc?hc.name:homeName);
  if(hg && ((hg.ground&&!/TBC/i.test(hg.ground)) || (hg.postcode&&!/TBC/i.test(hg.postcode)))){
    return {
      ground:hg.ground||rf.ground||'Venue TBC',
      postcode:hg.postcode||rf.postcode||'Postcode TBC',
      lat:hg.lat,lon:hg.lon,
      verification:hg.verification||'verified'
    };
  }

  return {
    ground:rf.ground||'Venue TBC',
    postcode:rf.postcode||'Postcode TBC',
    verification:'unverified'
  };
}
function competitionState(club){
  const f=club.fixture||{},r=resultFor(club),kickoff=parseKickoff(f),now=new Date();
  if(r){
    if(resultNeedsReplay(r))return {type:'replay',title:'↻ Replay required',result:r,replay:replayFixtureFor(club),next:null};
    const won=canonicalResultWinner(r)&&sameClubIdentity(canonicalResultWinner(r),club.name);
    return {type:won?'won':'eliminated',title:won?'✅ Through to the next round':'❌ Eliminated from the FA Cup',result:r,next:nextRoundInfo(club)};
  }
  if(kickoff&&now<kickoff)return {type:'upcoming',title:'Upcoming FA Cup tie',next:null};
  if(kickoff&&now>=kickoff)return {type:'played',title:'This tie has been played',result:null,next:nextRoundInfo(club)};
  return {type:'pending',title:'Fixture details pending',next:nextRoundInfo(club)};
}

function formatDateGB(value){
  if(!value)return 'Date TBC';
  const d=new Date(value+'T12:00:00');
  if(Number.isNaN(d.getTime()))return value;
  return d.toLocaleDateString('en-GB',{weekday:'long',day:'numeric',month:'long',year:'numeric'});
}
function nextProgressHtml(club,next){
  if(!next)return '';

  if(next.knownFixture){
    const k=next.knownFixture;
    const v=k.venue||{};
    return '<br><strong>Next: '+esc(k.home)+' v '+esc(k.away)+'</strong> • '+esc(k.round||next.name)+
      '<br>'+esc(formatDateGB(k.date))+' • '+esc(k.kickoff)+
      ' • '+esc(v.ground||'Venue TBC')+' • '+esc(v.postcode||'Postcode TBC');
  }

  let drawLine='';
  if(next.knownFixture){ drawLine=''; } else if(next.drawDate==='Draw already made'){
    drawLine='Draw already made';
  }else if(next.drawDate&&next.drawDate!=='TBC'){
    drawLine='Draw to be made on '+next.drawDate;
  }else{
    drawLine='Draw: TBC';
  }

  return '<br><strong>Next: '+esc(next.name)+'</strong>'+
    '<br>'+esc(tinFoilDisplayDate(next.date
```

### 5
```js
tinFoilStartResultHealthNotice,0);
/* TIN_FOIL_RESULT_HEALTH_END *//* TIN_FOIL_STATS_INTEGRITY_BEGIN */
function tinFoilStatsFixtureParts(text){
  const s=String(text||'').replace(/\s+/g,' ').trim();
  const m=s.match(/^(.+?)\s*\((\d+)\)\s*v\s*\((\d+)\)\s*(.+)$/i);
  if(!m)return null;
  return {home:m[1].trim(),homeScore:Number(m[2]),awayScore:Number(m[3]),away:m[4].trim()};
}
function tinFoilStatsWinnerFromFixture(text){
  const p=tinFoilStatsFixtureParts(text);
  if(!p||!Number.isFinite(p.homeScore)||!Number.isFinite(p.awayScore)||p.homeScore===p.awayScore)return '';
  return p.homeScore>p.awayScore?p.home:p.away;
}
function tinFoilCertificateWinner(r){
  if(r){
    const hs=Number(r.home_score),as=Number(r.away_score);
    if(Number.isFinite(hs)&&Number.isFinite(as)){
      if(hs===as)return '';
      return (hs>as?String(r.home||''):String(r.away||'')).trim();
    }
  }
  if(typeof canonicalResultWinner==='function')return canonicalResultWinner(r)||'';
  return r&&r.winner?r.winner:'';
}
function tinFoilStatsDisplayClubKey(name){
  return String(name||'').toLowerCase().replace(/&/g,' and ').replace(/\b(association football club|football club|fc|afc|cfc)\b/g,' ').replace(/[^a-z0-9]+/g,' ').trim().replace(/\s+/g,' ');
}
function tinFoilStatsFixtureCount(text){
  const s=String(text||'').replace(/\s+/g,' ');
  const re=/(?:^|\s)([^|]{1,100}?)\s*\(\d+\)\s*v\s*\(\d+\)\s*([^|]{1,100}?)(?=$|\s{2,}|\n)/ig;
  let n=0; while(re.exec(s)&&n<3)n++; return n;
}
function tinFoilStatsLeafElements(root){
  if(!root||typeof root.querySelectorAll!=='function')return [];
  return [...root.querySelectorAll('*')].filter(e=>!e.children||e.children.length===0);
}
function tinFoilStatsRepairRenderedRow(row){
  if(!row)return false;
  const leaves=tinFoilStatsLeafElements(row);
  let fixtureLeaf=null,parts=null;
  for(const leaf of leaves){
    const p=tinFoilStatsFixtureParts(leaf.textContent||'');
    if(p){fixtureLeaf=leaf;parts=p;break;}
  }
  if(!fixtureLeaf||!parts||parts.homeScore===parts.awayScore)return false;
  const winner=parts.homeScore>parts.awayScore?parts.home:parts.away;
  const homeKey=tinFoilStatsDisplayClubKey(parts.home),awayKey=tinFoilStatsDisplayClubKey(parts.away);
  const candidates=leaves.filter(leaf=>{
    if(leaf===fixtureLeaf)return false;
    const k=tinFoilStatsDisplayClubKey(leaf.textContent||'');
    return k&&(k===homeKey||k===awayKey);
  });
  
```

### 6
```js
FOIL_RESULT_HEALTH_END *//* TIN_FOIL_STATS_INTEGRITY_BEGIN */
function tinFoilStatsFixtureParts(text){
  const s=String(text||'').replace(/\s+/g,' ').trim();
  const m=s.match(/^(.+?)\s*\((\d+)\)\s*v\s*\((\d+)\)\s*(.+)$/i);
  if(!m)return null;
  return {home:m[1].trim(),homeScore:Number(m[2]),awayScore:Number(m[3]),away:m[4].trim()};
}
function tinFoilStatsWinnerFromFixture(text){
  const p=tinFoilStatsFixtureParts(text);
  if(!p||!Number.isFinite(p.homeScore)||!Number.isFinite(p.awayScore)||p.homeScore===p.awayScore)return '';
  return p.homeScore>p.awayScore?p.home:p.away;
}
function tinFoilCertificateWinner(r){
  if(r){
    const hs=Number(r.home_score),as=Number(r.away_score);
    if(Number.isFinite(hs)&&Number.isFinite(as)){
      if(hs===as)return '';
      return (hs>as?String(r.home||''):String(r.away||'')).trim();
    }
  }
  if(typeof canonicalResultWinner==='function')return canonicalResultWinner(r)||'';
  return r&&r.winner?r.winner:'';
}
function tinFoilStatsDisplayClubKey(name){
  return String(name||'').toLowerCase().replace(/&/g,' and ').replace(/\b(association football club|football club|fc|afc|cfc)\b/g,' ').replace(/[^a-z0-9]+/g,' ').trim().replace(/\s+/g,' ');
}
function tinFoilStatsFixtureCount(text){
  const s=String(text||'').replace(/\s+/g,' ');
  const re=/(?:^|\s)([^|]{1,100}?)\s*\(\d+\)\s*v\s*\(\d+\)\s*([^|]{1,100}?)(?=$|\s{2,}|\n)/ig;
  let n=0; while(re.exec(s)&&n<3)n++; return n;
}
function tinFoilStatsLeafElements(root){
  if(!root||typeof root.querySelectorAll!=='function')return [];
  return [...root.querySelectorAll('*')].filter(e=>!e.children||e.children.length===0);
}
function tinFoilStatsRepairRenderedRow(row){
  if(!row)return false;
  const leaves=tinFoilStatsLeafElements(row);
  let fixtureLeaf=null,parts=null;
  for(const leaf of leaves){
    const p=tinFoilStatsFixtureParts(leaf.textContent||'');
    if(p){fixtureLeaf=leaf;parts=p;break;}
  }
  if(!fixtureLeaf||!parts||parts.homeScore===parts.awayScore)return false;
  const winner=parts.homeScore>parts.awayScore?parts.home:parts.away;
  const homeKey=tinFoilStatsDisplayClubKey(parts.home),awayKey=tinFoilStatsDisplayClubKey(parts.away);
  const candidates=leaves.filter(leaf=>{
    if(leaf===fixtureLeaf)return false;
    const k=tinFoilStatsDisplayClubKey(leaf.textContent||'');
    return k&&(k===homeKey||k===awayKey);
  });
  if(!candidates.length)return false;
  cons
```
