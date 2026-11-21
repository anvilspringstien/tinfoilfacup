/* Standalone opt-in Shed diagnostic. Never imported into campaign/Clubfinder.
 * Only reads a JSON document. No local/session storage writes, mileage, custody,
 * verification, map navigation or mutation. Errors fail closed.
 */
import {pendingCustodianGround} from './entrant-ground-evidence.mjs';

const form = document.querySelector('#lookup');
const input = document.querySelector('#club');
const button = document.querySelector('#inspect');
const result = document.querySelector('#result');
let evidence = null;
function line(parent, label, value) {
  const p = document.createElement('p');
  const strong = document.createElement('strong');
  strong.textContent = label + ': ';
  p.append(strong, document.createTextNode(value));
  parent.appendChild(p);
}
function message(value) {
  result.replaceChildren();
  const p = document.createElement('p');
  p.textContent = value;
  result.appendChild(p);
}
async function loadEvidence() {
  try {
    const response = await fetch('../updater/entrant-home-ground-evidence-2026.json',
      {cache: 'no-store', credentials: 'same-origin'});
    if (!response.ok) throw new Error('evidence unavailable');
    const parsed = await response.json();
    if (parsed?.season !== '2026-27' || parsed?.safety?.automated_ground_promotion !== false ||
        parsed?.safety?.verified_location_badge_authorized !== false ||
        !Array.isArray(parsed.clubs)) throw new Error('invalid safety policy');
    evidence = parsed;
    button.disabled = false;
    message('Evidence loaded. Enter an exact club name to inspect its pending record.');
  } catch {
    evidence = null;
    button.disabled = true;
    message('Evidence not available for this deployment. No location is shown or promoted.');
  }
}
form.addEventListener('submit', event => {
  event.preventDefault();
  if (!evidence) return message('Evidence unavailable. No lookup performed.');
  const row = pendingCustodianGround(input.value, evidence);
  if (!row) return message('No unambiguous pending ground evidence for that identity.');
  result.replaceChildren();
  line(result, 'Official identity', row.club);
  line(result, 'Staged ground', row.ground);
  line(result, 'Staged postcode', row.postcode);
  line(result, 'Location status', 'Pending human review — NOT VERIFIED');
  const p = document.createElement('p');
  const a = document.createElement('a');
  a.href = row.evidenceSource;
  a.target = '_blank';
  a.rel = 'noopener noreferrer';
  a.textContent = 'Review independent source';
  p.appendChild(a);
  result.appendChild(p);
});
loadEvidence();
