/* Service worker di django-admin-mobile.
 *
 * Strategia: prima la rete, la cache solo come rete di salvataggio.
 * In un gestionale i dati vecchi fanno più danno della lentezza, quindi non
 * si serve mai una pagina dalla cache quando la rete risponde. La cache serve
 * a due cose sole: far partire l'app anche senza campo e mostrare una pagina
 * di cortesia invece dell'errore del browser.
 */
var CACHE = "{{ cache_name }}";
var OFFLINE = "{{ offline_url }}";
var STATIC_PREFIX = {{ static_url|safe }};

self.addEventListener("install", function (event) {
    event.waitUntil(
        caches.open(CACHE).then(function (cache) {
            return OFFLINE ? cache.add(OFFLINE) : null;
        }).catch(function () { /* senza rete l'installazione prosegue lo stesso */ })
    );
    self.skipWaiting();
});

self.addEventListener("activate", function (event) {
    event.waitUntil(
        caches.keys().then(function (names) {
            return Promise.all(names.map(function (name) {
                return name === CACHE ? null : caches.delete(name);
            }));
        }).then(function () { return self.clients.claim(); })
    );
});

self.addEventListener("fetch", function (event) {
    var request = event.request;
    if (request.method !== "GET") { return; }

    var url;
    try { url = new URL(request.url); } catch (e) { return; }
    if (url.origin !== self.location.origin) { return; }

    // File statici: rete, e copia in cache per quando la rete manca.
    if (STATIC_PREFIX && url.pathname.indexOf(STATIC_PREFIX) === 0) {
        event.respondWith(
            fetch(request).then(function (response) {
                if (response && response.ok) {
                    var copy = response.clone();
                    caches.open(CACHE).then(function (cache) { cache.put(request, copy); });
                }
                return response;
            }).catch(function () {
                return caches.match(request);
            })
        );
        return;
    }

    // Pagine: mai dalla cache. Senza rete si mostra la pagina di cortesia.
    if (request.mode === "navigate") {
        event.respondWith(
            fetch(request).catch(function () {
                return caches.match(OFFLINE).then(function (hit) {
                    return hit || new Response(
                        "Sei senza connessione.",
                        { status: 503, headers: { "Content-Type": "text/plain; charset=utf-8" } }
                    );
                });
            })
        );
    }
});
