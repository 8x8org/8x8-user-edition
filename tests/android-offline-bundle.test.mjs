import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const read = p => readFileSync(new URL('../'+p,import.meta.url),'utf8');
const activity=read('android-app/app/src/main/java/world/eightx8/user/MainActivity.java');
const handler=read('android-app/app/src/main/java/world/eightx8/user/PublicAssetHandler.java');
const build=read('android-app/app/build.gradle');
const webBuild=read('scripts/build-vercel-static.mjs');

test('preview loads a local trusted HTTPS asset origin, not stale external home',()=>{
 assert.match(activity,/WebViewAssetLoader.Builder/);
 assert.match(activity,/PublicAssetHandler.HOST/);
 assert.match(activity,/shouldInterceptRequest/);
 assert.match(activity,/web.loadUrl\(LOCAL_ORIGIN \+ "\/index.html\?carrier=android"\)/);
 assert.doesNotMatch(activity,/web.loadUrl\(BuildConfig.HOME_URL/);
});
test('real routes and MIME types are present for offline Studio and Agent Room',()=>{
 for(const route of ['studio/index.html','agents/index.html','stable/index.html'])assert.ok(handler.includes(route),route);
 for(const mime of ['text/html','application/javascript','image/svg+xml','application/manifest+json'])assert.ok(handler.includes(mime),mime);
 for(const file of ["'studio'", "'agents'", "'sw.js'", "'icon.svg'"])assert.ok(webBuild.includes(file),file);
});
test('untrusted URL schemes, traversals and private API routes are refused',()=>{
 assert.match(activity,/!"https"\.equals\(uri.getScheme\(\)\)/);
 assert.match(activity,/return !permittedOrigin\(request.getUrl\(\)\)/);
 assert.match(handler,/request.contains\("\.\."\)/);
 for(const fragment of ['api/','oauth/','private/','owner/'])assert.ok(handler.includes(fragment),fragment);
 assert.match(handler,/return missing\(\)/);
});
test('debug carrier build must fail closed without complete static site',()=>{
 assert.match(build,/androidx.webkit:webkit/);
 assert.match(build,/verifyEightx8PublicBundle/);
 assert.match(build,/assets.srcDir\(rootProject.file\('\.\.\/dist'\)\)/);
 assert.match(build,/dependsOn tasks.named\('verifyEightx8PublicBundle'\)/);
 assert.match(build,/Studio and Agent Room must not be the same fallback document/);
});

// Signing rotation across CI builds cannot override Android's package identity rules.
test('isolated offline acceptance never replaces existing dev or preview packages',()=>{
 assert.match(build,/offline\s*\{/);
 assert.match(build,/applicationIdSuffix '\.offline'/);
 assert.match(build,/manifestPlaceholders = \[eightx8AppLabel: '8x8 Offline'\]/);
 assert.match(build,/applicationIdSuffix '\.preview'/);
 assert.match(build,/applicationIdSuffix '\.dev'/);
});
