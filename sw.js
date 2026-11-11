/* Pizza Magna service worker: lets the installed game open without a connection.
   Network first, so every update shows up at once; the last copy fetched is kept for offline play.
   Only same-origin GET requests (the game's own files); analytics go straight to the network. */
const CACHE = 'pizza-magna-v1';
self.addEventListener('install', () => self.skipWaiting());
self.addEventListener('activate', e => e.waitUntil(self.clients.claim()));
self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET' || new URL(req.url).origin !== self.location.origin) return;
  e.respondWith(fetch(req).then(res => {
    if (res.ok) { const copy = res.clone(); caches.open(CACHE).then(c => c.put(req, copy)); }
    return res;
  }).catch(() => caches.match(req, {ignoreSearch: true})));
});
