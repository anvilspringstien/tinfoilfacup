/* BETA-only, read-only custodian ground evidence adapter.
 * No app integration or promotion: callers must explicitly opt in during Shed testing.
 * The canonical journey determines custody; this module only describes an exact
 * official identity's pending home-ground evidence. Never use tie venues as homes.
 */
export function entrantIdentityKey(value) {
  let name = String(value ?? '').toLowerCase().replace(/&/g, ' and ');
  name = name.replace(/\b(association football club|football club)\b/g, ' ');
  name = name.replace(/[^a-z0-9]+/g, ' ').trim();
  name = name.replace(/\b(fc|cfc)\b/g, ' ').replace(/\bafc\s*$/g, ' ');
  return name.replace(/\s+/g, ' ').trim();
}

export function pendingCustodianGround(club, evidence) {
  const key = entrantIdentityKey(club);
  if (!key || !evidence || evidence.season !== '2026-27'
      || evidence.safety?.automated_ground_promotion !== false
      || evidence.safety?.verified_location_badge_authorized !== false)
    return null;
  const conflicts = evidence.unresolved_conflicts || [];
  if (conflicts.some(row => entrantIdentityKey(row.official_identity) === key))
    return null;
  const matches = (evidence.clubs || []).filter(
    row => entrantIdentityKey(row.official_identity) === key
  );
  if (matches.length !== 1) return null; // fail closed on ambiguous identities
  const row = matches[0];
  if (!['awaiting-coordinates-and-human-promotion', 'awaiting-human-promotion']
      .includes(row.review_status) || row.source_review !== 'official-ground-and-postcode-confirmed'
      || !row.ground || !row.postcode || !row.official_home_ground_source)
    return null;
  // No coordinates, distance, mileage, verified badge or asserted home-venue.
  return Object.freeze({
    club: row.official_identity,
    ground: row.ground,
    postcode: row.postcode,
    evidenceSource: row.official_home_ground_source,
    locationStatus: 'pending-human-review',
    verified: false,
    coordinates: null
  });
}
