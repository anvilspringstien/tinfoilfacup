// Round before fitting the map or drawing its first leg so neither can
// recover the precise Home position from the exported image.
export function publicFlightStops(stops) {
  return stops.map(({lat, lon, short, next}, index) => index === 0
    ? {lat: Math.round(lat * 2) / 2, lon: Math.round(lon * 2) / 2, short: 'Home area', approximate: true}
    : {lat, lon, short, next});
}

export async function flightPathImage(svg) {
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
    canvas.height = 1240;
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
