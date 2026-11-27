(async function () {
  'use strict';

  const original = document.querySelector('.crest-compartment > .crest');
  if (!original || !CSS.supports('mask-image', 'url("disc.png")') || !CSS.supports('filter', 'drop-shadow(0 .5cqw .65cqw black)')) return;

  const shed = original.classList.contains('shed-astral-crest');
  if (shed && getComputedStyle(original).getPropertyValue('--shed-astral-styled').trim() !== '1') return;

  function wrap(className, ...children) {
    const element = document.createElement('div');
    element.className = className;
    element.append(...children);
    return element;
  }

  const scene = wrap('crest astral-portal');
  if (shed) scene.classList.add('astral-shed-scene');
  let art;
  let loadingArt;
  let showMotion = false;

  function updateArtwork() {
    const showLayers = Boolean(art && (!shed || showMotion));
    scene.classList.toggle('astral-layers-visible', showLayers);
    original.classList.toggle('astral-portal-ready', showLayers);
  }

  async function loadArtwork() {
    const crestAssets = 'assets/floating-cup/';
    const layers = [
      crestAssets + 'CREST_BASE_RING_IVORY.png',
      crestAssets + 'CREST_BASE_RING_INNER_WHITE.png',
      crestAssets + 'CREST_RINGS_PLUS_TEXT.png',
      crestAssets + 'ICONIC_CUP_TOP_LAYER.png',
      'assets/astral-portal/full-sky.webp',
    ].map(src => {
      const image = new Image();
      image.alt = '';
      image.src = src;
      return image;
    });
    try {
      await Promise.all(layers.map(image => image.decode()));
    } catch {
      return false;
    }

    const [ivory, , rings, cup, sky] = layers;
    art = wrap('astral-art',
      ivory,
      wrap('astral-opening', wrap('astral-plane', sky)),
      rings,
      wrap('astral-plane astral-near', cup));
    art.setAttribute('aria-hidden', 'true');
    scene.prepend(art);
    updateArtwork();
    return true;
  }

  if (!shed && !await loadArtwork()) return;
  original.before(scene);

  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  const orientation = window.DeviceOrientationEvent;
  const canTilt = window.isSecureContext && orientation && navigator.maxTouchPoints > 0;
  const zero = {x: 0, y: 0};
  let sample = zero;
  let filtered = zero;
  let reference = zero;
  let paintedX;
  let paintedY;
  let frame = 0;
  let lastFrame = 0;
  let neutral;
  let listening = false;
  let granted = false;
  let sensorTimeout;
  let button;
  let panel;
  let target;
  let dismiss;
  let status;

  function closePanel(focus = false) {
    if (!panel) return;
    panel.hidden = true;
    target.setAttribute('aria-expanded', 'false');
    if (focus) target.focus({preventScroll: true});
  }

  function follow(from, to, elapsed, timescale) {
    const weight = -Math.expm1(-elapsed / timescale);
    return {x: from.x + (to.x - from.x) * weight, y: from.y + (to.y - from.y) * weight};
  }

  function offset(value) {
    // A soft response to sensor noise with the same ±16° input cap as #751.
    // The output cap is ±1.5% of the crest width, one quarter of #751.
    const capped = Math.min(16, Math.abs(value));
    return -Math.sign(value) * .09375 * capped * (capped / (capped + .4)) * (16.4 / 16);
  }

  function paint(now) {
    const elapsed = Math.max(0, now - lastFrame);
    lastFrame = now;

    // Track the sample and the resting pose continuously. A held pose has
    // zero offset, with no timer-driven rebase or hard input threshold.
    filtered = follow(filtered, sample, elapsed, 45);
    reference = follow(reference, sample, elapsed, 400);
    const x = offset(filtered.x - reference.x).toFixed(3) + '%';
    const y = offset(filtered.y - reference.y).toFixed(3) + '%';
    if (x !== paintedX) scene.style.setProperty('--view-x', x);
    if (y !== paintedY) scene.style.setProperty('--view-y', y);
    paintedX = x;
    paintedY = y;

    // At this tolerance the remaining change is below 0.001px even at
    // tablet sizes. Leave the last paint in place when the scene is idle.
    const remaining = Math.hypot(sample.x - reference.x, sample.y - reference.y)
      + Math.hypot(sample.x - filtered.x, sample.y - filtered.y);
    frame = remaining > .005 ? requestAnimationFrame(paint) : 0;
  }

  function aim(x, y) {
    if (reduced.matches || document.hidden) return;
    if (sample.x === x && sample.y === y) return;
    sample = {x, y};
    if (shed && !showMotion) {
      showMotion = true;
      loadingArt ??= loadArtwork();
      updateArtwork();
    }
    if (!frame) {
      lastFrame = performance.now();
      frame = requestAnimationFrame(paint);
    }
  }

  function pause() {
    cancelAnimationFrame(frame);
    frame = 0;
    if (shed) {
      showMotion = false;
      updateArtwork();
    }
    sample = filtered = reference = zero;
    paintedX = paintedY = undefined;
    scene.style.removeProperty('--view-x');
    scene.style.removeProperty('--view-y');
  }

  function stop(label = 'Enable tilt') {
    clearTimeout(sensorTimeout);
    window.removeEventListener('deviceorientation', onTilt);
    listening = false;
    neutral = undefined;
    if (button) button.textContent = shed ? 'Enable crest motion' : label;
    if (dismiss) dismiss.textContent = 'Keep still';
    if (status) status.textContent = label === 'Tilt unavailable' ? 'Crest motion is unavailable.' : '';
    pause();
  }

  function onTilt(event) {
    if (document.hidden || !Number.isFinite(event.beta) || !Number.isFinite(event.gamma)) return;
    clearTimeout(sensorTimeout);
    const angle = screen.orientation?.angle ?? window.orientation ?? 0;
    if (!neutral || neutral.angle !== angle) {
      // Offset the new sensor coordinates so the current view survives a rebase.
      neutral = {beta: event.beta, gamma: event.gamma, angle, x: sample.x, y: sample.y};
      return;
    }
    const radians = angle * Math.PI / 180;
    const forward = ((event.beta - neutral.beta + 540) % 360) - 180;
    const sideways = event.gamma - neutral.gamma;
    aim(neutral.x + 1.35 * (sideways * Math.cos(radians) + forward * Math.sin(radians)),
      neutral.y + 1.35 * (forward * Math.cos(radians) - sideways * Math.sin(radians)));
  }

  if (canTilt) {
    button = document.createElement('button');
    button.type = 'button';
    button.textContent = shed ? 'Enable crest motion' : 'Enable tilt';
    button.addEventListener('click', async () => {
      if (listening) {
        stop();
        closePanel(true);
        return;
      }
      if (reduced.matches) return;
      button.disabled = true;
      if (status) status.textContent = '';
      try {
        if (!granted && typeof orientation.requestPermission === 'function') {
          granted = await orientation.requestPermission() === 'granted';
          if (!granted) {
            stop('Tilt blocked');
            if (status) status.textContent = 'Motion permission was declined. The crest will stay still.';
            return;
          }
        }
        if (reduced.matches || document.hidden) return;
        listening = true;
        button.textContent = shed ? 'Turn off crest motion' : 'Tilt off';
        if (dismiss) dismiss.textContent = 'Done';
        closePanel(true);
        window.addEventListener('deviceorientation', onTilt);
        sensorTimeout = setTimeout(() => stop('Tilt unavailable'), 2500);
      } catch {
        stop('Tilt unavailable');
      } finally {
        button.disabled = false;
      }
    });
    if (shed) {
      target = document.createElement('button');
      target.className = 'astral-motion-target';
      target.type = 'button';
      target.setAttribute('aria-label', 'Crest motion settings');
      target.setAttribute('aria-controls', 'astral-motion-panel');
      target.setAttribute('aria-expanded', 'false');

      dismiss = document.createElement('button');
      dismiss.type = 'button';
      dismiss.textContent = 'Keep still';
      dismiss.addEventListener('click', () => closePanel(true));
      status = document.createElement('p');
      status.setAttribute('role', 'status');
      panel = wrap('astral-motion-panel', button, dismiss, status);
      panel.id = 'astral-motion-panel';
      panel.setAttribute('role', 'group');
      panel.setAttribute('aria-label', 'Crest motion');
      panel.hidden = true;
      target.addEventListener('click', () => {
        if (!panel.hidden) {
          closePanel();
          return;
        }
        panel.hidden = false;
        target.setAttribute('aria-expanded', 'true');
        button.focus({preventScroll: true});
      });
      panel.addEventListener('keydown', event => {
        if (event.key === 'Escape') closePanel(true);
      });
      scene.append(target, panel);
    } else {
      button.className = 'astral-tilt';
      scene.append(button);
    }
  }

  original.parentElement.addEventListener('pointermove', event => {
    if (event.pointerType !== 'mouse' || listening || event.target === button || panel?.contains(event.target)) return;
    const rect = scene.getBoundingClientRect();
    if (event.clientX < rect.left || event.clientX > rect.right ||
        event.clientY < rect.top || event.clientY > rect.bottom) return;
    aim((event.clientX - rect.left - rect.width / 2) / rect.width * 32,
      (event.clientY - rect.top - rect.height / 2) / rect.height * 32);
  });

  reduced.addEventListener('change', () => {
    stop();
    closePanel();
  });
  document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
      neutral = undefined;
      pause();
    }
  });
})();
