const CACHE_NAME = 'cartolandia-cache-v2';

// Arquivos básicos que o app vai salvar no celular do usuário
const urlsToCache = [
  '/',
  '/static/manifest.json',
  '/static/media/logo.png',
  'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css',
  'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css',
  '/carreira/dashboard/'
];

// Instalação: salva os arquivos no cache (falha de um arquivo não impede a instalação)
self.addEventListener('install', event => {
  self.skipWaiting();
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache =>
      Promise.all(urlsToCache.map(url => cache.add(url).catch(() => null)))
    )
  );
});

// Ativação: limpa caches antigos e assume o controle das abas abertas
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(nomes => Promise.all(
      nomes.filter(n => n !== CACHE_NAME).map(n => caches.delete(n))
    )).then(() => self.clients.claim())
  );
});

// Rede primeiro; se estiver offline, tenta o cache
self.addEventListener('fetch', event => {
  if (event.request.method !== 'GET') return;
  event.respondWith(fetch(event.request).catch(() => caches.match(event.request)));
});

// ---------- Notificações push ----------
self.addEventListener('push', event => {
  let dados = {};
  try { dados = event.data ? event.data.json() : {}; } catch (e) { dados = { titulo: 'Cartolândia', texto: event.data ? event.data.text() : '' }; }
  const titulo = dados.titulo || 'Cartolândia';
  event.waitUntil(self.registration.showNotification(titulo, {
    body: dados.texto || '',
    icon: '/static/media/logo.png',
    badge: '/static/media/logo.png',
    tag: dados.tag || 'cartolandia',
    renotify: true,
    data: { url: dados.url || '/' },
  }));
});

self.addEventListener('notificationclick', event => {
  event.notification.close();
  const destino = (event.notification.data && event.notification.data.url) || '/';
  event.waitUntil(
    self.clients.matchAll({ type: 'window', includeUncontrolled: true }).then(janelas => {
      for (const j of janelas) {
        if ('focus' in j) { j.navigate(destino); return j.focus(); }
      }
      return self.clients.openWindow(destino);
    })
  );
});
