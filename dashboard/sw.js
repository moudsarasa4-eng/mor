// Service worker mínimo de Electricista OS.
// - Cachea la "cáscara" (index + manifest + icono) para abrir sin conexión.
// - NUNCA cachea las respuestas de la API (datos con token): esas van siempre a la red.
// - Maneja el click en la notificación para enfocar la app.
const CACHE = "eos-shell-v1";
const SHELL = ["./", "./index.html", "./manifest.webmanifest", "./icon.svg"];
const API_RE = /\/(prospectos|trabajos|agenda|insumos|gastos-operativos|empresa|diagnostico|auth|salud)/;

self.addEventListener("install", (e) => {
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(SHELL)).catch(() => {}));
  self.skipWaiting();
});

self.addEventListener("activate", (e) => {
  e.waitUntil(caches.keys().then((ks) => Promise.all(ks.filter((k) => k !== CACHE).map((k) => caches.delete(k)))));
  self.clients.claim();
});

self.addEventListener("fetch", (e) => {
  if (e.request.method !== "GET") return;              // POST/PATCH -> red
  const url = new URL(e.request.url);
  if (API_RE.test(url.pathname)) return;               // datos de la API -> red (default)
  e.respondWith(
    caches.match(e.request).then((hit) =>
      hit || fetch(e.request).then((resp) => {
        const copy = resp.clone();
        caches.open(CACHE).then((c) => c.put(e.request, copy)).catch(() => {});
        return resp;
      }).catch(() => caches.match("./index.html"))
    )
  );
});

self.addEventListener("notificationclick", (e) => {
  e.notification.close();
  e.waitUntil(
    self.clients.matchAll({ type: "window" }).then((ws) => {
      for (const w of ws) { if ("focus" in w) return w.focus(); }
      if (self.clients.openWindow) return self.clients.openWindow("./");
    })
  );
});
