// Use the live ticket's geometry and typography, with an explicit list of
// exportable fields. The private postcode is never sent to the canvas.
const postcode = /\b(?:GIR\s*0AA|[A-Z]{1,2}\d[A-Z\d]?\s*\d[A-Z]{2})\b/gi;
const checkedIn = "CHECKED IN · YOU'RE FLYING BARRY AIR - VERMIN FREE SINCE 2022";
const imageScale = 3;

export function boardingPassImage(pass, ground) {
  const bounds = pass.getBoundingClientRect();
  const scale = bounds.width / pass.offsetWidth;
  const width = pass.offsetWidth;
  const height = bounds.height / scale;
  const canvas = document.createElement('canvas');
  canvas.width = width * imageScale;
  canvas.height = Math.ceil(height * imageScale);
  const ctx = canvas.getContext('2d');
  if (!ctx) return Promise.reject(new Error('Image rendering is unavailable'));
  ctx.scale(imageScale, imageScale);

  function box(rect) {
    return {
      x: (rect.left - bounds.left) / scale,
      y: (rect.top - bounds.top) / scale,
      w: rect.width / scale,
      h: rect.height / scale
    };
  }

  function paintText(element, replacement, maxWidth) {
    const node = element.firstChild;
    const original = element.textContent;
    const safe = String(replacement ?? original).replace(postcode, '').trim();
    if (!safe || node?.nodeType !== Node.TEXT_NODE) return;
    const style = getComputedStyle(element);
    ctx.font = [style.fontWeight, style.fontSize, style.fontFamily].join(' ');
    ctx.fillStyle = style.color;
    ctx.letterSpacing = style.letterSpacing === 'normal' ? '0px' : style.letterSpacing;
    ctx.textBaseline = 'middle';

    const range = document.createRange();
    range.selectNodeContents(element);
    const rects = range.getClientRects();
    if (!rects.length) return;
    if (safe !== original || rects.length === 1) {
      const {x, y, h} = box(rects[0]);
      ctx.fillText(safe, x, y + h / 2, maxWidth ?? width - x - 12);
      return;
    }
    // Keep wraps at the same places as on the live ticket.
    let line;
    for (let i = 0; i < original.length; i++) {
      range.setStart(node, i);
      range.setEnd(node, i + 1);
      const rect = range.getBoundingClientRect();
      if (line?.rect.top === rect.top) {
        line.value += original[i];
        continue;
      }
      if (line) drawLine(line);
      line = {rect, value: original[i]};
    }
    if (line) drawLine(line);
  }

  function drawLine({rect, value}) {
    const {x, y, h} = box(rect);
    ctx.fillText(value, x, y + h / 2);
  }

  const ticketStyle = getComputedStyle(pass);
  const radius = parseFloat(ticketStyle.borderTopLeftRadius);
  ctx.save();
  ctx.beginPath();
  ctx.roundRect(0, 0, width, height, radius);
  ctx.clip();
  ctx.fillStyle = ticketStyle.backgroundColor;
  ctx.fillRect(0, 0, width, height);

  for (const selector of ['.pass-brand', '.boarding-stub']) {
    const element = pass.querySelector(selector);
    const {x, y, w, h} = box(element.getBoundingClientRect());
    ctx.fillStyle = getComputedStyle(element).backgroundColor;
    ctx.fillRect(x, y, w, h);
  }

  const stub = pass.querySelector('.boarding-stub');
  const stubStyle = getComputedStyle(stub);
  const tearY = box(stub.getBoundingClientRect()).y;
  ctx.strokeStyle = stubStyle.borderTopColor;
  ctx.setLineDash([3, 2]);
  ctx.beginPath();
  ctx.moveTo(0, tearY + .5);
  ctx.lineTo(width, tearY + .5);
  ctx.stroke();
  ctx.setLineDash([]);

  for (const element of pass.querySelectorAll(
    '.pass-brand span, .pass-passenger .label, #pigeon-name, #call-sign, ' +
    '.pass-metrics > div:last-child .label, #miles, #campaign-name, ' +
    '#next-heading, #next-fixture, #next-date, .boarding-stub .label, #flight-code'
  )) paintText(element);
  paintText(pass.querySelector('.pass-metrics > div:first-child .label'), 'DEPARTURE CODE');
  paintText(pass.querySelector('#departure-postcode'), 'F0O T1E');
  paintText(pass.querySelector('#next-venue'), ground ?? '');

  const checkbox = pass.querySelector('#check-in');
  const {x, y, w, h} = box(checkbox.getBoundingClientRect());
  ctx.fillStyle = getComputedStyle(checkbox).accentColor;
  ctx.beginPath();
  ctx.roundRect(x, y, w, h, 2);
  ctx.fill();
  ctx.strokeStyle = 'white';
  ctx.lineWidth = 1.6;
  ctx.lineCap = 'round';
  ctx.lineJoin = 'round';
  ctx.beginPath();
  ctx.moveTo(x + w * .24, y + h * .52);
  ctx.lineTo(x + w * .43, y + h * .71);
  ctx.lineTo(x + w * .77, y + h * .31);
  ctx.stroke();
  const checkLabel = pass.querySelector('#check-in-label');
  const checkX = box(checkLabel.getBoundingClientRect()).x;
  paintText(checkLabel, checkedIn, width - checkX - 12);

  ctx.lineWidth = 1;
  ctx.strokeStyle = ticketStyle.borderTopColor;
  ctx.beginPath();
  ctx.roundRect(.5, .5, width - 1, height - 1, radius);
  ctx.stroke();
  const notch = getComputedStyle(stub, '::before');
  const notchRadius = parseFloat(notch.width) / 2;
  const inset = parseFloat(notch.left) + notchRadius + parseFloat(stubStyle.borderLeftWidth) + 1;
  const notchY = tearY + parseFloat(stubStyle.borderTopWidth) + parseFloat(notch.top) + notchRadius;
  ctx.globalCompositeOperation = 'destination-out';
  for (const center of [inset, width - inset]) {
    ctx.beginPath();
    ctx.arc(center, notchY, notchRadius, 0, 2 * Math.PI);
    ctx.fill();
  }
  ctx.restore();

  return new Promise((resolve, reject) => {
    canvas.toBlob(blob => blob ? resolve(blob) : reject(new Error('PNG encoding failed')), 'image/png');
  });
}
