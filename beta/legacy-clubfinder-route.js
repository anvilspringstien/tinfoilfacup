// Keep bookmarked Clubfinder and Stats URLs on the current Campaign app.
(() => {
  const current = new URL(window.location.href);
  const stats = current.searchParams.get('stats') === '1';
  const destination = new URL(stats ? 'beta/clubfinder-beta.html' : 'beta/phone-frame.html', current);
  destination.search = current.search;
  destination.hash = current.hash;
  if (!stats) destination.searchParams.set('view', 'campaign');
  window.location.replace(destination.href);
})();
