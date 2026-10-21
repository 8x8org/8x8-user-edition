import test from 'node:test';
import assert from 'node:assert/strict';
import vm from 'node:vm';
import { readFileSync, existsSync } from 'node:fs';
const text = (p) => readFileSync(new URL('../' + p, import.meta.url),'utf8');
const page = text('atlas/index.html');
const src = text('atlas/one-fabric-public-catalog-v1.js');
const world = {};
vm.runInNewContext(src, world, {timeout: 2000});
const catalog = world.EIGHTX8_PUBLIC_CATALOG;
test('unified catalog has one root and unique module identities',()=>{
  assert.equal(catalog.canonicalRoot,'fabric://8x8/core');
  assert.equal(catalog.classification,'PUBLIC_PROJECTION_NOT_LIVE_INTEGRATION');
  assert.ok(catalog.modules.length >= 20);
  assert.equal(new Set(catalog.modules.map(x => x.id)).size,catalog.modules.length);
  assert.equal(new Set(catalog.skills.map(x => x.id)).size,catalog.skills.length);
});
test('real source routes have corresponding public pages, no invented provider endpoints',()=>{
 const existing = new Map([['/','v50.html'],['/atlas','atlas/index.html'],['/studio','studio/index.html'],['/observatory','observatory/index.html'],['/agents','agents/index.html'],['/world','stable/index.html'],['/telegram','telegram/index.html'],['/android','android/index.html'],['/presale','presale/index.html'],['/projects','projects/index.html']]);
 for(const m of catalog.modules){
   if(m.route){assert.ok(existing.has(m.route),m.route);assert.ok(existsSync(new URL('../'+existing.get(m.route),import.meta.url)),m.route)}
   else assert.ok(m.state !== 'LIVE',m.id);
 }
});
test('public source skills exist but never claim ChatGPT installation',()=>{
 for(const s of catalog.skills) {
   assert.ok(existsSync(new URL('../'+s.path,import.meta.url)),s.id);
   assert.equal(s.state,'SOURCE_ONLY');
 }
 assert.match(text('skills/one-fabric-unified-navigation/SKILL.md'),/source definition/);
});
test('public catalog and screen explicitly distinguish source from runtime',()=>{
 assert.match(page,/One Fabric · All-in-One Directory/);
 assert.match(page,/one-fabric-public-catalog-v1.js/);
 assert.match(page,/id="hub-filter"/);
 assert.match(page,/id="hub-modules"/);
 assert.match(page,/id="hub-skills"/);
 assert.match(page,/MCP and skills|MCP/);
 assert.match(page,/not operational merely because/i);
 assert.ok(!src.includes('fetch('));
 assert.ok(!src.includes('getUserMedia('));
 for(const x of ['BEGIN PRIVATE KEY','OWNER_ROOT','127.0.0.1','api_key=','SIGNING_STORE_PASSWORD'])assert.ok(!src.includes(x),x);
});
test('offline Android assets ship one unified catalog',()=>{
 const g=text('android-app/app/build.gradle');
 const build=text('scripts/build-vercel-static.mjs');
 assert.match(g,/assets.srcDir/);
 assert.match(build,/'atlas'/);
 const m=text('android-app/app/src/main/java/world/eightx8/user/PublicAssetHandler.java');
 assert.match(m,/case "atlas"/);
 assert.match(m,/application\/javascript/);
});

test('the public MCP metadata is derived from the same source and is not callable authority',()=>{
 const build=text('scripts/build-vercel-static.mjs');
 const routes=text('vercel.json');
 const handler=text('android-app/app/src/main/java/world/eightx8/user/PublicAssetHandler.java');
 assert.match(build,/mcp\/one-fabric-capability-catalog-v1.json/);
 assert.match(build,/runInNewContext/);
 assert.match(routes,/\"source\": \"\/mcp\/catalog\"/);
 assert.match(handler,/case \"mcp\/catalog\"/);
 assert.equal(catalog.classification,'PUBLIC_PROJECTION_NOT_LIVE_INTEGRATION');
});
