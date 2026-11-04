/* Card Cauldron demo service worker: network-first for the demo page, so a
   pushed demo update is never stuck behind an old cached page. Old caches
   (including the V2 playground cache) are deleted on activate. */
const CACHE = "ror-demo-oldplus-v1";
const FILES = ["./manifest.json", "./icon-192.png", "./icon-512.png"];
self.addEventListener("install", (e) => {
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(FILES)).then(() => self.skipWaiting()));
});
self.addEventListener("activate", (e) => {
  e.waitUntil(caches.keys().then((keys) => Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k)))).then(() => self.clients.claim()));
});
self.addEventListener("fetch", (e) => {
  if (e.request.method !== "GET") return;
  const url = new URL(e.request.url);
  const isPage = url.pathname.endsWith("/demo/") || url.pathname.endsWith("/demo/index.html") || url.pathname === "/demo";
  if (isPage) {
    e.respondWith(fetch(e.request).then((res) => { const c = res.clone(); caches.open(CACHE).then((cc) => cc.put(e.request, c)); return res; }).catch(() => caches.match(e.request, {ignoreSearch: true})));
  } else {
    e.respondWith(caches.match(e.request, {ignoreSearch: true}).then((hit) => hit || fetch(e.request)));
  }
});
