(async function () {
  'use strict';

  const original = document.querySelector('.crest-compartment > .crest');
  if (!original || !CSS.supports('perspective', '170cqw') || !CSS.supports('transform-style', 'preserve-3d')) return;

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
  const planes = document.createElement('div');
  planes.className = 'floating-cup-planes';
  planes.append(...layers);
  view.append(planes);
  scene.append(view);
  original.classList.add('floating-cup-original');
  original.before(scene);

  let frame = 0;
  let x = 0, y = 0, targetX = 0, targetY = 0;

  function paint() {
    frame = 0;
    x += (targetX - x) * .25;
    y += (targetY - y) * .25;
    planes.style.setProperty('--view-x', x.toFixed(2) + 'deg');
    planes.style.setProperty('--view-y', y.toFixed(2) + 'deg');
    if (Math.abs(targetX - x) > .05 || Math.abs(targetY - y) > .05) {
      frame = requestAnimationFrame(paint);
    }
  }

  function aim(horizontal, vertical) {
    if (reduced.matches) return;
    scene.dataset.moving = '';
    targetX = Math.max(-16, Math.min(16, -vertical));
    targetY = Math.max(-16, Math.min(16, horizontal));
    if (!frame) frame = requestAnimationFrame(paint);
  }

  function showStatic() {
    cancelAnimationFrame(frame);
    frame = 0;
    x = y = targetX = targetY = 0;
    planes.style.removeProperty('--view-x');
    planes.style.removeProperty('--view-y');
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
