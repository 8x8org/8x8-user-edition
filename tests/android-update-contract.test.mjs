import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const read = path => readFileSync(new URL('../'+path,import.meta.url),'utf8');
const manager=read('android-app/app/src/main/java/world/eightx8/user/VerifiedUpdateManager.java');
const provider=read('android-app/app/src/main/java/world/eightx8/user/VerifiedApkProvider.java');
const activity=read('android-app/app/src/main/java/world/eightx8/user/MainActivity.java');
const android=read('android-app/app/src/main/AndroidManifest.xml');
const build=read('scripts/build-vercel-static.mjs');
const latest=JSON.parse(read('updates/android/latest.json'));
test('Unpromoted release endpoint cannot silently advertise install',()=>{
 assert.equal(latest.schema,'eightx8.android.update.v1');
 assert.equal(latest.available,false);
 assert.equal(latest.apkUrl,null);
 assert.match(build,/'updates'/);
});
test('Owner must explicitly tap update and Android must approve install',()=>{
 assert.match(activity,/updates\.setOnClickListener\(/);
 assert.match(activity,/VerifiedUpdateManager\.check\(this\)/);
 assert.match(manager,/setPositiveButton\("Check"/);
 assert.match(manager,/setPositiveButton\("Install"/);
 assert.match(manager,/canRequestPackageInstalls\(\)/);
 assert.match(manager,/ACTION_MANAGE_UNKNOWN_APP_SOURCES/);
 assert.match(manager,/Intent\.ACTION_VIEW/);
 assert.ok(!manager.includes('pm install'));
 assert.ok(!manager.includes('ACTION_DELETE'));
 assert.ok(!manager.includes('uninstallPackage'));
});
test('Signing + integrity + same origin are independently checked before install',()=>{
 for(const fragment of ['SHA-256','sha256','signerSha256','getPackageArchiveInfo','getPackageInfo','getApkContentsSigners','packageName','getLongVersionCode','getPackageName()','setInstanceFollowRedirects(false)','APK_LIMIT','equals(hex(md.digest()))','verified-update.apk'])
  assert.ok(manager.includes(fragment),fragment);
 assert.match(manager,/version <= installed\.getLongVersionCode\(\)/);
 assert.match(manager,/!cert\.equals\(signer\(installed\)\)/);
 assert.match(manager,/!cert\.equals\(signer\(archive\)\)/);
 assert.match(manager,/!packageId\.equals\(archive\.packageName\)/);
});
test('Temporary update file accessible via read-only non-exported URI provider',()=>{
 assert.match(android,/android:name="\.VerifiedApkProvider"/);
 assert.match(android,/android:exported="false"/);
 assert.match(android,/android:grantUriPermissions="true"/);
 assert.match(provider,/MODE_READ_ONLY/);
 assert.match(provider,/verified-update\.apk/);
 assert.match(provider,/!\("r"\.equals\(mode\)\)/);
 assert.match(android,/REQUEST_INSTALL_PACKAGES/);
});
