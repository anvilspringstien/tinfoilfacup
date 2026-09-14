# Pigeon Miles At-a-Glance audit

READ ONLY. Production data unchanged.

## Current AT A GLANCE markup

```html
<section class="section"><div class="section-title">AT A GLANCE</div><div class="glance">'+
  '<div class="g"><div class="g-label">Rounds<br>Completed</div><div class="icon-circle"><img src="DATA_IMAGE_REDACTED" alt="Rounds Completed"></div><div class="g-num">'+rounds+'</div></div>'+
  '<div class="g"><div class="g-label">Matches<br>Played</div><div class="icon-circle"><img src="DATA_IMAGE_REDACTED" alt="Matches Played"></div><div class="g-num">'+matches+'</div></div>'+
  '<div class="g"><div class="g-label">Clubs<br>Encountered</div><div class="icon-circle"><img src="DATA_IMAGE_REDACTED" alt="Clubs Encountered"></div><div class="g-num">'+clubs.length+'</div></div>'+
  '<div class="g"><div class="g-label">Goals<br>Seen</div><div class="icon-circle"><img src="DATA_IMAGE_REDACTED" alt="Goals Seen"></div><div class="g-num">'+goals+'</div></div>'+
  '<div class="g"><div class="g-label">Grounds<br>Visited</div><div class="icon-circle"><img src="DATA_IMAGE_REDACTED" alt="Grounds Visited"></div><div class="g-num">'+grounds+'</div></div>'+
  /* TIN_FOIL_PIGEON_MILES_GLANCE */
  '<div class="g"><div class="g-label">Pigeon<br>Miles</div><div class="icon-circle" style="font-size:34px;line-height:1;display:flex;align-items:center;justify-content:center" aria-label="Pigeon Miles">🐦</div><div class="g-num">'+certEsc(pigeonMilesDisplay)+'</div></div>'+
  '</div></section>
```

## Current Pigeon Miles placement

```html
ass="g-num">'+grounds+'</div></div>'+
  /* TIN_FOIL_PIGEON_MILES_GLANCE */
  '<div class="g"><div class="g-label">Pigeon<br>Miles</div><div class="icon-circle" style="font-size:34px;line-height:1;display:flex;align-items:center;justify-content:center" aria-label="Pigeon Miles">🐦</div><div class="g-num">'+certEsc(pigeonMilesDisplay)+'</div></div>'+
  '</div></section>'+

  '<section class="section"><div class="section-title">THE JOURNEY SO FAR</div><div class="journey-head"><div>Round</div><div>Fixture</div><div>Date</div><div>Venue</div><div>Winner / Next Custodian</div></div>'+historyRows+'</section>'+

  '<section class="bottom"><div><div class="bt">STATISTICS</div><div class="list">• Home Games Played: '+homeGames+'<br>• Away Games Played: '+awayGames+'<br>• Wins by Current Custodian: '+custodianWins+'<br>• Draws: '+draws+'<br>• Defeats by Current Custodian: '+custodianDefeats+'<br>• Pigeon Miles Travelled: '+certEsc(pigeonMilesDisplay)+'</div></div>'+
  '<div class="next"><div class="bt">NEXT UP</div><div class="next-round">'+certEsc(nextRoundLabel)+'</div><div class="next-fixture">'+certEsc(nextTitle)+'</div><div class="next-meta">'+certEsc(nextDate)+(nextVenue?'<br>'+certEsc(nextVenue):'')+'</div>'+afterReplayHtml+'</div>'+
  '<div><div class="bt">NOTES</div><div class="notes">Pigeon Miles = twice the straight-line distance from your Campaign start postcode to each tie venue.</div></div></section>'+

  '<div class="motto"><span class="motto-star">★</span><span>The Journey Itself is The Source of Truth</span><span class="motto-star">★</span></div>'+
  '<div class="print"><button onclick="window.print()">Print / Save as PDF</button></div>'+
  '</main></body></html>';

  if(w){
    w.document.open();
    w.document.write(doc.replace("__LOGO__","DATA_IMAGE_REDACTED").replace("__CUP__","DATA_IMAGE_REDACTED"));
    w.document.close();
  }
}

async function go(){
 const input=document.getElementById('postcode'),btn=document.getElementById('findBtn'),status=document.getElementById('status'),results=document.getElementById('results');
 let pc=input.value.trim(),saved
```
