import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync,existsSync} from 'node:fs';
import {createHash} from 'node:crypto';
const read=path=>readFileSync(new URL('../'+path,import.meta.url),'utf8');
const exists=path=>existsSync(new URL('../'+path,import.meta.url));
const config=JSON.parse(read('vercel.json'));
const rewrites=new Map(config.rewrites.map(r=>[r.source,r.destination]));
const expected=new Map([
  ['/','/v50.html'],
  ['/studio','/studio/index.html'],
  ['/agents','/agents/index.html'],
  ['/atlas','/atlas/index.html'],
  ['/observatory','/observatory/index.html'],
  ['/mcp/catalog','/mcp/one-fabric-capability-catalog-v1.json'],
  ['/projects/world-atlas/','/projects/world-atlas/index.html'],
  ['/r3','/index.html']
]);
test('preserved original release routes, without changing protected rollback',()=>{
  assert.equal(new Set(config.rewrites.map(x=>x.source)).size,config.rewrites.length);
  for(const [route,destination] of expected) assert.equal(rewrites.get(route),destination,route);
  assert.equal(config.outputDirectory,'dist');
  assert.equal(config.buildCommand,'npm run build:vercel');
});
test('static build actually contains original distinct Studio, Agent Room and World pages',()=>{
  const pagePaths=['dist/v50.html','dist/studio/index.html','dist/agents/index.html',
    'dist/atlas/index.html','dist/observatory/index.html','dist/projects/world-atlas/index.html'];
  for(const path of pagePaths)assert.ok(exists(path),'missing: '+path);
  const hashes=pagePaths.map(p=>createHash('sha256').update(read(p)).digest('hex'));
  assert.equal(new Set(hashes).size,hashes.length,'distinct routes must not be the same fallback page');
  assert.match(read('dist/studio/index.html'),/8x8 Studio/i);
  assert.match(read('dist/agents/index.html'),/Agent Room/i);
  assert.match(read('dist/projects/world-atlas/index.html'),/64/);
});
test('MCP catalog is public source metadata only; no tool authorization is inferred',()=>{
  const p='dist/mcp/one-fabric-capability-catalog-v1.json';
  assert.ok(exists(p),'Missing generated catalog');
  const j=JSON.parse(read(p));
  assert.equal(j.canonicalRoot,'fabric://8x8/core');
  assert.ok(Array.isArray(j.modules));
  assert.ok(Array.isArray(j.skills));
  assert.ok(!read(p).includes('BEGIN PRIVATE KEY'));
  assert.ok(!read(p).includes('sk-proj-'));
  assert.ok(!exists('dist/protected-beta/account/index.html'));
  assert.ok(!exists('dist/core/smart_router.py'));
});
test('manifest/worker/media bundles exist and preserve truthful client-only constraints',()=>{
  for(const path of ['dist/icon.svg','dist/sw.js','dist/manifest.webmanifest',
    'dist/studio/media-core.mjs','dist/studio/film-808-release-gate.mjs',
    'dist/atlas/one-fabric-public-catalog-v1.js','dist/projects/world-atlas/subject-atlas.v1.json'])
    assert.ok(exists(path),'Missing '+path);
  const m=JSON.parse(read('dist/manifest.webmanifest'));
  assert.ok(m.shortcuts.some(s=>s.url==='/studio'));
  assert.ok(m.shortcuts.some(s=>s.url==='/agents'));
  const a=JSON.parse(read('dist/projects/world-atlas/subject-atlas.v1.json'));
  assert.equal(a.realms.length,8);
  assert.equal(a.realms.reduce((sum,r)=>sum+r.topics.length,0),64);
  assert.ok(a.realms.every(r=>r.topics.every(t=>t.authority==='NONE')));
  const sw=read('dist/sw.js');
  assert.match(sw,/No fallback for authenticated or unknown routes/);
});
