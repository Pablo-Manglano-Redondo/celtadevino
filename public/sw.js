// Service worker del Celta de Vino.
// - HTML, CSS y JS: primero la red (los datos de la liga cambian a diario) y, si no hay conexión,
//   la última copia guardada; si no hay copia de esa página, la página /offline.
// - Imágenes e iconos: la copia guardada al instante y se actualiza en segundo plano.
// - Vídeo y audio (peticiones por rangos) y otros orígenes: no se tocan.
// Al cambiar la lista de PRECACHE o la estrategia, sube VERSION para limpiar las cachés antiguas.
const VERSION = "v2";
const SHELL = "cdv-shell-" + VERSION;
const IMG = "cdv-img-" + VERSION;
const OFFLINE = "/offline";
const PRECACHE = [
  "/", OFFLINE, "/style.css", "/theme.js", "/app.js", "/goleadores.js", "/pwa.js", "/manifest.webmanifest",
  "/favicon.ico", "/icon-192.png", "/img/escudo.webp",
];

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(SHELL)
      .then((cache) => cache.addAll(PRECACHE.map((url) => new Request(url, { cache: "reload" }))))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((k) => k.startsWith("cdv-") && k !== SHELL && k !== IMG).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

// Solo se guardan respuestas completas (200) y sin redirecciones: una respuesta redirigida
// no se puede servir a una navegación.
const cacheable = (res) => res && res.ok && res.status === 200 && res.type === "basic" && !res.redirected;

async function networkFirst(event, isPage) {
  const { request } = event;
  const cache = await caches.open(SHELL);
  try {
    const res = await fetch(request);
    // Las páginas se guardan sin la query (?fbclid=…) para no acumular una copia por enlace.
    const key = isPage ? new URL(request.url).pathname : request;
    if (cacheable(res)) event.waitUntil(cache.put(key, res.clone()).catch(() => {}));
    return res;
  } catch (err) {
    const hit = await cache.match(request, { ignoreSearch: isPage });
    if (hit) return hit;
    if (isPage) return (await cache.match(OFFLINE)) || Response.error();
    throw err;
  }
}

async function staleWhileRevalidate(event) {
  const cache = await caches.open(IMG);
  const hit = await caches.match(event.request); // también las precargadas en SHELL
  const update = fetch(event.request).then((res) => {
    if (cacheable(res)) return cache.put(event.request, res.clone()).catch(() => {}).then(() => res);
    return res;
  });
  if (hit) {
    event.waitUntil(update.catch(() => {}));
    return hit;
  }
  return update;
}

self.addEventListener("fetch", (event) => {
  const { request } = event;
  if (request.method !== "GET" || request.headers.has("range")) return;
  const url = new URL(request.url);
  if (url.origin !== self.location.origin || url.pathname === "/sw.js") return;

  if (request.mode === "navigate") {
    event.respondWith(networkFirst(event, true));
  } else if (/\.(?:webp|png|jpe?g|gif|svg|ico)$/.test(url.pathname)) {
    event.respondWith(staleWhileRevalidate(event));
  } else if (/\.(?:css|js|webmanifest)$/.test(url.pathname)) {
    event.respondWith(networkFirst(event, false));
  }
  // El resto (vídeo, audio…) va directo a la red.
});
