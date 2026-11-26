(async function () {
  'use strict';

  const original = document.querySelector('.crest-compartment > .crest');
  if (!original || !CSS.supports('perspective', '170cqw') || !CSS.supports('perspective-origin', '50% 50%')) return;

  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  const orientation = window.DeviceOrientationEvent;
  const canTilt = window.isSecureContext && orientation && navigator.maxTouchPoints > 0;
  const filenames = [
    'CREST_BASE_RING_IVORY',
    'CREST_BASE_RING_INNER_WHITE',
    'CREST_RINGS_PLUS_TEXT',
    'ICONIC_CUP_TOP_LAYER',
  ];
  const layers = filenames.map(name => {
    const image = new Image();
    image.alt = '';
    image.src = 'assets/floating-cup/' + name + '.png';
    return image;
  });

  try {
    await Promise.all(layers.map(image => image.decode()));
  } catch {
    return; // Keep the approved crest if even one layer is missing.
  }

  const scene = document.createElement('div');
  scene.className = 'crest floating-cup';
  const view = document.createElement('div');
  view.className = 'floating-cup-view';
  view.setAttribute('aria-hidden', 'true');
  const [ivory, white, rings, cup] = layers;
  const cupDepth = document.createElement('div');
  cupDepth.className = 'floating-cup-depth';
  cupDepth.append(cup);
  view.append(ivory, white, rings, cupDepth);
  scene.append(view);
  original.classList.add('floating-cup-original');
  original.before(scene);

  // The artwork stays on its original depth plane. Shift the viewing centre
  // by at most 6% of the crest width, roughly a quarter of the previous travel.
  const viewpointOffset = value => Math.max(-16, Math.min(16, value)) * -.375;

  let frame = 0;
  let x = 0, y = 0, lastFrame = 0, lastMove = -Infinity;
  let sample = { x: 0, y: 0 };
  let reference = sample;

  function paint(now) {
    frame = 0;
    const moving = now - lastMove < 200;
    // A held pose becomes the neutral viewpoint. Small sensor jitter does not
    // restart the movement, and the camera eases to centre without overshoot.
    if (!moving) reference = sample;
    const targetX = viewpointOffset(sample.x - reference.x);
    const targetY = viewpointOffset(sample.y - reference.y);
    const follow = 1 - Math.exp(-Math.max(0, now - lastFrame) / 55);
    lastFrame = now;
    x += (targetX - x) * follow;
    y += (targetY - y) * follow;
    const settled = !moving && Math.hypot(x, y) < .02;
    if (settled) x = y = 0;
    cupDepth.style.setProperty('--view-x', x.toFixed(3) + '%');
    cupDepth.style.setProperty('--view-y', y.toFixed(3) + '%');
    if (!settled) frame = requestAnimationFrame(paint);
  }

  function aim(horizontal, vertical) {
    if (reduced.matches) return;
    scene.dataset.moving = '';
    if (Math.hypot(horizontal - sample.x, vertical - sample.y) < .25) return;
    sample = { x: horizontal, y: vertical };
    lastMove = performance.now();
    if (!frame) {
      lastFrame = lastMove;
      frame = requestAnimationFrame(paint);
    }
  }

  function showStatic() {
    cancelAnimationFrame(frame);
    frame = 0;
    x = y = 0;
    sample = reference = { x: 0, y: 0 };
    lastMove = -Infinity;
    cupDepth.style.removeProperty('--view-x');
    cupDepth.style.removeProperty('--view-y');
    delete scene.dataset.moving;
  }

  let listening = false;
  let neutral;
  let tiltButton;
  let waitingForSensor;
  let granted = false;

  function stopTilt(label = 'Enable tilt') {
    clearTimeout(waitingForSensor);
    window.removeEventListener('deviceorientation', onTilt);
    listening = false;
    neutral = undefined;
    if (tiltButton) {
      tiltButton.textContent = label;
    }
    showStatic();
  }

  function onTilt(event) {
    if (!Number.isFinite(event.beta) || !Number.isFinite(event.gamma)) return;
    clearTimeout(waitingForSensor);
    tiltButton.textContent = 'Tilt off';
    const angle = screen.orientation?.angle ?? window.orientation ?? 0;
    if (!neutral || neutral.angle !== angle) {
      neutral = { beta: event.beta, gamma: event.gamma, angle };
      showStatic();
      aim(0, 0);
      return;
    }
    const radians = angle * Math.PI / 180;
    const forward = ((event.beta - neutral.beta + 540) % 360) - 180;
    const sideways = event.gamma - neutral.gamma;
    const horizontal = sideways * Math.cos(radians) + forward * Math.sin(radians);
    const vertical = forward * Math.cos(radians) - sideways * Math.sin(radians);
    aim(horizontal * 1.35, vertical * 1.35);
  }

  if (canTilt) {
    tiltButton = document.createElement('button');
    tiltButton.className = 'floating-cup-tilt';
    tiltButton.type = 'button';
    tiltButton.textContent = 'Enable tilt';
    tiltButton.addEventListener('click', async () => {
      if (listening) {
        stopTilt();
        return;
      }
      if (reduced.matches) return;
      tiltButton.disabled = true;
      try {
        if (!granted && typeof orientation.requestPermission === 'function') {
          granted = await orientation.requestPermission() === 'granted';
          if (!granted) {
            stopTilt('Tilt blocked');
            return;
          }
        }
        if (reduced.matches || document.hidden) return;
        listening = true;
        tiltButton.textContent = 'Tilt off';
        window.addEventListener('deviceorientation', onTilt);
        waitingForSensor = setTimeout(() => stopTilt('Tilt unavailable'), 2500);
      } catch {
        stopTilt('Tilt unavailable');
      } finally {
        tiltButton.disabled = false;
      }
    });
    scene.append(tiltButton);
  }

  original.parentElement.addEventListener('pointermove', event => {
    if (event.pointerType !== 'mouse' || listening || event.target === tiltButton) return;
    const rect = scene.getBoundingClientRect();
    if (event.clientX < rect.left || event.clientX > rect.right ||
        event.clientY < rect.top || event.clientY > rect.bottom) {
      showStatic();
      return;
    }
    aim((event.clientX - rect.left - rect.width / 2) / rect.width * 32,
      (event.clientY - rect.top - rect.height / 2) / rect.height * 32);
  });
  original.parentElement.addEventListener('pointerleave', () => {
    if (!listening) showStatic();
  });

  reduced.addEventListener('change', () => stopTilt());
  document.addEventListener('visibilitychange', () => {
    if (document.hidden && listening) {
      neutral = undefined;
      showStatic();
    }
  });
})();
