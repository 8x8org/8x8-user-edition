import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import vm from 'node:vm';

const source = readFileSync(new URL('../sw.js', import.meta.url), 'utf8');
function fixture() {
  const events = new Map();
  const stored = new Map();
  const deleted = [];
  let claimed = false;
  const good = (type, {redirected=false, status=true}={}) => ({
    ok:status, type:'basic', redirected, headers:{get: name => name.toLowerCase()==='content-type' ? type : null},
    clone() { return this; }
  });
  const cache = {put:async(key,value)=>stored.set(typeof key==='string'?key:key.url,value)};
  const context = vm.createContext({
    URL,
    Response:{error:()=>({offline:true})},
    fetch: async target => {
      const path=typeof target==='string'?target:new URL(target.url).pathname;
      return good(path==='/icon.svg'?'text/html; charset=utf-8':
        path.endsWith('.mjs')?'text/javascript':path.endsWith('.webmanifest')?'application/manifest+json':'text/html');
    },
    caches:{
      open:async()=>cache,
      match:async(key)=>stored.get(typeof key==='string'?key:key.url),
      keys:async()=>['8x8-user-edition-public-studio-v1','8x8-sibling-cache'],
      delete:async key => {deleted.push(key);return true;}
    },
    self:{
      location:{origin:'https://8x8.example'},
      addEventListener:(name,cb)=>events.set(name,cb),
      skipWaiting:async()=>{},
      clients:{claim:async()=>{claimed=true;}}
    }
  });
  vm.runInContext(source,context,{filename:'sw.js'});
  return {context,events,stored,deleted,good,claimed:()=>claimed};
}
test('asset cache rejects HTML returned for SVG and redirected or opaque responses',()=>{
  const {context,good}=fixture();
  const accept=vm.runInContext('cacheable',context);
  assert.equal(accept('/icon.svg',good('text/html')),false);
  assert.equal(accept('/icon.svg',good('image/svg+xml; charset=utf-8')),true);
  assert.equal(accept('/icon.svg',good('image/svg+xml',{redirected:true})),false);
  assert.equal(accept('/icon.svg',{...good('image/svg+xml'),type:'opaque'}),false);
  assert.equal(accept('/studio/media-core.mjs',good('text/html')),false);
  assert.equal(accept('/studio/media-core.mjs',good('text/javascript')),true);
});
test('install does not cache invalid SVG even if host reports HTTP 200',async()=>{
  const f=fixture();let work;
  f.events.get('install')({waitUntil:promise=>{work=promise;}});
  await work;
  assert.equal(f.stored.has('/icon.svg'),false);
  assert.equal(f.stored.has('/studio/media-core.mjs'),true);
});
test('activation only evicts this public cache family',async()=>{
  const f=fixture();let work;
  f.events.get('activate')({waitUntil:promise=>{work=promise;}});
  await work;
  assert.deepEqual(f.deleted,['8x8-user-edition-public-studio-v1']);
  assert.equal(f.claimed(),true);
});
test('private and unknown navigation routes are never given offline public HTML',()=>{
  const f=fixture();let responded=false;
  const request=path=>({
    request:{url:'https://8x8.example'+path,method:'GET',mode:'navigate'},
    respondWith:()=>{responded=true;}
  });
  f.events.get('fetch')(request('/oauth/callback'));
  f.events.get('fetch')(request('/api/account'));
  assert.equal(responded,false);
  f.events.get('fetch')(request('/studio'));
  assert.equal(responded,true);
});
