// ©8x8 User Edition: safe static-only PWA cache. Never cache user media, OAuth, MCP, or APIs.
const CACHE='8x8-user-edition-public-studio-v1';
const ASSETS=['/','/v50.html','/icon.svg','/manifest.webmanifest','/studio/index.html','/studio/media-core.mjs'];
self.addEventListener('install',event=>event.waitUntil(caches.open(CACHE).then(async cache=>{
  await Promise.all(ASSETS.map(async path=>{try{const response=await fetch(path,{cache:'reload'});if(response.ok&&response.type==='basic')await cache.put(path,response);}catch{}}));
}).then(()=>self.skipWaiting())));
self.addEventListener('activate',event=>event.waitUntil(caches.keys().then(keys=>Promise.all(keys.filter(k=>k.startsWith('8x8-')&&k!==CACHE).map(k=>caches.delete(k)))).then(()=>self.clients.claim())));
self.addEventListener('fetch',event=>{
  const req=event.request,url=new URL(req.url);
  if(req.method!=='GET'||url.origin!==self.location.origin||url.pathname.startsWith('/api/')||url.pathname.startsWith('/mcp')||url.pathname.includes('oauth'))return;
  if(req.mode==='navigate'){
    event.respondWith(fetch(req).catch(async()=>await caches.match(url.pathname)||await caches.match('/')));
    return;
  }
  if(!ASSETS.includes(url.pathname))return;
  event.respondWith(caches.match(url.pathname).then(hit=>hit||fetch(req)));
});
