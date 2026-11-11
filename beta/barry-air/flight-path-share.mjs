// Round before fitting the map or drawing its first leg so neither can
// recover the precise Home position from the exported image.
export function publicFlightStops(stops) {
  return stops.map(({lat, lon, short, next}, index) => index === 0
    ? {lat: Number.isFinite(lat) ? Math.round(lat * 2) / 2 : lat, lon: Number.isFinite(lon) ? Math.round(lon * 2) / 2 : lon, short: 'Home area', approximate: true}
    : {lat, lon, short, next});
}

export async function flightPathImage(svg, attribution) {
  svg.setAttribute('width', '600');
  svg.setAttribute('height', '520');
  const style = document.createElementNS(svg.namespaceURI, 'style');
  style.textContent = `
    .land{fill:#eeeadd;stroke:#a9b3a1;stroke-width:.5;vector-effect:non-scaling-stroke}
    .gridline{fill:none;stroke:#5e8577;stroke-width:.5;opacity:.22}
    .region-label{fill:#597568;opacity:.6;font:10px Arial,sans-serif}
    .route-line{fill:none;stroke:#084c61;stroke-width:2.8;stroke-linecap:round;vector-effect:non-scaling-stroke}
    .future-line{stroke-dasharray:6 6}
    .hit,.halo{display:none}
    .point{fill:#084c61;stroke:#f4efdf;stroke-width:1.5;vector-effect:non-scaling-stroke}
    .future-point{fill:#f4efdf;stroke:#084c61}
    .home-area{fill:#084c6126;stroke:#084c61;stroke-width:1;stroke-dasharray:3 3;vector-effect:non-scaling-stroke}
    .stop-label{font:12px Arial,sans-serif;fill:#202f2b;paint-order:stroke;stroke:#eeeadd;stroke-linejoin:round}
  `;
  svg.prepend(style);

  const url = URL.createObjectURL(new Blob([new XMLSerializer().serializeToString(svg)], {type:'image/svg+xml'}));
  try {
    const map = new Image();
    map.src = url;
    await map.decode();

    const canvas = document.createElement('canvas');
    canvas.width = 1200;
    const attributionHeight = attribution ? 60 : 0;
    canvas.height = 1240 + attributionHeight * 2;
    const ctx = canvas.getContext('2d');
    if (!ctx) throw new Error('Image rendering is unavailable');
    ctx.scale(2, 2);
    ctx.fillStyle = '#084c61';
    ctx.fillRect(0, 0, 600, 46);
    ctx.fillStyle = '#f2eddd';
    ctx.font = 'bold 17px monospace';
    ctx.fillText('BARRY AIR', 18, 29);
    ctx.textAlign = 'right';
    ctx.fillText('THE FLIGHT PATH', 582, 29);
    ctx.textAlign = 'left';

    if (attribution) {
      const {name, callSign, milesFlown} = attribution;
      ctx.fillStyle = '#f2eddd';
      ctx.fillRect(0, 46, 600, attributionHeight);
      ctx.fillStyle = '#084c61';
      ctx.font = 'bold 21px Arial, sans-serif';
      ctx.fillText(name, 18, 71, 564);
      ctx.font = '15px Arial, sans-serif';
      const mileage = Number.isSafeInteger(milesFlown)
        ? new Intl.NumberFormat('en-GB').format(milesFlown) + ' miles flown'
        : 'Miles flown unavailable';
      ctx.fillText([callSign, mileage].filter(Boolean).join(' · '), 18, 92, 564);
      ctx.translate(0, attributionHeight);
    }

    ctx.fillStyle = '#dce5de';
    ctx.fillRect(0, 46, 600, 520);
    ctx.drawImage(map, 0, 46, 600, 520);
    ctx.fillStyle = '#084c61';
    ctx.font = 'bold 18px Arial, sans-serif';
    ctx.fillText('tinfoilfacup.com', 18, 548);
    ctx.fillStyle = '#f2eddd';
    ctx.fillRect(0, 566, 600, 54);
    ctx.fillStyle = '#335950';
    ctx.font = '13px Arial, sans-serif';
    ctx.strokeStyle = '#084c61';
    ctx.lineWidth = 2;
    for (const [x, label, dash] of [[18, 'Flown', []], [100, 'Next flight', [5, 4]]]) {
      ctx.setLineDash(dash);
      ctx.beginPath();
      ctx.moveTo(x, 586);
      ctx.lineTo(x + 22, 586);
      ctx.stroke();
      ctx.fillText(label, x + 29, 591);
    }
    ctx.font = '12px Arial, sans-serif';
    ctx.fillText('Map: Natural Earth', 18, 609);
    ctx.textAlign = 'right';
    ctx.fillText('Home area is approximate', 582, 609);
    return await new Promise((resolve, reject) => {
      canvas.toBlob(blob => blob ? resolve(blob) : reject(new Error('PNG encoding failed')), 'image/png');
    });
  } finally {
    URL.revokeObjectURL(url);
  }
}

const svgNS='http://www.w3.org/2000/svg';
function node(tag,attrs={},text){const e=document.createElementNS(svgNS,tag);for(const [k,v]of Object.entries(attrs))e.setAttribute(k,String(v));if(text!==undefined)e.textContent=text;return e;}
function projected(d){const k=(377.1-233.4)/(-1.557261+2.736535),merc=lat=>Math.log(Math.tan(Math.PI/4+lat*Math.PI/360))*180/Math.PI;return {x:377.1+(d.lon+1.557261)*k,y:175.6-(merc(d.lat)-merc(54.617311))*k};}
export function drawRoute(svg,stops,flights){
 svg.querySelectorAll('.route-line,[data-stop]').forEach(e=>e.remove());const outer=svg.querySelector('.map-content');const fit=node('g');while(outer.firstChild)fit.append(outer.firstChild);outer.append(fit);
 const located=stops.map((d,i)=>({...d,i})).filter(d=>Number.isFinite(d.lat)&&Number.isFinite(d.lon));if(!located.length)throw Error('Awaiting ground locations');const points=located.map(d=>({...d,...projected(d)}));const base=points.find(d=>d.i===0);let xs=points.map(p=>p.x),ys=points.map(p=>p.y),cx=(Math.min(...xs)+Math.max(...xs))/2,cy=(Math.min(...ys)+Math.max(...ys))/2;const scale=Math.min(440/Math.max(60,Math.max(...xs)-Math.min(...xs)),340/Math.max(60,Math.max(...ys)-Math.min(...ys)));fit.setAttribute('transform',`translate(${300-cx*scale} ${250-cy*scale}) scale(${scale})`);const stopsByIndex=new Map(points.map(p=>[p.i,{x:300+(p.x-cx)*scale,y:250+(p.y-cy)*scale}]));svg.setAttribute('tabindex','0');svg.setAttribute('aria-describedby','map-hint');
 // Trace the Campaign from ground to ground; mileage still counts home round trips.
 let previous=base;for(const flight of flights){const destination=points.find(p=>p.i===flight.stop);if(previous&&destination&&previous.i!==destination.i){fit.append(node('path',{class:'route-line'+(flight.status==='NEXT FLIGHT'?' future-line':''),'data-from':previous.i,'data-to':destination.i,d:`M${previous.x},${previous.y}L${destination.x},${destination.y}`}));}previous=destination;}
 for(const p of points){const g=node('g',{'data-stop':p.i,class:'map-stop',tabindex:0,role:'button','aria-label':p.short,transform:`translate(${p.x} ${p.y})`});g.append(node('circle',{class:'hit',r:22/scale}),node('circle',{class:'halo',r:15/scale}));
  g.append(node('circle',p.approximate?{class:'home-area',r:30/scale}:{class:'point'+(p.next?' future-point':''),r:6/scale}));const label=node('text',{class:'stop-label',x:(p.x>cx?-12:12)/scale,y:(p.i%2?-12:18)/scale,'text-anchor':p.x>cx?'end':'start','font-size':12/scale},p.short);if(p.i===0&&!p.approximate&&points.some(q=>q.i!==0&&Math.hypot(q.x-p.x,q.y-p.y)*scale<28))label.setAttribute('visibility','hidden');label.style.fontSize=12/scale+'px';label.style.strokeWidth=3/scale+'px';g.append(label);fit.append(g);}
 return {located,stopsByIndex};
}

export function saveBootRoomFlightPath(model) {
  const stops=publicFlightStops(model.stops).map(stop=>
    Number.isFinite(stop.lat)&&Number.isFinite(stop.lon) ? stop : null
  );
  const flights=model.flights.map(({stop,status})=>({stop,status}));
  const miles = model.miles?.miles;
  const key='tffc.barry.boot-flight.v1';
  if(!flights.some(flight=>stops[flight.stop])){
    localStorage.removeItem(key);
    return;
  }
  localStorage.setItem(key,JSON.stringify({
    identity:model.identity, callSign:'TF2AC '+model.digits, route:{stops,flights,...(Number.isFinite(miles)?{milesFlown:Math.round(miles)}:{})}
  }));
}

export async function bootRoomFlightImage({stops,flights,milesFlown}, author) {
  const response=await fetch(new URL('assets/route-map.svg',import.meta.url));
  if(!response.ok)throw new Error('Map unavailable');
  const svg=new DOMParser().parseFromString(await response.text(),'image/svg+xml').documentElement;
  if(svg.localName!=='svg')throw new Error('Map unavailable');
  drawRoute(svg,stops,flights);
  return flightPathImage(svg, author && {...author,milesFlown});
}
