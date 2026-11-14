const WIDTH = 790;
const HEIGHT = 1118;
const MARGIN = 32;
const RED = '#b90000';
const PAPER = '#fffdf1';

export async function statsSharePdf(sheet) {
  const text = selector => sheet.querySelector(selector)?.innerText.trim() || '';
  const images = [...sheet.querySelectorAll('.top img, .glance img')];
  await Promise.allSettled(images.map(image => image.decode()));
  const pages = [];
  let context, y;
  function page() {
    const canvas = sheet.ownerDocument.createElement('canvas');
    canvas.width = WIDTH * 2;
    canvas.height = HEIGHT * 2;
    context = canvas.getContext('2d');
    context.scale(2, 2);
    context.fillStyle = PAPER;
    context.fillRect(0, 0, WIDTH, HEIGHT);
    context.strokeStyle = RED;
    context.lineWidth = 4;
    context.strokeRect(10, 10, WIDTH - 20, HEIGHT - 20);
    pages.push(canvas);
    y = MARGIN;
  }
  function label(value, x, top, size, color = '#161514', bold = false, align = 'left') {
    context.font = (bold ? 'bold ' : '') + size + 'px Arial, sans-serif';
    context.fillStyle = color;
    context.textAlign = align;
    context.textBaseline = 'top';
    context.fillText(value, x, top);
  }
  function wrap(value, width, size) {
    context.font = size + 'px Arial, sans-serif';
    return value.split('\n').flatMap(line => {
      const output = [];
      let buffer = '';
      for (const word of line.split(/\s+/)) {
        const next = buffer ? buffer + ' ' + word : word;
        if (buffer && context.measureText(next).width > width) {
          output.push(buffer);
          buffer = word;
        } else buffer = next;
      }
      output.push(buffer);
      return output;
    });
  }
  function rule(top) {
    context.fillStyle = RED;
    context.fillRect(MARGIN, top, WIDTH - 2 * MARGIN, 1);
  }
  function heading(value) {
    rule(y);
    y += 12;
    label(value, WIDTH / 2, y, 23, RED, true, 'center');
    y += 35;
  }
  function art(image, x, top, size) {
    if (image?.naturalWidth) context.drawImage(image, x, top, size, size);
  }
  function block(value, size = 16) {
    for (const line of wrap(value, WIDTH - 2 * MARGIN, size)) {
      if (y + size + 5 > HEIGHT - MARGIN) page();
      label(line, MARGIN, y, size);
      y += size + 5;
    }
    y += 10;
  }

  page();
  label('STATS', MARGIN, y, 84, '#161514', true);
  art(images[0], WIDTH - MARGIN - 155, y, 155);
  label(text('.season'), WIDTH - MARGIN - 77, y + 166, 25, RED, true, 'center');
  y += 88;
  label(text('.sub'), MARGIN, y, 21, RED, true);
  y += 35;
  for (const club of sheet.querySelectorAll('.top-left .club')) {
    label(club.previousElementSibling.innerText, MARGIN, y, 14, RED, true);
    y += 20;
    for (const line of wrap(club.innerText, WIDTH - 2 * MARGIN - 175, 22)) {
      label(line, MARGIN, y, 22, '#161514', true);
      y += 26;
    }
    y += 8;
  }
  const identity = sheet.querySelector('.campaign-identity-band');
  if (identity) {
    rule(y);
    y += 10;
    block(identity.querySelector('.campaign-identity-label').innerText + ' ' +
      identity.querySelector('.campaign-identity-value').innerText, 14);
    const pigeon = identity.querySelector('input');
    if (pigeon?.value) block('PIGEON NAME: ' + pigeon.value, 14);
  }
  heading('AT A GLANCE');
  const cells = [...sheet.querySelectorAll('.glance .g')];
  const cellWidth = (WIDTH - 2 * MARGIN) / cells.length;
  cells.forEach((cell, index) => {
    const center = MARGIN + cellWidth * (index + .5);
    const lines = wrap(cell.querySelector('.g-label').innerText, cellWidth - 8, 12);
    lines.forEach((line, row) => label(line.toUpperCase(), center, y + row * 15, 12, '#161514', true, 'center'));
    art(cell.querySelector('img'), center - 25, y + 34, 50);
    label(cell.querySelector('.g-num').innerText, center, y + 91, 22, '#161514', true, 'center');
  });
  y += 123;

  const widths = [116, 190, 91, 161, 168];
  function fixturesHeading(value) {
    heading(value);
    let x = MARGIN;
    [...sheet.querySelectorAll('.journey-head > div')].forEach((cell, index) => {
      label(cell.textContent, x, y, 12, RED, true);
      x += widths[index];
    });
    y += 24;
  }
  fixturesHeading('THE CAMPAIGN SO FAR');
  if (text('.journey-empty')) block(text('.journey-empty'));
  for (const row of sheet.querySelectorAll('.journey-row')) {
    const cells = [...row.children].map((cell, index) => wrap(cell.innerText, widths[index] - 9, 14));
    const height = Math.max(...cells.map(lines => lines.length)) * 18 + 12;
    if (y + height > HEIGHT - MARGIN) {
      page();
      fixturesHeading('THE CAMPAIGN SO FAR');
    }
    let x = MARGIN;
    cells.forEach((lines, index) => {
      lines.forEach((line, lineIndex) => label(line, x, y + lineIndex * 18, 14, index === 4 ? RED : '#161514'));
      x += widths[index];
    });
    y += height - 5;
    rule(y);
    y += 5;
  }
  for (const section of sheet.querySelectorAll('.challenge-honours, .bottom > div')) {
    const title = section.querySelector('.section-title,.bt');
    if (!title) continue;
    if (y + 100 > HEIGHT - MARGIN) page();
    heading(title.innerText);
    for (const item of [...section.children].filter(child => child !== title)) {
      block(item.innerText);
    }
  }
  block(text('.motto'));
  return encodePdf(pages);
}

async function encodePdf(pages) {
  const encoder = new TextEncoder();
  const chunks = [];
  const offsets = [0];
  let length = 0;
  function append(value) {
    const bytes = typeof value === 'string' ? encoder.encode(value) : value;
    chunks.push(bytes);
    length += bytes.byteLength;
  }
  function object(number, body, bytes) {
    offsets[number] = length;
    append(number + ' 0 obj\n' + body);
    if (bytes) {
      append('\nstream\n');
      append(bytes);
      append('\nendstream');
    }
    append('\nendobj\n');
  }
  append('%PDF-1.4\n');
  object(1, '<< /Type /Catalog /Pages 2 0 R >>');
  const kids = pages.map((_, index) => (3 + index * 3) + ' 0 R').join(' ');
  object(2, '<< /Type /Pages /Count ' + pages.length + ' /Kids [' + kids + '] >>');
  for (const [index, canvas] of pages.entries()) {
    const number = 3 + index * 3;
    const blob = await new Promise(resolve => canvas.toBlob(resolve, 'image/jpeg', .94));
    if (!blob) throw new Error('Could not encode Stats page');
    const jpeg = new Uint8Array(await blob.arrayBuffer());
    canvas.width = canvas.height = 0;
    object(number, '<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /XObject << /PageImage ' +
      (number + 2) + ' 0 R >> >> /Contents ' + (number + 1) + ' 0 R >>');
    const content = encoder.encode('q 595 0 0 842 0 0 cm /PageImage Do Q');
    object(number + 1, '<< /Length ' + content.length + ' >>', content);
    object(number + 2, '<< /Type /XObject /Subtype /Image /Width ' + WIDTH * 2 + ' /Height ' + HEIGHT * 2 +
      ' /ColorSpace /DeviceRGB /BitsPerComponent 8 /Filter /DCTDecode /Length ' + jpeg.length + ' >>', jpeg);
  }
  const xref = length;
  append('xref\n0 ' + offsets.length + '\n0000000000 65535 f \n');
  for (const offset of offsets.slice(1)) append(String(offset).padStart(10, '0') + ' 00000 n \n');
  append('trailer\n<< /Size ' + offsets.length + ' /Root 1 0 R >>\nstartxref\n' + xref + '\n%%EOF\n');
  return new File(chunks, 'tin-foil-fa-cup-stats.pdf', {type: 'application/pdf'});
}
