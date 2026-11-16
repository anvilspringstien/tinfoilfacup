const postcode = /\b(?:GIR\s*0AA|[A-Z]{1,2}\d[A-Z\d]?\s*\d[A-Z]{2})\b/i;

export function validateFlightPath(path) {
  const invalid = () => { throw new Error('This Flight Path is unavailable. Reopen Barry Air to refresh it.'); };
  const {stops, flights, milesFlown} = path ?? {};
  if (!Array.isArray(stops) || stops.length > 32 || !Array.isArray(flights) ||
      flights.length < 1 || flights.length > 48) return invalid();
  const safeStops = stops.map((stop, index) => {
    if (stop === null) return null;
    const {lat, lon, short, next} = stop ?? {};
    if (!Number.isFinite(lat) || lat < 48 || lat > 62 ||
        !Number.isFinite(lon) || lon < -12 || lon > 4) return invalid();
    if (index === 0) return {
      lat: Math.round(lat * 2) / 2, lon: Math.round(lon * 2) / 2,
      short: 'Home area', approximate: true
    };
    if (typeof short !== 'string' || !short.trim() || short.length > 48 ||
        postcode.test(short) || /[\x00-\x1f\x7f]/.test(short)) return invalid();
    return {lat, lon, short, next: next === true};
  });
  const safeFlights = flights.map(flight => {
    const {stop, status} = flight ?? {};
    if (!Number.isInteger(stop) || stop < 1 || stop >= safeStops.length ||
        !['LANDED', 'NEXT FLIGHT'].includes(status)) return invalid();
    return {stop, status};
  });
  if (!safeFlights.some(flight => safeStops[flight.stop])) return invalid();
  return {stops: safeStops, flights: safeFlights,
    ...(Number.isSafeInteger(milesFlown) && milesFlown >= 0 && milesFlown <= 100000 ? {milesFlown} : {})};
}
