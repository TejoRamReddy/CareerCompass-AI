/* CareerCompass service worker.

   Caches the app shell so the pages open instantly on a slow connection and the
   site can be installed to a phone's home screen. It NEVER caches /api/ calls:
   interviews, results and dashboards always go to the server, so nobody sees
   stale results or someone else's data.

   Bump CACHE when shipping changes so old files are dropped. */

const CACHE = 'careercompass-shell-v1';
const SHELL = [
  './', 'index.html', 'demo.html', 'login.html', 'dashboard.html', 'share.html',
  'css/style.css', 'css/demo.css', 'css/app.css',
  'js/config.js', 'js/i18n.js', 'js/api.js', 'js/demo.js', 'js/auth.js',
  'js/dashboard.js', 'js/share.js', 'js/main.js', 'js/pwa.js',
  'assets/icon-192.png', 'manifest.webmanifest',
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE)
      // One missing file must not stop the whole install.
      .then((cache) => Promise.all(SHELL.map((url) => cache.add(url).catch(() => null))))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (event) => {
  const req = event.request;
  if (req.method !== 'GET') return;

  const url = new URL(req.url);
  if (url.origin !== self.location.origin) return;   // API on another origin, fonts: leave alone
  if (url.pathname.startsWith('/api/')) return;      // same-origin API: never cache

  // Network first, so a redeploy shows up immediately; cache is the offline fallback.
  event.respondWith(
    fetch(req)
      .then((res) => {
        if (res.ok) {
          const copy = res.clone();
          caches.open(CACHE).then((cache) => cache.put(req, copy));
        }
        return res;
      })
      .catch(() => caches.match(req).then((hit) => hit || caches.match('index.html')))
  );
});
