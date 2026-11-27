import {readFileSync} from 'node:fs';

export const acceptedSplash = readFileSync('beta/two-rooms-splash-iframe-proof.html', 'utf8')
  .replace('<title>Two rooms — Approved Master Splash</title>', '<title>Tin Foil FA Cup — BETA</title>')
  .replace('href="two-rooms-iframe-engine-proof.html"', 'href="clubfinder-journey.html"')
  .replace('</head>', '<script defer src="splash-campaign-label.js"></script></head>');
