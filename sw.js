// ©8x8 User Edition: versioned, public-only offline cache. No private/API/OAuth payloads.
const PREFIX = '8x8-user-edition-public-studio-';
const CACHE = PREFIX + 'v2';
const MIME = new Map([
  ['/', /^text\/html(?:;|$)/i],
  ['/v50.html', /^text\/html(?:;|$)/i],
  ['/icon.svg', /^image\/svg\+xml(?:;|$)/i],
  ['/manifest.webmanifest', /^application\/(?:manifest\+json|json)(?:;|$)/i],
  ['/studio/index.html', /^text\/html(?:;|$)/i],
  ['/observatory/index.html', /^text\/html(?:;|$)/i],
  ['/studio/media-core.mjs', /^(?:text|application)\/(?:javascript|ecmascript)(?:;|$)/i],
]);
const OFFLINE_NAV = new Map([
  ['/', '/'],
  ['/v50.html', '/v50.html'],
  ['/studio', '/studio/index.html'],
  ['/studio/', '/studio/index.html'],
  ['/studio/index.html', '/studio/index.html'],
  ['/observatory', '/observatory/index.html'],
  ['/observatory/', '/observatory/index.html'],
  ['/observatory/index.html', '/observatory/index.html'],
]);
function cacheable(path, response) {
  return !!response && response.ok && response.type === 'basic' &&
    !response.redirected && MIME.has(path) &&
    MIME.get(path).test(response.headers.get('content-type') || '');
}
self.addEventListener('install', event => event.waitUntil((async () => {
  const cache = await caches.open(CACHE);
  await Promise.all([...MIME.keys()].map(async path => {
    try {
      const response = await fetch(path, {cache:'reload', credentials:'omit', redirect:'error'});
      if (cacheable(path, response)) await cache.put(path, response);
    } catch { /* Missing or incorrect assets must not poison the offline cache. */ }
  }));
  await self.skipWaiting();
})()));
self.addEventListener('activate', event => event.waitUntil((async () => {
  const keys = await caches.keys();
  await Promise.all(keys.filter(key => key.startsWith(PREFIX) && key !== CACHE)
    .map(key => caches.delete(key)));
  await self.clients.claim();
})()));
self.addEventListener('fetch', event => {
  const req = event.request;
  const url = new URL(req.url);
  if (req.method !== 'GET' || url.origin !== self.location.origin) return;
  if (req.mode === 'navigate') {
    const offlinePath = OFFLINE_NAV.get(url.pathname);
    if (!offlinePath) return; // No fallback for authenticated or unknown routes.
    event.respondWith(fetch(req).catch(async () => {
      const cached = await caches.match(offlinePath, {cacheName:CACHE});
      return cached || Response.error();
    }));
    return;
  }
  if (url.search || !MIME.has(url.pathname)) return;
  event.respondWith((async () => {
    const cached = await caches.match(req, {cacheName:CACHE});
    if (cached && cacheable(url.pathname, cached)) return cached;
    const live = await fetch(req);
    // Never serve a same-origin HTML fallback as SVG, manifest or JavaScript.
    if (cacheable(url.pathname, live)) {
      const cache = await caches.open(CACHE);
      await cache.put(req, live.clone());
    }
    return live;
  })());
});
