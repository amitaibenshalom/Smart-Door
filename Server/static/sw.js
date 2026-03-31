const CACHE_NAME = 'cache-v1';

// Install event - just caches the offline fallback if we had one
self.addEventListener('install', (event) => {
    self.skipWaiting();
});

// Fetch event - always try the network first so your door data is live!
self.addEventListener('fetch', (event) => {
    event.respondWith(
        fetch(event.request).catch(() => {
            return new Response('Door monitor is completely offline. Check Pi WiFi.');
        })
    );
});