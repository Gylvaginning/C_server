self.addEventListener('install', function(event) {
	event.waitUntil(
		caches.open('mellomlager').then( function (cache) {
			return cache.addAll([
				'./webklientajax.html',
				'./index.html',
				'./honolulu.jpg',
				'./innlogging.xsd',
				'./hentdikt.xsd',
				'./serviceworker.js'
			
			]);
		})
	);
});

self.addEventListener('fetch', function (event) {
	event.respondWith(
		caches.match(event.request)
	);
});

self.addEventListener('click', function(event) {
	event.respondWith(
		caches.match(event.request)
	);
});
